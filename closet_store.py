"""ユーザーごとの服画像の保存・取得・削除。

プライバシー方針:
- すべての操作は user_id を必須とし、保存先は必ず「user_id 配下」に閉じる
- 画像ID(image_id)はサーバーが生成した uuid + 拡張子のみ許可（パス区切り等は拒否）
- 公開URLは発行しない。画像は呼び出し側(サーバー)がバイト列で読み出して表示する
"""

import hashlib
import io
import os
import re
import uuid
from pathlib import Path

from PIL import Image

ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png"}
MAX_BYTES = 10 * 1024 * 1024  # 1枚あたり10MBまで
MAX_IMAGES_PER_USER = 500
_ID_RE = re.compile(r"^[0-9a-f]{32}\.(jpg|png)$")


class ClosetError(Exception):
    """ユーザーに見せてよいエラー"""


def user_id_from_subject(subject: str) -> str:
    """ログインIDから、個人情報を含まないユーザーIDを作る"""
    return hashlib.sha256(subject.encode("utf-8")).hexdigest()[:32]


def _check_user_id(user_id: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{32}", user_id or ""):
        raise ClosetError("不正なユーザーIDです")


def _check_image_id(image_id: str) -> None:
    if not _ID_RE.fullmatch(image_id or ""):
        raise ClosetError("不正な画像IDです")


def validate_image(data: bytes) -> str:
    """画像として正しいか検査し、保存用の拡張子を返す"""
    if len(data) > MAX_BYTES:
        raise ClosetError("画像サイズが大きすぎます（10MBまで）")
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()
            fmt = img.format
    except Exception:
        raise ClosetError("画像として読み込めませんでした")
    if fmt not in ALLOWED_FORMATS:
        raise ClosetError("JPEG / PNG のみ対応しています")
    return ALLOWED_FORMATS[fmt]


class LocalBackend:
    """開発用: ローカルフォルダに保存する"""

    def __init__(self, root: Path):
        self.root = root

    def _dir(self, user_id: str) -> Path:
        d = self.root / user_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def list(self, user_id):
        return sorted(
            p.name for p in self._dir(user_id).iterdir() if _ID_RE.fullmatch(p.name)
        )

    def put(self, user_id, image_id, data):
        (self._dir(user_id) / image_id).write_bytes(data)

    def get(self, user_id, image_id):
        return (self._dir(user_id) / image_id).read_bytes()

    def delete(self, user_id, image_id):
        (self._dir(user_id) / image_id).unlink(missing_ok=True)


class GCSBackend:
    """本番用: 非公開の Cloud Storage バケットに保存する"""

    def __init__(self, bucket_name: str):
        from google.cloud import storage

        self.bucket = storage.Client().bucket(bucket_name)

    def list(self, user_id):
        blobs = self.bucket.client.list_blobs(self.bucket, prefix=f"{user_id}/")
        names = (b.name.split("/", 1)[1] for b in blobs)
        return sorted(n for n in names if _ID_RE.fullmatch(n))

    def put(self, user_id, image_id, data):
        self.bucket.blob(f"{user_id}/{image_id}").upload_from_string(data)

    def get(self, user_id, image_id):
        return self.bucket.blob(f"{user_id}/{image_id}").download_as_bytes()

    def delete(self, user_id, image_id):
        blob = self.bucket.blob(f"{user_id}/{image_id}")
        if blob.exists():
            blob.delete()


class Closet:
    """1ユーザー専用のクローゼット。user_id 以外の領域には触れない"""

    def __init__(self, backend, user_id: str):
        _check_user_id(user_id)
        self._b = backend
        self._uid = user_id

    def list_ids(self) -> list[str]:
        return self._b.list(self._uid)

    def add(self, data: bytes) -> str:
        ext = validate_image(data)
        if len(self.list_ids()) >= MAX_IMAGES_PER_USER:
            raise ClosetError(f"登録できるのは{MAX_IMAGES_PER_USER}枚までです")
        image_id = uuid.uuid4().hex + ext
        self._b.put(self._uid, image_id, data)
        return image_id

    def read(self, image_id: str) -> bytes:
        _check_image_id(image_id)
        return self._b.get(self._uid, image_id)

    def delete(self, image_id: str) -> None:
        _check_image_id(image_id)
        self._b.delete(self._uid, image_id)


def make_backend():
    bucket = os.getenv("CLOSET_BUCKET")
    if bucket:
        return GCSBackend(bucket)
    return LocalBackend(Path(os.getenv("CLOSET_DIR", "closet")))

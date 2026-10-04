"""ユーザー認証と服の画像の保存（Cloud Storage / ローカル）。

保存先の構造（バケット内、ローカルなら CLOSET_DIR 内）:
  users/<ユーザー名>/auth.json      パスワードのハッシュ
  users/<ユーザー名>/closet/<ファイル名>  服の画像
CLOSET_BUCKET が設定されていれば Cloud Storage、無ければローカルフォルダを使う。
"""
import hashlib
import hmac
import json
import os
import re
import secrets
from pathlib import Path

USERNAME_RE = re.compile(r"^[a-z0-9_-]{3,32}$")
IMAGE_EXTS = (".jpg", ".jpeg", ".png")
PBKDF2_ROUNDS = 200_000


def normalize_username(name: str) -> str | None:
    """正規化したユーザー名を返す。使えない文字列なら None。"""
    name = name.strip().lower()
    return name if USERNAME_RE.fullmatch(name) else None


def safe_filename(name: str) -> str:
    """パス区切りなどを除いた安全なファイル名にする。"""
    base = os.path.basename(name.replace("\\", "/"))
    return re.sub(r"[^\w.\-]", "_", base) or "image"


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ROUNDS).hex()


class _Backend:
    """read/write/list の最小インタフェース。"""

    def read(self, key: str) -> bytes | None: ...
    def create(self, key: str, data: bytes) -> bool:
        """存在しない場合のみ作成。既に有れば False。"""
    def write(self, key: str, data: bytes) -> None: ...
    def delete(self, key: str) -> None: ...
    def list(self, prefix: str) -> list[str]: ...


class LocalBackend(_Backend):
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / key

    def read(self, key):
        p = self._path(key)
        return p.read_bytes() if p.exists() else None

    def create(self, key, data):
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(p, "xb") as f:
                f.write(data)
        except FileExistsError:
            return False
        return True

    def write(self, key, data):
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def delete(self, key):
        self._path(key).unlink(missing_ok=True)

    def list(self, prefix):
        base = self._path(prefix)
        if not base.is_dir():
            return []
        return sorted(
            str(p.relative_to(self.root)) for p in base.iterdir() if p.is_file()
        )


class GcsBackend(_Backend):
    def __init__(self, bucket_name: str):
        from google.cloud import storage

        self.bucket = storage.Client().bucket(bucket_name)

    def read(self, key):
        blob = self.bucket.blob(key)
        return blob.download_as_bytes() if blob.exists() else None

    def create(self, key, data):
        from google.api_core.exceptions import PreconditionFailed

        try:
            self.bucket.blob(key).upload_from_string(data, if_generation_match=0)
        except PreconditionFailed:
            return False
        return True

    def write(self, key, data):
        self.bucket.blob(key).upload_from_string(data)

    def delete(self, key):
        blob = self.bucket.blob(key)
        if blob.exists():
            blob.delete()

    def list(self, prefix):
        return sorted(b.name for b in self.bucket.list_blobs(prefix=prefix + "/"))


def make_backend() -> _Backend:
    bucket = os.getenv("CLOSET_BUCKET")
    if bucket:
        return GcsBackend(bucket)
    return LocalBackend(Path(os.getenv("CLOSET_DIR", "closet")))


class Store:
    def __init__(self, backend: _Backend | None = None):
        self.backend = backend or make_backend()

    # --- 認証 ---
    def register(self, username: str, password: str) -> bool:
        """新規登録。ユーザー名が既に使われていれば False。"""
        salt = secrets.token_bytes(16)
        record = {"salt": salt.hex(), "hash": _hash_password(password, salt)}
        return self.backend.create(
            f"users/{username}/auth.json", json.dumps(record).encode()
        )

    def verify(self, username: str, password: str) -> bool:
        raw = self.backend.read(f"users/{username}/auth.json")
        if raw is None:
            return False
        record = json.loads(raw)
        actual = _hash_password(password, bytes.fromhex(record["salt"]))
        return hmac.compare_digest(actual, record["hash"])

    # --- 服の画像（常にユーザー名の配下のみ操作する） ---
    def _prefix(self, username: str) -> str:
        return f"users/{username}/closet"

    def save_image(self, username: str, filename: str, data: bytes) -> None:
        self.backend.write(f"{self._prefix(username)}/{safe_filename(filename)}", data)

    def list_images(self, username: str) -> list[str]:
        """ファイル名の一覧。"""
        prefix = self._prefix(username)
        return [
            k[len(prefix) + 1 :]
            for k in self.backend.list(prefix)
            if k.lower().endswith(IMAGE_EXTS)
        ]

    def load_image(self, username: str, filename: str) -> bytes | None:
        return self.backend.read(f"{self._prefix(username)}/{safe_filename(filename)}")

    def delete_image(self, username: str, filename: str) -> None:
        self.backend.delete(f"{self._prefix(username)}/{safe_filename(filename)}")

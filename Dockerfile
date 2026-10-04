FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py common.py style.py closet_store.py step2_weather_test.py ./
COPY views/ views/
COPY .streamlit/config.toml .streamlit/config.toml

# Cloud Run は秘密設定(secrets.toml)を /app/.streamlit/ に重ねてマウントし、
# config.toml が隠れる場合があるため、テーマは環境変数でも固定する
ENV STREAMLIT_THEME_BASE=light \
    STREAMLIT_THEME_PRIMARY_COLOR=#d62976

# Cloud Run は PORT 環境変数でポートを指定してくる（既定 8080）
ENV PORT=8080
EXPOSE 8080

CMD streamlit run app.py \
    --server.port=${PORT} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false

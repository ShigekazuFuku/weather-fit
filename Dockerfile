FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py step2_weather_test.py ./

# Cloud Run は PORT 環境変数でポートを指定してくる（既定 8080）
ENV PORT=8080
EXPOSE 8080

CMD streamlit run app.py \
    --server.port=${PORT} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false

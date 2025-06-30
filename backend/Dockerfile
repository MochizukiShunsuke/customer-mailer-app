# backend/Dockerfile

# ベースイメージとしてPython 3.9 を使用
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存ライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY ./src .

# コンテナがリッスンするポートを指定
EXPOSE 5000

# アプリケーションを実行
CMD ["python", "app.py"]
# frontend/Dockerfile

# ベースイメージとしてNode.js 20 を使用
FROM node:20

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係のファイルを先にコピー
COPY package.json ./

# 依存関係をコンテナ内でインストール
RUN npm install

# ソースコードをすべてコピー
COPY . .

# Angularが使用するポートを開放
EXPOSE 4200

# シンプルで安定した起動コマンド
CMD ["npm", "start"]

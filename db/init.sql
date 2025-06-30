-- db/init.sql

-- customers テーブルの作成
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- templates テーブルの作成
CREATE TABLE IF NOT EXISTS templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- settings テーブルの作成
CREATE TABLE IF NOT EXISTS settings (
    id INT PRIMARY KEY,
    sender_email VARCHAR(255),
    sender_password VARCHAR(255)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- attachments テーブルの作成
CREATE TABLE IF NOT EXISTS attachments (
    id INT PRIMARY KEY,
    original_filename VARCHAR(255),
    saved_path VARCHAR(255)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- データを投入 (初期データ)
-- ★★★ ここを修正: bodyに'{name} 'だけを設定 ★★★
INSERT INTO templates (id, title, body)
VALUES (1, '', '{name} ')
ON DUPLICATE KEY UPDATE 
    title=VALUES(title), 
    body=VALUES(body);

INSERT INTO settings (id, sender_email, sender_password)
VALUES (1, '', '')
ON DUPLICATE KEY UPDATE 
    sender_email=VALUES(sender_email), 
    sender_password=VALUES(sender_password);

INSERT INTO attachments (id, original_filename, saved_path)
VALUES (1, NULL, NULL)
ON DUPLICATE KEY UPDATE 
    original_filename=VALUES(original_filename),
    saved_path=VALUES(saved_path);

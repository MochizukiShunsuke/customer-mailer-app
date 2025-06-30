# backend/src/app.py

import os
import smtplib
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase # ★★★ 伝統的な方法で必要になります ★★★
from email import encoders         # ★★★ 伝統的な方法で必要になります ★★★
from email.header import Header
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# -----------------
# 初期設定 (変更なし)
# -----------------
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
host = os.environ.get('MYSQL_HOST')
dbname = os.environ.get('MYSQL_DATABASE')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{user}:{password}@{host}/{dbname}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------
# データベースモデル定義 (変更なし)
# -----------------
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(255))
    sender_password = db.Column(db.String(255))

class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255))
    saved_path = db.Column(db.String(255))

# -----------------
# APIエンドポイント (メール送信以外は変更なし)
# -----------------
@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = db.session.execute(db.select(Customer)).scalars().all()
    return jsonify([{'id': c.id, 'name': c.name, 'email': c.email} for c in customers])

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.json
    if not data or not 'name' in data or not 'email' in data:
        return jsonify({'error': '名前とメールアドレスは必須です'}), 400
    existing_customer = db.session.execute(db.select(Customer).where(Customer.email == data['email'])).scalar_one_or_none()
    if existing_customer:
        return jsonify({'error': 'このメールアドレスは既に使用されています'}), 409
    new_customer = Customer(name=data['name'], email=data['email'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'id': new_customer.id, 'name': new_customer.name, 'email': new_customer.email}), 201

@app.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({'error': '指定された顧客は見つかりません'}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f'顧客ID:{id}を削除しました。'})

@app.route('/api/templates/1', methods=['GET'])
def get_template():
    template = db.session.get(Template, 1)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    return jsonify({'id': template.id, 'title': template.title, 'body': template.body})

@app.route('/api/templates/1', methods=['PUT'])
def update_template():
    template = db.session.get(Template, 1)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    data = request.json
    template.title = data.get('title', template.title)
    template.body = data.get('body', template.body)
    db.session.commit()
    return jsonify({'id': template.id, 'title': template.title, 'body': template.body})

@app.route('/api/settings/1', methods=['GET'])
def get_settings():
    settings = db.session.get(Setting, 1)
    if not settings:
        return jsonify({'error': 'Settings not found'}), 404
    return jsonify({'sender_email': settings.sender_email or '', 'sender_password': settings.sender_password or ''})

@app.route('/api/settings/1', methods=['PUT'])
def update_settings():
    settings = db.session.get(Setting, 1)
    if not settings:
        return jsonify({'error': 'Settings not found'}), 404
    data = request.json
    settings.sender_email = data.get('sender_email', settings.sender_email)
    settings.sender_password = data.get('sender_password', settings.sender_password)
    db.session.commit()
    return jsonify({'message': '送信元設定を保存しました。'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        attachment = db.session.get(Attachment, 1)
        if not attachment:
            attachment = Attachment(id=1)
            db.session.add(attachment)
        attachment.original_filename = filename
        attachment.saved_path = filepath
        db.session.commit()
        return jsonify({'message': f'{filename} をアップロードしました。'})

@app.route('/api/attachment/1', methods=['GET'])
def get_attachment():
    attachment = db.session.get(Attachment, 1)
    if attachment and attachment.original_filename:
        return jsonify({'filename': attachment.original_filename})
    return jsonify({'filename': None})


@app.route('/api/send', methods=['POST'])
def send_emails():
    customers = db.session.execute(db.select(Customer)).scalars().all()
    if not customers:
        return jsonify({'error': '送信先の顧客がいません'}), 400
    template = db.session.get(Template, 1)
    if not template:
        return jsonify({'error': 'メールテンプレートが見つかりません'}), 400
    settings = db.session.get(Setting, 1)
    if not settings or not settings.sender_email or not settings.sender_password:
        return jsonify({'error': '送信元のメールアドレスまたはパスワードが設定されていません。'}), 500

    sender_email = settings.sender_email
    sender_password = settings.sender_password
    smtp_server = "smtp.gmail.com"
    port = 465
    attachment_info = db.session.get(Attachment, 1)

    errors = {}
    success_count = 0
    try:
        server = smtplib.SMTP_SSL(smtp_server, port)
        server.login(sender_email, sender_password)
        
        for customer in customers:
            try:
                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = customer.email
                message['Subject'] = Header(template.title, 'utf-8')

                body = template.body.replace('{name}', customer.name)
                message.attach(MIMEText(body, 'plain', 'utf-8'))

                # ★★★ ここからが修正部分 ★★★
                # 添付ファイル処理を、伝統的で確実な方法に戻しました
                if attachment_info and attachment_info.saved_path:
                    filepath = attachment_info.saved_path
                    if os.path.exists(filepath):
                        ctype, encoding = mimetypes.guess_type(filepath)
                        if ctype is None or encoding is not None:
                            ctype = 'application/octet-stream'
                        maintype, subtype = ctype.split('/', 1)

                        with open(filepath, 'rb') as fp:
                            # 添付ファイル用の部品（MIMEBase）を作成
                            part = MIMEBase(maintype, subtype)
                            # ファイルの中身を読み込ませる
                            part.set_payload(fp.read())
                        # Base64でエンコードする
                        encoders.encode_base64(part)
                        # ヘッダー情報を追加
                        part.add_header('Content-Disposition', 'attachment', filename=attachment_info.original_filename)
                        # メッセージに部品を合体させる
                        message.attach(part)
                # ★★★ ここまでが修正部分 ★★★

                server.sendmail(sender_email, customer.email, message.as_string())
                success_count += 1
            except Exception as e:
                # (デバッグ用のprint文は残しておきます)
                print(f"--- メール送信エラー発生 ---", flush=True)
                print(f"宛先: {customer.email}", flush=True)
                print(f"エラー内容: {e}", flush=True)
                print(f"--------------------------", flush=True)
                errors[customer.email] = str(e)

        server.quit()
        
    except Exception as e:
        print(f"--- SMTPサーバー接続エラー ---", flush=True)
        print(f"エラー内容: {e}", flush=True)
        print(f"----------------------------", flush=True)
        return jsonify({'error': f'メールサーバーへの接続に失敗しました: {e}'}), 500
        
    if errors:
        return jsonify({
            'message': f'{success_count}件の送信に成功し、{len(errors)}件でエラーが発生しました。',
            'errors': errors
        }), 207
    
    return jsonify({'message': f'全{success_count}件のメールを正常に送信しました。'})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)

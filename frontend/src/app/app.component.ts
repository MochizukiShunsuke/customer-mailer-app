// frontend/src/app/app.component.ts

import { Component, OnInit } from '@angular/core';
import { ApiService } from './api.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
    settings = { sender_email: '', sender_password: '' };
    customers: any[] = [];
    newCustomer = { name: '', email: '' };
    template = { title: '', body: '' };
    sending = false;
    notification = { message: '', type: '' };

    // ★★★ ファイル添付用のプロパティを追加 ★★★
    selectedFile: File | null = null;
    currentAttachment: string | null = null;

    constructor(private apiService: ApiService) { }

    ngOnInit() {
        this.loadCustomers();
        this.loadTemplate();
        this.loadSettings();
        this.loadAttachment(); // ★★★ 初期化時に添付ファイル情報も読み込む ★★★
    }

    // ★★★ ここからが添付ファイル関連のメソッド ★★★
    loadAttachment() {
        this.apiService.getAttachment().subscribe(
            (data: any) => {
                this.currentAttachment = data.filename;
            }
            // エラーは通知しない（ファイルがないのが普通なため）
        );
    }

    onFileSelected(event: any): void {
        const file = event.target.files[0];
        if (file) {
            this.selectedFile = file;
        }
    }

    onUpload(): void {
        if (this.selectedFile) {
            this.apiService.uploadFile(this.selectedFile).subscribe(
                (response: any) => {
                    this.showNotification(response.message, 'success');
                    // アップロード成功後、選択状態をリセットし、現在の添付ファイルを再読み込み
                    this.selectedFile = null;
                    this.loadAttachment();
                },
                (error: any) => {
                    this.showNotification('ファイルのアップロードに失敗しました。', 'error');
                }
            );
        }
    }
    // ★★★ ここまでが添付ファイル関連のメソッド ★★★

    loadSettings() {
        this.apiService.getSettings().subscribe(
            (data: any) => { this.settings = data; },
            (error: any) => { this.showNotification('送信元設定の読み込みに失敗しました。', 'error'); }
        );
    }

    saveSettings() {
        this.apiService.updateSettings(this.settings).subscribe(
            (response: any) => { this.showNotification(response.message, 'success'); },
            (error: any) => { this.showNotification('送信元設定の保存に失敗しました。', 'error'); }
        );
    }

    loadCustomers() {
        this.apiService.getCustomers().subscribe(
            (data: any[]) => { this.customers = data; },
            (error: any) => { this.showNotification('顧客リストの読み込みに失敗しました。', 'error'); }
        );
    }

    addCustomer() {
        this.apiService.addCustomer(this.newCustomer).subscribe(
            (data: any) => {
                this.customers.push(data);
                this.newCustomer = { name: '', email: '' };
                this.showNotification('顧客を追加しました。', 'success');
            },
            (error: any) => {
                const errorMessage = error.error?.error || '顧客の追加に失敗しました。';
                this.showNotification(errorMessage, 'error');
            }
        );
    }

    deleteCustomer(id: number) {
        if (confirm('この顧客を本当に削除してもよろしいですか？')) {
            this.apiService.deleteCustomer(id).subscribe(
                () => {
                    this.customers = this.customers.filter(c => c.id !== id);
                    this.showNotification('顧客を削除しました。', 'success');
                },
                (error: any) => {
                    this.showNotification('顧客の削除に失敗しました。', 'error');
                }
            );
        }
    }

    loadTemplate() {
        this.apiService.getTemplate().subscribe(
            (data: any) => { this.template = data; },
            (error: any) => { this.showNotification('テンプレートの読み込みに失敗しました。', 'error'); }
        );
    }

    updateTemplate() {
        this.apiService.updateTemplate(this.template).subscribe(
            () => { this.showNotification('テンプレートを保存しました。', 'success'); },
            (error: any) => { this.showNotification('テンプレートの保存に失敗しました。', 'error'); }
        );
    }

    sendEmails() {
        if (confirm(`現在の顧客リスト全員（${this.customers.length}人）にメールを送信しますか？`)) {
            this.sending = true;
            this.apiService.sendEmails().subscribe(
                (response: any) => {
                    this.showNotification(response.message, 'success');
                    this.sending = false;
                },
                (error: any) => {
                    const errorMessage = error.error?.message || error.error?.error || 'メール送信中にエラーが発生しました。';
                    this.showNotification(errorMessage, 'error');
                    this.sending = false;
                }
            );
        }
    }

    showNotification(message: string, type: 'success' | 'error') {
        this.notification.message = message;
        this.notification.type = type;
        setTimeout(() => {
            this.notification.message = '';
        }, 5000);
    }
}

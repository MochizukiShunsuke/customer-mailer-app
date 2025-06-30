// frontend/src/app/api.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private apiUrl = 'http://localhost:5000/api';

    constructor(private http: HttpClient) { }

    // (既存のメソッドは変更なし)
    getCustomers(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/customers`);
    }
    addCustomer(customer: { name: string; email: string }): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/customers`, customer);
    }
    deleteCustomer(id: number): Observable<any> {
        return this.http.delete<any>(`${this.apiUrl}/customers/${id}`);
    }
    getTemplate(): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/templates/1`);
    }
    updateTemplate(template: { title: string; body: string }): Observable<any> {
        return this.http.put<any>(`${this.apiUrl}/templates/1`, template);
    }
    getSettings(): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/settings/1`);
    }
    updateSettings(settings: { sender_email: string; sender_password: string }): Observable<any> {
        return this.http.put<any>(`${this.apiUrl}/settings/1`, settings);
    }
    sendEmails(): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/send`, {});
    }

    // ★★★ ここからが追加部分 ★★★

    // ファイルをアップロードするメソッド
    uploadFile(file: File): Observable<any> {
        const formData: FormData = new FormData();
        formData.append('file', file, file.name);
        return this.http.post(`${this.apiUrl}/upload`, formData);
    }

    // 現在の添付ファイル情報を取得するメソッド
    getAttachment(): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/attachment/1`);
    }

    // ★★★ ここまでが追加部分 ★★★
}

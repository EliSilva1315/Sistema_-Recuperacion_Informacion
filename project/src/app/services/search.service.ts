import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private _hasResults = false;
  private backendUrl = 'http://localhost:5000';
  
  constructor(private http: HttpClient) {}
  
  search(query: string): Observable<any> {
    this._hasResults = true;
    
    // Conecta con tu backend Python
    return this.http.post(`${this.backendUrl}/search`, { query: query });
  }
  
  hasResults(): boolean {
    return this._hasResults;
  }
}
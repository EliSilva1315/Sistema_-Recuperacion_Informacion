import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private _hasResults = false;
  private backendUrl = 'http://localhost:3000'; // Cambiado a puerto 3000
  
  constructor(private http: HttpClient) {}
  
  search(query: string): Observable<any> {
    this._hasResults = true;
    
    return this.http.post(`${this.backendUrl}/search`, { query: query });
  }
  
  hasResults(): boolean {
    return this._hasResults;
  }
}
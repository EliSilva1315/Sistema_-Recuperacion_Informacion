import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private _hasResults = false;
  
  constructor() {}
  
  search(query: string): Observable<any[]> {
    // This is a mock service that would normally call your backend API
    // For now, we'll just return an empty array and let the component
    // generate mock results
    
    // Set hasResults to true when a search is performed
    this._hasResults = true;
    
    // Return an empty array after a small delay to simulate API call
    return of([]).pipe(delay(500));
  }
  
  hasResults(): boolean {
    return this._hasResults;
  }
}
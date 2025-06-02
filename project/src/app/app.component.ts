import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from './components/layout/header/header.component';
import { FooterComponent } from './components/layout/footer/footer.component';
import { SearchComponent } from './components/search/search.component';
import { ResultsComponent } from './components/results/results.component';
import { SearchService } from './services/search.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    HeaderComponent,
    FooterComponent,
    SearchComponent,
    ResultsComponent
  ],
  template: `
    <div class="search-layout" [class.has-results]="hasResults">
      <app-header></app-header>

      <div class="search-content" [class.centered]="!hasResults">
        <div class="container">
          <app-search (searchSubmitted)="onSearchSubmitted($event)"></app-search>
          <app-results *ngIf="hasResults" [searchResults]="searchResults" [searchQuery]="searchQuery"></app-results>
        </div>
      </div>

      <app-footer></app-footer>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      min-height: 100vh;
    }
  `]
})
export class AppComponent {
  hasResults = false;
  searchResults: any[] = [];
  searchQuery = '';

  constructor(private searchService: SearchService) {}

  onSearchSubmitted(query: string) {
    this.searchQuery = query;
    
    if (query.trim() === '') {
      this.hasResults = false;
      this.searchResults = [];
      return;
    }
    
    // In a real application, this would be calling your backend API
    this.searchService.search(query).subscribe(results => {
      this.searchResults = results;
      this.hasResults = true;
    });
  }
}
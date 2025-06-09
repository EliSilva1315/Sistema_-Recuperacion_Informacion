import { Component, Output, EventEmitter, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SearchService } from '../../services/search.service';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="search-container" [class.has-results]="hasResults">
      <div class="search-header">
        <h1>Búsqueda <strong>Inteligente</strong></h1>
        <p class="lead">Encuentra lo que buscas con precisión y velocidad</p>
      </div>
      
      <div class="search-form">
        <div class="search-input-container">
          <input 
            type="text" 
            class="search-input" 
            placeholder="Buscar..."
            [(ngModel)]="searchQuery"
            (keyup.enter)="onSearch()"
            autocomplete="off"
            [autofocus]="!hasResults"
          >
          <i class="fas fa-search search-icon"></i>
          
          <button 
            class="clear-button" 
            [class.visible]="searchQuery.length > 0"
            (click)="clearSearch()"
          >
            <i class="fas fa-times"></i>
          </button>
        
          
          <button 
            class="search-button"
            [disabled]="searchQuery.trim().length === 0"
            (click)="onSearch()"
          >
            Buscar
          </button>
        </div>
      </div>
      
      <div class="search-suggestions" *ngIf="!hasResults && suggestions.length > 0">
        <h4>Búsquedas populares:</h4>
        <div class="suggestion-list">
          <div 
            class="suggestion-item" 
            *ngFor="let suggestion of suggestions"
            (click)="useSearchSuggestion(suggestion)"
          >
            {{ suggestion }}
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class SearchComponent {
  @Output() searchSubmitted = new EventEmitter<string>();
  
  searchQuery = '';
  hasResults = false;
  isListening = false;
  suggestions: string[] = [
    'call of duty', 
    'battle royale', 
    'multiplayer games',
    'first person shooter',
    'gaming graphics',
    'game mechanics'
  ];
  
  constructor(private searchService: SearchService) {
    this.hasResults = this.searchService.hasResults();
  }
  
  onSearch() {
    if (this.searchQuery.trim() === '') return;
    this.searchSubmitted.emit(this.searchQuery);
    this.hasResults = true;
  }
  
  clearSearch() {
    this.searchQuery = '';
    this.searchSubmitted.emit('');
    this.hasResults = false;
  }
  
  useSearchSuggestion(suggestion: string) {
    this.searchQuery = suggestion;
    this.onSearch();
  }
  
}
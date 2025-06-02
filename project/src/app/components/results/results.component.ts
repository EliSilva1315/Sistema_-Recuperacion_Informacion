import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="results-container visible">
      <div class="loader-container" [class.visible]="loading">
        <div class="loader">
          <div class="loader-circle"></div>
          <div class="loader-circle"></div>
        </div>
      </div>
      
      <div *ngIf="!loading">
        <div class="results-info">
          <div class="results-count">
            Aproximadamente <strong>{{ totalResults }}</strong> resultados para <strong>"{{ searchQuery }}"</strong> ({{ searchTime }} segundos)
          </div>
        </div>
        
        <div class="results-list">
          <ng-container *ngIf="displayedResults.length > 0; else noResults">
            <div *ngFor="let result of displayedResults" class="result-item" [class.featured]="result.featured">
              <a [href]="result.url" class="result-title" target="_blank">
                <span *ngIf="result.featured" class="featured-badge">Destacado</span>
                {{ result.title }}
              </a>
              <span class="result-url">{{ result.url }}</span>
              <p class="result-description">{{ result.description }}</p>
            </div>
          </ng-container>
          
          <ng-template #noResults>
            <div class="result-item-empty">
              <div class="empty-icon">
                <i class="fas fa-search"></i>
              </div>
              <h3>No se encontraron resultados</h3>
              <p>No pudimos encontrar coincidencias para "{{ searchQuery }}". Por favor, intenta con otras palabras clave o revisa la ortografía.</p>
              <button class="btn btn-primary" (click)="clearSearch()">Limpiar búsqueda</button>
            </div>
          </ng-template>
        </div>
        
        <div class="pagination" *ngIf="displayedResults.length > 0">
          <button 
            class="pagination-button pagination-prev" 
            [disabled]="currentPage === 1"
            (click)="changePage(currentPage - 1)"
          >
            <i class="fas fa-chevron-left"></i> Anterior
          </button>
          
          <ng-container *ngFor="let page of getPageNumbers()">
            <button 
              class="pagination-button" 
              [class.active]="page === currentPage"
              (click)="changePage(page)"
            >
              {{ page }}
            </button>
          </ng-container>
          
          <button 
            class="pagination-button pagination-next" 
            [disabled]="currentPage === totalPages"
            (click)="changePage(currentPage + 1)"
          >
            Siguiente <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class ResultsComponent implements OnChanges {
  @Input() searchResults: any[] = [];
  @Input() searchQuery = '';
  
  loading = true;
  currentPage = 1;
  resultsPerPage = 5;
  totalResults = 0;
  totalPages = 1;
  displayedResults: any[] = [];
  searchTime = '0.2';
  
  ngOnChanges(changes: SimpleChanges) {
    if (changes['searchQuery'] || changes['searchResults']) {
      this.loading = true;
      setTimeout(() => {
        this.processResults();
        this.loading = false;
      }, 800);
    }
  }
  
  processResults() {
    if (this.searchResults && this.searchResults.length > 0) {
      this.totalResults = this.searchResults.length;
    } else {
      this.generateMockResults();
    }
    this.updatePagination();
  }
  
  generateMockResults() {
    const query = this.searchQuery.toLowerCase();
    this.searchResults = [];
    
    this.addMockResult(
      'Búsqueda Inteligente con IA - Guía Completa',
      'https://example.com/busqueda-inteligente',
      'Aprende todo sobre los sistemas de búsqueda inteligente potenciados por IA. Esta guía cubre los conceptos básicos y avanzados.',
      new Date('2025-01-15'),
      true
    );
    
    for (let i = 0; i < 7; i++) {
      this.addMockResult(
        `${this.searchQuery} - Resultado ${i + 2}`,
        `https://example.com/resultado-${i + 2}`,
        `Este es un resultado de búsqueda para "${this.searchQuery}". Contiene información relacionada con tu búsqueda.`,
        new Date(Date.now() - Math.random() * 10000000000)
      );
    }
    
    this.totalResults = this.searchResults.length;
  }
  
  addMockResult(title: string, url: string, description: string, date: Date, featured: boolean = false) {
    this.searchResults.push({
      title,
      url,
      description,
      date,
      featured
    });
  }
  
  updatePagination() {
    this.totalPages = Math.ceil(this.searchResults.length / this.resultsPerPage);
    this.currentPage = Math.min(this.currentPage, this.totalPages);
    
    const startIndex = (this.currentPage - 1) * this.resultsPerPage;
    this.displayedResults = this.searchResults.slice(startIndex, startIndex + this.resultsPerPage);
  }
  
  changePage(page: number) {
    this.currentPage = page;
    this.updatePagination();
    
    const resultsElement = document.querySelector('.results-container');
    if (resultsElement) {
      resultsElement.scrollIntoView({ behavior: 'smooth' });
    }
  }
  
  getPageNumbers(): number[] {
    const pages: number[] = [];
    const maxPagesToShow = 5;
    
    if (this.totalPages <= maxPagesToShow) {
      for (let i = 1; i <= this.totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (this.currentPage <= 3) {
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
      } else if (this.currentPage >= this.totalPages - 2) {
        for (let i = this.totalPages - 4; i <= this.totalPages; i++) {
          pages.push(i);
        }
      } else {
        for (let i = this.currentPage - 2; i <= this.currentPage + 2; i++) {
          pages.push(i);
        }
      }
    }
    
    return pages;
  }
  
  clearSearch() {
    window.location.reload();
  }
}
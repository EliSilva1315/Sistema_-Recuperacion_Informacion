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
            <div *ngFor="let result of displayedResults" class="result-item">
              <a [href]="result.url || '#'" class="result-title" target="_blank">
                <span class="similarity-score">{{ (result.similarity_score * 100).toFixed(1) }}% coincidencia</span>
                {{ result.title || 'Documento ' + result.id }}
              </a>
              <span class="result-url" *ngIf="result.url">{{ result.url }}</span>
              <p class="result-description">
                {{ result.preview || result.text_original?.substring(0, 200) + '...' || 'Sin descripción disponible' }}
              </p>
              <div class="result-meta">
                <span class="result-rank">Posición: {{ result.rank }}</span>
                <span class="result-score">Score: {{ result.similarity_score?.toFixed(3) }}</span>
              </div>
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
  @Input() searchResponse: any = null; // Nueva propiedad para recibir toda la respuesta
  
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
      }, 500); // Reducido para mostrar resultados más rápido
    }
  }
  
  processResults() {
    if (this.searchResults && this.searchResults.length > 0) {
      // Usar datos reales del backend
      this.totalResults = this.searchResults.length;
      console.log('📊 Procesando resultados del backend:', this.searchResults);
    } else {
      this.totalResults = 0;
    }
    this.updatePagination();
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
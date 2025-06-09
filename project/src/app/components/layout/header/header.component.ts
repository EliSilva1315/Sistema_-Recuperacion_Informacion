import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header class="app-header">
      <div class="header-container">
        <a href="/" class="logo">
          <span>Búsqueda <strong>Inteligente</strong></span>
        </a>
        
        <div class="header-nav">
          <nav class="nav-links">
          </nav>
        </div>
      </div>
    </header>
  `,
  styles: []
})
export class HeaderComponent {}
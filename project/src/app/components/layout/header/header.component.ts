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
        
        <div class="header-actions">
          <button class="action-button" title="Configuración">
            <i class="fas fa-cog"></i>
          </button>
          <div class="user-menu">
            <button class="user-button">
              <div class="user-avatar">
                <img src="https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=100" alt="Usuario">
              </div>
              <span class="user-name">Usuario</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  `,
  styles: []
})
export class HeaderComponent {}
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <footer class="app-footer">
      <div class="footer-container">
        <div class="footer-content">
          <div class="footer-section">
            <h4>About</h4>
            <ul>
              <li><a href="#">Facultad de Ingeniería en Sistemas</a></li>
              <li><a href="#">Ingeniería en Ciencias de la Computación</a></li>
              <li><a href="#">Recuperación de la Información</a></li>
              <li><a href="#">Proyecto I Bimestre</a></li>
            </ul>
          </div>
          
          
          <div class="footer-section">
            <h4>Developers</h4>
            <ul>
              <li><a href="#">Elias Bolaños</a></li>
              <li><a href="#">Elizabeth Silva</a></li>
              <li><a href="#">Andrés Suarez</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            
            <div class="social-links">
              <a href="#"><i class="fab fa-twitter"></i></a>
              <a href="#"><i class="fab fa-facebook"></i></a>
              <a href="#"><i class="fab fa-instagram"></i></a>
            </div>
            
          </div>
        </div>
        
        <div class="footer-bottom">
          <div class="copyright">
            &copy; 2025 Búsqueda Inteligente. Todos los derechos reservados.
          </div>
          
        </div>
      </div>
    </footer>
  `,
  styles: []
})
export class FooterComponent {}
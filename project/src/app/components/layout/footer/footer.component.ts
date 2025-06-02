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
              <li><a href="#">About SearchEngine</a></li>
              <li><a href="#">How Search works</a></li>
              <li><a href="#">Privacy</a></li>
              <li><a href="#">Terms</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h4>Business</h4>
            <ul>
              <li><a href="#">Advertising</a></li>
              <li><a href="#">Business Solutions</a></li>
              <li><a href="#">Work with us</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h4>Developers</h4>
            <ul>
              <li><a href="#">Search API</a></li>
              <li><a href="#">Documentation</a></li>
              <li><a href="#">Status Dashboard</a></li>
              <li><a href="#">Contribute</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h4>Connect</h4>
            <p>Follow us on social media</p>
            <div class="social-links">
              <a href="#"><i class="fab fa-twitter"></i></a>
              <a href="#"><i class="fab fa-facebook"></i></a>
              <a href="#"><i class="fab fa-instagram"></i></a>
              <a href="#"><i class="fab fa-github"></i></a>
            </div>
            
            <div class="language-selector">
              <i class="fas fa-globe"></i>
              <select>
                <option value="en">English</option>
                <option value="es">Español</option>
                <option value="fr">Français</option>
                <option value="de">Deutsch</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="footer-bottom">
          <div class="copyright">
            &copy; 2025 SearchEngine. All rights reserved.
          </div>
          
          <div class="footer-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Cookie Policy</a>
          </div>
        </div>
      </div>
    </footer>
  `,
  styles: []
})
export class FooterComponent {}
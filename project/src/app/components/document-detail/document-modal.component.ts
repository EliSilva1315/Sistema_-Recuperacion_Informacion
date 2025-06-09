import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-document-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="modal-backdrop" (click)="onClose()"></div>
    <div class="modal-content" role="dialog" aria-modal="true" tabindex="-1">
      <button class="close-btn" (click)="onClose()" aria-label="Cerrar">&times;</button>
      <h2 class="modal-title">{{ title }}</h2>
      <div class="modal-divider"></div>
      <div class="modal-text">{{ text }}</div>
    </div>
  `,
  styles: [`
    .modal-backdrop {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.5);
      z-index: 1000;
      transition: background 0.2s;
    }
    .modal-content {
      position: fixed;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%);
      background: #fff;
      padding: 2.5rem 2rem 2rem 2rem;
      border-radius: 14px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.18);
      z-index: 1001;
      max-width: 520px;
      width: 92vw;
      min-height: 180px;
      outline: none;
      animation: modalFadeIn 0.25s cubic-bezier(.4,0,.2,1);
      display: flex;
      flex-direction: column;
      gap: 1.2rem;
    }
    @keyframes modalFadeIn {
      from { opacity: 0; transform: translate(-50%, -60%); }
      to { opacity: 1; transform: translate(-50%, -50%); }
    }
    .close-btn {
      position: absolute;
      top: 1.1rem;
      right: 1.2rem;
      background: none;
      border: none;
      font-size: 2.1rem;
      color: #888;
      cursor: pointer;
      transition: color 0.15s;
      z-index: 2;
    }
    .close-btn:hover, .close-btn:focus {
      color: #d32f2f;
      outline: none;
    }
    .modal-title {
      margin: 0 0 0.2em 0;
      font-size: 1.45rem;
      font-weight: 600;
      color: #222;
      text-align: left;
      line-height: 1.2;
    }
    .modal-divider {
      width: 100%;
      height: 2px;
      background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
      border-radius: 2px;
      margin-bottom: 0.5rem;
    }
    .modal-text {
      font-size: 1.08rem;
      color: #333;
      line-height: 1.7;
      max-height: 340px;
      overflow-y: auto;
      white-space: pre-line;
      padding-right: 2px;
      text-align: left;
    }
    @media (max-width: 600px) {
      .modal-content {
        padding: 1.2rem 0.7rem 1.2rem 0.7rem;
        max-width: 98vw;
      }
      .modal-title {
        font-size: 1.1rem;
      }
    }
  `]
})
export class DocumentModalComponent {
  @Input() title: string = '';
  @Input() text: string = '';
  @Output() close = new EventEmitter<void>();

  onClose() {
    this.close.emit();
  }
}

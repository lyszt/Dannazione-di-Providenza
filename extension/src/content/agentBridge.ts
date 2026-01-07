/**
 * Dannazione - Agent Bridge Content Script
 * Bridges web pages with the alive agent, providing overlay UI and interaction
 */

import browser from 'webextension-polyfill';
import './agentBridge.css';

interface OverlayState {
  visible: boolean;
  content: string;
  type: 'idle' | 'processing' | 'result' | 'error';
}

class AgentBridge {
  private overlay: HTMLElement | null = null;
  private state: OverlayState = {
    visible: false,
    content: '',
    type: 'idle',
  };

  constructor() {
    this.initialize();
  }

  private initialize() {
    console.log('[AgentBridge] Initializing on', window.location.href);
    this.createOverlay();
    this.setupMessageListeners();
    this.setupPageListeners();
  }

  private createOverlay() {
    if (this.overlay) return;

    this.overlay = document.createElement('div');
    this.overlay.id = 'dannazione-agent-overlay';
    this.overlay.className = 'agent-overlay hidden';

    this.overlay.innerHTML = `
      <div class="agent-overlay-content">
        <div class="agent-header">
          <span class="agent-title">Dannazione</span>
          <button class="agent-close" id="agent-close-btn">×</button>
        </div>
        <div class="agent-body" id="agent-body">
          <div class="agent-idle">
            <div class="agent-pulse"></div>
            <p>Agent ready</p>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(this.overlay);

    // Setup close button
    const closeBtn = this.overlay.querySelector('#agent-close-btn');
    closeBtn?.addEventListener('click', () => this.hideOverlay());
  }

  private setupMessageListeners() {
    browser.runtime.onMessage.addListener((message) => {
      console.log('[AgentBridge] Received message:', message);

      switch (message.type) {
        case 'GET_SELECTED_TEXT':
          return Promise.resolve({ text: this.getSelectedText() });

        case 'TRANSLATION_RESULT':
          this.showTranslationResult(message.result);
          break;

        case 'OCR_RESULT':
          this.showOCRResult(message.result);
          break;

        case 'AGENT_RESPONSE':
          this.showAgentResponse(message.response);
          break;

        case 'SHOW_PROCESSING':
          this.showProcessing(message.message);
          break;

        case 'TOGGLE_AGENT_OVERLAY':
          this.toggleOverlay();
          break;
      }

      return false;
    });
  }

  private setupPageListeners() {
    // Listen for text selection
    document.addEventListener('mouseup', () => {
      const selectedText = this.getSelectedText();
      if (selectedText.length > 0) {
        // Store selected text for quick access
        this.storeSelection(selectedText);
      }
    });

    // Listen for keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Ctrl+Shift+A - Toggle overlay
      if (e.ctrlKey && e.shiftKey && e.key === 'A') {
        e.preventDefault();
        this.toggleOverlay();
      }

      // Ctrl+Shift+T - Quick translate
      if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        const text = this.getSelectedText();
        if (text) {
          this.requestTranslation(text);
        }
      }
    });
  }

  private getSelectedText(): string {
    return window.getSelection()?.toString().trim() || '';
  }

  private storeSelection(text: string) {
    browser.storage.local.set({ lastSelection: text });
  }

  private showOverlay() {
    if (!this.overlay) return;
    this.overlay.classList.remove('hidden');
    this.state.visible = true;
  }

  private hideOverlay() {
    if (!this.overlay) return;
    this.overlay.classList.add('hidden');
    this.state.visible = false;
  }

  private toggleOverlay() {
    if (this.state.visible) {
      this.hideOverlay();
    } else {
      this.showOverlay();
    }
  }

  private updateOverlayContent(html: string, type: OverlayState['type']) {
    const body = this.overlay?.querySelector('#agent-body');
    if (!body) return;

    body.innerHTML = html;
    this.state.content = html;
    this.state.type = type;
  }

  private showProcessing(message: string) {
    this.showOverlay();
    this.updateOverlayContent(
      `
      <div class="agent-processing">
        <div class="agent-spinner"></div>
        <p>${message}</p>
      </div>
      `,
      'processing'
    );
  }

  private showTranslationResult(result: any) {
    this.showOverlay();
    this.updateOverlayContent(
      `
      <div class="agent-result">
        <h3>Translation</h3>
        <div class="result-section">
          <strong>Original:</strong>
          <p>${result.original}</p>
        </div>
        <div class="result-section">
          <strong>Translated:</strong>
          <p class="translation">${result.translated}</p>
        </div>
        ${
          result.alternatives
            ? `
          <div class="result-section">
            <strong>Alternatives:</strong>
            <ul>
              ${result.alternatives.map((alt: string) => `<li>${alt}</li>`).join('')}
            </ul>
          </div>
        `
            : ''
        }
      </div>
      `,
      'result'
    );
  }

  private showOCRResult(result: any) {
    this.showOverlay();
    this.updateOverlayContent(
      `
      <div class="agent-result">
        <h3>OCR Result</h3>
        <div class="result-section">
          <strong>Detected Text:</strong>
          <div class="ocr-text">${result.text}</div>
        </div>
        ${
          result.confidence
            ? `
          <div class="result-section">
            <strong>Confidence:</strong>
            <span class="confidence">${Math.round(result.confidence * 100)}%</span>
          </div>
        `
            : ''
        }
        <div class="result-actions">
          <button class="action-btn" id="copy-ocr-btn">Copy Text</button>
          <button class="action-btn" id="translate-ocr-btn">Translate</button>
        </div>
      </div>
      `,
      'result'
    );

    // Setup action buttons
    setTimeout(() => {
      document.getElementById('copy-ocr-btn')?.addEventListener('click', () => {
        navigator.clipboard.writeText(result.text);
        this.showNotification('Text copied to clipboard');
      });

      document.getElementById('translate-ocr-btn')?.addEventListener('click', () => {
        this.requestTranslation(result.text);
      });
    }, 0);
  }

  private showAgentResponse(response: string) {
    this.showOverlay();
    this.updateOverlayContent(
      `
      <div class="agent-result">
        <h3>Agent Response</h3>
        <div class="agent-response">${response}</div>
      </div>
      `,
      'result'
    );
  }

  private showNotification(message: string) {
    const notification = document.createElement('div');
    notification.className = 'agent-notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.classList.add('show');
    }, 10);

    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 2000);
  }

  private requestTranslation(text: string) {
    browser.runtime.sendMessage({
      type: 'TRANSLATE_TEXT',
      text,
    });
  }
}

// Initialize agent bridge
const agentBridge = new AgentBridge();

console.log('[AgentBridge] Content script loaded');

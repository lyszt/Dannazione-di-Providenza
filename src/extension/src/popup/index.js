import { LitElement, css, html } from 'lit';
import index from './config/index.js';

/**
 * Dannazione Popup
 * Main popup UI for the extension
 */
export class DannazionePopup extends LitElement {
  static get properties() {
    return {
      agentStatus: { type: Object },
      selectedText: { type: String },
    };
  }

  constructor() {
    super();
    this.agentStatus = {
      connected: false,
      status: 'idle',
    };
    this.selectedText = '';
  }

  connectedCallback() {
    super.connectedCallback();
    this.checkAgentStatus();
    this.getSelectedText();
  }

  async checkAgentStatus() {
    try {
      const response = await browser.runtime.sendMessage({
        type: 'GET_AGENT_STATUS',
      });
      this.agentStatus = response.status;
    } catch (error) {
      console.error('Failed to get agent status:', error);
      this.agentStatus = { connected: false, status: 'error' };
    }
  }

  async getSelectedText() {
    try {
      const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
      if (tab.id) {
        const response = await browser.tabs.sendMessage(tab.id, {
          type: 'GET_SELECTED_TEXT',
        });
        this.selectedText = response.text || '';
      }
    } catch (error) {
      console.error('Failed to get selected text:', error);
    }
  }

  async handleCaptureScreen() {
    try {
      await browser.runtime.sendMessage({ type: 'CAPTURE_SCREEN' });
      window.close();
    } catch (error) {
      console.error('Failed to capture screen:', error);
    }
  }

  async handleTranslate() {
    if (!this.selectedText) return;

    try {
      await browser.runtime.sendMessage({
        type: 'TRANSLATE_TEXT',
        text: this.selectedText,
      });
    } catch (error) {
      console.error('Failed to translate:', error);
    }
  }

  async handleToggleAgent() {
    try {
      await browser.runtime.sendMessage({ type: 'TOGGLE_AGENT' });
    } catch (error) {
      console.error('Failed to toggle agent:', error);
    }
  }

  render() {
    return html`
      <div class="popup-container">
        <header class="popup-header">
          <h1>Dannazione</h1>
          <div class="status-indicator ${this.agentStatus.connected ? 'connected' : 'disconnected'}">
            ${this.agentStatus.connected ? '●' : '○'}
          </div>
        </header>

        <div class="popup-content">
          <div class="agent-status">
            <p><strong>Agent:</strong> ${index.agent.name}</p>
            <p><strong>Status:</strong> ${this.agentStatus.status}</p>
          </div>

          <div class="quick-actions">
            <button @click=${this.handleCaptureScreen} class="action-btn primary">
              📸 Capture Screen
            </button>

            <button
              @click=${this.handleTranslate}
              class="action-btn secondary"
              ?disabled=${!this.selectedText}
            >
              🌐 Translate Selected
            </button>

            <button @click=${this.handleToggleAgent} class="action-btn secondary">
              🤖 Toggle Agent
            </button>
          </div>

          ${this.selectedText
            ? html`
                <div class="selected-text">
                  <strong>Selected Text:</strong>
                  <p>${this.selectedText.substring(0, 100)}${this.selectedText.length > 100 ? '...' : ''}</p>
                </div>
              `
            : ''}
        </div>
      </div>
    `;
  }

  static get styles() {
    return css`
      :host {
        display: block;
        width: 350px;
        min-height: 400px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        background: #1a1a1a;
        color: #e0e0e0;
      }

      .popup-container {
        display: flex;
        flex-direction: column;
        height: 100%;
      }

      .popup-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 8px 8px 0 0;
      }

      .popup-header h1 {
        font-size: 18px;
        font-weight: 600;
        color: white;
        margin: 0;
      }

      .status-indicator {
        font-size: 20px;
        transition: all 0.3s ease;
      }

      .status-indicator.connected {
        color: #4ade80;
        animation: pulse 2s ease-in-out infinite;
      }

      .status-indicator.disconnected {
        color: #f87171;
      }

      @keyframes pulse {
        0%,
        100% {
          opacity: 1;
        }
        50% {
          opacity: 0.5;
        }
      }

      .popup-content {
        flex: 1;
        padding: 16px;
        background: #2d2d2d;
      }

      .agent-status {
        background: #3a3a3a;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 16px;
      }

      .agent-status p {
        margin: 6px 0;
        font-size: 13px;
      }

      .agent-status strong {
        color: #9ca3af;
      }

      .quick-actions {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 16px;
      }

      .action-btn {
        padding: 12px 16px;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
      }

      .action-btn.primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
      }

      .action-btn.primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
      }

      .action-btn.secondary {
        background: #3a3a3a;
        color: #e0e0e0;
      }

      .action-btn.secondary:hover {
        background: #4a4a4a;
      }

      .action-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .selected-text {
        background: #3a3a3a;
        padding: 12px;
        border-radius: 6px;
        font-size: 12px;
      }

      .selected-text strong {
        display: block;
        margin-bottom: 8px;
        color: #9ca3af;
      }

      .selected-text p {
        color: #d1d5db;
        line-height: 1.5;
        margin: 0;
      }
    `;
  }
}

window.customElements.define('dannazione-popup', DannazionePopup);

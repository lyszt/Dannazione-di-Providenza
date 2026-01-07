import { LitElement, css, html } from 'lit';
import browser from 'webextension-polyfill';
import { translate } from '@vitalets/google-translate-api';
import config from '../config/index.js';

/**
 * Dannazione di Providenza - Popup
 */
export class DannazionePopup extends LitElement {
  static get properties() {
    return {
      selectedText: { type: String },
      translatedText: { type: String },
      isTranslating: { type: Boolean },
      overlayEnabled: { type: Boolean },
    };
  }

  constructor() {
    super();
    this.selectedText = '';
    this.translatedText = '';
    this.isTranslating = false;
    this.overlayEnabled = false;
  }

  connectedCallback() {
    super.connectedCallback();
    this.loadOverlayState();
    this.getSelectedText();
  }

  async loadOverlayState() {
    try {
      const result = await browser.storage.local.get('overlayEnabled');
      this.overlayEnabled = result.overlayEnabled || false;
    } catch (error) {
      console.error('Failed to load overlay state:', error);
    }
  }

  async toggleOverlay() {
    this.overlayEnabled = !this.overlayEnabled;
    try {
      await browser.storage.local.set({ overlayEnabled: this.overlayEnabled });

      // Notify all tabs about the change
      const tabs = await browser.tabs.query({});
      for (const tab of tabs) {
        if (tab.id) {
          browser.tabs.sendMessage(tab.id, {
            type: 'OVERLAY_TOGGLE',
            enabled: this.overlayEnabled,
          }).catch(() => {}); // Ignore errors for tabs that don't have content script
        }
      }
    } catch (error) {
      console.error('Failed to toggle overlay:', error);
    }
  }

  async getSelectedText() {
    try {
      const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
      if (tab.id) {
        const response = await browser.tabs.sendMessage(tab.id, {
          type: 'GET_SELECTED_TEXT',
        });
        this.selectedText = response?.text || '';

        if (this.selectedText) {
          this.translateText();
        }
      }
    } catch (error) {
      console.error('Failed to get selected text:', error);
    }
  }

  async translateText() {
    if (!this.selectedText) return;

    this.isTranslating = true;
    try {
      const result = await translate(this.selectedText, { to: 'en' });
      this.translatedText = result.text;
    } catch (error) {
      console.error('Translation failed:', error);
      this.translatedText = 'Translation failed';
    } finally {
      this.isTranslating = false;
    }
  }

  render() {
    return html`
      <div class="popup-container">
        <header class="popup-header">
          <h1>Dannazione di Providenza</h1>
        </header>

        <div class="settings-section">
          <div class="setting-item">
            <label>
              <span>Auto-translate on selection</span>
              <input
                type="checkbox"
                class="toggle"
                ?checked=${this.overlayEnabled}
                @change=${this.toggleOverlay}
              />
            </label>
          </div>
        </div>

        <div class="popup-content">
          ${this.selectedText
            ? html`
                <div class="text-section">
                  <div class="text-block">
                    <strong>Original:</strong>
                    <p>${this.selectedText}</p>
                  </div>

                  <div class="text-block translation">
                    <strong>Translation:</strong>
                    ${this.isTranslating
                      ? html`<p class="loading">Translating...</p>`
                      : html`<p>${this.translatedText || 'No translation available'}</p>`}
                  </div>
                </div>
              `
            : html`<p class="hint">Select text on the page</p>`}
        </div>
      </div>
    `;
  }

  static get styles() {
    return css`
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      :host {
        display: block;
        min-width: 400px;
        width: 450px;
        min-height: 500px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #1a1a1a;
        color: #e0e0e0;
      }

      .popup-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        margin: 0;
      }

      .popup-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px;
      }

      .popup-header h1 {
        font-size: 18px;
        font-weight: 600;
        color: white;
      }

      .settings-section {
        background: #252525;
        border-bottom: 1px solid #3a3a3a;
      }

      .setting-item {
        padding: 12px 16px;
      }

      .setting-item label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
        color: #e0e0e0;
        font-size: 14px;
      }

      .toggle {
        width: 40px;
        height: 20px;
        appearance: none;
        background: #3a3a3a;
        border-radius: 10px;
        position: relative;
        cursor: pointer;
        transition: background 0.3s;
      }

      .toggle:checked {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      .toggle::before {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: white;
        top: 2px;
        left: 2px;
        transition: left 0.3s;
      }

      .toggle:checked::before {
        left: 22px;
      }

      .popup-content {
        flex: 1;
        padding: 16px;
        background: #2d2d2d;
      }

      .hint {
        text-align: center;
        color: #9ca3af;
        margin-top: 40px;
      }

      .text-section {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }

      .text-block {
        background: #3a3a3a;
        padding: 12px;
        border-radius: 6px;
      }

      .text-block.translation {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
      }

      .text-block strong {
        display: block;
        margin-bottom: 8px;
        color: #9ca3af;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .text-block p {
        color: #d1d5db;
        line-height: 1.6;
        font-size: 14px;
      }

      .loading {
        color: #667eea;
        font-style: italic;
      }
    `;
  }
}

window.customElements.define('dannazione-popup', DannazionePopup);

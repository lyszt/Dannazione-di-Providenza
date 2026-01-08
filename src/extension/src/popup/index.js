import { LitElement, css, html } from 'lit';
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
      fromLang: { type: String },
      toLang: { type: String },
    };
  }

  constructor() {
    super();
    this.selectedText = '';
    this.translatedText = '';
    this.isTranslating = false;
    this.overlayEnabled = true;
    this.fromLang = 'auto';
    this.toLang = 'en';
    this.languages = [
      { code: 'auto', name: 'Auto Detect' },
      { code: 'en', name: 'English' },
      { code: 'es', name: 'Spanish' },
      { code: 'fr', name: 'French' },
      { code: 'de', name: 'German' },
      { code: 'it', name: 'Italian' },
      { code: 'pt', name: 'Portuguese' },
      { code: 'ru', name: 'Russian' },
      { code: 'ja', name: 'Japanese' },
      { code: 'zh-CN', name: 'Chinese (Simplified)' },
      { code: 'ko', name: 'Korean' },
      { code: 'ar', name: 'Arabic' },
      { code: 'hi', name: 'Hindi' },
      { code: 'tr', name: 'Turkish' },
      { code: 'pl', name: 'Polish' },
      { code: 'nl', name: 'Dutch' },
    ];
  }

  connectedCallback() {
    super.connectedCallback();
    this.loadSettings();
    this.getSelectedText();
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.local.get(['overlayEnabled', 'fromLang', 'toLang']);
      this.overlayEnabled = result.overlayEnabled !== undefined ? result.overlayEnabled : true;
      this.fromLang = result.fromLang || 'auto';
      this.toLang = result.toLang || 'en';
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  }

  async toggleOverlay() {
    this.overlayEnabled = !this.overlayEnabled;
    try {
      await chrome.storage.local.set({ overlayEnabled: this.overlayEnabled });

      // Notify all tabs about the change
      const tabs = await chrome.tabs.query({});
      for (const tab of tabs) {
        if (tab.id) {
          chrome.tabs.sendMessage(tab.id, {
            type: 'OVERLAY_TOGGLE',
            enabled: this.overlayEnabled,
          }).catch(() => {}); // Ignore errors for tabs that don't have content script
        }
      }
    } catch (error) {
      console.error('Failed to toggle overlay:', error);
    }
  }

  async handleFromLangChange(e) {
    this.fromLang = e.target.value;
    try {
      await chrome.storage.local.set({ fromLang: this.fromLang });
      // Re-translate if there's selected text
      if (this.selectedText) {
        this.translateText();
      }
    } catch (error) {
      console.error('Failed to save from language:', error);
    }
  }

  async handleToLangChange(e) {
    this.toLang = e.target.value;
    try {
      await chrome.storage.local.set({ toLang: this.toLang });
      // Re-translate if there's selected text
      if (this.selectedText) {
        this.translateText();
      }
    } catch (error) {
      console.error('Failed to save to language:', error);
    }
  }

  async getSelectedText() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      if (!tab || !tab.url || (!tab.url.startsWith('http://') && !tab.url.startsWith('https://'))) {
        this.selectedText = '';
        return;
      }

      if (tab.id) {
        try {
          const response = await chrome.tabs.sendMessage(tab.id, {
            type: 'GET_SELECTED_TEXT',
          });
          this.selectedText = response?.text || '';

          if (this.selectedText) {
            this.translateText();
          }
        } catch (msgError) {
          // Content script not loaded yet, inject it
          if (msgError.message.includes('Receiving end does not exist')) {
            try {
              await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['content.js']
              });

              // Wait a bit for injection
              await new Promise(resolve => setTimeout(resolve, 100));

              // Try again
              const response = await chrome.tabs.sendMessage(tab.id, {
                type: 'GET_SELECTED_TEXT',
              });
              this.selectedText = response?.text || '';

              if (this.selectedText) {
                this.translateText();
              }
            } catch (injectError) {
              // Page can't be scripted, silently ignore
              this.selectedText = '';
            }
          } else {
            throw msgError;
          }
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
      const result = await translate(this.selectedText, {
        from: this.fromLang === 'auto' ? undefined : this.fromLang,
        to: this.toLang
      });
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
              <span>From Language</span>
              <select class="lang-select" @change=${this.handleFromLangChange} .value=${this.fromLang}>
                ${this.languages.map(lang => html`
                  <option value=${lang.code} ?selected=${lang.code === this.fromLang}>
                    ${lang.name}
                  </option>
                `)}
              </select>
            </label>
          </div>

          <div class="setting-item">
            <label>
              <span>To Language</span>
              <select class="lang-select" @change=${this.handleToLangChange} .value=${this.toLang}>
                ${this.languages.filter(l => l.code !== 'auto').map(lang => html`
                  <option value=${lang.code} ?selected=${lang.code === this.toLang}>
                    ${lang.name}
                  </option>
                `)}
              </select>
            </label>
          </div>

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

      .lang-select {
        background: #3a3a3a;
        color: #e0e0e0;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 13px;
        cursor: pointer;
        outline: none;
        transition: border-color 0.2s;
      }

      .lang-select:hover {
        border-color: #667eea;
      }

      .lang-select:focus {
        border-color: #667eea;
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

import { LitElement, css, html } from 'lit';
import config from '../config/index.js';
import '../components/chat/index.js';
import '@material/web/button/outlined-button.js';
import '@material/web/checkbox/checkbox.js';

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
      activeTab: { type: String },
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
    this.activeTab = 'translate';
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

  switchTab(tab) {
    this.activeTab = tab;
  }

  render() {
    return html`
      <div class="popup-container min-w-[400px] w-[450px] min-h-[500px] font-sans bg-gray-900 text-gray-100">
        <header class="popup-header">
          <h1>Dannazione di Providenza</h1>
        </header>

        <div class="tabs">
          <button
            class="tab ${this.activeTab === 'translate' ? 'active' : ''}"
            @click=${() => this.switchTab('translate')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v1.99h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z" fill="currentColor"/>
            </svg>
            Translate
          </button>
          <button
            class="tab ${this.activeTab === 'chat' ? 'active' : ''}"
            @click=${() => this.switchTab('chat')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Chat
          </button>
        </div>

        ${this.activeTab === 'translate'
          ? html`
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
            `
          : html`
              <div class="chat-tab-content">
                <dannazione-chat></dannazione-chat>
              </div>
            `}
      </div>
    `;
  }
}

window.customElements.define('dannazione-popup', DannazionePopup);

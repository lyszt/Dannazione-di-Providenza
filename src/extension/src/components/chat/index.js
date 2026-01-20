import { LitElement, html } from 'lit';
import DannazioneAPI from '../../dannazione/index.js';
import config from '../../config/index.js';
import { resolveMarkdown } from 'lit-markdown';
/**
 * Dannazione di Providenza - Chat Component
 */
export class DannazioneChat extends LitElement {
  static get properties() {
    return {
      chatMessages: { type: Array },
      isLoading: { type: Boolean },
    };
  }

  constructor() {
    super();
    this.chatMessages = [];
    this.isLoading = false;
    this.api = new DannazioneAPI(config.api.baseUrl);
  }

  async sendChatMessage(message) {
    if (!message.trim()) return;

    this.chatMessages = [
      ...this.chatMessages,
      { user: message, bot: null }
    ];
    this.isLoading = true;

    const page = document.body.innerHTML;

    const response = await this.api.sendChatMessage(message, page);

    const lastIndex = this.chatMessages.length - 1;
    const updatedMessages = [...this.chatMessages];
    updatedMessages[lastIndex] = {
      user: message,
      bot: (response && typeof response.reply !== 'undefined') ? response.reply : 'No response'
    };

    this.chatMessages = updatedMessages;
    this.isLoading = false;
  }

  firstUpdated() {
    this.scrollToBottom();
  }

  updated(changedProperties) {
    if (changedProperties.has('chatMessages')) {
      this.scrollToBottom();
    }
  }

  scrollToBottom() {
    const chatSection = this.shadowRoot?.querySelector('.chat-section');
    if (chatSection) {
      chatSection.scrollTop = chatSection.scrollHeight;
    }
  }

  render() {
    return html`
      <div class="chat-container flex flex-col h-full w-full font-sans bg-gray-800 text-gray-100">
        <div class="chat-header">
          <h2>Chat</h2>
          <span class="chat-subtitle">Ask me anything</span>
        </div>

        <div class="chat-section">
          ${this.chatMessages.length === 0
            ? html`
                <div class="empty-state">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <p>Start a conversation</p>
                </div>
              `
            : this.chatMessages.map(
                (msg) => html`
                  <div class="message-group">
                    <div class="chat-message user">
                      <div class="message-content">${msg.user}</div>
                    </div>
                    ${msg.bot !== null
                      ? html`
                          <div class="chat-message bot">
                            <div class="message-avatar">
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                              </svg>
                            </div>
                            <div class="message-content">${resolveMarkdown(msg.bot, { includeImages: true, includeCodeBlockClassNames: true })}</div>
                          </div>
                        `
                      : html`
                          <div class="chat-message bot loading">
                            <div class="message-avatar">
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <!-- typing -->
                              </svg>
                            </div>
                            <div class="message-content">
                              <div class="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                              </div>
                            </div>
                          </div>
                        `}
                  </div>
                `
              )}
        </div>

        <div class="chat-input-container">
          <input
            type="text"
            class="chat-input"
            placeholder="Type your message..."
            ?disabled=${this.isLoading}
            @keydown=${(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendChatMessage(e.target.value);
                e.target.value = '';
              }
            }}
          />
          <button class="send-button" @click=${() => this.sendChatMessage(this.shadowRoot.querySelector('.chat-input').value)} ?disabled=${this.isLoading}>
            <!-- send icon -->
          </button>
        </div>
      </div>
    `;
  }
}

window.customElements.define('dannazione-chat', DannazioneChat);

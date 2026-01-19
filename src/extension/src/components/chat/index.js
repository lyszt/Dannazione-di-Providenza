import { LitElement, css, html } from 'lit';
import DannazioneAPI from '../../dannazione/index.js';
import config from '../../config/index.js';

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

    this.isLoading = true;
    // Add user message immediately
    this.chatMessages = [...this.chatMessages, { user: message, bot: null }];

    try {
      const response = await this.api.sendChatMessage(message, {});
      // Update the last message with bot response
      const lastIndex = this.chatMessages.length - 1;
      this.chatMessages = [
        ...this.chatMessages.slice(0, lastIndex),
        { user: message, bot: response.reply || response.message || 'No response' }
      ];
    } catch (error) {
      console.error("[Dannazione] Failed to send chat message:", error);
      // Update with error message
      const lastIndex = this.chatMessages.length - 1;
      this.chatMessages = [
        ...this.chatMessages.slice(0, lastIndex),
        { user: message, bot: 'Failed to get response. Please try again.' }
      ];
    } finally {
      this.isLoading = false;
    }
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
      <div class="chat-container">
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
                            <div class="message-content">${msg.bot}</div>
                          </div>
                        `
                      : html`
                          <div class="chat-message bot loading">
                            <div class="message-avatar">
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
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
              if (e.key === "Enter" && !this.isLoading) {
                this.sendChatMessage(e.target.value);
                e.target.value = "";
              }
            }}
          />
          <button
            class="send-button"
            ?disabled=${this.isLoading}
            @click=${(e) => {
              const input = this.shadowRoot.querySelector('.chat-input');
              if (input.value.trim()) {
                this.sendChatMessage(input.value);
                input.value = "";
              }
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
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
        width: 100%;
        height: 100%;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #2d2d2d;
        color: #e0e0e0;
      }

      .chat-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
      }

      .chat-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border-bottom: 1px solid #3a3a3a;
        padding: 16px;
      }

      .chat-header h2 {
        font-size: 16px;
        font-weight: 600;
        color: #e0e0e0;
        margin-bottom: 4px;
      }

      .chat-subtitle {
        font-size: 12px;
        color: #9ca3af;
      }

      .chat-section {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        scroll-behavior: smooth;
      }

      .chat-section::-webkit-scrollbar {
        width: 6px;
      }

      .chat-section::-webkit-scrollbar-track {
        background: #252525;
      }

      .chat-section::-webkit-scrollbar-thumb {
        background: #4a4a4a;
        border-radius: 3px;
      }

      .chat-section::-webkit-scrollbar-thumb:hover {
        background: #5a5a5a;
      }

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #6b7280;
        gap: 12px;
      }

      .empty-state svg {
        opacity: 0.5;
      }

      .empty-state p {
        font-size: 14px;
      }

      .message-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .chat-message {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        max-width: 85%;
        animation: slideIn 0.2s ease-out;
      }

      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateY(10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .chat-message.user {
        align-self: flex-end;
        flex-direction: row-reverse;
      }

      .chat-message.bot {
        align-self: flex-start;
      }

      .message-avatar {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
      }

      .message-content {
        padding: 10px 14px;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.5;
        word-wrap: break-word;
        overflow-wrap: break-word;
      }

      .chat-message.user .message-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
      }

      .chat-message.bot .message-content {
        background: #3a3a3a;
        color: #d1d5db;
        border-bottom-left-radius: 4px;
      }

      .chat-message.bot.loading .message-content {
        padding: 14px;
      }

      .typing-indicator {
        display: flex;
        gap: 4px;
        align-items: center;
      }

      .typing-indicator span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #667eea;
        animation: typing 1.4s infinite;
      }

      .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
      }

      .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
      }

      @keyframes typing {
        0%, 60%, 100% {
          opacity: 0.3;
          transform: translateY(0);
        }
        30% {
          opacity: 1;
          transform: translateY(-8px);
        }
      }

      .chat-input-container {
        display: flex;
        gap: 8px;
        padding: 12px 16px;
        background: #252525;
        border-top: 1px solid #3a3a3a;
      }

      .chat-input {
        flex: 1;
        padding: 10px 12px;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        background: #2d2d2d;
        color: #e0e0e0;
        font-size: 14px;
        font-family: inherit;
        outline: none;
        transition: all 0.2s;
      }

      .chat-input::placeholder {
        color: #6b7280;
      }

      .chat-input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }

      .chat-input:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .send-button {
        width: 40px;
        height: 40px;
        border: none;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        flex-shrink: 0;
      }

      .send-button:hover:not(:disabled) {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
      }

      .send-button:active:not(:disabled) {
        transform: translateY(0);
      }

      .send-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    `;
  }
}

window.customElements.define('dannazione-chat', DannazioneChat);

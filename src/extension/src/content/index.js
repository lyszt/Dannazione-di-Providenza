/**
 * Dannazione di Providenza - Content Script
 */

import DannazioneAPI from '../dannazione/index.js';
import config from '../config/index.js';
import { marked } from 'marked';

const api = new DannazioneAPI(config.api.baseUrl);

console.log('[Dannazione] Content script loaded on', window.location.href);

let overlayEnabled = true;
let translationOverlay = null;
let isTranslating = false;
let chatOverlay = null;
let isChatOpen = false;

// Load overlay state from storage
chrome.storage.local.get('overlayEnabled').then((result) => {
  overlayEnabled = result.overlayEnabled !== undefined ? result.overlayEnabled : true;
  if (overlayEnabled) {
    attachSelectionListener();
  }
});

// Handle messages from background/popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Dannazione] Received message:', message);

  switch (message.type) {
    case 'GET_SELECTED_TEXT':
      sendResponse({ text: getSelectedText() });
      break;

    case 'OVERLAY_TOGGLE':
      overlayEnabled = message.enabled;
      if (overlayEnabled) {
        attachSelectionListener();
      } else {
        detachSelectionListener();
        hideOverlay();
      }
      break;
  }

  return false;
});

// Get selected text from page
function getSelectedText() {
  return window.getSelection()?.toString().trim() || '';
}

// Attach selection listener
function attachSelectionListener() {
  document.addEventListener('mouseup', handleTextSelection);
}

// Detach selection listener
function detachSelectionListener() {
  document.removeEventListener('mouseup', handleTextSelection);
}

// Handle text selection
async function handleTextSelection(event) {
  if (!overlayEnabled) return;

  const selectedText = getSelectedText();

  if (!selectedText) {
    hideOverlay();
    return;
  }

  if (isTranslating) return;

  // Send selection to backend
  try {
    await api.sendSelection(selectedText);
  } catch (error) {
    console.error('[Dannazione] Failed to send selection:', error);
  }

  // Get selection coordinates
  const selection = window.getSelection();
  if (!selection.rangeCount) return;

  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();

  // Show overlay with loading state
  showOverlay(rect, selectedText, 'Translating...');

  // Request translation from background script
  isTranslating = true;
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'TRANSLATE_TEXT',
      text: selectedText,
    });
    showOverlay(rect, selectedText, response.translation);
  } catch (error) {
    console.error('Translation failed:', error);
    showOverlay(rect, selectedText, 'Translation failed');
  } finally {
    isTranslating = false;
  }
}

// Show translation overlay
function showOverlay(rect, original, translation) {
  // Remove existing overlay
  if (translationOverlay) {
    translationOverlay.remove();
  }

  // Create overlay
  translationOverlay = document.createElement('div');
  translationOverlay.className = 'dannazione-translation-overlay';
  translationOverlay.innerHTML = `
    <div class="dannazione-overlay-close">×</div>
    <div class="dannazione-overlay-section">
      <strong>Original:</strong>
      <p>${escapeHtml(original)}</p>
    </div>
    <div class="dannazione-overlay-section translation">
      <strong>Translation:</strong>
      <p>${escapeHtml(translation)}</p>
    </div>
  `;

  // Position overlay
  const top = rect.bottom + window.scrollY + 10;
  const left = rect.left + window.scrollX;

  translationOverlay.style.top = `${top}px`;
  translationOverlay.style.left = `${left}px`;

  // Add to page
  document.body.appendChild(translationOverlay);

  // Add close button handler
  const closeBtn = translationOverlay.querySelector('.dannazione-overlay-close');
  closeBtn.addEventListener('click', hideOverlay);

  // Close on click outside
  setTimeout(() => {
    document.addEventListener('click', handleOutsideClick);
  }, 100);
}

// Hide overlay
function hideOverlay() {
  if (translationOverlay) {
    translationOverlay.remove();
    translationOverlay = null;
  }
  document.removeEventListener('click', handleOutsideClick);
}

// Handle click outside overlay
function handleOutsideClick(event) {
  if (translationOverlay && !translationOverlay.contains(event.target)) {
    hideOverlay();
  }
}

// Escape HTML
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Chat functionality
let chatMessages = [];

function createChatOverlay() {
  if (chatOverlay) return;

  chatOverlay = document.createElement('div');
  chatOverlay.className = 'dannazione-chat-overlay';
  chatOverlay.innerHTML = `
    <div class="dannazione-chat-header">
      <div class="chat-header-content">
        <div class="message-avatar">
        
        </div>
        <span>Providentia</span>
      </div>
      <div class="chat-header-actions">
        <button class="dannazione-chat-clear" title="Clear conversation">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="dannazione-chat-close">×</button>
      </div>
    </div>
    <div class="dannazione-chat-messages" id="dannazione-chat-messages">
      <div class="dannazione-chat-empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p>Start a conversation</p>
      </div>
    </div>
    <div class="dannazione-chat-input-container">
      <input
        type="text"
        class="dannazione-chat-input"
        placeholder="Type your message..."
        id="dannazione-chat-input"
      />
      <button class="dannazione-chat-send" id="dannazione-chat-send">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  `;

  document.body.appendChild(chatOverlay);

  // Add event listeners
  const closeBtn = chatOverlay.querySelector('.dannazione-chat-close');
  const clearBtn = chatOverlay.querySelector('.dannazione-chat-clear');
  const sendBtn = chatOverlay.querySelector('#dannazione-chat-send');
  const input = chatOverlay.querySelector('#dannazione-chat-input');

  closeBtn.addEventListener('click', toggleChat);
  clearBtn.addEventListener('click', clearChat);
  sendBtn.addEventListener('click', () => sendChatMessage(input.value));
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage(input.value);
    }
  });
}

function clearChat() {
  const messagesContainer = chatOverlay.querySelector('#dannazione-chat-messages');

  // Clear all messages
  messagesContainer.innerHTML = `
    <div class="dannazione-chat-empty">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p>Start a conversation</p>
    </div>
  `;

  // Clear the chat messages array
  chatMessages = [];

  console.log('[Dannazione] Chat cleared');
}

function toggleChat() {
  isChatOpen = !isChatOpen;
  const toggleBtn = document.querySelector('.dannazione-chat-toggle');

  if (isChatOpen) {
    if (!chatOverlay) {
      createChatOverlay();
    }
    chatOverlay.classList.add('open');
    if (toggleBtn) toggleBtn.classList.add('hidden');
  } else {
    if (chatOverlay) {
      chatOverlay.classList.remove('open');
    }
    if (toggleBtn) toggleBtn.classList.remove('hidden');
  }
}

async function sendChatMessage(message) {
  if (!message.trim()) return;

  const input = chatOverlay.querySelector('#dannazione-chat-input');
  const messagesContainer = chatOverlay.querySelector('#dannazione-chat-messages');

  // Clear input
  input.value = '';
  input.disabled = true;

  // Remove empty state if exists
  const emptyState = messagesContainer.querySelector('.dannazione-chat-empty');
  if (emptyState) {
    emptyState.remove();
  }

  // Add user message
  const userMsg = document.createElement('div');
  userMsg.className = 'dannazione-chat-message user';
  userMsg.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
  messagesContainer.appendChild(userMsg);

  // Add loading bot message
  const botMsg = document.createElement('div');
  botMsg.className = 'dannazione-chat-message bot loading';
  botMsg.innerHTML = `
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
  `;
  messagesContainer.appendChild(botMsg);

  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  try {
    const response = await api.sendChatMessage(message, {});
    const responseText = response.reply || response.message || 'No response';

    // Update bot message with response
    botMsg.className = 'dannazione-chat-message bot';
    botMsg.innerHTML = `
      <div class="message-avatar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="message-content markdown-body">${marked.parse(responseText)}</div>
    `;
  } catch (error) {
    console.error('[Dannazione] Failed to send chat message:', error);
    botMsg.className = 'dannazione-chat-message bot error';
    botMsg.innerHTML = `
      <div class="message-avatar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="message-content">Failed to get response. Please try again.</div>
    `;
  } finally {
    input.disabled = false;
    input.focus();
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}

// Create chat toggle button
function createChatToggleButton() {
  const toggleBtn = document.createElement('button');
  toggleBtn.className = 'dannazione-chat-toggle';
  toggleBtn.innerHTML = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
  toggleBtn.addEventListener('click', toggleChat);
  document.body.appendChild(toggleBtn);
}

// Initialize chat
createChatToggleButton();

// Inject overlay styles
const style = document.createElement('style');
style.textContent = `
  .dannazione-translation-overlay {
    position: absolute;
    z-index: 2147483647;
    background: rgba(26, 26, 26, 0.98);
    border: 1px solid rgba(102, 126, 234, 0.5);
    border-radius: 8px;
    padding: 12px;
    min-width: 300px;
    max-width: 500px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #e0e0e0;
    backdrop-filter: blur(10px);
  }

  .dannazione-overlay-close {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 4px;
    font-size: 20px;
    color: #9ca3af;
    transition: all 0.2s;
  }

  .dannazione-overlay-close:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .dannazione-overlay-section {
    margin-bottom: 12px;
  }

  .dannazione-overlay-section:last-child {
    margin-bottom: 0;
  }

  .dannazione-overlay-section.translation {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
    padding: 8px;
    border-radius: 4px;
  }

  .dannazione-overlay-section strong {
    display: block;
    margin-bottom: 4px;
    color: #9ca3af;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .dannazione-overlay-section p {
    margin: 0;
    color: #e0e0e0;
    font-size: 14px;
    line-height: 1.5;
  }

  /* Chat Toggle Button */
  .dannazione-chat-toggle {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    z-index: 2147483646;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .dannazione-chat-toggle:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5);
  }

  .dannazione-chat-toggle.hidden {
    opacity: 0;
    pointer-events: none;
    transform: scale(0.8);
  }

  /* Chat Overlay */
  .dannazione-chat-overlay {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 380px;
    height: 550px;
    background: rgba(26, 26, 26, 0.98);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    z-index: 2147483647;
    display: flex;
    flex-direction: column;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    opacity: 0;
    transform: translateY(20px) scale(0.95);
    pointer-events: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
  }

  .dannazione-chat-overlay.open {
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: all;
  }

  .dannazione-chat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
    border-bottom: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 16px 16px 0 0;
  }

  .chat-header-content {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #e0e0e0;
    font-weight: 600;
    font-size: 16px;
  }

  .chat-header-content svg {
    color: #667eea;
  }

  .chat-header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .dannazione-chat-clear {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    color: #9ca3af;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
  }

  .dannazione-chat-clear:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .dannazione-chat-close {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    color: #9ca3af;
    font-size: 28px;
    line-height: 1;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
  }

  .dannazione-chat-close:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .dannazione-chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    scroll-behavior: smooth;
  }

  .dannazione-chat-messages::-webkit-scrollbar {
    width: 6px;
  }

  .dannazione-chat-messages::-webkit-scrollbar-track {
    background: rgba(37, 37, 37, 0.5);
  }

  .dannazione-chat-messages::-webkit-scrollbar-thumb {
    background: rgba(74, 74, 74, 0.8);
    border-radius: 3px;
  }

  .dannazione-chat-messages::-webkit-scrollbar-thumb:hover {
    background: rgba(90, 90, 90, 0.8);
  }

  .dannazione-chat-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #6b7280;
    gap: 12px;
  }

  .dannazione-chat-empty svg {
    opacity: 0.5;
  }

  .dannazione-chat-empty p {
    font-size: 14px;
    margin: 0;
  }

  .dannazione-chat-message {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    max-width: 85%;
    animation: slideInChat 0.2s ease-out;
  }

  @keyframes slideInChat {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .dannazione-chat-message.user {
    align-self: flex-end;
    flex-direction: row-reverse;
  }

  .dannazione-chat-message.bot {
    align-self: flex-start;
  }

  .dannazione-chat-message .message-avatar {
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

  .dannazione-chat-message .message-content {
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
    overflow-wrap: break-word;
    color: #e0e0e0;
  }

  .dannazione-chat-message.user .message-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 4px;
  }

  .dannazione-chat-message.bot .message-content {
    background: rgba(58, 58, 58, 0.9);
    color: #d1d5db;
    border-bottom-left-radius: 4px;
  }

  .dannazione-chat-message.bot.error .message-content {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
  }

  .dannazione-chat-message.bot.loading .message-content {
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
    animation: typingBounce 1.4s infinite;
  }

  .typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes typingBounce {
    0%, 60%, 100% {
      opacity: 0.3;
      transform: translateY(0);
    }
    30% {
      opacity: 1;
      transform: translateY(-8px);
    }
  }

  .dannazione-chat-input-container {
    display: flex;
    gap: 8px;
    padding: 12px 16px;
    background: rgba(37, 37, 37, 0.8);
    border-top: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 0 0 16px 16px;
  }

  .dannazione-chat-input {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid rgba(74, 74, 74, 0.8);
    border-radius: 8px;
    background: rgba(45, 45, 45, 0.8);
    color: #e0e0e0;
    font-size: 14px;
    font-family: inherit;
    outline: none;
    transition: all 0.2s;
  }

  .dannazione-chat-input::placeholder {
    color: #6b7280;
  }

  .dannazione-chat-input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
  }

  .dannazione-chat-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .dannazione-chat-send {
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

  .dannazione-chat-send:hover:not(:disabled) {
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }

  .dannazione-chat-send:active:not(:disabled) {
    transform: translateY(0);
  }

  .dannazione-chat-send:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Markdown rendering in bot messages */
  .markdown-body p {
    margin: 0 0 8px 0;
  }

  .markdown-body p:last-child {
    margin-bottom: 0;
  }

  .markdown-body h1, .markdown-body h2, .markdown-body h3,
  .markdown-body h4, .markdown-body h5, .markdown-body h6 {
    margin: 12px 0 6px 0;
    color: #e0e0e0;
    font-weight: 600;
    line-height: 1.3;
  }

  .markdown-body h1 { font-size: 1.3em; }
  .markdown-body h2 { font-size: 1.2em; }
  .markdown-body h3 { font-size: 1.1em; }

  .markdown-body ul, .markdown-body ol {
    margin: 4px 0 8px 0;
    padding-left: 20px;
  }

  .markdown-body li {
    margin-bottom: 2px;
  }

  .markdown-body code {
    background: rgba(0, 0, 0, 0.3);
    padding: 1px 5px;
    border-radius: 4px;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 0.9em;
    color: #c4b5fd;
  }

  .markdown-body pre {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 8px;
    padding: 10px 12px;
    margin: 6px 0;
    overflow-x: auto;
  }

  .markdown-body pre code {
    background: none;
    padding: 0;
    border-radius: 0;
    font-size: 0.85em;
    color: #d1d5db;
  }

  .markdown-body blockquote {
    border-left: 3px solid #667eea;
    margin: 6px 0;
    padding: 4px 12px;
    color: #9ca3af;
    background: rgba(102, 126, 234, 0.08);
    border-radius: 0 4px 4px 0;
  }

  .markdown-body a {
    color: #818cf8;
    text-decoration: underline;
  }

  .markdown-body a:hover {
    color: #a5b4fc;
  }

  .markdown-body strong {
    color: #e0e0e0;
    font-weight: 600;
  }

  .markdown-body em {
    color: #c4b5fd;
  }

  .markdown-body hr {
    border: none;
    border-top: 1px solid rgba(102, 126, 234, 0.2);
    margin: 10px 0;
  }

  .markdown-body table {
    border-collapse: collapse;
    width: 100%;
    margin: 6px 0;
    font-size: 0.9em;
  }

  .markdown-body th, .markdown-body td {
    border: 1px solid rgba(74, 74, 74, 0.8);
    padding: 6px 10px;
    text-align: left;
  }

  .markdown-body th {
    background: rgba(102, 126, 234, 0.15);
    color: #e0e0e0;
    font-weight: 600;
  }
`;
document.head.appendChild(style);

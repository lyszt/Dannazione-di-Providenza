/**
 * Dannazione - Background Service Worker
 * Manages agent connection, message routing, and extension lifecycle
 */

import browser from 'webextension-polyfill';
import config from '../config';

interface AgentConnection {
  ws: WebSocket | null;
  connected: boolean;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
}

class AgentManager {
  private connection: AgentConnection = {
    ws: null,
    connected: false,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
  };

  constructor() {
    this.initialize();
  }

  private initialize() {
    console.log('[AgentManager] Initializing...');
    this.setupMessageListeners();
    this.setupCommandListeners();
    this.connectToAgent();
  }

  private connectToAgent() {
    const wsUrl = config.agent.wsUrl;
    console.log(`[AgentManager] Connecting to agent at ${wsUrl}...`);

    try {
      this.connection.ws = new WebSocket(wsUrl);

      this.connection.ws.onopen = () => {
        console.log('[AgentManager] Connected to agent');
        this.connection.connected = true;
        this.connection.reconnectAttempts = 0;
        this.notifyConnectionStatus(true);
      };

      this.connection.ws.onmessage = (event) => {
        this.handleAgentMessage(event.data);
      };

      this.connection.ws.onerror = (error) => {
        console.error('[AgentManager] WebSocket error:', error);
        this.connection.connected = false;
        this.notifyConnectionStatus(false);
      };

      this.connection.ws.onclose = () => {
        console.log('[AgentManager] Disconnected from agent');
        this.connection.connected = false;
        this.notifyConnectionStatus(false);
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('[AgentManager] Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private attemptReconnect() {
    if (this.connection.reconnectAttempts >= this.connection.maxReconnectAttempts) {
      console.log('[AgentManager] Max reconnect attempts reached');
      return;
    }

    this.connection.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.connection.reconnectAttempts), 30000);

    console.log(
      `[AgentManager] Reconnecting in ${delay}ms (attempt ${this.connection.reconnectAttempts}/${this.connection.maxReconnectAttempts})`
    );

    setTimeout(() => {
      this.connectToAgent();
    }, delay);
  }

  private notifyConnectionStatus(connected: boolean) {
    browser.runtime.sendMessage({
      type: 'AGENT_CONNECTION_STATUS',
      connected,
    }).catch(() => {
      // Ignore errors when no listeners are available
    });
  }

  private handleAgentMessage(data: string) {
    try {
      const message = JSON.parse(data);
      console.log('[AgentManager] Received from agent:', message);

      // Route message to appropriate handler
      switch (message.type) {
        case 'TRANSLATION_RESULT':
          this.handleTranslationResult(message);
          break;
        case 'OCR_RESULT':
          this.handleOCRResult(message);
          break;
        case 'AGENT_RESPONSE':
          this.handleAgentResponse(message);
          break;
        default:
          console.warn('[AgentManager] Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('[AgentManager] Failed to parse agent message:', error);
    }
  }

  private handleTranslationResult(message: any) {
    // Send translation result to content script
    browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
      if (tabs[0]?.id) {
        browser.tabs.sendMessage(tabs[0].id, {
          type: 'TRANSLATION_RESULT',
          result: message.result,
        });
      }
    });
  }

  private handleOCRResult(message: any) {
    // Send OCR result to content script
    browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
      if (tabs[0]?.id) {
        browser.tabs.sendMessage(tabs[0].id, {
          type: 'OCR_RESULT',
          result: message.result,
        });
      }
    });
  }

  private handleAgentResponse(message: any) {
    // Display agent response in overlay
    browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
      if (tabs[0]?.id) {
        browser.tabs.sendMessage(tabs[0].id, {
          type: 'AGENT_RESPONSE',
          response: message.response,
        });
      }
    });
  }

  private setupMessageListeners() {
    browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
      console.log('[AgentManager] Received message:', message);

      switch (message.type) {
        case 'GET_AGENT_STATUS':
          sendResponse({
            status: {
              connected: this.connection.connected,
              status: this.connection.connected ? 'idle' : 'disconnected',
            },
          });
          break;

        case 'CAPTURE_SCREEN':
          this.handleCaptureScreen();
          break;

        case 'TRANSLATE_TEXT':
          this.sendToAgent({
            type: 'TRANSLATE_TEXT',
            text: message.text,
          });
          break;

        case 'TOGGLE_AGENT':
          this.handleToggleAgent();
          break;

        default:
          console.warn('[AgentManager] Unknown message type:', message.type);
      }

      return false;
    });
  }

  private setupCommandListeners() {
    browser.commands.onCommand.addListener((command) => {
      console.log('[AgentManager] Command received:', command);

      switch (command) {
        case 'capture-screen':
          this.handleCaptureScreen();
          break;
        case 'toggle-agent':
          this.handleToggleAgent();
          break;
        case 'quick-translate':
          this.handleQuickTranslate();
          break;
      }
    });
  }

  private async handleCaptureScreen() {
    try {
      const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
      if (!tab.id) return;

      // Capture visible tab
      const dataUrl = await browser.tabs.captureVisibleTab(undefined, { format: 'png' });

      // Send to agent for OCR processing
      this.sendToAgent({
        type: 'OCR_REQUEST',
        image: dataUrl,
      });

      // Notify content script to show processing overlay
      await browser.tabs.sendMessage(tab.id, {
        type: 'SHOW_PROCESSING',
        message: 'Processing screenshot...',
      });
    } catch (error) {
      console.error('[AgentManager] Failed to capture screen:', error);
    }
  }

  private async handleToggleAgent() {
    try {
      const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
      if (!tab.id) return;

      await browser.tabs.sendMessage(tab.id, {
        type: 'TOGGLE_AGENT_OVERLAY',
      });
    } catch (error) {
      console.error('[AgentManager] Failed to toggle agent:', error);
    }
  }

  private async handleQuickTranslate() {
    try {
      const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
      if (!tab.id) return;

      const response = await browser.tabs.sendMessage(tab.id, {
        type: 'GET_SELECTED_TEXT',
      });

      if (response.text) {
        this.sendToAgent({
          type: 'TRANSLATE_TEXT',
          text: response.text,
        });
      }
    } catch (error) {
      console.error('[AgentManager] Failed to quick translate:', error);
    }
  }

  private sendToAgent(message: any) {
    if (!this.connection.connected || !this.connection.ws) {
      console.warn('[AgentManager] Not connected to agent');
      browser.notifications.create({
        type: 'basic',
        iconUrl: 'images/icon.png',
        title: 'Dannazione',
        message: 'Agent is not connected. Please check your connection.',
      });
      return;
    }

    try {
      this.connection.ws.send(JSON.stringify(message));
      console.log('[AgentManager] Sent to agent:', message);
    } catch (error) {
      console.error('[AgentManager] Failed to send to agent:', error);
    }
  }
}

// Initialize agent manager
const agentManager = new AgentManager();

console.log('[Background] Service worker initialized');

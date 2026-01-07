import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import browser from 'webextension-polyfill';
import config from '../config';
import './popup.css';

interface AgentStatus {
  connected: boolean;
  status: 'idle' | 'processing' | 'error';
  lastActivity?: string;
}

const Popup: React.FC = () => {
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    connected: false,
    status: 'idle',
  });

  const [selectedText, setSelectedText] = useState<string>('');

  useEffect(() => {
    // Check agent connection status
    checkAgentStatus();

    // Get selected text from current tab
    getSelectedText();
  }, []);

  const checkAgentStatus = async () => {
    try {
      const response = await browser.runtime.sendMessage({
        type: 'GET_AGENT_STATUS',
      });
      setAgentStatus(response.status);
    } catch (error) {
      console.error('Failed to get agent status:', error);
      setAgentStatus({ connected: false, status: 'error' });
    }
  };

  const getSelectedText = async () => {
    try {
      const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
      if (tab.id) {
        const response = await browser.tabs.sendMessage(tab.id, {
          type: 'GET_SELECTED_TEXT',
        });
        setSelectedText(response.text || '');
      }
    } catch (error) {
      console.error('Failed to get selected text:', error);
    }
  };

  const handleCaptureScreen = async () => {
    try {
      await browser.runtime.sendMessage({ type: 'CAPTURE_SCREEN' });
      window.close();
    } catch (error) {
      console.error('Failed to capture screen:', error);
    }
  };

  const handleTranslate = async () => {
    if (!selectedText) return;

    try {
      await browser.runtime.sendMessage({
        type: 'TRANSLATE_TEXT',
        text: selectedText,
      });
    } catch (error) {
      console.error('Failed to translate:', error);
    }
  };

  const handleToggleAgent = async () => {
    try {
      await browser.runtime.sendMessage({ type: 'TOGGLE_AGENT' });
    } catch (error) {
      console.error('Failed to toggle agent:', error);
    }
  };

  const openOptions = () => {
    browser.runtime.openOptionsPage();
  };

  return (
    <div className="popup-container">
      <header className="popup-header">
        <h1>Dannazione</h1>
        <div className={`status-indicator ${agentStatus.connected ? 'connected' : 'disconnected'}`}>
          {agentStatus.connected ? '●' : '○'}
        </div>
      </header>

      <div className="popup-content">
        <div className="agent-status">
          <p>
            <strong>Agent:</strong> {config.agent.name}
          </p>
          <p>
            <strong>Status:</strong> {agentStatus.status}
          </p>
          {agentStatus.lastActivity && (
            <p>
              <strong>Last Activity:</strong> {agentStatus.lastActivity}
            </p>
          )}
        </div>

        <div className="quick-actions">
          <button onClick={handleCaptureScreen} className="action-btn primary">
            📸 Capture Screen
          </button>

          <button
            onClick={handleTranslate}
            className="action-btn secondary"
            disabled={!selectedText}
          >
            🌐 Translate Selected
          </button>

          <button onClick={handleToggleAgent} className="action-btn secondary">
            🤖 Toggle Agent
          </button>
        </div>

        {selectedText && (
          <div className="selected-text">
            <strong>Selected Text:</strong>
            <p>{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}</p>
          </div>
        )}
      </div>

      <footer className="popup-footer">
        <button onClick={openOptions} className="options-link">
          ⚙️ Options
        </button>
      </footer>
    </div>
  );
};

const root = document.getElementById('root');
if (root) {
  createRoot(root).render(<Popup />);
}

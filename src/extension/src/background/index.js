/**
 * Dannazione di Providenza - Background Script
 * Manages connection to FastAPI server and message routing
 */

import config from '../config/index.js';
import DannazioneAPI from '../dannazione/index.js';
import { translate } from '@vitalets/google-translate-api';

const API_BASE_URL = config.api.baseUrl;

const api = new DannazioneAPI(API_BASE_URL);
api.initialize();

// Listen for page changes
browser.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // Only trigger when page has finished loading
  if (changeInfo.status === 'complete' && tab.url) {
    console.log('[Dannazione] Page loaded:', tab.url);

    try {
      const results = await browser.scripting.executeScript({
        target: { tabId: tabId },
        func: () => ({
          html: document.body.innerHTML,
          url: window.location.href,
          title: document.title,
        })
      });

      if (results && results[0]) {
        await api.sendContext(results[0].result);
      }
    } catch (error) {
      console.error('[Dannazione] Error getting page context:', error);
    }
  }
});

// Handle messages from content scripts and popup
browser.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  console.log('[Dannazione] Background received message:', message);

  if (message.type === 'TRANSLATE_TEXT') {
    try {
      const result = await translate(message.text, { to: 'en' });
      return Promise.resolve({ translation: result.text });
    } catch (error) {
      console.error('[Dannazione] Translation failed:', error);
      return Promise.resolve({ translation: 'Translation failed' });
    }
  }

  return false;
});

console.log('[Dannazione] Background script initialized');






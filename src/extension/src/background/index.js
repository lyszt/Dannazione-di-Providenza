/**
 * Dannazione di Providenza - Background Script
 * Manages connection to FastAPI server and message routing
 */

import config from '../config/index.js';
import DannazioneAPI from '../dannazione/index.js';

const API_BASE_URL = config.api.baseUrl;

const api = new DannazioneAPI(API_BASE_URL);
api.initialize();

// Inject content script into all existing tabs on extension load/reload
async function injectContentScriptIntoAllTabs() {
  try {
    const tabs = await chrome.tabs.query({});
    for (const tab of tabs) {
      // Only inject into http/https pages
      if (tab.id && tab.url && (tab.url.startsWith('http://') || tab.url.startsWith('https://'))) {
        try {
          await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['content.js']
          });
          console.log(`[Dannazione] Injected content script into tab ${tab.id}: ${tab.url}`);
        } catch (error) {
          // Silently ignore errors for protected pages
          if (!error.message.includes('ExtensionsSettings policy')) {
            console.warn(`[Dannazione] Could not inject into tab ${tab.id}:`, error.message);
          }
        }
      }
    }
  } catch (error) {
    console.error('[Dannazione] Error injecting content scripts:', error);
  }
}

// Inject on extension load
injectContentScriptIntoAllTabs();

// Re-inject on extension install or update
chrome.runtime.onInstalled.addListener(() => {
  console.log('[Dannazione] Extension installed/updated, injecting content scripts');
  injectContentScriptIntoAllTabs();
});

// Listen for page changes
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // Only trigger when page has finished loading
  if (changeInfo.status === 'complete' && tab.url) {
    // Skip extension pages, chrome:// pages, etc.
    if (!tab.url.startsWith('http://') && !tab.url.startsWith('https://')) {
      return;
    }

    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: () => ({
          html: document.body.innerHTML,
          url: window.location.href,
          title: document.title,
        })
      });

      if (results && results[0] && results[0].result) {
        await api.sendContext(results[0].result);
      }
    } catch (error) {
      // Silently ignore pages that can't be scripted
      if (!error.message.includes('ExtensionsSettings policy')) {
        console.error('[Dannazione] Error getting page agent:', error);
      }
    }
  }
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[Dannazione] Background received message:', message);

  if (message.type === 'TRANSLATE_TEXT') {
    // Handle async translation
    (async () => {
      try {
        // Get language settings from storage
        const settings = await chrome.storage.local.get(['fromLang', 'toLang']);
        const fromLang = settings.fromLang || 'auto';
        const toLang = settings.toLang || 'en';

        const response = await fetch(`${API_BASE_URL}/translate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: message.text,
            from_lang: fromLang,
            to_lang: toLang
          })
        });

        if (response.ok) {
          const data = await response.json();
          sendResponse({ translation: data.translation });
        } else {
          throw new Error(`Server error: ${response.status}`);
        }
      } catch (error) {
        console.error('[Dannazione] Translation failed:', error);
        sendResponse({ translation: 'Translation failed: ' + error.message });
      }
    })();

    return true;
  }

  return false;
});

console.log('[Dannazione] Background script initialized');


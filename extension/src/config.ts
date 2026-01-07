/**
 * Dannazione - Configuration
 * Dynamic configuration for the alive agent extension
 */

// Agent environment configuration
const AGENT_ENV = 0; // 0: LOCAL, 1: DEV, 2: PROD

interface AgentConfig {
  wsUrl: string;
  apiUrl: string;
  name: string;
}

const AGENT_CONFIGS: Record<number, AgentConfig> = {
  0: {
    wsUrl: 'ws://localhost:8765',
    apiUrl: 'http://localhost:8765',
    name: 'LOCAL',
  },
  1: {
    wsUrl: 'ws://localhost:8766',
    apiUrl: 'http://localhost:8766',
    name: 'DEV',
  },
  2: {
    wsUrl: 'ws://localhost:8767',
    apiUrl: 'http://localhost:8767',
    name: 'PROD',
  },
};

export const getAgentConfig = (): AgentConfig => {
  return AGENT_CONFIGS[AGENT_ENV] || AGENT_CONFIGS[0];
};

export const config = {
  agent: getAgentConfig(),

  // OCR Configuration
  ocr: {
    defaultEngine: 'tesseract', // 'tesseract' | 'easyocr' | 'paddleocr'
    languages: ['eng', 'por', 'spa', 'fra', 'deu', 'ita', 'jpn'],
  },

  // Translation Configuration
  translation: {
    defaultService: 'google', // 'google' | 'deepl' | 'local'
    targetLanguage: 'en',
  },

  // LLM Configuration
  llm: {
    defaultModel: 'phi-3.5',
    temperature: 0.7,
    maxTokens: 2048,
  },

  // UI Configuration
  ui: {
    overlayOpacity: 0.95,
    theme: 'dark', // 'dark' | 'light' | 'auto'
    fontSize: 14,
  },

  // Hotkeys
  hotkeys: {
    captureScreen: 'Ctrl+Shift+S',
    toggleAgent: 'Ctrl+Shift+A',
    quickTranslate: 'Ctrl+Shift+T',
  },

  // Feature Flags
  features: {
    voiceResponse: true,
    contextAware: true,
    autoTranslate: false,
    smartSuggestions: true,
  },
};

export default config;

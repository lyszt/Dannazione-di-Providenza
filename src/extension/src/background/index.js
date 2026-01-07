/**
 * Dannazione di Providenza - Background Script
 * Manages connection to FastAPI server and message routing
 */

import index from './config/index.js';

const API_BASE_URL = index.api.baseUrl;

class DannazioneAPI {
  constructor() {
    this.initialize();
  }

  initialize() {
    console.log('[Dannazione] Initializing...');
  }

}

const api = new DannazioneAPI();

console.log('[Dannazione] Background script initialized');


class DannazioneAPI {
  constructor(base_url) {
    this.base_url = base_url;
    this.initialize();
  }

  initialize() {
    console.log('[Dannazione] Initializing...');
  }

  async sendContext(contextData) {
    try {
      const response = await fetch(`${this.base_url}/context`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(contextData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('[Dannazione] Context sent successfully:', data);
      return data;
    } catch (error) {
      console.error('[Dannazione] Failed to send context:', error);
      throw error;
    }
  }
}

export default DannazioneAPI;


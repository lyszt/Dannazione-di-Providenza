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
      // Ensure the data structure matches the server's ContextRequest model
      const payload = {
        url: contextData.url,
        title: contextData.title,
        html: contextData.html || contextData.body || '',
        type: contextData.type || 'default'
      };

      const response = await fetch(`${this.base_url}/context`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
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

  async sendSelection(text) {
    try {
      const response = await fetch(`${this.base_url}/context/select`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('[Dannazione] Selection sent successfully:', data);
      return data;
    } catch (error) {
      console.error('[Dannazione] Failed to send selection:', error);
      throw error;
    }
  }

  async sendChatMessage(prompt, body = {}) {
    try {
      const response = await fetch(`${this.base_url}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt, body }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log('[Dannazione] Chat message sent successfully:', data);
      return data;
    } catch (error) {
      console.error('[Dannazione] Failed to send chat message:', error);
      throw error;
    }
  }
}

export default DannazioneAPI;

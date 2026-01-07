import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import browser from 'webextension-polyfill';
import config from '../config';
import './popup.css';

interface Settings {
  ocrEngine: string;
  translationService: string;
  targetLanguage: string;
  theme: string;
  voiceResponse: boolean;
  autoTranslate: boolean;
  smartSuggestions: boolean;
}

const Options: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({
    ocrEngine: config.ocr.defaultEngine,
    translationService: config.translation.defaultService,
    targetLanguage: config.translation.targetLanguage,
    theme: config.ui.theme,
    voiceResponse: config.features.voiceResponse,
    autoTranslate: config.features.autoTranslate,
    smartSuggestions: config.features.smartSuggestions,
  });

  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const stored = await browser.storage.sync.get('settings');
      if (stored.settings) {
        setSettings({ ...settings, ...stored.settings });
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const saveSettings = async () => {
    try {
      await browser.storage.sync.set({ settings });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  const handleChange = (key: keyof Settings, value: string | boolean) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="options-container" style={{ maxWidth: '800px', margin: '0 auto', padding: '24px' }}>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>
          Dannazione
        </h1>
        <p style={{ color: '#9ca3af' }}>Configure your alive agent settings</p>
      </header>

      <div style={{ display: 'grid', gap: '24px' }}>
        <section style={{ background: '#2d2d2d', padding: '20px', borderRadius: '8px' }}>
          <h2 style={{ fontSize: '20px', marginBottom: '16px' }}>OCR Settings</h2>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#9ca3af' }}>
              OCR Engine
            </label>
            <select
              value={settings.ocrEngine}
              onChange={(e) => handleChange('ocrEngine', e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                background: '#3a3a3a',
                border: '1px solid #4a4a4a',
                borderRadius: '6px',
                color: '#e0e0e0',
              }}
            >
              <option value="tesseract">Tesseract</option>
              <option value="easyocr">EasyOCR</option>
              <option value="paddleocr">PaddleOCR</option>
            </select>
          </div>
        </section>

        <section style={{ background: '#2d2d2d', padding: '20px', borderRadius: '8px' }}>
          <h2 style={{ fontSize: '20px', marginBottom: '16px' }}>Translation Settings</h2>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#9ca3af' }}>
              Translation Service
            </label>
            <select
              value={settings.translationService}
              onChange={(e) => handleChange('translationService', e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                background: '#3a3a3a',
                border: '1px solid #4a4a4a',
                borderRadius: '6px',
                color: '#e0e0e0',
              }}
            >
              <option value="google">Google Translate</option>
              <option value="deepl">DeepL</option>
              <option value="local">Local Model</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: '#9ca3af' }}>
              Target Language
            </label>
            <select
              value={settings.targetLanguage}
              onChange={(e) => handleChange('targetLanguage', e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                background: '#3a3a3a',
                border: '1px solid #4a4a4a',
                borderRadius: '6px',
                color: '#e0e0e0',
              }}
            >
              <option value="en">English</option>
              <option value="pt">Portuguese</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
              <option value="ja">Japanese</option>
            </select>
          </div>
        </section>

        <section style={{ background: '#2d2d2d', padding: '20px', borderRadius: '8px' }}>
          <h2 style={{ fontSize: '20px', marginBottom: '16px' }}>Appearance</h2>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: '#9ca3af' }}>
              Theme
            </label>
            <select
              value={settings.theme}
              onChange={(e) => handleChange('theme', e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                background: '#3a3a3a',
                border: '1px solid #4a4a4a',
                borderRadius: '6px',
                color: '#e0e0e0',
              }}
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="auto">Auto</option>
            </select>
          </div>
        </section>

        <section style={{ background: '#2d2d2d', padding: '20px', borderRadius: '8px' }}>
          <h2 style={{ fontSize: '20px', marginBottom: '16px' }}>Features</h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={settings.voiceResponse}
                onChange={(e) => handleChange('voiceResponse', e.target.checked)}
                style={{ width: '18px', height: '18px' }}
              />
              <span>Enable voice responses</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={settings.autoTranslate}
                onChange={(e) => handleChange('autoTranslate', e.target.checked)}
                style={{ width: '18px', height: '18px' }}
              />
              <span>Auto-translate selected text</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={settings.smartSuggestions}
                onChange={(e) => handleChange('smartSuggestions', e.target.checked)}
                style={{ width: '18px', height: '18px' }}
              />
              <span>Enable smart suggestions</span>
            </label>
          </div>
        </section>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            onClick={saveSettings}
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
            }}
          >
            {saved ? '✓ Saved!' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
};

const root = document.getElementById('root');
if (root) {
  createRoot(root).render(<Options />);
}

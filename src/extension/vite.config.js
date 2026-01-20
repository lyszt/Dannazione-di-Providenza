import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import fs from 'fs';
import path from 'path';
import tailwindcss from '@tailwindcss/vite'

const isDev = process.env.NODE_ENV === 'development';

// Plugin to generate manifest.json from template
function generateManifest() {
  return {
    name: 'generate-manifest',
    writeBundle(options, bundle) {
      const manifestTemplate = JSON.parse(
        fs.readFileSync('src/manifest.template.json', 'utf-8')
      );

      // Get all JS and CSS files from the bundle
      const resources = Object.keys(bundle).filter(
        (fileName) => fileName.endsWith('.js') || fileName.endsWith('.css')
      );

      // Extract existing web_accessible_resources configuration
      const templateWAR = Array.isArray(manifestTemplate.web_accessible_resources)
        ? manifestTemplate.web_accessible_resources[0] ?? {}
        : {};

      const matches = Array.isArray(templateWAR.matches) && templateWAR.matches.length > 0
        ? templateWAR.matches
        : ['<all_urls>'];

      const staticResources = Array.isArray(templateWAR.resources)
        ? templateWAR.resources
        : [];

      // Combine static and dynamic resources
      const combinedResources = Array.from(
        new Set([...staticResources, ...resources])
      );

      // Update manifest with combined resources
      manifestTemplate.web_accessible_resources = [
        {
          resources: combinedResources,
          matches,
        },
      ];

      const outDir = options.dir || 'dist';
      fs.writeFileSync(
        path.resolve(outDir, 'manifest.json'),
        JSON.stringify(manifestTemplate, null, 2)
      );

      console.log('✓ manifest.json generated');
    },
  };
}

export default defineConfig({
  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: 'popup.html',
          dest: '.',
        },
        {
          src: 'public/*',
          dest: '.',
        },
      ],
    }),

    generateManifest(),
    tailwindcss(),
  ],

  build: {
    outDir: 'dist',
    emptyOutDir: true,
    target: 'es2022',
    sourcemap: isDev ? true : false,
    minify: isDev ? false : 'terser',

    rollupOptions: {
      input: {
        popup: path.resolve(import.meta.dirname, 'src/popup/index.js'),
        background: path.resolve(import.meta.dirname, 'src/background/index.js'),
        content: path.resolve(import.meta.dirname, 'src/content/index.js'),
      },

      output: {
        // Use ES format - background supports it, content will be bundled as single file
        format: 'es',
        inlineDynamicImports: true,
        manualChunks: undefined,  // Disable all code splitting

        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'background') return 'background.js';
          if (chunkInfo.name === 'popup') return 'popup.js';
          if (chunkInfo.name === 'content') return 'content.js';
          return '[name].js';
        },

        assetFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'popup.css') return 'popup.css';
          return '[name].[ext]';
        },
      },
    },

    chunkSizeWarningLimit: 1000,
  },

  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
});

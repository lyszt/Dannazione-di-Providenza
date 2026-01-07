import { defineConfig, type PluginOption } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import fs from 'fs';
import { visualizer } from 'rollup-plugin-visualizer';

const shouldAnalyze = process.env.ANALYZE === 'true';
const isDev = process.env.NODE_ENV === 'development';

/**
 * Generates manifest.json from manifest.template.json
 * Dynamically adds web_accessible_resources based on build output
 */
function generateManifest(): PluginOption {
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

      console.log('✓ manifest.json generated with dynamic resources');
    },
  };
}

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [],
      },
    }),

    viteStaticCopy({
      targets: [
        {
          src: 'popup.html',
          dest: '.',
        },
        {
          src: 'options.html',
          dest: '.',
        },
        {
          src: 'public/images/*',
          dest: 'images',
        },
      ],
    }),

    generateManifest(),
  ],

  server: {
    hmr: true,
    port: 5173,
  },

  build: {
    outDir: 'dist',
    emptyOutDir: true,
    target: 'es2022',
    sourcemap: isDev ? true : false,
    minify: isDev ? false : 'terser',

    terserOptions: isDev
      ? undefined
      : {
          compress: {
            ecma: 2020 as const,
            module: true,
            passes: 2,
            pure_getters: true,
            toplevel: false,
            drop_console: false,
            drop_debugger: true,
            unsafe_arrows: false,
            unsafe_methods: false,
          },
          mangle: {
            toplevel: false,
          },
          format: {
            comments: false,
            ecma: 2020 as const,
          },
        },

    rollupOptions: {
      input: {
        popup: path.resolve(__dirname, 'src/popup/index.tsx'),
        options: path.resolve(__dirname, 'src/popup/options.tsx'),
        background: path.resolve(__dirname, 'src/background/index.ts'),
        agentBridge: path.resolve(__dirname, 'src/content/agentBridge.ts'),
      },

      plugins: [
        shouldAnalyze &&
          visualizer({
            filename: path.resolve(__dirname, 'stats/bundle.html'),
            template: 'treemap',
            gzipSize: true,
            brotliSize: true,
            open: false,
          }),
      ].filter(Boolean),

      output: {
        format: 'es',

        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'background') return 'background.js';
          if (chunkInfo.name === 'popup') return 'popup.js';
          if (chunkInfo.name === 'options') return 'options.js';
          if (chunkInfo.name === 'agentBridge') return 'agentBridge.js';
          return '[name].[hash].js';
        },

        chunkFileNames: '[name].[hash].js',

        assetFileNames: (assetInfo) => {
          const name = assetInfo.name || '';
          if (name === 'popup.css') return 'popup.css';
          if (name === 'options.css') return 'options.css';
          if (name === 'agentBridge.css') return 'agentOverlay.css';
          if (name.endsWith('.css')) return '[name].css';
          return '[name].[hash].[ext]';
        },

        manualChunks: undefined,
      },
    },

    chunkSizeWarningLimit: 1000,
    cssCodeSplit: true,
    cssMinify: true,
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  optimizeDeps: {
    include: ['react', 'react-dom', 'webextension-polyfill'],
  },
});

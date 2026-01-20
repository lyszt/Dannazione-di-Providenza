const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');
const fs = require('fs');

module.exports = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',

  entry: {
    background: './src/background/index.js',
    content: './src/content/index.js',
    popup: './src/popup/index.js',
  },

  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
    clean: true,
  },

  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
    ],
  },

  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'popup.html', to: 'popup.html' },
        { from: 'public', to: '.' },
        { from: 'src/styles', to: 'styles' },
        {
          from: 'src/manifest.template.json',
          to: 'manifest.json',
          transform(content) {
            const manifest = JSON.parse(content.toString());
            return JSON.stringify(manifest, null, 2);
          },
        },
      ],
    }),
  ],

  optimization: {
    // Don't split chunks - bundle everything into entry files
    splitChunks: false,
    runtimeChunk: false,
  },

  devtool: process.env.NODE_ENV === 'production' ? false : 'cheap-module-source-map',
};

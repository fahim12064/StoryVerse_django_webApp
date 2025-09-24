const path = require('path');

module.exports = {
  entry: {
    main: './static/js/main.js',
    notifications: './static/js/notifications.js',
    messaging: './static/js/messaging.js',
    interactions: './static/js/interactions.js',
  },
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, 'static/js/dist'),
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
};
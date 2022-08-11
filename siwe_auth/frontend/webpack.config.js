const path = require('path');

module.exports = {
  mode: 'production',
  entry: './src/index.js',
  resolve: {
    fallback: {
      fs: false,
      path: false,
      util: false
    }
  },
  output: {
    filename: 'login.js',
    path: path.resolve(__dirname, '../static/siwe_auth/js')
  }
};

/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

var webpack = require('webpack');

var DEBUG = process.env.NODE_ENV !== 'production';
var mode = DEBUG ? 'development' : 'production';

// XXX: kinda hard-coded, although we should stick to /static/ really
var STATIC_URL = (DEBUG ? '/static/' : '/assets/') + '/js/';

var entries = {
  'admin/general': './admin/general/app.js',
  admin: './admin/app.js',
  user: './user/app.js',
  common: ['./common.js'],
  editor: ['./editor/app.js'],
  reports: ['./reports/app.js'],
};

var resolve = {
  modules: [
    'node_modules',
    'shared',
  ],
  alias: {
    pootle: __dirname,

    jquery: __dirname + '/vendor/jquery/jquery.js',
    backbone: __dirname + '/vendor/backbone/backbone.js',

    'backbone-move': __dirname + '/vendor/backbone/backbone.move.js',
    'backbone-safesync': __dirname + '/vendor/backbone/backbone.safesync.js',

    'jquery-bidi': __dirname + '/vendor/jquery/jquery.bidi.js',
    'jquery-easing': __dirname + '/vendor/jquery/jquery.easing.js',
    'jquery-flot': __dirname + '/vendor/jquery/jquery.flot.js',
    'jquery-flot-stack': __dirname + '/vendor/jquery/jquery.flot.stack.js',
    'jquery-flot-marks': __dirname + '/vendor/jquery/jquery.flot.marks.js',
    'jquery-flot-time': __dirname + '/vendor/jquery/jquery.flot.time.js',
    'jquery-highlightRegex': __dirname + '/vendor/jquery/jquery.highlightRegex.js',
    'jquery-history': __dirname + '/vendor/jquery/jquery.history.js',
    'jquery-magnific-popup': __dirname + '/vendor/jquery/jquery.magnific-popup.js',
    'jquery-select2': __dirname + '/vendor/jquery/jquery.select2.js',
    'jquery-serializeObject': __dirname + '/vendor/jquery/jquery.serializeObject.js',
    'jquery-tipsy': __dirname + '/vendor/jquery/jquery.tipsy.js',
    'jquery-utils': __dirname + '/vendor/jquery/jquery.utils.js',

    levenshtein: __dirname + '/vendor/levenshtein.js', // FIXME: use npm module
    moment: __dirname + '/vendor/moment.js', // FIXME: use npm module
    odometer: __dirname + '/vendor/odometer.js', // FIXME: use npm module
    spin: __dirname + '/vendor/spin.js', // FIXME: use npm module
  },
};

/* Plugins */

var plugins = [
  new webpack.IgnorePlugin(/^\.\/locale$/, /vendor$/),
  new webpack.ProvidePlugin({
    'window.Backbone': 'backbone',
  }),
];

/* Exported configuration */

var config = {
  mode,
  context: __dirname,
  entry: entries,
  output: {
    path: __dirname,
    publicPath: STATIC_URL,
    filename: '[name]/app.bundle.js',
    chunkFilename: '[name]/app.bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.css/,
        use: [
          'style-loader',
          'css-loader',
        ],
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        options: {
          babelrc: false,
          cacheDirectory: true,
          presets: [
            require.resolve('babel-preset-env'),
            require.resolve('babel-preset-react'),
          ],
        },
        exclude: /node_modules|vendor|.*\.test\.js/,
      },
    ],
  },
  resolve: resolve,
  plugins: plugins,
  optimization: {
    runtimeChunk: 'single',
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]|[\\/]vendor[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },
};

if (DEBUG) {
  config.devtool = '#source-map';
  config.output.pathinfo = true;
}

module.exports = config;

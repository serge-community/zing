/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

var webpack = require('webpack');
var path = require('path');

var env = process.env.NODE_ENV;
var DEBUG = env !== 'production';


var entries = {
  'admin/general': './admin/general/app.js',
  admin: './admin/app.js',
  user: './user/app.js',
  common: ['./common.js'],
  editor: ['./editor/app.js'],
  reports: ['./reports/app.js'],
  vendor: [
    'react', 'react-dom', 'jquery', 'underscore', 'backbone',
  ],
};


var resolve = {
  modulesDirectories: ['node_modules', 'shared'],
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
  }
};


// Read extra `resolve.root` paths from the `WEBPACK_ROOT` envvar
// and merge the entry definitions from the manifest files
var root = process.env.WEBPACK_ROOT;
if (root !== undefined) {
  var customPaths = root.split(';');
  resolve.root = [path.join(__dirname, 'node_modules')].concat(customPaths);

  function mergeWithArrays(target, source) {
    var rv = Object(target);
    var value;
    Object.getOwnPropertyNames(source).forEach(function (key) {
      value = source[key];
      // Merge values if a key exists both in source and target objects and the
      // target contains an array
      if (target.hasOwnProperty(key) && Array.isArray(target[key])) {
        value = target[key].concat(source[key]);
      }
      rv[key] = value;
    });

    return rv;
  }

  for (var i=0; i<customPaths.length; i++) {
    var customPath = customPaths[i];

    try {
      var manifestEntries = require(path.join(customPath, 'manifest.json'));
      entries = mergeWithArrays(entries, manifestEntries);
    } catch (e) {
      console.error(e.message);
    }
  }
}


/* Plugins */

var plugins = [];

if (!DEBUG) {
  plugins = [
    new webpack.optimize.UglifyJsPlugin(),
    new webpack.optimize.OccurenceOrderPlugin(),
  ];
} else {
  env = 'development';
}

plugins.push.apply(plugins, [
  new webpack.DefinePlugin({
    'process.env': {NODE_ENV: JSON.stringify(env)}
  }),
  new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
  new webpack.ContextReplacementPlugin(
    /codemirror[\/\\]mode$/,
    /htmlmixed|markdown|rst|textile/
  ),
  new webpack.ProvidePlugin({
    'window.Backbone': 'backbone',
  }),
  new webpack.optimize.CommonsChunkPlugin('vendor', 'vendor.bundle.js')
]);


/* Exported configuration */

var config = {
  context: __dirname,
  entry: entries,
  output: {
    path: __dirname,
    publicPath: process.env.WEBPACK_PUBLIC_PATH,
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
            require.resolve('babel-preset-es2015'),
            require.resolve('babel-preset-react'),
          ],
        },
        exclude: /node_modules|vendor|.*\.test\.js/,
      },
    ],
  },
  resolve: resolve,
  plugins: plugins,
};


if (DEBUG) {
  config.devtool = '#source-map';
  config.output.pathinfo = true;
}


module.exports = config;

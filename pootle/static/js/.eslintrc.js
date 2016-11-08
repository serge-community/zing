module.exports = {
  'extends': 'airbnb',
  env: {
    browser: true,
  },
  parserOptions: {
    ecmaVersion: 6,
    ecmaFeatures: {
      jsx: true,
    },
    sourceType: 'module',
  },
  globals: {
    gettext: false,
    ngettext: false,
    interpolate: false,
    l: false,
    s: false,
    PTL: false,
    require: false,
  },
  plugins: [
    'react',
  ],
  rules: {
    'react/prefer-es6-class': 0,
    'react/prefer-stateless-function': 1,

    // see http://blog.javascripting.com/2015/09/07/fine-tuning-airbnbs-eslint-config/
    'no-cond-assign': [2, 'except-parens'],
  },
};

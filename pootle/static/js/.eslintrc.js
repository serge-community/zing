module.exports = {
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
    global: false,
    ngettext: false,
    interpolate: false,
    s: false,
    PTL: false,
    require: false,
  },
  plugins: [
    'react',
  ],
  rules: {
    'curly': 'error',
    'no-cond-assign': [2, 'except-parens'],
    'no-console': 'error',
    'no-constant-condition': 'error',
    'no-empty': ['error', { allowEmptyCatch: true }],
    'no-extra-semi': 'error',
    'no-redeclare': 'error',
    'no-self-assign': 'error',
    'no-undef': 'error',
    'no-unreachable': 'error',
    'no-unused-vars': 'error',
    'no-useless-escape': 'error',

    "react/jsx-uses-react": "error",
    "react/jsx-uses-vars": "error",
    'react/prefer-es6-class': 0,
    'react/prefer-stateless-function': 1,
  },
};

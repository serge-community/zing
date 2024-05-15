'use strict';

const ORGANIZATION_NAME = 'serge-community'
const PROJECT_NAME = 'zing';
const GH_URL = `https://github.com/${ORGANIZATION_NAME}/${PROJECT_NAME}/`;
const GH_EDIT_URL = `${GH_URL}edit/master/docs/`;

const siteConfig = {
  title: 'Zing',
  tagline: 'Opinionated translation server for continuous localization.',
  url: 'https://serge-community.github.io/zing/',
  baseUrl: '/zing/',
  cleanUrl: true,
  projectName: PROJECT_NAME,
  headerLinks: [
    {
      doc: 'introduction',
      label: 'Docs',
    },
    {
      page: 'faq',
      label: 'FAQ',
    },
    {
      href: GH_URL,
      label: "GitHub",
      external: true,
    },
  ],
  /* path to images for header/footer */
  headerIcon: 'img/logo.svg',
  //favicon: 'img/favicon.png',
  /* colors for website */
  colors: {
    primaryColor: '#222',
    secondaryColor: '#444',
  },
  // This copyright info is used in /core/Footer.js and blog rss/atom feeds.
  copyright:
    'Copyright © ' + new Date().getFullYear() + ' Zing Contributors',
  organizationName: ORGANIZATION_NAME, // or set an env variable ORGANIZATION_NAME
  projectName: PROJECT_NAME, // or set an env variable PROJECT_NAME
  editUrl: GH_EDIT_URL,
  highlight: {
    // Highlight.js theme to use for syntax highlighting in code blocks
    theme: 'default',
  },
  scripts: [],

  // Custom config keys
  repoURL: GH_URL,
};

module.exports = siteConfig;

'use strict';

const React = require('react');

const CompLibrary = require('../../core/CompLibrary.js');
const Container = CompLibrary.Container;
const MarkdownBlock = CompLibrary.MarkdownBlock;

const siteConfig = require(process.cwd() + '/siteConfig.js');


const contents = [
  {
    question: 'Where can I get help?',
    answer: `Feel free to ask questions in [our Gitter channel](${siteConfig.gitterURL}).`,
  },
  {
    question: 'Where can I report a bug?',
    answer: `Please file an issue [on GitHub](${siteConfig.repoURL + "issues/new"}).`,
  },
  {
    question: 'Who maintains and develops Zing?',
    answer: `Zing is built by the localization team at [Evernote](https://www.evernote.com/).`,
  },
  {
    question: 'Is Zing actively developed?',
    answer: 'While the current feature set already fulfills the needs of Evernote, Zing is actively supported by fixing bugs and upgrading to newer versions of libraries.',
  },
  {
    question: 'Is Zing production-ready?',
    answer: `Yes. The [Evernote Translation Server](https://translate.evernote.com/) runs Zing, and it's an important part of the day-to-day business.`,
  },
  {
    question: 'Is Zing stable across versions?',
    answer: `Zing adheres to [Semantic Versioning](https://semver.org/), and because **it hasn't reached a 1.0 version yet, anything might change anytime and there can be backwards incompatible changes** between releases.`,
  },
  {
    question: 'Why does Zing only work with PO files?',
    answer: 'The guiding principle for Zing is integrating well with Serge in order to provide a flexible continuous localization workflow. As such, it only requires to support an interchange file format, and Gettext PO has resulted to be a perfect fit in our experience of over 8 years.',
  },
]


class Help extends React.Component {
  render() {
    return (
      <div className="docMainWrapper wrapper">
        <Container className="mainContainer documentContainer postContainer">
          <div className="post">
            {contents.map(entry => [
              <header className="postHeader">
                <h2>{entry.question}</h2>
              </header>,
              <MarkdownBlock>{entry.answer}</MarkdownBlock>
            ])}
          </div>
        </Container>
      </div>
    );
  }
}

module.exports = Help;

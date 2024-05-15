'use strict';

const React = require('react');

const CompLibrary = require('../../core/CompLibrary.js');
const Container = CompLibrary.Container;
const GridBlock = CompLibrary.GridBlock;

const siteConfig = require(process.cwd() + '/siteConfig.js');

const URL_FEATURE_SERGE = docUrl('continuous-localization.html');
const URL_FEATURE_EDITOR = docUrl('editor.html');
const URL_FEATURE_INVOICES = docUrl('invoices.html');

function imgUrl(img) {
  return siteConfig.baseUrl + 'img/' + img;
}

function docUrl(doc, language) {
  return siteConfig.baseUrl + 'docs/' + (language ? language + '/' : '') + doc;
}

class Button extends React.Component {
  render() {
    return (
      <div className="pluginWrapper buttonWrapper">
        <a className="button" href={this.props.href} target={this.props.target}>
          {this.props.children}
        </a>
      </div>
    );
  }
}

Button.defaultProps = {
  target: '_self',
};

const SplashContainer = props => (
  <div className="homeContainer">
    <div className="homeSplashFade">
      <div className="wrapper homeWrapper">{props.children}</div>
    </div>
  </div>
);

const Logo = props => (
  <div className="projectLogo">
    <img src={props.img_src} />
  </div>
);

const PromoSection = props => (
  <div className="section promoSection">
    <div className="promoRow">
      <div className="pluginRowBlock">{props.children}</div>
    </div>
  </div>
);

class HomeSplash extends React.Component {
  render() {
    let language = this.props.language || '';
    return (
      <SplashContainer>
        <div className="inner">
          <img src={imgUrl('logo.svg')} className="titleLogo" />
          <h2 className="projectTitle">
            {siteConfig.title}
            <small>{siteConfig.tagline}</small>
          </h2>
          <PromoSection>
            <Button href={docUrl('introduction', language)}>Documentation</Button>
          </PromoSection>
        </div>
      </SplashContainer>
    );
  }
}

const Block = props => (
  <Container
    padding={['bottom', 'top']}
    id={props.id}
    background={props.background}>
    <GridBlock align="center" contents={props.children} layout={props.layout} />
  </Container>
);

const Features = props => (
  <Block layout="threeColumn" id="features">
    {[
      {
        content: `Online Computer-Assisted [Translation environment](${URL_FEATURE_EDITOR}) with helpful hints for translators.`,
        image: imgUrl('feat-editor.svg'),
        imageAlign: 'top',
        imageUrl: URL_FEATURE_EDITOR,
        title: 'Online Editor',
      },
      {
        content: `Seamless [integration with Serge](${URL_FEATURE_SERGE}) to enable true and robust continuous localization.`,
        image: imgUrl('feat-serge.svg'),
        imageAlign: 'top',
        imageUrl: URL_FEATURE_SERGE,
        title: 'Serge Integration',
      },
      {
        content: `Built-in [invoicing and reporting](${URL_FEATURE_INVOICES}) capabilities to track and pay for the work done by translators.`,
        image: imgUrl('feat-invoicing.svg'),
        imageAlign: 'top',
        imageUrl: URL_FEATURE_INVOICES,
        title: 'Invoicing and Reporting',
      },
    ]}
  </Block>
);

class Index extends React.Component {
  render() {
    let language = this.props.language || '';

    return (
      <div>
        <HomeSplash language={language} />
        <div className="mainContainer">
          <Features />
        </div>
      </div>
    );
  }
}

module.exports = Index;

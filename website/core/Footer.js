'use strict';

const React = require('react');

class Footer extends React.Component {
  render() {
    const currentYear = new Date().getFullYear();
    return (
      <footer className="nav-footer" id="footer">
        <section className="copyright">
          Copyright &copy; {currentYear} Zing Contributors.
        </section>
      </footer>
    );
  }
}

module.exports = Footer;

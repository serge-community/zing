/*
 * Copyright (C) Pootle contributors.
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import ReactDOM from 'react-dom';

import LayeredComponent from './LayeredComponent';
import ModalContainer from './ModalContainer';

export function showModal(props) {
  const div = document.createElement('div');
  document.body.appendChild(div);

  return ReactDOM.render(
    <Modal
      {...props}
      onClose={() => {
        ReactDOM.unmountComponentAtNode(div);
        document.body.removeChild(div);
        if ('onClose' in props) {
          props.onClose();
        }
      }}
    />,
    div
  );
}

export const ModalHeader = ({ children }) => (
  <div className="lightbox-header">{children}</div>
);

ModalHeader.propTypes = {
  children: React.PropTypes.node.isRequired,
};

export const ModalFooter = ({ children }) => (
  <div className="lightbox-footer">{children}</div>
);

ModalFooter.propTypes = {
  children: React.PropTypes.node.isRequired,
};

const Modal = React.createClass({
  propTypes: {
    children: React.PropTypes.node.isRequired,
    onCanClose: React.PropTypes.func,
    onClose: React.PropTypes.func.isRequired,
    title: React.PropTypes.node,
    showClose: React.PropTypes.bool,
    className: React.PropTypes.string,
    header: React.PropTypes.func,
    footer: React.PropTypes.func,
  },

  /* Lifecycle */

  getDefaultProps() {
    return {
      title: '',
      showClose: true,
    };
  },

  /* Handlers */

  handleClose() {
    if ('onCanClose' in this.props && !this.props.onCanClose()) {
      return;
    }

    // Parent components need to take care of rendering the component
    // and unmounting it according to their needs; one can also use
    // showModal() convenience function that will take care of
    // unmounting on close
    this.props.onClose();
  },

  /* Layout */

  renderHeader() {
    if (this.props.header) {
      return <ModalHeader>{this.props.header()}</ModalHeader>;
    }

    const title = this.props.title && (
      <div className="lightbox-title">{this.props.title}</div>
    );
    const closeBtn = this.props.showClose && (
      <button
        className="icon-close lightbox-close"
        onClick={this.handleClose}
      ></button>
    );

    return (
      <ModalHeader>
        {title}
        {closeBtn}
      </ModalHeader>
    );
  },

  renderFooter() {
    if (this.props.footer) {
      return <ModalFooter>{this.props.footer()}</ModalFooter>;
    }

    return null;
  },

  renderLayer() {
    return (
      <ModalContainer {...this.props}>
        {this.renderHeader()}
        <div className="lightbox-content">{this.props.children}</div>
        {this.renderFooter()}
      </ModalContainer>
    );
  },

  render() {
    return <LayeredComponent>{this.renderLayer()}</LayeredComponent>;
  },
});

export default Modal;

/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';


const propTypes = {
  children: React.PropTypes.node.isRequired,
  tag: React.PropTypes.oneOfType([
    React.PropTypes.func,
    React.PropTypes.string,
  ]),
  title: React.PropTypes.string,
};

const defaultProps = {
  title: '',
  tag: 'a',
};

const contextTypes = {
  onToggle: React.PropTypes.func.isRequired,
};


// XXX: make icon-desc optional via prop?
const DropdownToggle = ({ children, title, tag: Tag }, context) => {
  const extraProps = title ? { title } : {};

  return (
    <Tag
      onClick={() => context.onToggle()}
      {...extraProps}
    >
      <span className="dropdown-label">
        {children}
      </span>
      <span className="icon-desc" />
    </Tag>
  );
};

DropdownToggle.propTypes = propTypes;
DropdownToggle.defaultProps = defaultProps;
DropdownToggle.contextTypes = contextTypes;


export default DropdownToggle;

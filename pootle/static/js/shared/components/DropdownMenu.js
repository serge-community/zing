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
};

const contextTypes = {
  isOpen: React.PropTypes.bool.isRequired,
  onMenuMouseDown: React.PropTypes.func.isRequired,
  onMenuMouseUp: React.PropTypes.func.isRequired,
};


const DropdownMenu = ({ children }, context) => {
  if (!context.isOpen) {
    // FIXME: use `null` once in React 15+
    // Refs. https://github.com/facebook/react/issues/5355
    return <noscript />;
  }

  return (
    <div
      className="dropdown-container"
      onMouseDown={context.onMenuMouseDown}
      onMouseUp={context.onMenuMouseUp}
      role="menu"
      tabIndex="0"
    >
      {children}
    </div>
  );
};

DropdownMenu.propTypes = propTypes;
DropdownMenu.contextTypes = contextTypes;


export default DropdownMenu;

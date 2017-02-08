/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import DueDatePicker from './DueDatePicker';

import { dueTime } from 'utils/dueTime';
import { t } from 'utils/i18n';


class DueDateWidget extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      isOpen: false,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.dueOn !== nextProps.dueOn) {
      this.setState((prevState) => ({ isOpen: !prevState.isOpen }));
    }
  }

  handleClick() {
    this.setState((prevState) => ({
      isOpen: !prevState.isOpen,
    }));
  }

  render() {
    const { dueOn } = this.props;

    let dueOnMsg = t('No due date set');
    let dueOnTooltip = '';
    if (dueOn) {
      dueOnMsg = dueTime(dueOn * 1000);
      dueOnTooltip = (new Date(dueOn * 1000)).toUTCString();
    }

    const styles = {
      widgetContainer: {
        position: 'relative',
      },
      popupContainer: {
        position: 'absolute',
        width: '25em', // randomish
        padding: '1em',

        border: '1px solid #d9d9d9',
        borderRadius: '0 0 3px 3px',
        backgroundColor: '#eee',
      },
      dropdownToggle: {
        fontFamily: 'ZingIcons',
      },
    };

    return (
      <div style={styles.widgetContainer}>
        <a
          className="due-dates-widget"
          title={dueOnTooltip}
          onClick={() => this.handleClick()}
        >
          {dueOnMsg}
          <span
            style={styles.dropdownToggle}
          >J</span>
        </a>
        {this.state.isOpen &&
          <div style={styles.popupContainer}>
            <DueDatePicker
              id={this.props.id}
              dueOn={dueOn}
              onRemove={this.props.onRemove}
              onUpdate={this.props.onUpdate}
            />
          </div>
        }
      </div>
    );
  }

}

DueDateWidget.propTypes = {
  dueOn: React.PropTypes.number,
  id: React.PropTypes.number,
  onRemove: React.PropTypes.func.isRequired,
  onUpdate: React.PropTypes.func.isRequired,
};
DueDateWidget.defaultProps = {
  dueOn: 0,
  id: 0,
};


export default DueDateWidget;

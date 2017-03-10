/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import DayPicker, { DateUtils } from 'react-day-picker';

import { t } from 'utils/i18n';

// XXX: use CSS modules so we only customize what's needed
import './DueDatePicker.css';


/**
 * Convert a Date object `date` into an ISO 8601-formatted date.
 */
function toISODate(date) {
  return date.toISOString().slice(0, -14);
}


class DueDatePicker extends React.Component {

  constructor(props) {
    super(props);

    this.initiallySelectedDay = (
      this.props.dueOn ? new Date(this.props.dueOn * 1000) : new Date()
    );
    this.state = {
      selectedDay: this.initiallySelectedDay,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.dueOn !== nextProps.dueOn) {
      this.initiallySelectedDay = (
        nextProps.dueOn ? new Date(nextProps.dueOn * 1000) : new Date()
      );
      this.setState({ selectedDay: this.initiallySelectedDay });
    }
  }

  canBeSubmitted() {
    return (
      !this.props.dueOn ||
      toISODate(this.state.selectedDay) !== toISODate(this.initiallySelectedDay)
    );
  }

  handleDayClick(day) {
    this.setState({ selectedDay: day });
  }

  handleSubmit(e) {
    e.preventDefault();

    if (!this.canBeSubmitted()) {
      return;
    }

    this.props.onUpdate(toISODate(this.state.selectedDay));
  }

  render() {
    const { id } = this.props;
    const { selectedDay } = this.state;
    const start = DateUtils.addMonths(selectedDay, -1);
    const end = DateUtils.addMonths(selectedDay, 6);

    return (
      <div className="duedate-picker">
        <DayPicker
          initialMonth={selectedDay}
          selectedDays={selectedDay}
          fromMonth={start}
          toMonth={end}
          onDayClick={(day) => this.handleDayClick(day)}
        />
        <div className="duedate-picker-buttons">
        {id > 0 &&
          <button
            type="button"
            className="btn btn-danger"
            onClick={() => this.props.onRemove(id)}
          >
            {t('Remove Due Date')}
          </button>
        }
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!this.canBeSubmitted()}
            onClick={(e) => this.handleSubmit(e)}
          >
            {t('Set Due Date')}
          </button>
        </div>
      </div>
    );
  }

}

DueDatePicker.propTypes = {
  id: React.PropTypes.number,
  dueOn: React.PropTypes.number,
  onRemove: React.PropTypes.func.isRequired,
  onUpdate: React.PropTypes.func.isRequired,
};
DueDatePicker.defaultProps = {
  id: 0,
  dueOn: 0,
};


export default DueDatePicker;

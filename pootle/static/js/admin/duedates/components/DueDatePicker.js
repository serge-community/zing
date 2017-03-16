/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';
import DayPicker, { DateUtils } from 'react-day-picker';

import { t, tct, dateTimeTzFormatter } from 'utils/i18n';

import { formatDueTime } from '../utils';

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

    this.committedDay = (
      this.props.dueOn ? new Date(this.props.dueOn * 1000) : new Date()
    );
    this.state = {
      selectedDay: this.committedDay,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.dueOn !== nextProps.dueOn) {
      this.committedDay = (
        nextProps.dueOn ? new Date(nextProps.dueOn * 1000) : new Date()
      );
      this.setState({ selectedDay: this.committedDay });
    }
  }

  canBeSubmitted() {
    return (
      !this.props.dueOn ||
      toISODate(this.state.selectedDay) !== toISODate(this.committedDay)
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

  renderHint() {
    const { selectedDay } = this.state;

    if (!selectedDay) {
      // XXX: hackish but works for now
      const timezone = (new Intl.DateTimeFormat(PTL.settings.UI_LOCALE, {
        timeZone: PTL.settings.TIME_ZONE,
        timeZoneName: 'long',
      })).format(1).split(' ').slice(1).join(' ');
      const hintMsg = tct(
        'Use the calendar below to select a date by 9:00AM of which ' +
        ' (in %(timezone)s) this section should be completed.',
        { timezone }
      );

      return (
        <p className="hint">{hintMsg}</p>
      );
    }

    // FIXME: this needs TZ info! otherwise times will be incorrect/in local TZ
    const selectedDayMs = this.state.selectedDay.getTime();
    return (
      <div>
        <p>{dateTimeTzFormatter.format(selectedDayMs)}</p>
        <p>{formatDueTime(selectedDayMs)}</p>
      </div>
    );
  }

  render() {
    const { id } = this.props;
    const { committedDay } = this;
    const now = new Date();
    const start = DateUtils.addMonths(now, -1);
    const end = DateUtils.addMonths(now, 6);

    return (
      <div className="duedate-picker">
        {this.renderHint()}
        <DayPicker
          initialMonth={committedDay}
          fromMonth={start}
          toMonth={end}
          onDayClick={(day) => this.handleDayClick(day)}
          onDayFocus={(day) => this.handleDayClick(day)}
          modifiers={{
            committed: (day) => DateUtils.isSameDay(day, committedDay),
            selected: (day) => DateUtils.isSameDay(day, this.state.selectedDay),
          }}
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

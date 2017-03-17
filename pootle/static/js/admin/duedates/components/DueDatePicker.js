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
import { toServerDate, setServerHours } from 'utils/time';

import { formatDueTime } from '../utils';

// XXX: use CSS modules so we only customize what's needed
import './DueDatePicker.css';


class DueDatePicker extends React.Component {

  constructor(props) {
    super(props);

    this.committedDay = (
      this.props.dueOn ? new Date(this.props.dueOn * 1000) : null
    );
    this.state = {
      selectedDay: this.committedDay,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.dueOn !== nextProps.dueOn) {
      this.committedDay = (
        nextProps.dueOn ? new Date(nextProps.dueOn * 1000) : null
      );
      this.setState({ selectedDay: this.committedDay });
    }
  }

  canBeSubmitted() {
    return (
      this.state.selectedDay &&
      !DateUtils.isSameDay(this.state.selectedDay, this.committedDay)
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

    this.props.onUpdate(
      this.state.selectedDay.toISOString().slice(0, -14)
    );
  }

  renderHint() {
    const { selectedDay } = this.state;

    if (!selectedDay) {
      const timezone = `UTC${PTL.settings.TZ_OFFSET_DISPLAY}`;
      const hintMsg = tct(
        'Due time: 9:00am %(timezone)s',
        { timezone }
      );
      return (
        <div className="current-selection placeholder">
          <p>{t('Please select a due date')}</p>
          <p>{hintMsg}</p>
        </div>
      );
    }

    const serverDate = toServerDate(selectedDay);
    const serverDateStartOfDay = setServerHours(serverDate, 9, 0);
    return (
      <div className="current-selection">
        <p>{dateTimeTzFormatter.format(serverDateStartOfDay)}</p>
        <p>{formatDueTime(serverDateStartOfDay)}</p>
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
        <DayPicker
          initialMonth={committedDay || now}
          fromMonth={start}
          toMonth={end}
          onDayClick={(day) => this.handleDayClick(day)}
          onDayFocus={(day) => this.handleDayClick(day)}
          modifiers={{
            committed: (day) => DateUtils.isSameDay(day, committedDay),
            selected: (day) => DateUtils.isSameDay(day, this.state.selectedDay),
          }}
        />
        {this.renderHint()}
        <div className="duedate-picker-buttons">
        {id > 0 &&
          <button
            type="button"
            className="btn btn-danger"
            onClick={() => this.props.onRemove(id)}
          >
            {t('Remove')}
          </button>
        }
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!this.canBeSubmitted()}
            onClick={(e) => this.handleSubmit(e)}
          >
            {t('Set')}
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

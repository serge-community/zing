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
 * Convert a unix timestamp `ts` into an ISO 8601-formatted date.
 */
function fromUnixTimestamp(ts) {
  if (!ts) {
    return '';
  }
  return (new Date(ts * 1000)).toISOString().slice(0, -14);
}


class DueDatePicker extends React.Component {

  constructor(props) {
    super(props);

    this.initialIsoDate = fromUnixTimestamp(this.props.dueOn);
    this.state = {
      isoDate: this.initialIsoDate,
    };
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.dueOn !== nextProps.dueOn) {
      this.initialIsoDate = fromUnixTimestamp(nextProps.dueOn);
      this.setState({ isoDate: this.initialIsoDate });
    }
  }

  canBeSubmitted() {
    return (
      this.state.isoDate !== this.initialIsoDate &&
      this.state.isoDate.trim()
    );
  }

  handleDayClick(day) {
    this.setState(() => ({
      isoDate: day.toISOString().slice(0, -14),
    }));
  }

  handleSubmit(e) {
    e.preventDefault();

    if (!this.canBeSubmitted()) {
      return;
    }

    this.props.onUpdate(this.state.isoDate.slice(0, 10));
  }

  render() {
    const styles = {
      buttonsRow: {
        marginTop: '1em',
        float: 'right',
      },
      button: {
        margin: '0 1em',
      },
    };

    const now = new Date();
    const selectedDate = new Date(this.state.isoDate);
    // XXX: check bounds with respect to initial month?
    const start = DateUtils.addMonths(now, -1);
    const end = DateUtils.addMonths(now, 6);
    const { id } = this.props;
    return (
      <div>
        <DayPicker
          initialMonth={selectedDate}
          selectedDays={selectedDate}
          fromMonth={start}
          toMonth={end}
          onDayClick={(day) => this.handleDayClick(day)}
        />
        <div
          style={styles.buttonsRow}
        >
        {id > 0 &&
          <button
            type="button"
            className="btn btn-danger"
            style={styles.button}
            onClick={() => this.props.onRemove(id)}
          >
            {t('Remove Due Date')}
          </button>
        }
          <button
            type="submit"
            className="btn btn-primary"
            style={styles.button}
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

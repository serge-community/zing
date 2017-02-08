/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import React from 'react';

import { t } from 'utils/i18n';


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

  componentDidMount() {
    this.pickerEl.focus();
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

  handleChange() {
    this.setState(() => ({
      isoDate: this.pickerEl.value,
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
      picker: {
        boxSizing: 'border-box',  // FIXME: this should be part of reset
        margin: '0 1em',
        width: '100px',
      },
      buttonsRow: {
        marginTop: '1em',
        float: 'right',
      },
      button: {
        margin: '0 1em',
      },
    };

    const { id } = this.props;
    return (
      <form onSubmit={(e) => this.handleSubmit(e)}>
        <div>
          <label htmlFor="picker">{t('Due date (ISO):')}</label>
          <input
            type="text"
            id="picker"
            maxLength={15}
            style={styles.picker}
            ref={(el) => {
              this.pickerEl = el;
            }}
            onChange={() => this.handleChange()}
            onSubmit={() => this.handleSet()}
            value={this.state.isoDate}
          />
        </div>
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
          >
            {t('Set Due Date')}
          </button>
        </div>
      </form>
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

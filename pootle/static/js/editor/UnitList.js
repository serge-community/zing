/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import $ from 'jquery';

import UnitAPI from 'api/UnitAPI';

import Unit from './Unit';


class UnitsList {

  constructor(props) {
    this.uids = [];
    this.units = {};
    this.idx = -1;
    this.uid = undefined;
    this.unit = undefined;
    this.length = 0;

    this.visibleRowsBefore = 8;
    this.visibleRowsAfter = 29;
    this.prefetchRows = 5; // extra rows around visible ones

    this.props = props;
  }

  fetchUids(reqData) {
    return UnitAPI.fetchUids(reqData).then(
      (data) => {
        this.begin = data.begin || 0;
        this.end = data.end || 0;
        this.total = data.total || 0;
        this.uids = data.uids;
        this.length = data.uids.length;
        this.uid = undefined;

        if (this.total === 0) {
          return false;
        }
        return true;
      },
      (xhr, status) => this.handleFetchError(xhr, status)
    );
  }

  fetchFullUnitData(uid) {
    return UnitAPI.fetchFullUnitData(uid).then(data => data);
  }

  handleUnitChange(uid) {
    if (this.props.onUnitChange) {
      // note that technically this.uid may be already different
      // from passed uid
      this.props.onUnitChange(uid);
    }
    this.cleanupUnusedUnits();
  }

  handleContextDataChange(uid, ctxData) {
    if (this.props.onContextData) {
      // note that technically this.uid may be already different
      // from passed uid
      this.props.onContextData(uid, ctxData);
    }
  }

  handleFetchError(xhr, status) {
    if (this.props.onFetchError) {
      this.props.onFetchError(xhr, status);
    }
  }

  goto(uid) {
    if (uid === this.uid) {
      return;
    }
    this.uid = uid;
    this.idx = this.uids.indexOf(this.uid);
    if (this.idx <= -1) {
      return;
    }

    if (this.unit && this.unit.isFullyLoaded()) {
      this.unit.invalidateEditor();
    }

    this.unit = this.units[this.uid];
    if (!this.uid) {
      return;
    }

    $.when(
      this.prefetchUnits(),
      this.fetchFullUnitData(uid)
    ).then(
      (noData, fullUnitData) => {
        // Unit wasn't prefetched yet
        if (!this.unit) {
          this.unit = this.units[uid];
        }
        this.unit.provideFullData(fullUnitData);
        this.handleUnitChange(uid);
      },
      (xhr, status) => this.handleFetchError(xhr, status)
    );
  }

  loadContextRows() {
    const { uid } = this;
    if (this.unit.contextData) {
      this.handleContextDataChange(uid, this.unit.contextData);
      return;
    }

    // TODO: instead of `gap` and `qty` specify the number of units
    // before/after the given uid
    UnitAPI.fetchContextRows(this.uid, { gap: 0, qty: 5 }).then(
      (data) => {
        if (!data || !data.ctx) {
          return;
        }

        // wrap returned data into Unit objects
        const ctxData = {
          before: data.ctx.before.map(unitData => new Unit(unitData)),
          after: data.ctx.after.map(unitData => new Unit(unitData)),
        };

        this.unit.contextData = ctxData;
        this.handleContextDataChange(uid, ctxData);
      },
      (xhr, status) => this.handleFetchError(xhr, status)
    );
  }

  gotoPrev() {
    const idx = Math.max(0, this.idx - 1);
    this.goto(this.uids[idx]);
  }

  gotoNext() {
    const idx = Math.min(this.uids.length, this.idx + 1);
    this.goto(this.uids[idx]);
  }

  getPosition() {
    return this.begin + this.idx + 1;
  }

  isOnFirstUnit() {
    return this.idx <= 0; // -1 or 0
  }

  isOnLastUnit() {
    return this.idx === this.uids.length - 1;
  }

  firstUnitInVicinity(vicinity) {
    return Math.max(0, this.idx - vicinity);
  }

  lastUnitInVicinity(vicinity) {
    return Math.min(this.uids.length - 1, this.idx + vicinity);
  }

  visibleUnitsBefore() {
    // TODO: instead of just reporting unis to render,
    // can we use a callback whenever the visible units change?
    const start = this.firstUnitInVicinity(this.visibleRowsBefore);
    const end = this.idx - 1;
    return this.uids.slice(start, end + 1);
  }

  visibleUnitsAfter() {
    // TODO: instead of just reporting unis to render,
    // can we use a callback whenever the visible units change?
    const start = this.idx + 1;
    const end = this.lastUnitInVicinity(this.visibleRowsAfter);
    return this.uids.slice(start, end + 1);
  }

  prefetchUnits() {
    const start = this.firstUnitInVicinity(this.visibleRowsBefore + this.prefetchRows);
    const end = this.lastUnitInVicinity(this.visibleRowsAfter + this.prefetchRows);
    const uids = this.uids.slice(start, end + 1);

    const unitsToFetch = uids.filter(uid => !this.units.hasOwnProperty(uid));

    // Do not request anything until there are enough `prefetchRows` amount of
    // units to be fetched.
    if (!unitsToFetch.length ||
        (unitsToFetch.length < this.prefetchRows && start !== 0)) {
      return;
    }

    UnitAPI.fetchUnits({ uids: unitsToFetch }).then(
      (units) => {
        if (!units) {
          return;
        }

        Object.keys(units).forEach((uid) => {
          if (this.units[uid]) {
            return; // unit was already loaded
          }
          const unit = units[uid];
          this.units[uid] = new Unit({
            id: uid,
            source: unit.source,
            sourceLang: unit.source_lang,
            target: unit.target,
            targetLang: unit.target_lang,
          });
        });
      },
      (xhr, status) => this.handleFetchError(xhr, status)
    );
  }

  cleanupUnusedUnits() {
    const aboveStart = 0;
    const aboveEnd = this.firstUnitInVicinity(
      this.visibleRowsBefore + this.prefetchRows
    ) - 1;
    this.cleanupUnitsInRange(aboveStart, aboveEnd);

    const belowStart = this.lastUnitInVicinity(
      this.visibleRowsAfter + this.prefetchRows
    ) + 1;
    const belowEnd = this.length - 1;
    this.cleanupUnitsInRange(belowStart, belowEnd);
  }

  cleanupUnitsInRange(start, end) {
    for (let i = start; i <= end; i++) {
      const uid = this.uids[i];
      if (this.units[uid]) {
        delete this.units[uid];
      }
    }
  }

}


export default UnitsList;

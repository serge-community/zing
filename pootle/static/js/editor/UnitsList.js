/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import UnitAPI from 'api/UnitAPI';
import Unit from './Unit';

class UnitsList {

  constructor() {
    this.uids = [];
    this.units = {};
    this.idx = -1;
    this.uid = undefined;
    this.unit = undefined;
    this.length = 0;
    this.ready = false;
    this.onUnitChange = undefined;
    this.onViewRowsChange = undefined;
    this.onEmptyResults = undefined;
    this.visibleRowsBefore = 8;
    this.visibleRowsAfter = 29;
    this.prefetchRows = 5; // extra rows around visible ones
  }

  init(uids) {
    this.uids = uids;
    this.length = this.uids.length;

    // if the uid was set before, try to update its index
    // or clear uid if it is not found in the new set
    if (this.uid) {
      this.idx = this.uids.indexOf(this.uid);
      if (this.idx === -1) {
        this.uid = undefined;
      }
    }
    this.goto(this.uid || this.uids[0]);
  }

  fetchUids(reqData) {
    console.log('UnitsList.fetchUids(), reqData:', reqData);
    UnitAPI.fetchUids(reqData).then(
      (data) => {
        this.begin = data.begin || 0;
        this.end = data.end || 0;
        this.total = data.total || 0;
        this.init(data.uids);
        if (this.total === 0) {
          this.handleEmptyResults(reqData);
        }
      },
      this.error
    );
  }

  handleUnitChange(uid) {
    console.log('UnitsList.handleUnitChange(), uid:', uid);
    if (this.onUnitChange) {
      // note that technically this.uid may be already different
      // from passed uid
      this.onUnitChange(uid);
    }
    this.cleanupUnusedUnits();
    this.prefetchUnits();
  }

  handleViewRowsChange(uid) {
    console.log('UnitsList.handleViewRowsChange(), uid:', uid);
    if (this.onViewRowsChange) {
      // note that technically this.uid may be already different
      // from passed uid
      this.onViewRowsChange(uid);
    }
    this.cleanupUnusedUnits();
    this.prefetchUnits();
  }

  handleContextDataChange(uid) {
    console.log('UnitsList.handleContextDataChange(), uid:', uid);
    if (this.onContextData) {
      // note that technically this.uid may be already different
      // from passed uid
      this.onContextData(uid);
    }
  }

  handleEmptyResults(reqData) {
    console.log('UnitsList.handleEmptyResults()');
    if (this.onEmptyResults) {
      this.onEmptyResults(reqData);
    }
  }

  goto(uid) {
    this.uid = uid;
    this.idx = this.uids.indexOf(this.uid);
    if (this.idx > -1) {
      this.unit = this.units[this.uid];
      if (this.uid) {
        if (!this.unit || !this.unit.isFullyLoaded()) {
          this.fetchFullUnitData(this.uid);
        } else {
          this.handleUnitChange(uid);
        }
      }
    }
    return this.idx;
  }

  loadContextRows() {
    const uid = this.uid;
    if (!this.unit.contextData) {
      UnitAPI.fetchContextRows(this.uid,
        // TODO: instead of `gap` and `qty` specify the number of units before/after the given uid
        { gap: 0, qty: 5 }).then(
        (data) => {
          if (!data || !data.ctx) {
            return;
          }
          // wrap returned data into Unit objects
          const out = {
            before: [],
            after: [],
          };

          if (data.ctx.before) {
            for (let i = 0; i < data.ctx.before.length; i++) {
              out.before.push(new Unit(data.ctx.before[i]));
            }
          }
          if (data.ctx.after) {
            for (let i = 0; i < data.ctx.after.length; i++) {
              out.after.push(new Unit(data.ctx.after[i]));
            }
          }
          this.unit.contextData = out;
          this.handleContextDataChange(uid);
        },
        this.error
      );
    } else {
      this.handleContextDataChange(uid);
    }
  }

  gotoPrev() {
    const idx = Math.max(0, this.idx - 1);
    return this.goto(this.uids[idx]);
  }

  gotoNext() {
    const idx = Math.min(this.uids.length, this.idx + 1);
    return this.goto(this.uids[idx]);
  }

  getPosition() {
    return this.begin + this.idx + 1;
  }

  gotoPosition(pos) {
    if (this.uids.length === 0) {
      return;
    }

    let idx = pos - this.begin - 1;

    if (idx < 0) {
      idx = 0;
    }
    if (idx > this.uids.length - 1) {
      idx = this.uids.length - 1;
    }

    this.goto(this.uids[idx]);
  }

  onFirstUnit() {
    return this.idx <= 0; // -1 or 0
  }

  onLastUnit() {
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
    const originalUid = this.uid;

    const filteredUids = [];

    for (let i = 0; i < uids.length; i++) {
      const uid = uids[i];
      if (!this.units[uid]) {
        filteredUids.push(uid);
      }
    }

    if (!filteredUids.length) {
      return; // nothing to do
    }

    UnitAPI.fetchViewRows({ uids: filteredUids }).then(
      (data) => {
        let hasNewData;

        this.ready = true;

        if (!data.rows) {
          return;
        }

        Object.keys(data.rows).forEach((uid) => {
          if (this.units[uid]) {
            return; // unit was already loaded
          }
          hasNewData = true;
          this.units[uid] = new Unit(data.rows[uid]);
        });

        if (hasNewData) {
          // TODO: fire this only if the rows in the viewport have changed
          this.handleViewRowsChange(originalUid);
        }
      },
      this.error
    );
  }

  cleanupUnusedUnits() {
    const start1 = 0;
    const end1 = this.firstUnitInVicinity(this.visibleRowsBefore + this.prefetchRows) - 1;
    this.cleanupUnitsInRange(start1, end1);

    const start2 = this.lastUnitInVicinity(this.visibleRowsAfter + this.prefetchRows) + 1;
    const end2 = this.length - 1;
    this.cleanupUnitsInRange(start2, end2);
  }

  cleanupUnitsInRange(start, end) {
    for (let i = start; i <= end; i++) {
      const uid = this.uids[i];
      if (this.units[uid]) {
        console.log('deleting unit from cache:', uid);
        delete this.units[uid];
      }
    }
  }

  fetchFullUnitData(uid) {
    console.log('UnitsList.fetchFullUnitData(), uid:', uid);
    UnitAPI.fetchFullUnitData(uid).then(
      (data) => {
        this.units[uid] = new Unit(data);
        this.goto(uid);
      },
      this.error
    );
  }

}

export default UnitsList;

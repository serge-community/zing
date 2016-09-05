/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import expect from 'expect';
import { describe, it } from 'mocha';

import { dueTime, _dueTimeMessage, _overdueTimeMessage } from './dueTime';


describe('dueTime', () => {
  it('returns an empty string for undefined time deltas', () => {
    expect(dueTime('')).toEqual('');
    expect(dueTime(null)).toEqual('');
    expect(dueTime(undefined)).toEqual('');
    expect(dueTime('Invalid')).toEqual('');
    expect(dueTime('2016-14-12')).toEqual('');
    expect(dueTime('2016-12-12 12:02:11')).toEqual('');
    expect(dueTime('2016-12-12 25:02:11')).toEqual('');
    expect(dueTime('2016-12-12T12:02:11+00:00')).toEqual('');
  });
});


describe('dueTimeMessage', () => {
  const tests = [
    {
      unit: 'immediately due times',
      delta: {
        seconds: 0,
        minutes: 0,
        hours: 0,
        days: 0,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Due right now',
    },
    {
      unit: 'immediately due times (seconds of difference)',
      delta: {
        seconds: 55,
        minutes: 0,
        hours: 0,
        days: 0,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Due right now',
    },
    {
      unit: 'immediately due times (minutes of difference)',
      delta: {
        seconds: 29,
        minutes: 5,
        hours: 0,
        days: 0,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Due right now',
    },
    {
      unit: 'hours of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 0,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Due in 23 hours',
    },
    {
      unit: 'days of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 6,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Due in 6 days',
    },
    {
      unit: 'weeks of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 8,
        weeks: 3,
        months: 0,
        years: 0,
      },
      expected: 'Due in 3 weeks',
    },
    {
      unit: 'months of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 8,
        weeks: 3,
        months: 4,
        years: 0,
      },
      expected: 'Due in 4 months',
    },
    {
      unit: 'years of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 8,
        weeks: 3,
        months: 4,
        years: 6,
      },
      expected: 'Due in 6 years',
    },
  ];

  tests.forEach((test) => {
    it(`covers ${test.unit}`, () => {
      expect(_dueTimeMessage(test.delta)).toEqual(test.expected);
    });
  });
});


describe('overDueTimeMessage', () => {
  const tests = [
    {
      unit: 'immediately overdue times',
      delta: {
        seconds: 0,
        minutes: 0,
        hours: 0,
        days: 0,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Overdue right now',
    },
    {
      unit: 'immediately overdue times (seconds of difference)',
      delta: {
        seconds: 55,
        minutes: 0,
        hours: 0,
        days: 0,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Overdue right now',
    },
    {
      unit: 'immediately overdue times (minutes of difference)',
      delta: {
        seconds: 29,
        minutes: 5,
        hours: 0,
        days: 0,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Overdue right now',
    },
    {
      unit: 'hours of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 0,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Overdue by 23 hours',
    },
    {
      unit: 'days of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 6,
        weeks: 0,
        months: 0,
        years: 0,
      },
      expected: 'Overdue by 6 days',
    },
    {
      unit: 'weeks of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 8,
        weeks: 3,
        months: 0,
        years: 0,
      },
      expected: 'Overdue by 3 weeks',
    },
    {
      unit: 'months of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 8,
        weeks: 3,
        months: 4,
        years: 0,
      },
      expected: 'Overdue by 4 months',
    },
    {
      unit: 'years of difference',
      delta: {
        seconds: 9,
        minutes: 2,
        hours: 23,
        days: 8,
        weeks: 3,
        months: 4,
        years: 6,
      },
      expected: 'Overdue by 6 years',
    },
  ];

  tests.forEach((test) => {
    it(`covers ${test.unit}`, () => {
      expect(_overdueTimeMessage(test.delta)).toEqual(test.expected);
    });
  });
});

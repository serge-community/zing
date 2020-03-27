/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import expect from 'expect';
import lolex from 'lolex';
import { describe, it } from 'mocha';

import { formatTimeDelta } from './time';

describe('formatTimeDelta', () => {
  describe('below threshold', () => {
    const tests = [
      {
        unit: 'seconds',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-01T00:00:45+00:00',
        expected: 'a few seconds',
      },
      {
        unit: 'minutes',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-01T00:45:00+00:00',
        expected: '45 minutes',
      },
      {
        unit: 'hours',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-01T22:28:00+00:00',
        expected: '22 hours',
      },
      {
        unit: 'days',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-07T00:00:00+00:00',
        expected: '6 days',
      },
      {
        unit: 'weeks',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-25T00:00:00+00:00',
        expected: '3 weeks',
      },
      {
        unit: 'months',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-12-01T00:00:00+00:00',
        expected: '11 months',
      },
      {
        unit: 'years',
        now: '2016-01-01T00:00:00+00:00',
        args: '2017-01-01T00:00:00+00:00',
        expected: 'a year',
      },
    ];

    tests.forEach((test) => {
      it(`calculates ${test.unit} of difference`, () => {
        lolex.install(Date.parse(test.now));
        expect(formatTimeDelta(Date.parse(test.args))).toEqual(test.expected);
      });
    });
  });

  describe('above threshold', () => {
    const tests = [
      {
        unit: 'seconds',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-01T00:00:46+00:00',
        expected: 'a minute',
      },
      {
        unit: 'minutes',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-01T00:46:00+00:00',
        expected: 'an hour',
      },
      {
        unit: 'hours',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-01T22:30:00+00:00',
        expected: 'a day',
      },
      {
        unit: 'days',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-08T00:00:00+00:00',
        expected: 'a week',
      },
      {
        unit: 'weeks',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-01-26T00:00:00+00:00',
        expected: 'a month',
      },
      {
        unit: 'months',
        now: '2016-01-01T00:00:00+00:00',
        args: '2016-12-02T00:00:00+00:00',
        expected: 'a year',
      },
    ];

    tests.forEach((test) => {
      it(`calculates ${test.unit} of difference`, () => {
        lolex.install(Date.parse(test.now));
        expect(formatTimeDelta(Date.parse(test.args))).toEqual(test.expected);
      });
    });
  });

  describe('with direction added', () => {
    const tests = [
      {
        unit: 'past',
        now: '2017-01-01T00:00:00+00:00',
        args: '2016-01-01T00:00:00+00:00',
        expected: 'a year ago',
      },
      {
        unit: 'future',
        now: '2016-01-01T00:00:00+00:00',
        args: '2017-01-01T00:00:00+00:00',
        expected: 'in a year',
      },
    ];

    tests.forEach((test) => {
      it(`formats ${test.unit} times`, () => {
        lolex.install(Date.parse(test.now));
        expect(
          formatTimeDelta(Date.parse(test.args), { addDirection: true })
        ).toEqual(test.expected);
      });
    });
  });
});

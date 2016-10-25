/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import expect from 'expect';
import { describe, it } from 'mocha';

import AutoIconModule from './AutoIcon';
const calcAbbreviation = AutoIconModule.__GetDependency__(
  'calcAbbreviation'
);

const calcHue = AutoIconModule.__GetDependency__(
  'calcHue'
);

describe('AutoIcon', () => {
  it('returns proper abbreviations', () => {
    expect(calcAbbreviation('John Doe', 2)).toEqual('JD');
    expect(calcAbbreviation('Foo & Baz', 2)).toEqual('FB');
    expect(calcAbbreviation('Foo and Etc', 2)).toEqual('FE');
    expect(calcAbbreviation('FOO Bar', 2)).toEqual('FB');
    expect(calcAbbreviation('FooBar', 2)).toEqual('FO');
    expect(calcAbbreviation('foobar', 2)).toEqual('FO');
    expect(calcAbbreviation('Foo 1 2 Bar', 2)).toEqual('FB');
    expect(calcAbbreviation('123', 2)).toEqual('12');

    expect(calcAbbreviation('John Doe', 1)).toEqual('J');
    expect(calcAbbreviation('Foo & Baz', 1)).toEqual('F');
    expect(calcAbbreviation('Foo and Etc', 1)).toEqual('F');
    expect(calcAbbreviation('FOO Bar', 1)).toEqual('F');
    expect(calcAbbreviation('FooBar', 1)).toEqual('F');
    expect(calcAbbreviation('foobar', 1)).toEqual('F');
    expect(calcAbbreviation('Foo 1 2 Bar', 1)).toEqual('F');
    expect(calcAbbreviation('123', 1)).toEqual('1');
  });

  it('returns proper hue values', () => {
    expect(calcHue('John Doe')).toEqual(20);
    expect(calcHue('Foo & Baz')).toEqual(275);
    expect(calcHue('Foo and Etc')).toEqual(66);
    expect(calcHue('FOO Bar')).toEqual(321);
    expect(calcHue('FooBar')).toEqual(68);
    expect(calcHue('foobar')).toEqual(246);
    expect(calcHue('Foo 1 2 Bar')).toEqual(115);
    expect(calcHue('123')).toEqual(207);
  });
});

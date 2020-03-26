/*
 * Copyright (C) Zing contributors.
 *
 * This file is a part of the Zing project. It is distributed under the GPL3
 * or later license. See the LICENSE file for a copy of the license and the
 * AUTHORS file for copyright and authorship information.
 */

import expect from 'expect';
import { describe, it } from 'mocha';

import { split, splitPootlePath, getTranslateUrl } from './url';


describe('url', () => {
  describe('split', () => {
    it('returns the remainder after a split', () => {
      expect(
        split('/foo/bar/baz/blah/', '/', 2)
      ).toEqual(['', 'foo', 'bar/baz/blah/']);
    });
  });

  describe('splitPootlePath', () => {
    it('handles empty paths', () => {
      expect(splitPootlePath('')).toEqual([null, null, '', '']);
    });

    it('handles root paths', () => {
      expect(splitPootlePath('/')).toEqual([null, null, '', '']);
    });

    it('handles empty project paths', () => {
      expect(splitPootlePath('/projects/')).toEqual([null, null, '', '']);
    });

    it('splits language paths', () => {
      expect(splitPootlePath('/ru/')).toEqual(['ru', null, '', '']);
    });

    it('splits project paths', () => {
      expect(splitPootlePath('/projects/foo/')).toEqual([null, 'foo', '', '']);
    });

    it('splits translation project paths', () => {
      expect(splitPootlePath('/ru/foo/')).toEqual(['ru', 'foo', '', '']);
    });

    it('splits TP-level directories', () => {
      const tests = [
        {
          path: '/ru/foo/bar/',
          expected: ['ru', 'foo', 'bar/', ''],
        },
        {
          path: '/ru/foo/bar/baz/',
          expected: ['ru', 'foo', 'bar/baz/', ''],
        },
      ];
      tests.forEach(test => {
        expect(splitPootlePath(test.path)).toEqual(test.expected);
      });
    });

    it('splits project-level directories', () => {
      const tests = [
        {
          path: '/projects/foo/bar/',
          expected: [null, 'foo', 'bar/', ''],
        },
        {
          path: '/projects/foo/bar/baz/',
          expected: [null, 'foo', 'bar/baz/', ''],
        },
      ];
      tests.forEach(test => {
        expect(splitPootlePath(test.path)).toEqual(test.expected);
      });
    });

    it('splits TP-level files', () => {
      const tests = [
        {
          path: '/ru/foo/bar',
          expected: ['ru', 'foo', '', 'bar'],
        },
        {
          path: '/ru/foo/bar.po',
          expected: ['ru', 'foo', '', 'bar.po'],
        },
        {
          path: '/ru/foo/bar/baz',
          expected: ['ru', 'foo', 'bar/', 'baz'],
        },
        {
          path: '/ru/foo/bar/baz/blah.po',
          expected: ['ru', 'foo', 'bar/baz/', 'blah.po'],
        },
        {
          path: '/ru/foo/bar/baz.po',
          expected: ['ru', 'foo', 'bar/', 'baz.po'],
        },
      ];
      tests.forEach(test => {
        expect(splitPootlePath(test.path)).toEqual(test.expected);
      });
    });

    it('splits project-level files', () => {
      const tests = [
        {
          path: '/projects/foo/bar',
          expected: [null, 'foo', '', 'bar'],
        },
        {
          path: '/projects/foo/bar.po',
          expected: [null, 'foo', '', 'bar.po'],
        },
        {
          path: '/projects/foo/bar/baz',
          expected: [null, 'foo', 'bar/', 'baz'],
        },
        {
          path: '/projects/foo/bar/baz/blah.po',
          expected: [null, 'foo', 'bar/baz/', 'blah.po'],
        },
        {
          path: '/projects/foo/bar/baz.po',
          expected: [null, 'foo', 'bar/', 'baz.po'],
        },
      ];
      tests.forEach(test => {
        expect(splitPootlePath(test.path)).toEqual(test.expected);
      });
    });
  });

  it('constructs translate URLs from internal paths', () => {
    const tests = [
      {
        path: '/',
        expected: '/projects/translate/',
      },
      {
        path: '/ru/',
        expected: '/ru/translate/',
      },
      {
        path: '/ru/foo/bar/baz.po',
        expected: '/ru/foo/translate/bar/baz.po',
      },
      {
        path: '/projects/foo/',
        expected: '/projects/foo/translate/',
      },
      {
        path: '/projects/foo/bar/baz',
        expected: '/projects/foo/translate/bar/baz',
      },
      {
        path: '/projects/foo/bar/baz/blah.po',
        expected: '/projects/foo/translate/bar/baz/blah.po',
      },
    ];
    tests.forEach(test => {
      expect(getTranslateUrl(test.path)).toEqual(test.expected);
    });
  });
});

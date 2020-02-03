Zing Changelog
==============

v.next (unreleased)
-------------------

* Tasks: removed limit of displaying 10 tasks.
* Fixed bug where language list wouldn't be properly recalculated.


v0.8.9 (2018-11-07)
-------------------

* Do not use local time for mtime optimizations (#77).
  Important: this change won't enable file change optimizations until the next
  time `update_stores` is run. This means the first run after this change is
  applied will potentially be slow.
* Users will now be able to access export view in cross-language contexts
  (permissions apply) (#361).


v0.8.8 (2018-06-12)
-------------------

* Fixed installation instructions (#348).
* Checks: fixed bug where language-specific checks would prevent check stats
  from being loaded (#343).
* Top scorers: the information will be provided taking entire days into account,
  starting at midnight (#342).


v0.8.7 (2018-05-29)
-------------------

* Due dates: fixed deadlock when updating/deleting deadlines (#340).
* Adding projects/languages via the UI won't trigger creation of translation
  projects and file scanning.
  This must be done via the management commands, which will take care of setting
  up the translation projects and initializing them (#263).
* Adjusted default permission set to be more restrictive. This only affects to
  new installations (#337).


v0.8.6 (2018-05-28)
-------------------

* Invoices:
  * Fixed an issue where the carry-over balance wouldn't be properly reported
    in emails (#332).
  * Added support for negative carry-over balances (#335).
* Editor: made copying from source text actually work (#333).


v0.8.5 (2018-05-02)
-------------------

* Fixed bug which prevented adding static pages (#331).


v0.8.4 (2018-04-23)
-------------------

* Enforced uniqueness of email addresses at the DB level (#295).
* Editor: fixed a bug where view rows wouldn't expose proper styling (#329).
* Browser: the languages dropdown now also matches locale codes (#330).


v0.8.3 (2018-03-27)
-------------------

* Fixed issue when saving users without linkedin accounts (#321).
* Fixed issue where static pages wouldn't update their timestamps (#316).
* Moved `LEGALPAGE_NOCHECK_PREFIXES` setting into a constant (#319).
* Removed captcha middleware and associated setting (#315).
* Removed `ZING_INSTANCE_ID`. This can easily be implemented by anyone (#314).
* Cleaned up setting names and removed obsoletes (#313):
  * `POOTLE_TM_SERVER` -> `ZING_TM_SERVER`
  * `POOTLE_CONTACT_EMAIL` -> `ZING_CONTACT_EMAIL`
  * `POOTLE_TRANSLATION_DIRECTORY` -> `ZING_TRANSLATION_DIRECTORY`
  * `POOTLE_SCORE_COEFFICIENTS` -> `ZING_SCORE_COEFFICIENTS`
  * `POOTLE_SIGNUP_ENABLED` -> `ZING_SIGNUP_ENABLED`
  * `POOTLE_MT_BACKENDS` -> `ZING_MT_BACKENDS`
  * `POOTLE_CAPTCHA_ENABLED` -> `ZING_CAPTCHA_ENABLED`
  * `POOTLE_CONTACT_REPORT_EMAIL` -> `ZING_CONTACT_REPORT_EMAIL`
  * `POOTLE_QUALITY_CHECKER` -> `ZING_QUALITY_CHECKER`
  * `POOTLE_SYNC_FILE_MODE` -> `ZING_SYNC_FILE_MODE`
  * `POOTLE_REPORTS_MARK_FUNC` -> `ZING_REPORTS_MARK_FUNC`
  * `POOTLE_TITLE` -> `ZING_TITLE`
  * `POOTLE_INSTANCE_ID` -> `ZING_INSTANCE_ID`
  * `POOTLE_WORDCOUNT_FUNC` -> `ZING_WORDCOUNT_FUNC`
  * `POOTLE_LEGALPAGE_NOCHECK_PREFIXES` -> `ZING_LEGALPAGE_NOCHECK_PREFIXES`
  * `POOTLE_LOG_DIRECTORY` -> `ZING_LOG_DIRECTORY`


v0.8.2 (2018-01-31)
-------------------

* Editor: properly provide source values for determining the editor to be used.


v0.8.1 (2018-01-31)
-------------------

* Editor: fixed a bug where the Plurr editor would go away and miss its state
  (#310).


v0.8.0 (2018-01-29)
-------------------

* Editor: incorporated live editor for Plurr-formatted strings (#303).
* Fixed a bug where the editor would crash if a terminology unit contained
  suggestions (#291).
* TM is now simplified to a single server and sane defaults are provided for
  settings (#298).
* Removed `SetLocale` middleware (#301).
* Cleaned up unused commands:
  * `dump`, `find_duplicate_emails`, `update_user_email` (#296)
  * `list_languages`, `list_projects`, `contributors`, `changed_languages`,
    `test_checks` (#297)
  * `webpack`, which has been replaced by an `npm` script (#304).
* Cleaned up unused settings:
  * `POOTLE_CUSTOM_TEMPLATE_CONTEXT` (#293)
  * `POOTLE_META_USERS` 
  * `POOTLE_CONTACT_ENABLED` (consolidated into `POOTLE_CONTACT_EMAIL`)
  * `PARSE_POOL_CULL_FREQUENCY` and `PARSE_POOL_SIZE` (moved to constants)
  * `POOTLE_CACHE_TIMEOUT` (moved to a constant)


v0.7.0 (2018-01-10)
-------------------

* Dropped support for IE11 (#275).
* JS assets are built with the latest version of Webpack and Babel (#272, #278,
  #279).
* Editor: fixed bug which prevented from reopening the last unit once it was
  closed after a submission (#251).
* Removed the so-called "announcements" because their use-case is already
  covered by due dates (#284).
* Removed the redirect field from static pages (#285).


v0.6.0 (2017-12-12)
-------------------

* Upgraded to Django 1.11.


v0.5.4 (2017-12-07)
-------------------

* Invoices: added GBP to the list of currencies (#269).


v0.5.3 (2017-08-16)
-------------------

* Removed expensive server stats from the admin dashboard (#260).
* Fixed bug in social account verification before linking it to an existing
  local account (#262).


v0.5.2 (2017-07-21)
-------------------

* Worked around an issue in older versions of Android+Webkit, where timezones
  would be reported as abbreviations, and not as IANA compliant names. This
  broke client scripts.


v0.5.1 (2017-05-29)
-------------------

* Fixed invoice emails' company/department data.
* Fixed pending task retrieval when updates happened (#256).


v0.5.0 (2017-05-01)
-------------------

* Integrated feature to generate invoices for translators (#255).


v0.4.1 (2017-04-25)
-------------------

* Fixed browsing pages for fully untranslated stores.


v0.4.0 (2017-04-06)
-------------------

* New feature: pending tasks (#252).
  Administrators can set due dates for projects or resources, which will then be
  visible to translators on any browsing page within a language context.


v0.3.2 (2017-04-04)
-------------------

* Fixed a synchronization bug where obsolete but unsynced units could not be
  resurrected (#246).


v0.3.1 (2017-02-15)
-------------------

* Fixed reference in static pages which prevented the editor from showing up.
* Removed unused `clear_stats` command. Use `flush_cache --stats` instead (#197).
* Fixed subject line for emails sent via the contact form (#203).


v0.3.0 (2017-02-06)
-------------------

* Django 1.10 support (#174)


v0.2.1 (2017-01-26)
-------------------

* Browsing pages hide empty navigation items by default. Likewise, non-admin
  users can no longer access empty paths (#129).
* Editor:
  * fixed consistency bug in language names (#157).
  * fixed geometry of editing area after common actions (#155).
  * improved UX around 'units not found' cases (#166).


v0.2.0 (2017-01-17)
-------------------

* Editor:
  * Reworked the way unit fetching is done (#8).
  * The list of units always takes up the entire screen.
  * Navigating between units now preserves the editor's vertical position.
  * New easy way to preview context rows by just hovering over the unit link.
  * Tweaked the UI for displaying obsolete messages (#94).
  * Streamlined indexed TM data and made the UI more robust (#96).
* Optimized terminology access (#144).


v0.1.4 (2016-12-19)
-------------------

* Fixed browser table sorting for total/untranslated columns (#120).
* Restricted access to project-wide export views (#142).
* Quality checks now default to a site-wide checker (#119). In the future,
  project-specific checkers will be disallowed.
* Implemented view testing via snapshots (#45). More tests will need to be
  adapted although this puts in place the scaffolding to write tests using
  this technique.
* Removed multiple file format support in favor of a single interchange format
  (#115).
* Removed support for deploying to subpaths (#140).
* Removed unused config utilities (#114).
* Removed unmaintained web-based terminology management (#123).
* Removed unused `ignoredfiles` project field (#139).


v0.1.3 (2016-11-30)
-------------------

* Editor: fixed a bug where self-closing (X)HTML tags would be displayed as
  opening+closing tags (#105).
* Improved `tags_differ` check to take into account CDATA sections as if they
  were tags (#104).


v0.1.2 (2016-11-29)
-------------------

* Editor:
  * Added the ability to select groups of failing checks (#80).
  * Multiple UI tweaks, making better use of the available space.
  * Removed support for the amaGama TM, as the built-in TM suffices (#92).
* Fixed table sorting for last updated columns (#91).
* Fixed stats auto-expanding when browsing to files (#97).
* Removed extra layer of serialization (#88).
* Removed external language mapping (#100).
* Removed project-specific directory layouts (#102).
* Removed support for the special "templates" language (#103).


v0.1.1 (2016-11-12)
-------------------

* Fixed display of dates in the timeline (#82).
* Editor: removed the ability to jump to units by index (#79).


v0.1.0 (2016-11-09)
-------------------

* Initial version diverging off Pootle.
* Django 1.9 support (#24, #39, #76).
* Cleaned up features out of the scope of the project:
  * Upload/download of user files (#36).
  * Virtual folders (#38).
  * VCS/FS support (#41).
  * Adding languages to projects via the admin UI (#66).
* Added Mac-aware keyboard shortcuts and popup keyboard help (#51).
* UI Redesign, which includes:
  * New project name, logo, icons (#61)
  * Updated Welcome page, user profile page (#54).
  * Updated, more compact header (#49).
  * Footer is no more (#47).
  * Avatars show initials if Gravatar image is not available (#46).
  * Updated dialog and button styles (#50).
* Improved the way data is provided to, and rendered on, a browser page;
  this speeds up page rendering, especially on large tables (#37).
* Optimized the amount of data that is cached, so that overall it takes less
  space. Note this requires running a server-wide `refresh_stats` (#37, #75).


Pre 0.1.0
---------

Please consult [Pootle's own
changelog](http://docs.translatehouse.org/projects/pootle/en/2.8.0b3/releases/index.html)
for specific details.

Zing Changelog
==============

v0.1.2 (in development)
-----------------------

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

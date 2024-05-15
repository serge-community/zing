How to Contribute
=================

Reporting Issues
----------------

Before creating a new report, please make sure [the issue is not already on
file](https://github.com/serge-community/zing/issues/).

Write your report so that you ensure developers are fixing the issue rather than
spending time trying to understand it.  If we can't see it or replicate it,
likely we can't fix it.

Checklist:

* Bug description is clear yet concise.
* Clear instructions to reliably replicate the issue.
* Screenshots rather than descriptions of screens.
* Full traceback if one occurred.
* Links to the actual issue.

Common Sense
------------

Before contributing any code, please:

* Do not write any line of code without consulting about it first, trivial fixes
  being an exception. Note the project might not be interested in some changes,
  especially when these are substantial or not in line with the [goals and
  vision](https://github.com/serge-community/zing/blob/master/GOALS.md).
* Think if any code is needed at all: [The Best Code is No Code At
  All](http://blog.codinghorror.com/the-best-code-is-no-code-at-all/).

Commits
-------

Keep the commit log as healthy as the code. It is one of the first places new
contributors will look at the project.

* No more than one change per commit. There should be no changes in a commit
  which are unrelated to its message.
* Follow [these conventions](http://chris.beams.io/posts/git-commit/) when
  writing the commit message.

Pull Requests
-------------

We incorporate changes to the mainline `master` branch by using Pull Requests.

* When filing a Pull Request, make sure it is rebased on top of the most recent
  `master`.
* Every Pull Request should pass all tests on its own and the build must be
  passing. Ideally each commit should too.

Also see: [Github Help: Using Pull
Requests](https://help.github.com/articles/using-pull-requests/).

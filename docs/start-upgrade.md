---
id: upgrading
title: Upgrading
---

From time to time there might be the need to upgrade Zing to incorporate bug
fixes, new features, or customizations.


## Preparation

Before performing any upgrades, make sure to:

* Read through the
  [changes](https://github.com/evernote/zing/blob/master/CHANGES.md) about to be
  applied.
* Backup your database.
* Stop all external processes interacting with Zing (e.g. a continuous localization
  cycle).
* Stop your background RQ workers.
* Shut down the Zing server, to avoid external interactions from interfering
  with the upgrade process. For this, you may want to implement a maintenance
  mode specific to your deployment.


## Upgrading

You will need to grab the newest code and upgrade database schemas, as well as
rebuild static assets so that the latest changes make effect.

```shell
pip install -U <new-version>
```
```shell
zing migrate
```
```shell
zing build_assets
```

Should there be any, please also make sure to follow instructions specific to
particular releases.

You are now ready to restart the background worker processes, as well as
to re-enable external access to Zing.

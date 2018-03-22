---
id: workflow-overview
title: Workflow
sidebar_label: Overview
---

In this section we will show you how Zing works with files and the prerequisites
it involves. Knowing all of that, you will be ready to setup your own projects
and workflows.

## Prerequisites

### Interchange File Format

For interchange purposes between external processes/workflows and the Zing
translation database, Zing by design [only uses Gettext PO files](faq.html).
This fits perfectly when [integrating with Serge](workflow-serge-integration.md).

### File Location

Interchange translation files will be looked under the directory specified by
the
[`ZING_TRANSLATION_DIRECTORY`](ref-settings.md#zing-translation-directory)
setting.

You should make sure the OS process running Zing has enough rights to access
this directory.

### Directory Structure

Under the [translation directory](#file-location), Zing expects a specific
directory structure where it can find project- and language-specific files.

At the root there will be directories named after the _project code_. Under
project directories, there will be directories named after the _locale code_.
The combination of a project and a locale is a _translation project_.

An example structure would be as follows:

```
myproject/
|-- eu
|   |-- subfolder
|   |   `-- bar.po
|   `-- foo.po
|-- ca
|   `-- foo.po
`-- ru
    `-- foo.po
```

Note how individual translation projects can contain arbitrary files. In other
words, under translation projects, the structure of the filesystem can be freely
laid out.

Likewise, translation files and directories can differ across languages within
the same project.

### Locale Codes

The _locale codes_ used for filesystem synchronization as well as for browsing
URLs are defined in the _Administration_ -> _Languages_ section of the Zing User
Interface.

By default, a set of common pre-defined locale codes is included, which should
be enough for most cases. Should you need to use different locale codes, this is
the place to adjust them as needed.


## Project Creation

Setting up projects enables separation of work and allows Zing to match files to
projects. The mapping of filesystem and database projects is done via the
_project code_.

Projects need to be explicitly created in the Zing User Interface before using
any file synchronization commands. This can be done in the _Administration_ ->
_Projects_ section of Zing, by clicking the _Add Project_ button and filling in
the project code and display name.


## File Synchronization

Synchronization between the file system and the Zing database occurs via the
`update_stores` and `sync_stores` commands.

By default, these commands work across the entire server but at will, they can
work selectively to synchronize files only to specific projects, languages or
translation projects.

### `update_stores`

The `update_stores` command will take translation interchange files, and import
them to the Zing database, effectively reflecting in the database the state of
the files on disk.

New languages added on disk will be auto-discovered, whereas languages that
ceased to exist will be disabled.

To learn more, please refer to the [`update_stores` command
reference](ref-commands.md#update-stores).

### `sync_stores`

The `sync_stores` command will take the state of the database and reflect it in
the files on disk. This is the opposite of `update_stores`.

To learn more, please refer to the [`sync_stores` command
reference](ref-commands.md#sync-stores).


## Automating the Workflow

Knowing all of this, you are now ready to insert Zing as part of your
localization workflow.

The level of automation is really up to you — from bash scripts to cron jobs.
The more automated and robust, the fastest and cheapest the entire localization
workflow will be.

We are particularly fond of automating all parts of the process in what we call
[continuous localization](workflow-continuous-localization.md), which is a
recommended option to consider next.


## Reference

Commands:

* [`sync_stores`](ref-commands.md#sync_stores)
* [`update_stores`](ref-commands.md#update_stores)

Settings:

* [`ZING_SYNC_FILE_MODE`](ref-settings.md#zing-sync-file-mode)
* [`ZING_TRANSLATION_DIRECTORY`](ref-settings.md#zing-translation-directory)

---
id: project-setup
title: Project Setup
---

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
reference](ref-commands.md#update_stores).

### `sync_stores`

The `sync_stores` command will take the state of the database and reflect it in
the files on disk. This is the opposite of `update_stores`.

To learn more, please refer to the [`sync_stores` command
reference](ref-commands.md#sync_stores).


## Reference

Commands:

* [`sync_stores`](ref-commands.md#sync_stores)
* [`update_stores`](ref-commands.md#update_stores)

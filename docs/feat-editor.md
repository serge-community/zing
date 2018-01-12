---
id: editor
title: Translation Editor
---

Being a CAT (Computer-Assisted Translation) tool, Zing includes a powerful
translation editor with multiple features.

## Translation Memory

Zing can aid translators by suggesting texts that have previously been
translated.

Translation Memory suggestions are automatically retrieved when you open a new
translation unit — these are displayed below the editing widget.

The differences between the current string and the suggested string are
highlighted, allowing translators to easily spot what has changed.

### Configuring

To enable Translation Memory support, first ensure you have an Elasticsearch
server up & running and accessible from the Zing server. Then, proceed to
specify the connection details in the
[`POOTLE_TM_SERVER`](ref-settings.md#pootle-tm-server) setting.

If you just set up the TM server and your Zing server already had projects with
existing translations, you may want to populate the TM index:

```shell
zing update_tmserver
```

This is a one-time operation: after this, Zing will keep the TM index
up-to-date.

### Reference

Commands:

* [`update_tmserver`](ref-commands.md#update_tmserver)

Settings:

* [`POOTLE_TM_SERVER`](ref-settings.md#pootle-tm-server)


## Machine Translation

Zing has the ability to use online Machine Translation (MT) Services to give
suggestions to translators.

### Configuring

To enable a certain Machine Translation Service, edit your configuration file
and add the desired service within the
[`POOTLE_MT_BACKENDS`](ref-settings.md#pootle-mt-backends).

### Reference

Settings:

* [`POOTLE_MT_BACKENDS`](ref-settings.md#pootle-mt-backends)

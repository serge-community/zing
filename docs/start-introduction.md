---
id: introduction
title: Introduction
---

## What is Zing?

Zing is an opinionated online translation tool intended to use in a continuous
localization workflow. It integrates nicely with [Serge](https://serge.io/).

## Requirements

At its core, Zing is a server built using Python and the Django framework. It
runs on UNIX-like Operating Systems and requires:

* Python 2.7
* Redis
* MySQL _(PostgreSQL should also work, but hasn't been widely tested)_
* Elasticsearch _(when using the Translation Memory support)_

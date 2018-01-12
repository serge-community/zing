---
id: continuous-localization
title: Continuous Localization
---

One of the guiding principles of Zing is enabling _continuous localization_.

Provided [projects are already setup](workflow-overview.md#project-creation) in
the Zing server, the general idea for such a workflow would be to:

1. [Pull translations](workflow-overview.md#update-stores) from Zing to the
   filesystem.
2. Run your localization toolchain. This must take care of:
    1. Merging the latest translations with the latest localizable resource
  files from your development repositories.
    2. Placing the resulting files in the [translation
  directory](workflow-overview.md#file-location).
3. [Push the updated translations](workflow-overview.md#sync-stores) to the Zing
   database.

The first and last steps are covered by Zing. The intermediate step is up to
your particular process. Nonetheless, localization is hard, so are its
processes, that's why we suggest [using
Serge](#continuous-localization-with-serge) for this matter.


## Continuous Localization with Serge

[Serge](https://serge.io) is a command-line tool that helps us remove the burden
of having to deal with [multiple localization file
formats](https://serge.io/docs/file-formats/), [version control
systems](https://serge.io/docs/version-control/), exotic directory layouts and
locale codes, as well as other minor details that affect global localization
projects.  [Serge is extensible](https://serge.io/docs/modular-architecture/)
too, so that if some of the built-in features or behaviors do not suffice, you
can adapt it to your own needs.

### Integration

In order to integrate the [Serge localization
workflow](https://serge.io/docs/localization-cycle/) with our Zing translation
server, we first need to [install Serge](https://serge.io/download/) in the same
server as Zing.

After that, we will need to [configure a Serge
job](https://serge.io/docs/configuration-files/) and specify we want to use the
`pootle` plugin. Along with that, we need to define the path to the `zing`
executable in our server, as well as the _project code_ we are using for the
project described by the job we are configuring.

To learn more about how to configure Serge, please refer to the [Serge + Pootle
integration guide](https://serge.io/docs/guides/pootle/) which is part of the
Serge documentation.

---
id: installation
title: Installation
---

> The installation instructions **do not fully work** for the time being as we
> are planning to change some internal details. Please bear with us while we are
> in the process to fix this! 🙏


## Preparation

We will create a virtual environment so that dependencies are installed
independent of system packages.

To create the environment, `cd` to a directory of your choice and run
`virtualenv` by providing a meaningful name for the new environment:

```shell
virtualenv zing-env
```

To activate the virtual environment, run the `activate` script:

```shell
source zing-env/bin/activate
```

This will prepend `(zing-env)` to your shell prompt, indicating the virtual
environment is active.


## Installing Zing

Use `pip` to install Zing into the virtual environment:

```shell
pip install https://github.com/evernote/zing/archive/master.zip
```

This will also fetch and install Zing's dependencies.

To verify that everything is installed correctly, you should be able to access
the `zing` command line tool within your environment.


```shell
zing --version
Zing |release|
```

Now you are ready to [perform the initial setup](intro-initial-setup.md).

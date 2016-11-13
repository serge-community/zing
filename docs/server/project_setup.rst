.. _project_setup:

Create a Project
================

Now that you have the server running, you can setup a project to translate on
the server.


Pre-requisites
--------------

Zing has the following pre-requisites:

- The project uses PO files for interchange.
- These files must exist on the server, following a specific directory layout.
- Zing is correctly set up and running, including at least one **rqworker** process.
- You are logged into the Zing server using and administrator account.


.. _project_setup#placing-translation-files:

Placing translation files
-------------------------

You need to place the translation files for your new project in a location where
Zing can read and write them. The location is specified by the
:setting:`POOTLE_TRANSLATION_DIRECTORY` setting.

The layout Zing understands is having a main project directory, where
subdirectories are named after language codes. Any files within these
directories that match the interchange format are considered for translation.
Therefore your localization process should generate files that match this
criterion.

The most basic directory structure would be as follows.
::

    └── project_code
        └── lang_code1
        |   └── foo.po
        └── lang_code2
        |   └── foo.po
        ...
        |
        └── lang_codeN
            └── foo.po


There is no limit on what you place within each language subdirectory. So for
example, translation files and directories can differ across languages within
the same project.


.. _project_setup#creating-the-project:

Creating the project
--------------------

At the top navigation bar you will see your username. Click on it and the main
top menu will be displayed, then click on **Admin** (highlighted in red):

.. image:: ../_static/accessing_admin_interface.png


Within the administration interface, go to the **Projects** tab and you will see
a **New Project** button:

.. image:: ../_static/add_project_button.png


Click on that button and the **Add Project** form will be displayed. Enter the
new project's details. **Code** must match the name of the directory within
:setting:`POOTLE_TRANSLATION_DIRECTORY` that contains the project translation
files. You can also provide a **Full Name** which will be displayed across the
UI to users.

.. image:: ../_static/add_project_form.png


Clicking on the **Save** button below will scan the filesystem for existing
files and import them to the database. The new project can now be browsed and
it's ready for translation.


.. _project_setup#updating-strings:

Updating strings for existing project
-------------------------------------

Whenever developers modify strings or localization managers add/remove
languages, the translation interchange files need to be kept in sync with the
translation server's database.

Synchronization is perfomed via the ``sync_stores`` and ``update_stores``
commands.

First off, the translation interchange files need to reflect the latest state of
things in the translation server.

.. code-block:: console

    $ zing sync_stores --project=my-project


With this updated files in place, now it is up to your specific localization
process to further synchronize them with the resource files you get from the
developers' side.

Once you get the updated files back from your localization chain, it's time to
push them back to the translation server.

.. code-block:: console

    $ pootle update_stores --project=my-project

Any new languages will made automatically available, while removed languages
won't show up.

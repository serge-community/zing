.. _translation_memory:

Translation Memory
==================

Pootle provides suggested translations to the current string.  Translator can
use these suggestions as their translation or to aid their translation.

Suggestions are based on previous translations of similar strings.  These
Translation Memory (TM) matches mean that you can speed up your translation and
ensure consistency across your work.


.. _translation_memory#using_translation_memory:

Using Translation Memory
------------------------

Translation Memory suggestions are automatically retrieved when you enter a new
translation unit. These are displayed below the editing widget.  You can insert
a TM suggestion by clicking on the suggestion row.

The differences between the current string and the suggested string are
highlighted, this allows you to see how the two differ and helps you make
changes to the suggestion to make it work as the current translation.


.. _translation_memory#configuring_translation_memory:

Configuring Translation Memory
------------------------------

Translation Memory will work out of the box with a default Pootle installation.


.. _translation_memory#elasticsearch_based_tms:

Elasticsearch-based TMs
~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 2.7

Pootle can retrieve TM matches stored on Elasticsearch-based TM servers.
These TM servers require
`Elasticsearch <https://www.elastic.co/products/elasticsearch>`_ to be
installed and running.

.. note:: Elasticsearch depends on Java. Note that some systems may ship with
  OpenJDK, however `elasticsearch recommends using Oracle JDK
  <https://www.elastic.co/guide/en/elasticsearch/reference/1.6/setup-service.html#_installing_the_oracle_jdk>`_.


The settings can be adjusted with :setting:`POOTLE_TM_SERVER`. A configuration
example for can be found in the default :file:`~/.pootle/pootle.conf`.


The TM can be populated using the :djadmin:`update_tmserver` command:

.. code-block:: console

   (env) $ pootle update_tmserver


Once populated Pootle will keep Local TM up-to-date.

It is possible to have several Elasticsearch-based external TM servers working
at once, along with the Elasticsearch-based local TM server. In order to do so
just add new entries to :setting:`POOTLE_TM_SERVER`:

.. code-block:: python

    POOTLE_TM_SERVER = {

        ...

        'libreoffice': {
            'ENGINE': 'pootle.core.search.backends.ElasticSearchBackend',
            'HOST': 'localhost',
            'PORT': 9200,
            'INDEX_NAME': 'whatever',
            'WEIGHT': 0.9,
            'MIN_SCORE': 'AUTO',
        },
    }

Make sure :setting:`INDEX_NAME <POOTLE_TM_SERVER-INDEX_NAME>` is unique. You
might also want to tweak :setting:`WEIGHT <POOTLE_TM_SERVER-WEIGHT>` to change
the score of the TM results in relation to other TM servers (valid values are
between ``0.0`` and ``1.0``).

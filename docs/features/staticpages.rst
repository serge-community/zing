.. _staticpages:

Static Pages
============

Pootle makes it easy to setup additional custom content without too much
effort.

There are three types of static pages:

#. Regular -- these work like normal web pages and are able to present
   additional content such as a "Getting Started" page.  You will want to add
   these into other :doc:`UI customisation </developers/customization>`.
#. Legal -- in addition to presenting content like a Regular page, Legal pages
   require that users agree to the content otherwise they are logged off the
   system.  Use these pages for presenting terms of service or changes in
   licensing terms that user must accept before they can use or continue to use
   Pootle.


Use **Admin -- Static Pages** to create and manage static pages.

The static pages are by default formatted using HTML. But you can use Markdown
or RestructuredText by setting :setting:`POOTLE_MARKUP_FILTER` correctly.


Links in static pages
---------------------

When linking to a static page externally or in any customisations, your links
would be pointing to ``/pages/$slug``, such as ``/pages/gettting-started``.

For linking to another static page from within a static page use the
``#/$slug`` syntax.  Thus, if you created a *Getting Started* page as a static
page which pointed to your *Licence Statement* legal page we'd use this
``#/licence_statement`` in the URL.

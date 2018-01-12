---
id: invoices
title: Invoices
sidebar_label: Invoice Generation
---

Out of users' activity and with the help of some extra configuration, Zing is
able to generate monthly-based invoices and optionally send them via e-mail.
This is useful when paid contractors and/or agencies are involved in the
translation process.


## Calculation of Payments

Payments are calculated based on the [rates set for
users](#configuring-invoices) and the amount of work they have performed during
the month being processed. Rates can be set per translated word, per reviewed
word or per hour.

The amount of work is measured considering the following activities:

* The number of translated words.
* The number of reviewed words.
* The number of hours dedicated to a specific [paid task](#paid-tasks).

Each type of work is multiplied by the rates set for the user, and is summed up
to get the total amount corresponding to the work performed during the month.

Note this might not be the final amount though, as it still needs to go through
potential carry-overs and extra payments.


### Carry-overs and Extra Payments

A minimal amount to be paid can optionally be set on a user-specific basis via
the `minimal_payment` user configuration key. In such cases, when the total
amount to be paid for the current month is lower than the minimal payment amount
set for a user, the total amount will be carried over to the next month.

When running the command in a subsequent month, the carried-over amount will be
added to the totals as a correction.

Extra fixed amounts to be paid can also be added for individuals, as a way to
indicate reimbursements for transaction fees or similar. This is controlled by
the `extra_add` user configuration key.


### Paid Tasks

There might be ocassions where some translation activities happened out of
Zing (e.g. via spreadsheets or documents sent via e-mail), and the way to
track these is by manually adding paid tasks.

Such tasks can refer to the translation or review of a certain amount of words,
as well as hour-based activities. Other type of corrections can be added here,
too. These tasks allow adding a description to easily identify the type of work
being reported.

In order to manually add paid tasks, administrators can go to the *Reports*
section of the administration site, select a user from the drop-down and add
tasks below.

Alternatively, this can also be done by translators themselves by going to their
statistics page and adding the tasks right below their daily activity graph.
This option is only available to them once an administrator has set payment
rates for them.


### Subcontractors

A paid contractor can act as an agency that has multiple translators. All their
work is consolidated and added in one invoice for the main contractor, along
with the report on how much money they owe each subcontractor.

This is controlled by the optional `subcontractors` user configuration key.


### Currencies

Currencies can be set in a user-by-user basis, however this is **currently limited
to USD, EUR, GBP, CNY and JPY**.


## Configuring Invoices

It's necessary to configure two aspects before proceeding to generate invoices:

* Specify the **users** for whom invoices will be generated, as well as their
  payment details.

  This is detailed in the setting description for
  [`ZING_INVOICES_RECIPIENTS`](ref-settings.md#zing-invoices-recipients).

* Set the user-specific **payment rates** (per-word, per-review, per-hour) for a
  given period.

  This needs to be set in the *Reports* section of the administration site.
  Select the user from the drop-down and set its rate below. Specific tasks to
  be accounted for payment can also be added manually here.

You may also want to specify the full path to the location where the invoices
will be generated. This is controlled by the `ZING_INVOICES_DIRECTORY` setting.


## Adjusting the Look & Feel

Before actually sending any invoices, you will want to check how the generated
invoices look like and adjust the layout and styling to match your company's
needs.

The default templates provide a good starting point, so initially you can set
the pre-defined `ZING_INVOICES_COMPANY` and `ZING_INVOICES_DEPARTMENT` settings
to some sensible values for your use-case and see if the result is of your
liking.

Provided you already followed all the previous configuration steps, you can run
`zing generate_invoices` and check for the generated output under
`ZING_INVOICES_DIRECTORY`.

In case you are not satisfied with the look & feel of invoices or their wording
(note the default invoices are in English), you can completely customize the
templates being used by [copying them to your custom templates
location](https://docs.djangoproject.com/en/1.11/ref/settings/#dirs) and
modifying them at your will. Re-running the `generate_invoices` command will use
them automatically.


## Generating PDFs

Invoices can optionally be generated in PDF format too, which will also be sent
via e-mail.

PDF generation requires [PhantomJS](https://phantomjs.org/). Check its website
and documentation for installation instructions. Once it's available on your
server, you will need to set the absolute path to the `phantomjs` binary in the
`ZING_INVOICES_PHANTOMJS_BIN` setting and subsequent runs of `generate_invoices`
will generate PDFs as well.


## Reference

Commands:

* `generate_invoices`

Settings:

* `ZING_INVOICES_COMPANY`
* `ZING_INVOICES_DEPARTMENT`
* `ZING_INVOICES_DIRECTORY`
* `ZING_INVOICES_PHANTOMJS_BIN`
* `ZING_INVOICES_RECIPIENTS`

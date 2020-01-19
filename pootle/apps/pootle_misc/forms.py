# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import forms
from django.forms.models import ModelChoiceIterator
from django.utils.translation import ugettext_lazy as _


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field):
        self.field = field
        self.choice_groups = field.choice_groups

    def __iter__(self):
        if self.field.empty_label is not None:
            yield (u'', self.field.empty_label)

        for title, queryset in self.choice_groups:
            if title is not None:
                yield (title, [self.choice(choice) for choice in queryset])
            else:
                for choice in queryset:
                    yield self.choice(choice)


class GroupedModelChoiceField(forms.ModelChoiceField):
    """A `ModelChoiceField` with grouping capabilities.

    :param choice_groups: List of tuples including the `title` and `queryset` of
        each individual choice group.
    """

    def __init__(self, choice_groups, *args, **kwargs):
        self.choice_groups = choice_groups
        super(GroupedModelChoiceField, self).__init__(*args, **kwargs)

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)
    choices = property(_get_choices, forms.ModelChoiceField._set_choices)


def make_search_form(*args, **kwargs):
    """Factory that instantiates one of the search forms below."""
    request = kwargs.pop('request', None)

    if request is not None:
        sparams_cookie = request.COOKIES.get('pootle-search')

        if sparams_cookie:
            import json
            import urllib.parse

            try:
                initial_sparams = json.loads(urllib.parse.unquote(sparams_cookie))
            except ValueError:
                pass
            else:
                if (isinstance(initial_sparams, dict) and
                    'sfields' in initial_sparams):
                    kwargs.update({
                        'initial': initial_sparams,
                    })

    return SearchForm(*args, **kwargs)


class SearchForm(forms.Form):
    """Normal search form for translation projects."""

    search = forms.CharField(
        widget=forms.TextInput(attrs={
            'size': '15',
            'placeholder': _('Search'),
            'title': _("Search (Ctrl+Shift+S)<br/>Type and press Enter to "
                       "search"),
        }),
    )
    soptions = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(
            ('exact', _('Exact Match')),
        ),
    )
    sfields = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(
            ('source', _('Source Text')),
            ('target', _('Target Text')),
            ('notes', _('Comments')),
            ('locations', _('Locations'))
        ),
        initial=['source', 'target'],
    )

# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import re
import urllib.parse
from collections import OrderedDict

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from pootle_language.models import Language
from pootle_project.models import Project


LANGCODE_RE = re.compile(
    "^[a-z]{2,}([_-]([a-z]{2,}|[0-9]{3}))*(@[a-z0-9]+)?$", re.IGNORECASE
)


class LanguageForm(forms.ModelForm):

    specialchars = forms.CharField(strip=False)

    class Meta(object):
        model = Language
        fields = (
            "id",
            "code",
            "fullname",
            "specialchars",
            "nplurals",
            "pluralequation",
        )

    def clean_code(self):
        if not LANGCODE_RE.match(self.cleaned_data["code"]):
            raise forms.ValidationError(
                _("Language code does not follow the ISO convention")
            )

        return self.cleaned_data["code"]

    def clean_specialchars(self):
        """Ensures inputted characters are unique."""
        chars = self.cleaned_data["specialchars"]
        return u"".join(OrderedDict((char, None) for char in list(chars)).keys())


class ProjectForm(forms.ModelForm):

    source_language = forms.ModelChoiceField(
        label=_("Source Language"), queryset=Language.objects.none()
    )

    class Meta(object):
        model = Project
        fields = (
            "id",
            "code",
            "fullname",
            "checkstyle",
            "source_language",
            "report_email",
            "screenshot_search_prefix",
            "disabled",
        )

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        self.fields["source_language"].queryset = Language.objects.all()

    def clean_fullname(self):
        return self.cleaned_data["fullname"].strip()

    def clean_code(self):
        return self.cleaned_data["code"].strip()


class BaseUserForm(forms.ModelForm):
    def clean_linkedin(self):
        url = self.cleaned_data["linkedin"]

        if url is None or url == "":
            return None

        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc.endswith("linkedin.com") or (
            not parsed.path.startswith("/in/") or len(parsed.path) < 5
        ):
            raise forms.ValidationError(
                _("Please enter a valid LinkedIn user profile URL.")
            )

        return url


class UserForm(BaseUserForm):

    password = forms.CharField(
        label=_("Password"), required=False, widget=forms.PasswordInput
    )

    class Meta(object):
        model = get_user_model()
        fields = (
            "id",
            "username",
            "is_active",
            "full_name",
            "email",
            "is_superuser",
            "twitter",
            "linkedin",
            "website",
            "bio",
        )

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        # Require setting the password for new users
        if self.instance.pk is None:
            self.fields["password"].required = True

    def save(self, commit=True):
        password = self.cleaned_data["password"]

        if password != "":
            user = super(UserForm, self).save(commit=False)
            user.set_password(password)

            if commit:
                user.save()
        else:
            user = super(UserForm, self).save(commit=commit)

        return user

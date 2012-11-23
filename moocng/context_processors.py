# Copyright 2012 Rooter Analysis S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.contrib.sites.models import Site, RequestSite
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models


def site(request):
    """Sets in the present context information about the current site."""

    # Current SiteManager already handles prevention of spurious
    # database calls. If the user does not have the Sites framework
    # installed, a RequestSite object is an appropriate fallback.
    try:
        models.get_app('sites')
        site_obj = Site.objects.get_current()
    except ImproperlyConfigured:
        site_obj = RequestSite(request)
    return {'site': site_obj}


def theme(request):
    context = {
        'theme': {
            'logo': settings.STATIC_URL + u'img/logo.png',
            'subtitle': u'Knowledge for the masses',
            'top_banner': settings.STATIC_URL + u'img/top_banner.jpg',
            'right_banner1': settings.STATIC_URL + u'img/right_banner1.jpg',
            'right_banner2': settings.STATIC_URL + u'img/right_banner2.jpg',
            'bootstrap_css': settings.STATIC_URL + u'css/bootstrap.min.css',
            'moocng_css': settings.STATIC_URL + u'css/moocng.css',
        }
    }

    try:
        context['theme'].update(settings.MOOCNG_THEME)
    except AttributeError:
        pass

    try:
        context['show_tos'] = settings.SHOW_TOS
    except AttributeError:
        context['show_tos'] = True

    return context


def google_analytics(request):
    context = {}
    try:
        context['google_analytics'] = settings.GOOGLE_ANALYTICS_CODE
    except AttributeError:
        context['google_analytics'] = ''
    return context


def accounts_urls(request):
    try:
        registry_url = settings.REGISTRY_URL
    except AttributeError:
        try:
            registry_url = reverse("userena_signup")
        except NoReverseMatch:
            registry_url = '#'

    try:
        profile_url = settings.PROFILE_URL
    except AttributeError:
        try:
            mapping = {'username': request.user.username}
            profile_url = settings.LOGIN_REDIRECT_URL % mapping
        except AttributeError:
            profile_url = '#'

    try:
        changepw_url = settings.CHANGEPW_URL
    except AttributeError:
        try:
            changepw_url = reverse("userena_password_change",
                                   args=[request.user.username])
        except NoReverseMatch:
            changepw_url = '#'

    try:
        logout_url = reverse("saml2_logout")
    except NoReverseMatch:
        try:
            logout_url = settings.LOGOUT_URL
        except AttributeError:
            logout_url = '#'

    try:
        login_url = reverse("saml2_login")
    except NoReverseMatch:
        try:
            login_url = settings.LOGIN_URL
        except AttributeError:
            login_url = '#'

    return {
        'registry_url': registry_url,
        'profile_url': profile_url,
        'changepw_url': changepw_url,
        'logout_url': logout_url,
        'login_url': login_url,
    }

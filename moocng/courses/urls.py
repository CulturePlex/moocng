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

from django.conf.urls import include, patterns, url

from moocng.courses.feeds import AnnouncementFeed


urlpatterns = patterns(
    'moocng.courses.views',
    url(r'^$', 'home', name='home'),

    # Flatpages
    url(r'^faq/$', 'flatpage', {'page': 'faq'}, name='faq'),
    url(r'^methodology/$', 'flatpage', {'page': 'methodology'},
        name='methodology'),
    url(r'^legal/$', 'flatpage', {'page': 'legal'}, name='legal'),
    url(r'^tos/$', 'flatpage', {'page': 'tos'}, name='tos'),
    url(r'^copyright/$', 'flatpage', {'page': 'copyright'},
        name='copyright'),

    url(r'^transcript/$', 'transcript', name='transcript'),

    url(r'^course/(?P<course_slug>[-\w]+)/$', 'course_overview',
        name='course_overview'),
    url(r'^course/(?P<course_slug>[-\w]+)/classroom/$', 'course_classroom',
        name='course_classroom'),
    url(r'^course/(?P<course_slug>[-\w]+)/progress/$', 'course_progress',
        name='course_progress'),
    url(r'^course/(?P<course_slug>[-\w]+)/announcement/(?P<announcement_slug>[-\w]+)/$',
        'announcement_detail', name='announcement_detail'),
    url(r'^course/(?P<course_slug>[-\w]+)/announcements_feed/$',
        AnnouncementFeed(), name='announcements_feed'),

    # Teacher's course administration
    url(r'^course/(?P<course_slug>[-\w]+)/teacheradmin/',
        include('moocng.teacheradmin.urls')),

    # Teacher's course administration
    url(r'^course/(?P<course_slug>[-\w]+)/discussion/',
        include('moocng.discussion.urls')),
)

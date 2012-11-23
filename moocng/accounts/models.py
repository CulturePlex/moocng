# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from userena.models import UserenaLanguageBaseProfile


class UserProfile(UserenaLanguageBaseProfile):
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
    )
    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)
    website = models.URLField(_('website'), blank=True, verify_exists=False)
    location = models.CharField(_('location'), max_length=255, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    about_me = models.TextField(_('about me'), blank=True)
    user = models.OneToOneField(User, verbose_name=_('user'))

    @property
    def age(self):
        if not self.birth_date:
            return False
        else:
            today = datetime.date.today()
            # Raised when birth date is February 29 and the current year is not
            # a leap year.
            try:
                birthday = self.birth_date.replace(year=today.year)
            except ValueError:
                day = today.day - 1 if today.day != 1 else today.day + 2
                birthday = self.birth_date.replace(year=today.year, day=day)
            if birthday > today:
                return today.year - self.birth_date.year - 1
            else:
                return today.year - self.birth_date.year


@receiver(post_save, sender=User)
def create_profile_account(*args, **kwargs):
    user = kwargs.get("instance", None)
    created = kwargs.get("created", False)
    if user and created:
        try:
            user.get_profile()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=user)

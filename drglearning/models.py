from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Career(models.Model):

    career_id = models.PositiveIntegerField(verbose_name=_(u'Id'))
    name = models.CharField(_("Name"), max_length=255)
    code = models.CharField(_("Code to unlock"), max_length=128,
                            blank=True, null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @staticmethod
    def get_objects_for(obj):
        obj_type = ContentType.objects.get_for_model(obj)
        objects = Career.objects.filter(content_type__pk=obj_type.id,
                                        object_id=obj.id)
        return objects


class Player(models.Model):
    code = models.CharField(_("Code"), unique=True, max_length=128)
    display_name = models.CharField(_("Display name"), max_length=120)
    email = models.CharField(_("E-mail"), unique=True, max_length=90)
    image = models.ImageField(_("Image"), upload_to="players", null=True,
                              blank=True)
    image_url = models.URLField(_("Image URL"), null=True, blank=True)
    token = models.CharField(_("Token"), max_length=128, default="")
    default = models.BooleanField(_(u"Is the default player?"))
    user = models.ForeignKey(User, verbose_name=_(u'User'),
                             related_name='players')

    def __unicode__(self):
        return self.code

    def save(self, *args, **kwargs):
        super(Player, self).save(*args, **kwargs)
        defaults = self.user.players.filter(default=True)
        if defaults.count() > 1 and self.user:
            self.user.players.exclude(id=defaults[0].id).update(default=False)

    def get_name(self):
        if self.display_name and self.email:
            return u"{0} ({1})".format(self.display_name, self.email)
        elif self.display_name or self.email:
            return u"{0}".format(self.display_name or self.email)
        else:
            return u"{0}...".format(self.code[:10])

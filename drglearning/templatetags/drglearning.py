from django.conf import settings
from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()


@register.filter
@stringfilter
def drglearning_careers(course_slug):
    careers = getattr(settings, "DRGLEARNING_CAREERS", {}).get(course_slug, [])
    return careers

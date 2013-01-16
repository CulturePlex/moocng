from django import template

from drglearning.models import Career

register = template.Library()


@register.filter
def drglearning_careers(obj):
    careers = Career.get_objects_for(obj)
    return careers

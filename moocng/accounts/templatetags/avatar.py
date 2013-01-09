from django import template

from easy_thumbnails.files import get_thumbnailer
from gravatar.templatetags.gravatar import gravatar_img_for_user

register = template.Library()


@register.inclusion_tag('accounts/avatar.html')
def avatar_for_user(user, size=None, *args, **kwargs):
    try:
        profile = user.get_profile()
    except:
        profile = None
    try:
        width, height = size.split("x")
    except:
        width, height = size, size
    return {
        'user': user,
        'profile': profile,
        'size': "%sx%s" % (width, height),
        'width': width,
        'height': height,
    }


@register.simple_tag
def avatar_img_for_user(user, size=None, *args, **kwargs):
    context = avatar_for_user(user, size, *args, **kwargs)
    if context["profile"]:
        thumbnailer = get_thumbnailer(context["profile"].mugshot)
        thumbnail_options = {'size': (context["width"], context["height"])}
        thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
        context.update({
            "thumbnail_url": thumbnail.url,
            "username": user.username,
        })
        html = """<img src="{thumbnail_url}" title="Avatar for {username}"
alt="Avatar for {username}"
height="{height}" width="{width}">""".format(**context)
        return html
    else:
        return gravatar_img_for_user(user, size)

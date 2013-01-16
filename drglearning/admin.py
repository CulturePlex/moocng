from django.contrib import admin

from drglearning.models import Career, Player


class CareerAdmin(admin.ModelAdmin):

    list_display = ('career_id', 'name', 'content_type', 'object_id')
    list_filter = ('object_id', 'content_type')


class PlayerAdmin(admin.ModelAdmin):

    list_display = ('user', 'display_name', 'email', 'code')
    list_filter = ('user', )


admin.site.register(Career, CareerAdmin)
admin.site.register(Player, PlayerAdmin)

from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("drglearning.views",
    url(r"^$",
        "drglearning_careers",
        name="drglearning_careers"
    ),
    url(r"^settings/$",
        "drglearning_settings",
        name="drglearning_settings"
    ),
    url(r"^player/(?P<player_id>\w+)/remove/$",
        "drglearning_player_remove",
        name="drglearning_player_remove"
    ),
)

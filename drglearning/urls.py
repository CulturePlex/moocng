from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("drglearning.views",
    url(r"^$",
        "careers",
        name="drglearning_careers"
    ),
    url(r"^settings/$",
        "settings",
        name="drglearning_settings"
    ),
)

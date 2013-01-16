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
)

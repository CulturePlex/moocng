from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("",
    url(r"^$",
        "drglearning.views.careers",
        name="drglearning_careers"
    ),
)

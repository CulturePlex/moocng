from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("",
    url(r"^$",
        "moocng.discussion.views.question_list",
        name="discussion_question_list"
    ),
    url(r"^ask/$",
        "moocng.discussion.views.question_create",
        name="discussion_question_create"
    ),
    url(r"^question/(?P<question_id>\d+)/$",
        "moocng.discussion.views.question_detail",
        name="discussion_question_detail"
    ),
    url(r"^question/(?P<question_id>\d+)/accept/(?P<response_id>\d+)/$",
        "moocng.discussion.views.mark_accepted",
        name="discussion_mark_accepted"
    ),

    # Question voting
    url(r"^question/(?P<question_id>\d+)/vote/(?P<direction>up|down|clear)/$",
        "moocng.discussion.views.question_vote",
        name="discussion_question_vote"
    ),

    url(r"^question/(?P<question_id>\d+)/delete/$",
        "moocng.discussion.views.question_delete",
        name="discussion_question_delete"
    ),

    # Response voting
    url(r"^response/(?P<response_id>\d+)/vote/(?P<direction>up|down|clear)/$",
        "moocng.discussion.views.response_vote",
        name="discussion_response_vote"
    ),

    url(r"^response/(?P<response_id>\d+)/delete/$",
        "moocng.discussion.views.response_delete",
        name="discussion_response_delete"
    ),
)

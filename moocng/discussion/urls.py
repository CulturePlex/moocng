from django.conf.urls.defaults import patterns, url

from voting.views import vote_on_object

from moocng.discussion.models import Question


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

    # Response voting
    url(r"^response/(?P<response_id>\d+)/vote/(?P<direction>up|down|clear)/$",
        "moocng.discussion.views.response_vote",
        name="discussion_response_vote"
    ),
)

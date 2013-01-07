from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _

from voting.models import Vote

from moocng.courses.models import Course
from moocng.discussion.forms import AskQuestionForm, AddResponseForm
from moocng.discussion.groups import group_and_bridge, group_context
from moocng.discussion.models import Question, Response


workflow = import_module(getattr(settings, "DISCUSSION_WORKFLOW_MODULE",
                                 "moocng.discussion.workflow"))


@login_required
def question_list(request, course_slug, **kwargs):
    course = get_object_or_404(Course, slug=course_slug)

    group, bridge = group_and_bridge(kwargs)

    questions = Question.objects.filter(course=course)
    questions = questions.order_by("-score", "created", "id")

    if group:
        questions = group.content_objects(questions)
    else:
        questions = questions.filter(group_content_type=None)

    ctx = group_context(group, bridge)
    ctx.update({
        "course": course,
        "show_material": True,
        "group": group,
        "questions": questions,
    })

    ctx = RequestContext(request, ctx)
    return render_to_response("discussion/question_list.html", ctx)


@login_required
def question_create(request, course_slug, **kwargs):
    course = get_object_or_404(Course, slug=course_slug)
    group, bridge = group_and_bridge(kwargs)

    if request.method == "POST":
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.course = course
            question.save()
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = AskQuestionForm()

    ctx = group_context(group, bridge)
    ctx.update({
        "course": course,
        "show_material": True,
        "group": group,
        "form": form,
    })

    ctx = RequestContext(request, ctx)
    return render_to_response("discussion/question_create.html", ctx)


@login_required
def question_detail(request, course_slug, question_id, **kwargs):
    course = get_object_or_404(Course, slug=course_slug)
    group, bridge = group_and_bridge(kwargs)

    questions = Question.objects.all()

    if group:
        questions = group.content_objects(questions)
    else:
        questions = questions.filter(group_content_type=None)

    question = get_object_or_404(questions, pk=question_id)
    responses = question.responses.order_by("-score", "created", "id")

    if question.user == request.user:
        is_me = True
    else:
        is_me = False

    if request.method == "POST":
        add_response_form = AddResponseForm(request.POST)

        if add_response_form.is_valid():
            response = add_response_form.save(commit=False)
            response.question = question
            response.user = request.user
            response.save()
            return HttpResponseRedirect(response.get_absolute_url())
    else:
        if not is_me or request.user.is_staff:
            add_response_form = AddResponseForm()
        else:
            add_response_form = None

    can_mark_accepted = workflow.can_mark_accepted(request.user, question)
    ctx = group_context(group, bridge)
    ctx.update({
        "course": course,
        "show_material": True,
        "group": group,
        "can_mark_accepted": can_mark_accepted,
        "question": question,
        "responses": responses,
        "add_response_form": add_response_form,
    })

    ctx = RequestContext(request, ctx)
    return render_to_response("discussion/question_detail.html", ctx)


@login_required
def question_vote(request, course_slug, question_id, direction):
    course = get_object_or_404(Course, slug=course_slug)
    questions = Question.objects.filter(course=course)
    question = get_object_or_404(questions, pk=question_id)
    if direction == 'up':
        Vote.objects.record_vote(question, request.user, +1)
    elif direction == 'down':
        Vote.objects.record_vote(question, request.user, -1)
    elif direction == 'clear':
        Vote.objects.record_vote(question, request.user, 0)
    return HttpResponseRedirect(question.get_absolute_url())


@login_required
def mark_accepted(request, course_slug, question_id, response_id, **kwargs):
    course = get_object_or_404(Course, slug=course_slug)
    # if request.method != "POST":
    #     return HttpResponseNotAllowed(["POST"])

    group, bridge = group_and_bridge(kwargs)
    questions = Question.objects.all()

    if group:
        questions = group.content_objects(questions)
    else:
        questions = questions.filter(group_content_type=None)

    question = get_object_or_404(questions, pk=question_id, course=course)

    if not workflow.can_mark_accepted(request.user, question):
        msg = _("You are not allowed to mark this question accepted.")
        return HttpResponseForbidden(msg)

    response = question.responses.get(pk=response_id)
    response.accept()
    return HttpResponseRedirect(response.question.get_absolute_url())


@login_required
def response_vote(request, course_slug, response_id, direction):
    get_object_or_404(Course, slug=course_slug)
    responses = Response.objects.all()
    response = get_object_or_404(responses, pk=response_id)
    if direction == 'up':
        Vote.objects.record_vote(response, request.user, +1)
    elif direction == 'down':
        Vote.objects.record_vote(response, request.user, -1)
    elif direction == 'clear':
        Vote.objects.record_vote(response, request.user, 0)
    return HttpResponseRedirect(response.question.get_absolute_url())

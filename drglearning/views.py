from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from moocng.courses.models import Course
from moocng.courses.utils import is_teacher as is_teacher_test

from drglearning.models import Career, Player
from drglearning.forms import ImportPlayerForm
from drglearning.utils import create_player


@login_required
def careers(request, course_slug, **kwargs):
    course = get_object_or_404(Course, slug=course_slug)
    careers = Career.get_objects_for(course)
    if not careers:
        raise Http404(u"Dr. Glearning course not found")
    if not request.user.players.count():
        reversed_url = reverse("drglearning_settings", args=[course_slug])
        return HttpResponseRedirect(reversed_url)
    else:
        #TODO: Manage multiple players
        player = request.user.players.filter(default=True)[0]
    is_enrolled = course.students.filter(id=request.user.id).exists()
    is_teacher = is_teacher_test(request.user, course)
    ctx = {
        "course": course,
        "show_material": True,
        "is_enrolled": is_enrolled,
        "is_teacher": is_teacher,
        "careers": careers,
        "player": player,
    }
    ctx = RequestContext(request, ctx)
    return render_to_response("drglearning/careers.html", ctx)


@login_required
def settings(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    import_player_form = ImportPlayerForm()
    if "nope" in request.GET:
        player_json = create_player(request.get_host())
        if "token" in player_json and "code" in player_json:
            player = Player.objects.create(
                code=player_json["code"],
                display_name=request.user.get_full_name(),
                email=request.user.email,
                token=player_json["token"],
                image_url=player_json["image_url"],
            )

    elif request.POST:
        import_player_form = ImportPlayerForm(request.POST)
        if import_player_form.is_valid():
            player = import_player_form.save(commit=False)
            player.user = request.user
            player.save()
            reversed_url = reverse("drglearning_careers", args=[course_slug])
            return HttpResponseRedirect(reversed_url)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    is_teacher = is_teacher_test(request.user, course)
    ctx = {
        "course": course,
        "show_material": True,
        "players": request.user.players,
        "import_player_form": import_player_form,
        "is_enrolled": is_enrolled,
        "is_teacher": is_teacher,
    }
    ctx = RequestContext(request, ctx)
    return render_to_response("drglearning/settings.html", ctx)

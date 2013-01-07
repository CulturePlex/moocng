from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from moocng.courses.models import Course
from moocng.courses.utils import is_teacher as is_teacher_test


@login_required
def careers(request, course_slug, **kwargs):
    course = get_object_or_404(Course, slug=course_slug)
    careers = getattr(settings, "DRGLEARNING_CAREERS", {}).get(course.slug, [])
    if not careers:
        raise Http404
    is_enrolled = course.students.filter(id=request.user.id).exists()
    is_teacher = is_teacher_test(request.user, course)
    ctx = {
        "course": course,
        "show_material": True,
        "is_enrolled": is_enrolled,
        "is_teacher": is_teacher,
        "careers": careers
    }
    ctx = RequestContext(request, ctx)
    return render_to_response("drglearning/careers.html", ctx)

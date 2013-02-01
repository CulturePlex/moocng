# Copyright 2012 Rooter Analysis S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime

from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils import simplejson
from django.utils.translation import ugettext as _

from gravatar.templatetags.gravatar import gravatar_img_for_email

from moocng.accounts.templatetags.avatar import avatar_img_for_user
from moocng.courses.models import Course, KnowledgeQuantum, Option, Announcement
from moocng.courses.views import unit_badge_classes
from moocng.courses.forms import AnnouncementForm
from moocng.teacheradmin.decorators import is_teacher_or_staff
from moocng.teacheradmin.forms import CourseForm
from moocng.teacheradmin.models import Invitation
from moocng.teacheradmin.utils import (send_invitation,
                                       send_removed_notification)
from moocng.videos.tasks import process_video_task


@is_teacher_or_staff
def teacheradmin_stats(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    return render_to_response('teacheradmin/stats.html', {
        'course': course,
        'is_enrolled': is_enrolled,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_units(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    return render_to_response('teacheradmin/units.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'unit_badge_classes': simplejson.dumps(unit_badge_classes),
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_units_forcevideoprocess(request, course_slug):
    if not 'kq' in request.GET:
        return HttpResponse(status=400)
    kq = get_object_or_404(KnowledgeQuantum, id=request.GET['kq'])

    question_list = kq.question_set.all()
    if len(question_list) > 0:
        process_video_task.delay(question_list[0].id)
    return HttpResponse()


@is_teacher_or_staff
def teacheradmin_units_question(request, course_slug, kq_id):
    kq = get_object_or_404(KnowledgeQuantum, id=kq_id)
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    question_list = kq.question_set.all()
    if len(question_list) > 0:
        obj = question_list[0]
    else:
        return HttpResponse(status=400)

    if 'HTTP_REFERER' in request.META:
        goback = request.META['HTTP_REFERER']
    else:
        goback = None

    if obj is None:
        raise Http404(_('The KQ with the %s id doesn\'t exists') % kq_id)

    if request.method == 'POST':
        data = simplejson.loads(request.raw_post_data)
        option = obj.option_set.create(**data)
        data['id'] = option.id
        return HttpResponse(simplejson.dumps(data),
                            mimetype='application/json')
    else:
        json = [{
                'id': opt.id,
                'optiontype': opt.optiontype,
                'solution': opt.solution,
                'text': opt.text,
                'x': opt.x, 'y': opt.y,
                'width': opt.width, 'height': opt.height,
                } for opt in obj.option_set.all()]
        context = {
            'course': course,
            'is_enrolled': is_enrolled,
            'object_id': obj.id,
            'original': obj,
            'options_json': simplejson.dumps(json),
            'goback': goback,
        }
        return render_to_response('teacheradmin/question.html', context,
                                  context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_units_option(request, course_slug, kq_id, option_id):
    option = get_object_or_404(Option, id=option_id)

    if request.method == 'PUT':
        data = simplejson.loads(request.raw_post_data)
        for key, value in data.items():
            if key != 'id':
                setattr(option, key, value)
        option.save()
        return HttpResponse(simplejson.dumps(data),
                            mimetype='application/json')

    elif request.method == 'DELETE':
        option.delete()
        return HttpResponse('')

    elif request.method == 'GET':
        data = {
            'id': option.id,
            'optiontype': option.optiontype,
            'solution': option.solution,
            'x': option.x, 'y': option.y,
            'width': option.width, 'height': option.height,
        }
        return HttpResponse(simplejson.dumps(data),
                            mimetype='application/json')


@is_teacher_or_staff
def teacheradmin_teachers(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    teachers = course.teachers.all()
    teachers = [{
                'id': t.id,
                'username': t.get_full_name() or t.username,
                'gravatar': avatar_img_for_user(t, 20),
                } for t in teachers]
    invitations = Invitation.objects.filter(course=course)
    invitations = [{
                   'id': -1,
                   'username': inv.email,
                   'gravatar': gravatar_img_for_email(inv.email, 20),
                   } for inv in invitations]
    teachers.extend(invitations)

    return render_to_response('teacheradmin/teachers.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'teachers': teachers,
        'request': request,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_teachers_delete(request, course_slug, email_or_id):
    course = get_object_or_404(Course, slug=course_slug)
    response = HttpResponse()

    try:
        validate_email(email_or_id)
        # is email, so is an invitation
        try:
            invitation = Invitation.objects.get(email=email_or_id,
                                                course=course)
            invitation.delete()
            send_removed_notification(request, email_or_id, course)
        except Invitation.DoesNotExist:
            response = HttpResponse(status=404)
    except ValidationError:
        # is an id
        try:
            user = User.objects.get(id=email_or_id)
            if user == course.owner:
                response = HttpResponse(status=401)
            else:
                course.teachers.remove(user)
                send_removed_notification(request, user.email, course)
        except (ValueError, User.DoesNotExist):
            response = HttpResponse(status=404)

    return response


@is_teacher_or_staff
def teacheradmin_teachers_invite(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    email_or_id = request.POST['data']
    user = None
    response = None

    try:
        validate_email(email_or_id)
        # is email
        try:
            user = User.objects.get(email=email_or_id)
        except User.DoesNotExist:
            pass
    except ValidationError:
        # is id
        try:
            user = User.objects.get(id=email_or_id)
        except (ValueError, User.DoesNotExist):
            response = HttpResponse(status=404)

    if user is not None:
        course.teachers.add(user)
        name = user.get_full_name()
        if not name:
            name = user.username
        data = {
            'id': user.id,
            'name': name,
            'pending': False
        }
        response = HttpResponse(simplejson.dumps(data),
                                mimetype='application/json')
    elif response is None:
        if Invitation.objects.filter(email=email_or_id).filter(course=course).count() == 0:
            invitation = Invitation(host=request.user, email=email_or_id,
                                    course=course, datetime=datetime.now())
            invitation.save()
            send_invitation(request, invitation)
            data = {
                'id': -1,
                'name': email_or_id,
                'pending': True
            }
            response = HttpResponse(simplejson.dumps(data),
                                    mimetype='application/json')
        else:
            response = HttpResponse(status=409)

    return response


@is_teacher_or_staff
def teacheradmin_teachers_transfer(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    ident = request.POST['data']

    if request.user != course.owner:
        return HttpResponse(status=401)

    response = HttpResponse()

    try:
        user = User.objects.get(id=ident)
        course.owner = user
        course.save()
    except (ValueError, User.DoesNotExist):
        response = HttpResponse(status=404)

    return response


@is_teacher_or_staff
def teacheradmin_info(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    errors = ''
    success = False

    if request.method == 'POST':
        form = CourseForm(data=request.POST, instance=course,
                          files=request.FILES)
        if form.is_valid():
            form.save()
            success = True
        else:
            errors = form.get_pretty_errors()

    return render_to_response('teacheradmin/info.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'errors': errors,
        'success': success,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    announcements = course.announcement_set.all()

    return render_to_response('teacheradmin/announcements.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'announcements': announcements,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements_view(request, course_slug, announ_slug):
    announcement = get_object_or_404(Announcement, slug=announ_slug, course__slug=course_slug)
    course = announcement.course
    is_enrolled = course.students.filter(id=request.user.id).exists()
    return render_to_response('teacheradmin/announcement_view.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'announcement': announcement,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements_edit(request, course_slug, announ_slug=None):

    if announ_slug is None:
        announcement = None
    else:
        announcement = get_object_or_404(Announcement, slug=announ_slug, course__slug=course_slug)

    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.instance.slug = slugify(form.instance.title)
            if Announcement.objects.filter(slug=form.instance.slug).exists():
                messages.error(request, _("There is a announce with the same title"))
            else:
                if not announcement:
                    form.instance.course = course
                form.save()

                return HttpResponseRedirect(reverse("teacheradmin_announcements_view", args=[course_slug, form.instance.slug]))

    else:
        form = AnnouncementForm(instance=announcement)

    return render_to_response('teacheradmin/announcement_edit.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'announcement': announcement,
        'form': form,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_announcements_delete(request, course_slug, announ_slug):

    announcement = get_object_or_404(Announcement, slug=announ_slug, course__slug=course_slug)
    announcement.delete()

    return HttpResponseRedirect(reverse("teacheradmin_announcements", args=[course_slug]))


@is_teacher_or_staff
def teacheradmin_emails(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()

    return render_to_response('teacheradmin/emails.html', {
        'course': course,
        'is_enrolled': is_enrolled,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_students(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = course.students.filter(id=request.user.id).exists()
    teachers_ids = [t["id"] for t in course.teachers.values("id")]
    institutions = course.institutions
    institutions_values = institutions.values("domains")
    institutions_domains = [i["domains"] for i in institutions_values]

    students = course.students.all().order_by("first_name").order_by("username")
    students = [{
                'id': s.id,
                'username': s.get_full_name() or s.username,
                'email': s.email,
                'is_member': institutions.is_member(s, institutions_domains),
                'is_teacher': s.id in teachers_ids,
                'gravatar': avatar_img_for_user(s, 20),
                } for s in students.select_related()]

    return render_to_response('teacheradmin/students.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'students': students,
        'request': request,
    }, context_instance=RequestContext(request))


@is_teacher_or_staff
def teacheradmin_students_delete(request, course_slug, student_id):
    course = get_object_or_404(Course, slug=course_slug)
    response = HttpResponse()

    try:
        user = User.objects.get(id=student_id)
        course.students.remove(user)
        # send_removed_notification(request, user.email, course)
    except (ValueError, User.DoesNotExist):
        response = HttpResponse(status=404)

    return response


@is_teacher_or_staff
def teacheradmin_students_enrol(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    student_id = request.POST['data']
    user = None
    response = None
    try:
        user = User.objects.get(id=student_id)
    except (ValueError, User.DoesNotExist):
        response = HttpResponse(status=404)

    if course.students.filter(id=user.id).exists():
        user = None
        response = HttpResponse(status=405)

    if user is not None:
        course.students.add(user)
        name = user.get_full_name()
        if not name:
            name = user.username
        data = {
            'id': user.id,
            'name': name,
            'email': user.email,
            'is_member': course.institutions.is_member(user),
            'is_teacher': course.teachers.filter(id=user.id).exists(),
            'is_owner': course.owner == user,
            'institutions': course.institutions.exists(),
            'gravatar': avatar_img_for_user(user, 20),
        }
        response = HttpResponse(simplejson.dumps(data),
                                mimetype='application/json')
    elif response is None:
        #TODO: Send an invitation?
        response = HttpResponse(status=409)

    return response

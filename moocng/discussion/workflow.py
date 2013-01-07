from moocng.courses.utils import is_teacher as is_teacher_test


def can_mark_accepted(user, question):
    return question.user == user


def can_delete_response(user, response):
    return is_teacher_test(user, response.question.course)


def can_delete_question(user, question):
    return is_teacher_test(user, question.course)

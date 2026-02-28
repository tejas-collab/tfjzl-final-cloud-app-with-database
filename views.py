from django.shortcuts import render, get_object_or_404
from .models import Course, Question, Choice, Submission, Enrollment
from django.http import HttpResponseRedirect
from django.urls import reverse


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=request.user, course=course)

    selected_choices = []
    for key, value in request.POST.items():
        if key.startswith('choice'):
            selected_choices.append(value)

    submission = Submission.objects.create(enrollment=enrollment)

    for choice_id in selected_choices:
        choice = Choice.objects.get(pk=int(choice_id))
        submission.choices.add(choice)

    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result', args=(course.id, submission.id))
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    total_score = 0
    earned_score = 0

    questions = Question.objects.filter(course=course)

    for question in questions:
        total_score += question.grade
        correct_choices = question.choice_set.filter(is_correct=True)
        selected_choices = submission.choices.filter(question=question)

        if set(correct_choices) == set(selected_choices):
            earned_score += question.grade

    context = {
        'course': course,
        'score': earned_score,
        'total_score': total_score,
        'passed': earned_score >= total_score * 0.5
    }

    return render(request, 'onlinecourse/exam_result.html', context)

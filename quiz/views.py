# -*- coding: utf-8 -*-
# import random
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from quiz.models import Category, Quiz, Sitting, Question, Answer
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'quiz_categories.html', {
        'categories': Category.objects.all(),
    })


@login_required
def view_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    quizzes = Quiz.objects.filter(category=category)
    return render(request, 'quiz_category.html', {
        'category': category,
        'quizzes': quizzes})


@login_required
def quiz_take(request, quiz_id):
    # TODO:
    #   * Can there really be more than one sitting? Is that good?
    #   * If there can be several, use filter immediately.
    #   * If there can be only one, use get and do not catch
    #     Sitting.MultipleObjectsReturned since it will never occur

    quiz = Quiz.objects.get(id=quiz_id)

    try:
        previous_sitting = Sitting.objects.get(
            user=request.user,
            quiz=quiz,
            complete=False)

    except Sitting.DoesNotExist:
        #  start new quiz
        sitting = Sitting.objects.new_sitting(request.user, quiz)
        return load_next_question(request, sitting, quiz)

    except Sitting.MultipleObjectsReturned:
        #  if more than one sitting found
        previous_sitting = Sitting.objects.filter(
            user=request.user,
            quiz=quiz,
            complete=False)[0]  # use the first one

        return load_next_question(request, previous_sitting, quiz)

    else:
        #  use existing quiz
        return load_next_question(request, previous_sitting, quiz)


@login_required
def load_next_question(request, sitting, quiz):
    """
    Load the next question, including outcome of
    previous question, using the sitting
    """
    previous = {}

    if 'guess' in request.GET and request.GET['guess']:
        #  if there has been a previous question
        #  returns a dictionary with previous question details
        previous = question_check(request, quiz, sitting)
        sitting.remove_first_question()  # remove the first question

    question_ID = sitting.get_next_question()

    if not question_ID:
        #  no questions left
        return final_result(request, sitting, previous)

    next_question = Question.objects.get(id=question_ID)

    return render_to_response('question.html',
                              {'quiz': quiz,
                               'question': next_question,
                               'previous': previous,
                               },
                              context_instance=RequestContext(request)
                              )


@login_required
def question_check(request, quiz, sitting):
    """
    Check if a question is correct, adds to score if needed
    and return the previous questions details
    """
    # quiz_id = str(quiz.id)
    guess = request.GET['guess']  # id of the guessed answer
    answer = Answer.objects.get(id=guess)
    # question object (only question related to an answer)
    question = answer.question

    if answer.correct:
        outcome = "correct"
        sitting.add_to_score(1)  # add 1 to sitting score.
    else:
        outcome = "incorrect"
        sitting.add_incorrect_question(question)

    if not quiz.answers_at_end:  # display answer after each question
        return {'previous_answer': answer,
                'previous_outcome': outcome, 'previous_question': question, }
    else:  # display all answers at end
        return {}


@login_required
def final_result(request, sitting, previous):
    """
    The result page for a logged in user
    """
    quiz = sitting.quiz
    score = sitting.get_current_score()
    incorrect = sitting.get_incorrect_questions()
    max_score = quiz.question_set.all().count()
    percent = sitting.get_percent_correct()

    sitting.mark_quiz_complete()  # mark as complete

    if not quiz.exam_paper:  # if we do not plan to store the outcome
        sitting.delete()  # delete the sitting to free up DB space

    if not quiz.answers_at_end:  # answer was shown after each question
        return render_to_response('result.html', {
            'quiz': quiz,
            'score': score,
            'max_score': max_score,
            'percent': percent,
            'previous': previous},
            context_instance=RequestContext(request))
    else:  # show all questions and answers
        questions = quiz.question_set.all()
        return render_to_response('result.html', {
            'quiz': quiz,
            'score': score,
            'max_score': max_score,
            'percent': percent,
            'questions': questions,
            'incorrect_questions': incorrect},
            context_instance=RequestContext(request))

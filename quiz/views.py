# -*- coding: utf-8 -*-
# import random
# from django.shortcuts import render_to_response
# from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from quiz.models import Category, Quiz  # , Question, Answer


def index(request):
    return render(request, 'quiz_categories.html', {
        'categories': Category.objects.all(),
    })


def view_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    quizzes = Quiz.objects.filter(category=category)
    return render(request, 'quiz_category.html', {
        'category': category,
        'quizzes': quizzes})


# def quiz_take(request, quiz_name):
#     """
#     Initial handler for the quiz.
#     1. Tests if user is logged in.
#     2. Decides whether this is the start of a new quiz.
#     """
#
#     quiz = Quiz.objects.get(url=quiz_name.lower())
#     #  url refers to the SEO friendly url specified in model.quiz
#
#     if request.user.is_authenticated():  # logged in user
#         try:
#             previous_sitting = Sitting.objects.get(
#                 user=request.user,
#                 quiz=quiz,
#                 complete=False)
#
#         except Sitting.DoesNotExist:
#             #  start new quiz
#             return user_new_quiz_session(request, quiz)
#
#         except Sitting.MultipleObjectsReturned:
#             #  if more than one sitting found
#             previous_sitting = Sitting.objects.filter(
#                 user=request.user,
#                 quiz=quiz,
#                 complete=False)[0]  # use the first one
#
#             return user_load_next_question(request, previous_sitting, quiz)
#
#         else:
#             #  use existing quiz
#             return user_load_next_question(request, previous_sitting, quiz)
#
#     else:  # anon user
#         quiz_id = str(quiz.id)
#         q_list = quiz_id + "_q_list"
#
#         #  check if anon user has a recent session for this quiz
#         if q_list in request.session:
#             # load up previous session
#             return load_anon_next_question(request, quiz)
#         else:
#             # new session for anon user
#             return new_anon_quiz_session(request, quiz)
#
#
# def new_anon_quiz_session(request, quiz):
#     """
#     Sets the session variables when starting a quiz
#     for the first time when not logged in
#     """
#
#     # set the session to expire after 3 days
#     request.session.set_expiry(259200)
#
#     questions = quiz.question_set.all()
#     question_list = []
#     for question in questions:
#         # question_list is a list of question IDs, which are integers
#         question_list.append(question.id)
#
#     if quiz.random_order:
#         random.shuffle(question_list)
#
#     quiz_id = str(quiz.id)
#
#     score = quiz_id + "_score"
#     # session score for anon users
#     request.session[score] = int(0)
#
#     q_list = quiz_id + "_q_list"
#     # session list of questions
#     request.session[q_list] = question_list
#
#     if 'page_count' not in request.session:
#         # session page count for adverts
#         request.session['page_count'] = int(0)
#
#     return load_anon_next_question(request, quiz)
#
#
# def user_new_quiz_session(request, quiz):
#     """
#     initialise the Sitting class
#     """
#     sitting = Sitting.objects.new_sitting(request.user, quiz)
#
#     if 'page_count' not in request.session:
#         # session page count for adverts
#         request.session['page_count'] = int(0)
#
#     return user_load_next_question(request, sitting, quiz)
#
#
# def load_anon_next_question(request, quiz):
#     """
#     load up the next question, including the outcome of the previous question
#     """
#     quiz_id = str(quiz.id)
#     q_list = quiz_id + "_q_list"
#     question_list = request.session[q_list]
#     previous = {}
#
#     if 'guess' in request.GET and request.GET['guess']:
#         #  if there has been a previous question
#         #  returns a dictionary with previous question details
#         previous = question_check_anon(request, quiz)
#
#         question_list = question_list[1:]  # move onto next question
#         request.session[q_list] = question_list
#
#         counter = request.session['page_count']
#         request.session['page_count'] = counter + 1
#
#     if not request.session[q_list]:
#         #  no questions left!
#         return final_result_anon(request, quiz, previous)
#
#     show_advert = False
#
#     """
#     This is a counter that allows you to add something
#     into the template every X amount of pages.
#     In my original site, I used this to show a full page
#     advert every 10 pages.
#     """
#
#     # try:
#     #     if request.session['page_count'] > 0 and
#     #         request.session['page_count'] % 10 == 0:
#     #         #  advert page every 10 questions
#     #         counter = request.session['page_count']
#     #         request.session['page_count'] = counter + 1
#     #         show_advert = True
#
#     # except KeyError:
#     #     # since one hasnt been started, make it now
#     #     request.session['page_count'] = int(0)
#
#     next_question_id = question_list[0]
#     question = Question.objects.get(id=next_question_id)
#
#     return render_to_response('quiz/question.html',
#                               {'quiz': quiz,
#                                'question': question,
#                                'previous': previous,
#                                'show_advert': show_advert,
#                                },
#                               context_instance=RequestContext(request))
#
#
# def user_load_next_question(request, sitting, quiz):
#     """
#     load the next question, including outcome of
#     previous question, using the sitting
#     """
#     previous = {}
#
#     if 'guess' in request.GET and request.GET['guess']:
#         #  if there has been a previous question
#         #  returns a dictionary with previous question details
#         previous = question_check_user(request, quiz, sitting)
#         sitting.remove_first_question()  # remove the first question
#
#         counter = request.session['page_count']
#         request.session['page_count'] = counter + 1
#
#     question_ID = sitting.get_next_question()
#
#     if not question_ID:
#         #  no questions left
#         return final_result_user(request, sitting, previous)
#
#     show_advert = False
#
#     # try:
#     #     if request.session['page_count'] > 0 and
#     #         request.session['page_count'] % 10 == 0:
#     #         #  advert page every 10 questions
#     #         counter = request.session['page_count']
#     #         request.session['page_count'] = counter + 1
#     #         show_advert = True
#
#     # except KeyError:
#     #     # since one hasnt been started, make it now
#     #     request.session['page_count'] = int(0)
#
#     next_question = Question.objects.get(id=question_ID)
#
#     return render_to_response('quiz/question.html',
#                               {'quiz': quiz,
#                                'question': next_question,
#                                'previous': previous,
#                                'show_advert': show_advert,
#                                },
#                               context_instance=RequestContext(request)
#                               )
#
#
# def final_result_anon(request, quiz, previous):
#     """
#     display the outcome of the completed quiz for anon
#
#     To do:
#         if answers_at_end == True then display all
#         questions with correct answers
#     """
#     quiz_id = str(quiz.id)
#     max_score = quiz.question_set.all().count()
#     score = quiz_id + "_score"
#     score = request.session[score]
#     percent = int(round((float(score) / float(max_score)) * 100))
#     if score == 0:
#         score = "nil points"
#
#     session_score, session_possible = anon_session_score(request)
#
#     if not quiz.answers_at_end:  # if answer was shown after each question
#         return render_to_response('quiz/result.html', {
#             'score': score,
#             'max_score': max_score,
#             'percent': percent,
#             'previous': previous,
#             'session': session_score,
#             'possible': session_possible},
#             context_instance=RequestContext(request))
#     else:  # show all questions and answers
#         questions = quiz.question_set.all()
#         return render_to_response('quiz/result.html', {
#             'score': score,
#             'max_score': max_score,
#             'percent': percent,
#             'questions': questions,
#             'session': session_score,
#             'possible': session_possible},
#             context_instance=RequestContext(request))
#
#
# def final_result_user(request, sitting, previous):
#     """
#     The result page for a logged in user
#     """
#     quiz = sitting.quiz
#     score = sitting.get_current_score()
#     incorrect = sitting.get_incorrect_questions()
#     max_score = quiz.question_set.all().count()
#     percent = sitting.get_percent_correct()
#
#     sitting.mark_quiz_complete()  # mark as complete
#
#     if not quiz.exam_paper:  # if we do not plan to store the outcome
#         sitting.delete()  # delete the sitting to free up DB space
#
#     if not quiz.answers_at_end:  # answer was shown after each question
#         return render_to_response('quiz/result.html', {
#             'quiz': quiz,
#             'score': score,
#             'max_score': max_score,
#             'percent': percent,
#             'previous': previous},
#             context_instance=RequestContext(request))
#     else:  # show all questions and answers
#         questions = quiz.question_set.all()
#         return render_to_response('quiz/result.html', {
#             'quiz': quiz,
#             'score': score,
#             'max_score': max_score,
#             'percent': percent,
#             'questions': questions,
#             'incorrect_questions': incorrect},
#             context_instance=RequestContext(request))
#
#
# def question_check_anon(request, quiz):
#     """
#     check if a question is correct, adds to score if needed
#     and return the previous questions details
#     """
#     quiz_id = str(quiz.id)
#     guess = request.GET['guess']
#     answer = Answer.objects.get(id=guess)
#     question = answer.question  # the id of the question
#
#     if answer.correct:
#         outcome = "correct"
#         score = quiz_id + "_score"
#         current = request.session[score]
#         current = int(current) + 1
#         request.session[score] = current  # add 1 to the score
#         anon_session_score(request, 1, 1)
#
#     else:
#         outcome = "incorrect"
#         anon_session_score(request, 0, 1)
#
#     if not quiz.answers_at_end:  # display answer after each question
#         return {'previous_answer': answer,
#                 'previous_outcome': outcome, 'previous_question': question, }
#
#     else:  # display all answers at end
#         return {}
#
#
# def question_check_user(request, quiz, sitting):
#     """
#     check if a question is correct, adds to score if needed
#     and return the previous questions details
#     """
#     # quiz_id = str(quiz.id)
#     guess = request.GET['guess']  # id of the guessed answer
#     answer = Answer.objects.get(id=guess)
#     # question object (only question related to an answer)
#     question = answer.question
#
#     if answer.correct:
#         outcome = "correct"
#         sitting.add_to_score(1)  # add 1 to sitting score.
#         user_progress_score_update(request, question.category, 1, 1)
#     else:
#         outcome = "incorrect"
#         sitting.add_incorrect_question(question)
#         user_progress_score_update(request, question.category, 0, 1)
#
#     if not quiz.answers_at_end:  # display answer after each question
#         return {'previous_answer': answer,
#                 'previous_outcome': outcome, 'previous_question': question, }
#     else:  # display all answers at end
#         return {}
#
#
# def user_progress_score_update(request, category, score, possible):
#     """
#     update the overall category score for the progress section
#     """
#     try:
#         progress = Progress.objects.get(user=request.user)
#
#     except Progress.DoesNotExist:
#         # no current progress object, make one
#         progress = Progress.objects.new_progress(request.user)
#
#     progress.update_score(category, score, possible)
#
#
# def anon_session_score(request, add=0, possible=0):
#     """
#     returns the session score
#     if number passed in then add this to the running
#     total and then return session score
#     examples:
#         x, y = anon_session_score(1, 1) will add 1 out of a possible 1
#         x, y = anon_session_score(0, 2) will add 0 out of a possible 2
#         x, y = anon_session_score() will return the session score
#             only without modification
#     """
#     if "session_score" not in request.session:
#         # start total if not already running
#         request.session["session_score"] = 0
#         request.session["session_score_possible"] = 0
#
#     if possible > 0:  # if changes are due
#         score = request.session["session_score"]
#         score = score + add
#         request.session["session_score"] = score
#
#         denominator = request.session["session_score_possible"]
#         denominator = denominator + possible
#         request.session["session_score_possible"] = denominator
#
#     return (request.session["session_score"],
#             request.session["session_score_possible"])
#
#
# def progress(request):
#     """
#     displays a dashboard for the user to monitor their progress
#
#     to do:
#         progress for each category - total average score, pie chart,
#         line graph over time
#         overall progress - current session, 7 days and 28 day line graph
#         previous practice exam results
#     """
#
#     if not request.user.is_authenticated():  # if anon
#         # display session score and encourage to sign up
#         score, possible = anon_session_score(request)
#         return render_to_response(
#             'quiz/signup.html',
#             {'anon_score': score, 'anon_possible': possible, },
#             context_instance=RequestContext(request))
#
#     try:
#         progress = Progress.objects.get(user=request.user)
#
#     except Progress.DoesNotExist:
#         # viewing progress for first time.
#         # Most likely just signed up as redirect to progress after signup
#         # no current progress object, make one
#         progress = Progress.objects.new_progress(request.user)
#         return render_to_response(
#             'quiz/progress.html',
#             {'new_user': True},
#             context_instance=RequestContext(request))
#
#     cat_scores = progress.list_all_cat_scores()
#     # dict {category name: list of three integers [score, possible, percent]}
#
#     exams = progress.show_exams()  # queryset of the exams a user has sat
#
#     return render_to_response(
#         'quiz/progress.html',
#         {'cat_scores': cat_scores, 'exams': exams},
#         context_instance=RequestContext(request))

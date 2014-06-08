# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from program.models import Activity
from thematic.models import Thematic
from django.utils.translation import ugettext_lazy as _


class Quiz(Activity):
    """
    Quiz is a container that can be filled with various
    different question types or other content
    """

    CLASSIC = 'classic'
    STARTING = 'starting'
    ENDING = 'ending'
    KINDS = (
        (CLASSIC, _(u'classique')),
        (STARTING, _(u'début')),
        (ENDING, _(u'fin'))
    )

    kind = models.CharField(
        max_length=20, choices=KINDS, blank=True, default=CLASSIC)

    title = models.CharField(max_length=250)

    description = models.TextField(blank=True,
                                   help_text="a description of the quiz")

    random_order = models.BooleanField(
        blank=False,
        default=False,
        help_text="Display the questions in a " +
        "random order or as they are set?")

    answers_at_end = models.BooleanField(
        blank=False,
        default=False,
        help_text="Correct answer is NOT shown after question. " +
        "Answers displayed at end")

    # TODO: is this field useful?
    exam_paper = models.BooleanField(
        blank=False,
        default=False,
        help_text="If yes, the result of each attempt " +
        "by a user will be stored")

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def get_usa_url(self, usa_id):
        return reverse('my_quiz_details', args=[usa_id])

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return self.title


class Question(models.Model):

    quiz = models.ManyToManyField(Quiz, blank=True,
                                  related_name='questions')

    thematic = models.ForeignKey(Thematic, blank=True, null=True,
                                 related_name='questions')

    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the question text that you want displayed",
        verbose_name='Question')

    explanation = models.TextField(
        max_length=2000,
        blank=True,
        help_text="Explanation to be shown after " +
        "the question has been answered.",
        verbose_name='Explanation')

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['thematic']

    def __unicode__(self):
        return self.content


class Answer(models.Model):
    question = models.ForeignKey(Question)

    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the answer text that you want displayed")

    correct = models.BooleanField(
        blank=False,
        default=False,
        help_text="Is this a correct answer?")

    def __unicode__(self):
        return self.content


class SittingManager(models.Manager):
    """
    Custom manager for the Sitting model
    """
    def new_sitting(self, user, quiz):
        """
        Called at the start of a new attempt at a quiz
        """
        if quiz.random_order:
            question_set = quiz.questions.all().order_by('?')
        else:
            question_set = quiz.questions.all()

        questions = ""
        for question in question_set:
            # string of IDs seperated by commas
            questions = questions + str(question.id) + ","

        new_sitting = self.create(
            user=user,
            quiz=quiz,
            question_list=questions,
            incorrect_questions="",
            current_score=0,
            complete=False)
        new_sitting.save()
        return new_sitting


class Sitting(models.Model):
    """
    Used to store the progress of logged in users sitting an exam.
    Replaces the session system used by anon users.
    user is the logged in user.
    Anon users use sessions to track progress
    question_list is a list of id's of the unanswered questions.
    Stored as a textfield to allow >255 chars. quesion_list
    is in csv format.

    incorrect_questions is a list of id's of the questions answered wrongly
    current_Score is a total of the answered questions value. Needs to be
    converted to int when used.
    complete - True when exam complete. Should only be stored if
    quiz.exam_paper is true, or DB will swell quickly in size
    """

    user = models.ForeignKey('auth.User')  # one user per exam class
    quiz = models.ForeignKey(Quiz)
    # another awful csv. Always end with a comma
    question_list = models.TextField()
    # more awful csv. Always end with a comma
    incorrect_questions = models.TextField(blank=True)
    # a string of the score ie 19  convert to int for use
    # TODO: Why is this a string? Change to int
    current_score = models.IntegerField(default=0)
    complete = models.BooleanField(default=False, blank=False)
    objects = SittingManager()

    def get_next_question(self):
        """
        Returns the next question ID (as an integer).
        If no question is found, returns False
        Does NOT remove the question from the front of the list.
        """
        # TODO: Simplify this method
        # finds the index of the first comma in the string
        first_comma = self.question_list.find(',')
        # if no question number is found
        if first_comma == -1 or first_comma == 0:
            return False

        # up to but not including the first comma
        qID = self.question_list[:first_comma]

        return qID

    def remove_first_question(self):
        """
        Removes the first question on the list.
        Does not return a value.
        """
        # TODO: Simplify this method (split/join/pop/remove)
        # finds the index of the first comma in the string
        first_comma = self.question_list.find(',')
        # if question number IS found
        if first_comma != -1 or first_comma != 0:  # TODO: this is always true!
            # saves from the first number after the first comma
            temp = self.question_list[first_comma+1:]
            self.question_list = temp
        self.save()  # TODO: saving is useless if it hasn't been modified!

    def add_to_score(self, points):
        """
        Adds the points to the running total.
        Does not return anything
        """
        present_score = self.get_current_score()
        updated_score = present_score + int(points)
        self.current_score = updated_score
        self.save()

    def get_current_score(self):
        """
        returns the current score as an integer
        """
        return self.current_score

    def get_percent_correct(self):
        """
        returns the percentage correct as an integer
        """
        nb_questions = self.quiz.questions.all().count()
        if nb_questions == 0:
            return 0
        return int(round((float(self.current_score) / float(
            nb_questions)) * 100))

    def mark_quiz_complete(self):
        """
        Changes the quiz to complete.
        Does not return anything
        """
        self.complete = True
        self.save()

    def add_incorrect_question(self, question):
        """
        Adds the uid of an incorrect question to the list
        of incorrect questions
        The question object must be passed in
        Does not return anything
        """
        current_incorrect = self.incorrect_questions
        question_id = question.id
        if current_incorrect == "":
            updated = str(question_id) + ","
        else:
            updated = current_incorrect + str(question_id) + ","
        self.incorrect_questions = updated
        self.save()

    def get_incorrect_questions(self):
        """
        Returns a list of IDs that indicate all the questions that have
        been answered incorrectly in this sitting
        """
        # string of question IDs as CSV  ie 32,19,22,3,75
        question_list = self.incorrect_questions
        # list of strings ie [32,19,22,3,75]
        split_questions = question_list.split(',')
        return split_questions

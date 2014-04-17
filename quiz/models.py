# -*- coding: utf-8 -*-
from django.db import models

# Uncomment this and "choices" in the Category model
# to prepopulate the categories
# CATEGORY_CHOICES = (('Endocrinology', 'Endocrinology'),
#                     ('Dermatology', 'Dermatology'),
#                     ('Psychiatry', 'Psychiatry'),
#                     ('Cardiology', 'Cardiology'))


class Category(models.Model):
    """
    Category for a quiz or question
    """

    # TODO: blank/null?
    # TODO: fixed choices?
    name = models.CharField(
        max_length=250,
        # choices=CATEGORY_CHOICES,
        unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.name


class Quiz(models.Model):
    """
    Quiz is a container that can be filled with various
    different question types or other content
    """

    title = models.CharField(max_length=60, blank=False)

    description = models.TextField(blank=True,
                                   help_text="a description of the quiz")

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True)

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

    def __unicode__(self):
        return self.title


class Question(models.Model):

    quiz = models.ManyToManyField(Quiz, blank=True)

    category = models.ForeignKey(Category, blank=True, null=True)

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
        ordering = ['category']

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

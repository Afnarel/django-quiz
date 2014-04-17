import re

from django.db import models
# from django.conf import settings
# from django.utils.encoding import smart_str
# from django.contrib.auth.models import User

"""
If you want to prepopulate the category choices then use the
following and uncomment 'choices' in the category model
I have left in my original set as an example
"""

CATEGORY_CHOICES = (('Endocrinology', 'Endocrinology'),
                    ('Dermatology', 'Dermatology'),
                    ('Cellular Biology', 'Cellular Biology'),
                    ('Neurology', 'Neurology'),
                    ('Gastroenterology', 'Gastroenterology'),
                    ('Statistics', 'Statistics'),
                    ('Rheumatology', 'Rheumatology'),
                    ('Tropical medicine', 'Tropical medicine'),
                    ('Respiratory', 'Respiratory'),
                    ('Immunology', 'Immunology'),
                    ('Nephrology', 'Nephrology'),
                    ('Genetic Medicine', 'Genetic Medicine'),
                    ('Haematology', 'Haematology'),
                    ('Pharmacology', 'Pharmacology'),
                    ('Physiology', 'Physiology'),
                    ('Ophthalmology', 'Ophthalmology'),
                    ('Anatomy', 'Anatomy'),
                    ('Biochemistry', 'Biochemistry'),
                    ('empty', 'empty'),
                    ('Psychiatry', 'Psychiatry'),
                    ('Cardiology', 'Cardiology'),
                    )


class CategoryManager(models.Manager):
    """
    Custom manager for Progress class
    """
    def new_category(self, category):
        """
        add a new category
        """
        new_category = self.create(category=category)
        new_category.save()


class Category(models.Model):
    """
    Category used to define a category for either a quiz or question
    """

    category = models.CharField(max_length=250,
                                blank=True,
                                # choices=CATEGORY_CHOICES,
                                unique=True,
                                null=True,
                                )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.category


class Quiz(models.Model):
    """
    Quiz is a container that can be filled with various
    different question types or other content
    """

    title = models.CharField(max_length=60,
                             blank=False,
                             )

    description = models.TextField(blank=True,
                                   help_text="a description of the quiz",
                                   )

    url = models.CharField(max_length=60,
                           blank=False,
                           help_text="an SEO friendly url",
                           verbose_name='SEO friendly url',
                           )

    category = models.ForeignKey(Category,
                                 null=True,
                                 blank=True,
                                 )

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

    exam_paper = models.BooleanField(
        blank=False,
        default=False,
        help_text="If yes, the result of each attempt " +
        "by a user will be stored")

    def save(self, force_insert=False, force_update=False):
        self.url = self.url.replace(' ', '-').lower()
        self.url = ''.join(
            letter for letter in self.url if letter.isalnum() or letter == '-')
        super(Quiz, self).save(force_insert, force_update)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __unicode__(self):
        return self.title


"""
Progress is used to track an individual signed in users
score on different quiz's and categories
"""


class ProgressManager(models.Manager):
    """
    Custom manager for Progress class
    """
    def new_progress(self, user):
        """
        method to call when a user is accessing the
        progress section for the first time
        """
        new_progress = self.create(user=user, score='')
        new_progress.save()
        return new_progress


class Progress(models.Model):
    """
    Stores the score for each category, max possible
    and previous exam paper scores
    Data stored in csv using the format
    [category, score, possible, category, score, possible, ...]
    """

    user = models.OneToOneField('auth.User')  # one user per progress class
    # The god awful csv. guido forgive me. Always end this with a comma
    score = models.TextField()
    objects = ProgressManager()

    def list_all_cat_scores(self):
        """
        Returns a dict in which the key is the category name
        and the item is a list of three integers.
        The first is the number of questions correct,
        the second is the possible best score,
        the third is the percentage correct.
        The dict will have one key for every category that you have defined.
        """

        categories = Category.objects.all()
        score_before = self.score
        output = {}

        for cat in categories:  # for each of the categories
            # group 1 is score, group 2 is possible
            my_regex = re.escape(cat.category) + r",(\d+),(\d+),"
            match = re.search(my_regex, self.score, re.IGNORECASE)

            if match:
                score = int(match.group(1))
                possible = int(match.group(2))
                try:
                    percent = int(round((
                        float(score) / float(possible)) * 100))
                except:
                    percent = 0
                score_list = [score, possible, percent]
                output[cat.category] = score_list

            else:  # Is possible to remove/comment this section out
                # Temporarily store the current csv that lists all the scores
                temp = self.score
                # Add the class that is not listed at the end.
                # Always end with a comma
                temp = temp + cat.category + ",0,0,"
                self.score = temp
                output[cat.category] = [0, 0]

        if len(self.score) > len(score_before):  # if changes have been made
            self.save()  # save only at the end to minimise disc writes

        return output

    def check_cat_score(self, category_queried):
        """
        pass in a category, get the users score
        and possible score as x,y respectively
        note: score returned as integers
        """

        category_test = Category.objects.filter(
            category=category_queried).exists()

        if not category_test:
            # TODO: make this useful!
            return "error",  "category does not exist"

        # group 1 is score, group 2 is possible
        my_regex = re.escape(category_queried) + r",(\d+),(\d+),"
        match = re.search(my_regex, self.score, re.IGNORECASE)

        if match:
            score = int(match.group(1))
            possible = int(match.group(2))
            return score, possible

        # if not found, and since category exists,
        # add category to the csv with 0 points
        else:
            """
            #  removed to lower disk writes
            temp = self.score
            temp = temp + category_queried + ",0,0,"  # always end with a comma
            self.score = temp
            self.save()
            """
            return 0, 0

    def update_score(self, category_queried, score_to_add, possible_to_add):
        """
        pass in category, amount to increase score and max
        possible increase if all were correct does not return anything
        data stored in csv using the format
        [category, score, possible, category, score, possible, ...]
        """

        category_test = Category.objects.filter(
            category=category_queried).exists()

        if not category_test:
            # to do: make useful
            return "error",  "category does not exist"

        # group 1 is score, group 2 is possible
        my_regex = re.escape(str(category_queried)) + r",(\d+),(\d+),"
        match = re.search(my_regex, self.score, re.IGNORECASE)

        if match:
            current_score = int(match.group(1))
            current_possible = int(match.group(2))
            updated_current_score = current_score + score_to_add
            updated_current_possible = current_possible + possible_to_add

            new_score = str(category_queried) + "," + str(
                updated_current_score) + "," + str(
                updated_current_possible) + ","

            temp = self.score
            found_instance = match.group()
            # swap the old score for the new one
            temp = temp.replace(found_instance, new_score)

            self.score = temp
            self.save()

        else:
            """
            if not present but a verified category,
            add with the points passed in
            """
            temp = self.score
            temp = temp + str(category_queried) + "," + str(
                score_to_add) + "," + str(possible_to_add) + ","
            self.score = temp
            self.save()

    def show_exams(self):
        """
        finds the previous exams marked as 'exam papers'
        returns a queryset of complete exams
        """
        #  list of exam objects from user that are complete
        return Sitting.objects.filter(user=self.user).filter(complete=True)


class SittingManager(models.Manager):
    """
    custom manager for Sitting class
    """
    def new_sitting(self, user, quiz):
        """
        method to call at the start of each new attempt at a quiz
        """
        if quiz.random_order:
            question_set = quiz.question_set.all().order_by('?')
        else:
            question_set = quiz.question_set.all()

        questions = ""
        for question in question_set:
            # string of IDs seperated by commas
            questions = questions + str(question.id) + ","

        new_sitting = self.create(
            user=user,
            quiz=quiz,
            question_list=questions,
            incorrect_questions="",
            current_score="0",
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
    current_score = models.TextField()
    complete = models.BooleanField(default=False, blank=False)
    objects = SittingManager()

    def get_next_question(self):
        """
        Returns the next question ID (as an integer).
        If no question is found, returns False
        Does NOT remove the question from the front of the list.
        """
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
        # finds the index of the first comma in the string
        first_comma = self.question_list.find(',')
        # if question number IS found
        if first_comma != -1 or first_comma != 0:
            # saves from the first number after the first comma
            temp = self.question_list[first_comma+1:]
            self.question_list = temp
        self.save()

    def add_to_score(self, points):
        """
        Adds the points to the running total.
        Does not return anything
        """
        present_score = self.get_current_score()
        updated_score = present_score + int(points)
        self.current_score = str(updated_score)
        self.save()

    def get_current_score(self):
        """
        returns the current score as an integer
        """
        return int(self.current_score)

    def get_percent_correct(self):
        """
        returns the percentage correct as an integer
        """
        return int(round((float(self.current_score) / float(
            self.quiz.question_set.all().count())) * 100))

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


class Question(models.Model):

    quiz = models.ManyToManyField(Quiz, blank=True, )
    category = models.ForeignKey(Category, blank=True, null=True, )
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

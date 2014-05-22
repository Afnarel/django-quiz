from django.contrib import admin
from quiz.models import Quiz, Question, Answer
from forms import QuizAdminForm


class QuestionInline(admin.TabularInline):
    model = Question.quiz.through
    filter_horizontal = ('content',)


class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('name', 'thematic',)
    list_filter = ('thematic',)
    search_fields = ('description', 'thematic',)


class QuestionAdmin(admin.ModelAdmin):

    def quiz_list(self, question):
        return ','.join(['%s (%s)' % (quiz.name, quiz.pk)
                        for quiz in question.quiz.all()])

    list_display = ('content', 'thematic', 'quiz_list')
    list_filter = ('thematic',)
    fields = ('content', 'thematic', 'quiz', 'explanation',)

    search_fields = ('content',)
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)

from django.contrib import admin
from quiz.models import Quiz, Category, Question, Answer
from forms import QuizAdminForm


class QuestionInline(admin.TabularInline):
    model = Question.quiz.through
    filter_horizontal = ('content',)


class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('title', 'category',)
    list_filter = ('category',)
    search_fields = ('description', 'category',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category',)
    list_filter = ('category',)
    fields = ('content', 'category', 'quiz', 'explanation',)

    search_fields = ('content',)
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)

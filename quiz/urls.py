try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url

urlpatterns = patterns(
    'quiz.views',
    url(r'^$', 'index',
        name='quiz_categories'),

    url(r'^category/(?P<category_id>\d+)', 'view_category',
        name='quiz_category'),

    url(r'^take/(?P<quiz_id>\d+)/$', 'quiz_take',
        name='quiz_take'),
)

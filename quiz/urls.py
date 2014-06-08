try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url

urlpatterns = patterns(
    'quiz.views',
    # url(r'^$', 'index',
    #     name='quiz_thematics'),

    # url(r'^thematic/(?P<thematic_id>\d+)', 'view_thematic',
    #     name='quiz_thematic'),

    # url(r'^take/(?P<quiz_id>\d+)/$', 'quiz_take',
    #     name='quiz_take'),
)

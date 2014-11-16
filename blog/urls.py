from django.conf.urls.defaults import *
from blog import views

urlpatterns = patterns('',
    #Main Page
    (r'^$', views.index),

    #Entries by category
    (r'^category/(?P<category>\w+)/$', views.entries_by_category, {},'cat_view'),

    #Entries by tag
    (r'^tag/(?P<tag>\w+)/$', views.entries_by_tag, {}, 'tag_view'),

    #Entries by date
    (r'^(?P<year>\d{4})/$', views.entries_by_year, {}, 'archive_year'),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/$', views.entries_by_month, {}, 'archive_month'),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.entries_by_day, {}, 'archive_day'),

    #Entry detail page
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', views.entry_detail, {}, 'entry_detail'),

    #Entry modification. Login required.
    (r'^entryadd/$', views.entry_add, {},'entry_add'),
    (r'^entryedit/(?P<id>\d+)$', views.entry_edit, {},'entry_edit'),
    (r'^entrydelete/(?P<id>\d+)$', views.entry_delete, {},'entry_delete'),

    #Session management
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name':'login.html'}, 'login'),
    (r'^logout/$',views.user_logout, {},'logout'),
)
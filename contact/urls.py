from django.conf.urls import patterns, url

from contact import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='contact_index'),
    url(r'^importuserfromad/', views.import_user_from_ad, name='import_user_from_ad'),
    url(r'^importlogontoad/', views.import_logon_to_ad, name='import_logon_to_ad'),
)
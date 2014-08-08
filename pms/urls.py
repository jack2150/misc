from django.conf.urls import patterns, url

from pms import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='pms'),

    # view portfolio data table
    url(r'^index', views.index, name='index'),
    url(r'^test1', views.index2, name='index2'),

    # select csv files for import
    url(r'^import/select', views.import_select_date, name='import_select_date'),

    # import data into db
    url(r'^import/single/$', views.import_position, name='import_position'),
    url(r'^import/single/(?P<date>[-\w]+)/$', views.import_position, name='import_position'),

)


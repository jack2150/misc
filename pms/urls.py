from django.conf.urls import patterns, url

from pms import views

urlpatterns = patterns(
    '',

    # position: view
    url(r'^position/$', views.position,
        name='position_view'),
    url(r'^position/(?P<date>[-\w]+)/$', views.position,
        name='position_view'),

    # position: select files to import
    url(r'^position/import/select/$', views.position_select_files,
        name='position_select_files'),

    # position: import file to db
    url(r'^import/single/$', views.position_import_single,
        name='position_import_single'),
    url(r'^import/single/(?P<date>[-\w]+)/$', views.position_import_single,
        name='position_import_single'),

    # position: ajax check date exists
    url(r'^position/exists/$', views.position_exists,
        name='position_exists'),
    url(r'^position/exists/(?P<date>[-\w]+)/$', views.position_exists,
        name='position_exists'),
)


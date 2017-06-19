from django.conf.urls import url

from portal import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^s/(?P<token>[a-z0-9\-]{36})/(?P<file_path>.+)', views.get_file, name='get-file'),

    url(r'^browse/$', views.NodeDetail.as_view(), name='node-root'),
    url(r'^browse/(?P<pk>[a-z0-9\-]{36})/', views.NodeDetail.as_view(), name='node-detail'),

    url(r'^share/$', views.ShareDetail.as_view()),
    url(r'^share/(?P<uuid>[a-z0-9\-]{36})/$', views.ShareDetail.as_view(), name='share-root'),
    url(r'^share/(?P<uuid>[a-z0-9\-]{36})/(?P<node>[a-z0-9\-]{36})/$', views.ShareDetail.as_view(), name='share-sub-node'),
]

urlpatterns = format_suffix_patterns(urlpatterns)



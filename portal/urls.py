from django.conf.urls import url

from portal import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^$', views.root, name='root'),
    url(r'^(?P<node_uuid>[a-z0-9\-]{36})$', views.admin_browse, name='admin-browse-node'),

    url(r'^serve/(?P<token>[a-z0-9\-]{36})$', views.browse_share, name='show-root-share'),
    url(r'^serve/(?P<token>[a-z0-9\-]{36})/(?P<node_uuid>[a-z0-9\-]{36})$', views.browse_share, name='show-sub-share'),

    url(r'^s/(?P<token>[a-z0-9\-]{36})/(?P<file_path>.+)', views.get_file, name='get-file'),

    url(r'^shareapi/$', views.ShareCreate.as_view()),
    url(r'^shareapi/(?P<uuid>[a-z0-9\-]{36})/$', views.ShareDetail.as_view()),
    url(r'^sharenode/(?P<uuid>[a-z0-9\-]{36})/(?P<node>[a-z0-9\-]{36})/$', views.ShareDetail.as_view()),


    url(r'^test/(?P<pk>[a-z0-9\-]{36})/', views.NodeDetail.as_view(), name='node-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)



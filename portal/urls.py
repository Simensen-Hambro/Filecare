from django.conf.urls import url

from portal import views


urlpatterns = [
    url(r'^$', views.root, name='root'),
    url(r'^(?P<node_uuid>[a-z0-9]{32})$', views.admin_browse, name='admin-browse-node'),

    url(r'^serve/(?P<token>[a-z0-9]{32})$', views.browse_share, name='show-root-share'),
    url(r'^serve/(?P<token>[a-z0-9]{32})/(?P<node_uuid>[a-z0-9]{32})$', views.browse_share, name='show-sub-share'),

    url(r'^s/(?P<token>[a-z0-9]{32})/(?P<file_path>.+)', views.get_file, name='get-file'),
]

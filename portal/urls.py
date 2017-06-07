from django.conf.urls import url
from portal import views
from django.conf import settings

urlpatterns = [
    url(r'^serve/(?P<token>[a-z0-9]{32})$', views.serve_share, name='show-root-share'),
    url(r'^serve/(?P<token>[a-z0-9]{32})/(?P<node_token>[a-z0-9]{32})$', views.serve_share, name='show-sub-share'),
    url(r'^s/(?P<token>[a-z0-9]{32})/(?P<file_path>.+)', views.get_file, name='get-file'),
]
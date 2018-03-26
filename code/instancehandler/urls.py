from django.conf.urls import url
from instancehandler import views

urlpatterns = [
    url(r'^(?P<type>[ns|vnf]+)/list/', views.list, name='list'),
    url(r'^create/', views.create, name='create'),
    url(r'^(?P<type>[ns|vnf]+)/(?P<vim_id>[0-9a-z-]+)/delete$', views.delete, name='delete'),
    url(r'^(?P<type>[ns|vnf]+)/(?P<vim_id>[0-9a-z-]+)', views.show, name='show'),

]
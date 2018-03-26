from django.conf.urls import url
from vimhandler import views

urlpatterns = [
    url(r'^list/', views.list, name='list'),
    url(r'^create/', views.create, name='create'),
    url(r'^(?P<vim_id>[0-9a-z-]+)/delete$', views.delete, name='delete'),
    url(r'^(?P<vim_id>[0-9a-z-]+)', views.show, name='show'),

]
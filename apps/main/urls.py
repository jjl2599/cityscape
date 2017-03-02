from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^users$', views.create_user),
    url(r'^home$', views.home),
    url(r'^sessions$', views.login_user),
    url(r'^logout$', views.logout),
    url(r'^create_page$', views.create_page),
    url(r'^store$', views.store),
    url(r'^create_player/(?P<user_id>\d+)$', views.create_player),
    url(r'^use_item/(?P<player_id>\d+)/(?P<item_type>\w+)/$', views.use_item),
    url(r'^buy_item/(?P<player_id>\d+)/(?P<item_type>\w+)/$', views.buy_item),
    url(r'^attack/(?P<player_id>\d+)$', views.attack),
    url(r'^revive/(?P<grave_id>\d+)$', views.revive),
]

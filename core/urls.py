from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('room', views.room, name='room'), 
    path('setting', views.setting, name='setting'), 
    path('signup', views.signup, name='signup'),
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='foolow'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('like-post', views.like_post, name='like-post'),
    path('search',views.search,name='search'),
    path('generate_csrf_token',views.generate_csrf_token,name='generate_csrf_token'),
    path('createandgettoken',views.createandgettoken,name='search'),
    path('create_member/',views.createMember ,name='createmember'),
    path('get_member/', views.getMember,name="getmember"),
    path('delete_member/', views.deleteMember,name="deletemember"),
    path('followering/', views.followdisplay,name="followering"),
]
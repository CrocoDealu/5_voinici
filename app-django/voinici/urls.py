from django.contrib import admin
from django.urls import path, include
from .views import home  
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', home, name='home'),
    path('theory/inclined_plane/', views.inclined_plane_view, name='inclined_plane'),
    path('theory/collision/', views.collision_view, name='collision'),
    path('theory/pendulum/', views.pendulum_view, name='pendulum'),
    path('quiz/', views.quiz_view, name='quiz'),  # generic quiz path 
]

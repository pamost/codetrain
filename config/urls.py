"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

app_name = 'app'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),

    path('set-user/', views.set_user, name='set_user'),
    path('user-stats/', views.user_stats, name='user_stats'),
    path('logout-user/', views.logout_user, name='logout_user'),
    path('get-user-data/', views.get_user_data, name='get_user_data'),
    path('update-user/', views.update_user, name='update_user'),

    path('card/create/', views.card_create, name='card_create'),
    path('remember-card/', views.remember_card, name='remember_card'),
    path('unremember-card/', views.unremember_card, name='unremember_card'),

    path('quiz/<int:topic_id>/', views.topic_quiz, name='topic_quiz'),
    path('quiz-result/', views.quiz_result, name='quiz_result'),

    path('<slug:lang_slug>/', views.topics, name='topics'),
]

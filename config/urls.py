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
from app.views import home_page, set_user, user_stats, logout_user, get_user_data, update_user

app_name = 'app'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('set-user/', set_user, name='set_user'),
    
    path('user-stats/', user_stats, name='user_stats'),
    path('logout-user/', logout_user, name='logout_user'),
    path('get-user-data/', get_user_data, name='get_user_data'),
    path('update-user/', update_user, name='update_user'),
]

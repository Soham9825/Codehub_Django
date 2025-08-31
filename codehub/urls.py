"""
URL configuration for codehub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path,include
from accounts.views import *

urlpatterns = [
    path('', home , name = "home" ),
    path("accounts/", include("allauth.urls")),
    path('signup/', signup , name = "signup" ),
    path('login/', login , name = "login" ),
    path('logout/', logout , name = "logout" ),
    path('premium/', premium , name = "premium" ),
    path('forgotpassword/', forgotpassword, name='forgotpassword'),
    path('verifyemail/', verifyemail , name = "verifyemail" ),
    path('resend_verification_email/', resend_verification_email, name='resend_verification_email'),
    path("problems/", problem_list, name="problem_list"),
    path("problems/<slug:problem_slug>/submit/", submit_solution, name="submit_solution"),
    path('terms/', terms, name='terms'),
    path('privacy-policy/', privacypolicy, name='privacypolicy'),
    path('explore/', explore, name='explore'),
    path('dashboard/dsa/content/<str:topic_name>/', dsa_topic_content, name='dsa_topic_content'),
    path('dashboard/sql/content/<str:topic_name>/', sql_topic_content, name='sql_topic_content'),
    path('dashboard/dsa/', dsadashboard, name='dsadashboard'),
    path('dashboard/sql/', sqldashboard, name='sqldashboard'),
    path('admin/', admin.site.urls),
]

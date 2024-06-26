"""
URL configuration for erp_eudora_vinos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from authuser import views

urlpatterns = [
    path('', include('website.urls')),
    path('admin/', admin.site.urls),
    path('admin/', include('django.contrib.auth.urls')),
    # Incluimos las urls de la app website que sera la encargada de mostrar la pagina web
    
    path('accounts/', include('django.contrib.auth.urls')),
    #path('login/', views.LoginView.as_view(), name='login')
    
    #LOGOUT
    path('salir/', views.salir , name='salir')
]


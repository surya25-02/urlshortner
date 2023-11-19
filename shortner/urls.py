from django.contrib import admin
from django.urls import path
from shortner.views import UserLogin, UserLogout, UserSignup, GetShortLink, HomeView, URLShortenerAPI, DashboardView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login', UserLogin.as_view(), name="login"),
    path('logout', UserLogout.as_view(), name="logout"),
    path('signup', UserSignup.as_view(), name="signup"),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('api/shortlink', URLShortenerAPI.as_view()),
    path('api/docs/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('<str:short_code>', GetShortLink.as_view(), name="getshortlink"),
]
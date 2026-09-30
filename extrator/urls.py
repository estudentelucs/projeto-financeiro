from django.urls import path
from . import views

app_name = 'extrator'

urlpatterns = [
    path('', views.index, name='index'),
    path('processar/', views.processar_pdf, name='processar_pdf'),
]

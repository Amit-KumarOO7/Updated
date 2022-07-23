from django.urls import path
from . import views

app_name = 'ca_intermediate'

urlpatterns = [
    path('', views.IndexView.as_view(),name='index'),
    path('caim/',views.RootCAIMView,name='caim'),
    # path('info/<pk>/',views.InfoView,name='info_success')
    
]
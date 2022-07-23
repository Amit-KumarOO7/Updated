from django.urls import path
from . import views

app_name = 'csr_cert'

urlpatterns = [
    path('csr/',views.CSRView,name='csr'),
    path('cssr/',views.CSSRView,name='cssr'),
    path('certChain/<id>',views.getCertChain,name='certChain')
]
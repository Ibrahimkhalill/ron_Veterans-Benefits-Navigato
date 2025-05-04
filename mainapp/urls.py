from django.urls import path
from . import views

urlpatterns = [
    path('vaform/submit/', views.submit_form_api, name='submit_va_form'),
    path('all-vaform/user/', views.va_form_list, name='get_user_va_forms'),
    path('vaform/update-status/<int:form_id>/', views.update_va_form_status, name='update_va_form_status'),
    path('vaform/delete/<int:form_id>/', views.delete_va_form, name='delete_va_form'),
]

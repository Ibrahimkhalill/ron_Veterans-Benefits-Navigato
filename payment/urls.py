# subscriptions/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("create-checkout-session/", views.create_checkout_session, name="create_checkout_session"),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("success/", views.checkout_success, name="checkout_success"),
    path("cancel/", views.checkout_cencel, name="checkout_cancel"),
    path("me/", views.get_subscription, name="get_subscription"),
    path("get_all/subscribtions/", views.get_all_subscription, name="get_all_subscription"),
    path("get_all/subscribtions-plan/", views.get_all_plan, name="get_all_plan"),
    
    # get all calulation for dashboard
    path("get_all/calculate_for_dashboard/", views.calculate_all_for_dashboard, name="calculate_all_for_dashboard"),
    path("get_all/calculate_yearly_revenue/", views.calculate_yearly_revenue, name="calculate_yearly_revenue"),
]

from django.shortcuts import render
from rest_framework import status

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
# Create your views here.
import stripe
from rest_framework.response import Response
from django.http import JsonResponse , HttpResponse
from collections import defaultdict
from datetime import datetime
from .models import Subscription , SubscriptionPlan
from authentications.models import UserProfile, CustomUser
from .serializers import *
from mainapp.models import VaForm
import os
from dotenv import load_dotenv
load_dotenv()
# Set your Stripe secret key
stripe.api_key = os.getenv("API_KEY")

# Webhook secret (get this from your Stripe Dashboard)
endpoint_secret ="whsec_0vI37WvYEqcg3NHTUIPWYxYt0WmQm7dK"



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    # DOMAIN = "https://lamprey-included-lion.ngrok-free.app/api/payment"  # Replace with your actual domain

    # Get the data from the frontend
    price_id = request.data.get("price_id")  # Stripe price ID
    plan_name = request.data.get("plan_name")  # Name of the subscription plan
    duration_type = request.data.get("duration_type")  # Type of the plan (monthly/yearly)

    if not price_id or not plan_name or not duration_type:
        return Response({"error": "Missing price_id, plan_name, or plan_type"}, status=400)

    user = request.user

    try:
        # Create the Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,  # Use dynamic price_id from frontend
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"http://localhost:5173/payment_success/",
            cancel_url=f"http://localhost:5173/payment_cancel",
            metadata={  # Attach metadata to the session
                "user_id": str(user.id),  # Include the user ID for tracking
                "plan_name": plan_name,  # Include the plan name
                "plan_type": duration_type,  # Include the plan type
                "custom_note": "Tracking payment for subscription",
            },
        )

        return Response({"checkout_url": session.url}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

    
    

@api_view(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')


    try:
        # Verify the webhook signature
       event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print(f"Error verifying webhook signature: {str(e)}")
        return Response({"error": "Webhook signature failed"}, status=400)

    # Handle checkout completion (when a subscription is created or updated)
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Retrieve metadata
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        stripe_subscription_id = session.get("subscription")

        if not user_id or not stripe_subscription_id:
            print(f"Missing user_id or subscription_id in metadata: {metadata}")
            return Response({"error": "Missing user_id or subscription_id"}, status=400)

        try:
            user = get_object_or_404(CustomUser, id=user_id)

            # Fetch subscription details from Stripe
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)

            # Access the subscription items and get period data
            subscription_item = stripe_subscription["items"]["data"][0]
            current_period_start = subscription_item.get("current_period_start")
            current_period_end = subscription_item.get("current_period_end")

            # # If current_period_start or current_period_end are missing, return an error or handle appropriately
            if not current_period_start or not current_period_end:
                print(f"Missing subscription period data: {stripe_subscription}")
                return Response({"error": "Missing subscription period information from Stripe"}, status=400)

            # Convert the timestamps to datetime
            current_period_start = datetime.fromtimestamp(current_period_start)
            current_period_end = datetime.fromtimestamp(current_period_end)
            print(f"current_period_start: {current_period_start}, current_period_end: {current_period_end}")

            # Retrieve the plan from the Stripe subscription object
            plan_id = subscription_item["price"]["id"]  # Extract the price ID (plan ID)

            # Fetch the corresponding plan from your SubscriptionPlan model
            subscription_plan = get_object_or_404(SubscriptionPlan, price_id=plan_id)  # Fetch by price_id

            # Update or create the subscription in your database
            try:
                # Try to get the existing subscription
                subscription = Subscription.objects.get(user=user)
                subscription.start_date = current_period_start
                subscription.end_date = current_period_end
                subscription.is_active = True
                subscription.plan = subscription_plan  # Set the plan dynamically
                subscription.price = subscription_plan.amount
                subscription.status = "premium"  # Update status to premium
                subscription.stripe_subscription_id = stripe_subscription_id
                subscription.save()

            except Subscription.DoesNotExist:
                # If no subscription exists for this user, create a new one
                Subscription.objects.create(
                    user=user,
                    plan=subscription_plan,
                    start_date=current_period_start,
                    end_date=current_period_end,
                    is_active=True,
                    price=subscription_plan.amount,
                    status="premium",  # Set status to premium for this new subscription
                    stripe_subscription_id = stripe_subscription_id
                )
                
        except Exception as e:
            print(f"Error processing subscription for user {user_id}: {str(e)}")
            return Response({"error": "Error processing subscription"}, status=400)

    # Handle subscription cancellation or other events
    elif event["type"] == "invoice.payment_failed" or event["type"] == "customer.subscription.deleted":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})

        user_id = metadata.get("user_id")

        if user_id:
            try:
                user = get_object_or_404(CustomUser, id=user_id)

                # Deactivate the subscription if payment failed or subscription was deleted
                subscription = Subscription.objects.get(user=user)
                subscription.is_active = False
                subscription.save()
            except Subscription.DoesNotExist:
                pass

    return Response({"status": "success"}, status=200)

def checkout_success(request):
    return HttpResponse("Your checkout was successful!", status=200)


def checkout_cencel(request):
    return HttpResponse("Your checkout was successful!", status=200)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription(request):
    """
    Retrieve the subscription details for the authenticated user.
    """
    user = request.user
    try:
        # Retrieve subscription for the current user
        subscription = Subscription.objects.get(user=user)
        serializer = SubscriptionSerializer(subscription)
        return Response({"subscription": serializer.data}, status=200)
    except Subscription.DoesNotExist:
        return Response({"message": "No subscription found for this user."}, status=404)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_subscription(request):
    subscriptions = Subscription.objects.select_related('user').all()
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response({"subscriptions": serializer.data}, status=200)


@api_view(['GET'])
def get_all_plan(request):
    plans = SubscriptionPlan.objects.all()
    serializer = SubscriptionPlanSerializer(plans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)






# @background(schedule=60)  # Check every 60 seconds (adjust as needed)
# def check_subscription_status():
#     """
#     Automatically check and deactivate expired free trials or subscriptions.
#     """
#     now = datetime.now()

#     # Check for expired free trials
#     free_trial_expired = Subscription.objects.filter(
#         free_trial=True, free_trial_end__lte=now
#     )
#     for subscription in free_trial_expired:
#         subscription.free_trial = False
#         subscription.save()
#         print(f"Free trial expired for user {subscription.user.username}")

#     # Check for expired subscriptions
#     subscription_expired = Subscription.objects.filter(
#         is_active=True, end_date__lte=now
#     )
#     for subscription in subscription_expired:
#         subscription.is_active = False
#         subscription.save()
#         print(f"Subscription expired for user {subscription.user.username}")

#     print("Checked free trial and subscription statuses.")
    
    

# @api_view(['GET'])

# def get_all_subscription(request):
   
#     # Get or create the user's subscription object
#     subscription = Subscription.objects.all()
#     # Check if the user already has a Stripe customer ID
#     subscription_serializer = SubscriptionSerializer(subscription, many=True)

#     return Response(subscription_serializer.data, status=200)


def get_invoices_by_subscription(subscription_id):
    """
    Fetch all invoices associated with a subscription.
    """
    try:
        invoices = stripe.Invoice.list(subscription=subscription_id)
        return invoices
    except stripe.error.StripeError as e:
        # Handle Stripe API errors
        print(f"Stripe Error: {e}")
        return None


def get_total_revenue_by_subscription(subscription_id):
    """
    Calculate the total revenue for a specific subscription based on paid invoices.
    """
    invoices = get_invoices_by_subscription(subscription_id)
    if not invoices:
        return 0  # Return 0 if the Stripe API call fails

    total_revenue = 0
    for invoice in invoices.auto_paging_iter():
        if invoice.get("paid", False):  # Safely access "paid" to avoid KeyError
            total_revenue += invoice.get("amount_paid", 0) / 100  # Stripe amounts are in cents

    return total_revenue


@api_view(["GET"])
def calculate_all_for_dashboard(request):
    """
    Calculate the revenue for all users and classify them into free and pro users.
    """
    # Step 1: Fetch all Stripe subscriptions
    subscriptions = Subscription.objects.all()
    if not subscriptions:
        return Response({"error": "Failed to fetch subscriptions from Stripe"}, status=500)

    # Step 2: Classify users
    user_count = Subscription.objects.all().count()  # Count active users
    
    va_form_count = VaForm.objects.all().count()  # Count all VA forms
    va_form_submission_app_count = VaForm.objects.filter(status="approved").count()  # Count all VA forms
    # Step 3: Calculate total revenue
    total_revenue = 0
    for subscription in subscriptions:
        if subscription.stripe_subscription_id is not None:
            subscription_revenue = get_total_revenue_by_subscription(subscription.stripe_subscription_id)
            total_revenue += subscription_revenue

    # Step 4: Build response
    response = {
        "total_user": user_count,
        "submission_count": va_form_count,
        "complete_rate": va_form_submission_app_count,
        "total_revenue": round(total_revenue, 2),  # Ensure total revenue is rounded to 2 decimal places
    }

    return Response(response, status=200)


@api_view(["GET"])
def calculate_yearly_revenue(request):
    """
    Calculate monthly revenue starting from the first subscription year to the current year.
    """
    # Step 1: Fetch all subscriptions from the database
    subscriptions = Subscription.objects.all()
    form_submissions = VaForm.objects.all()
    if not subscriptions:
        return Response({"error": "No subscriptions found"}, status=404)

    # Step 2: Calculate revenue grouped by year and month
    yearly_monthly_revenue = defaultdict(lambda: {month: 0 for month in range(1, 13)})  # Year -> Month -> Revenue
    yearly_monthly_submissions = defaultdict(lambda: {month: 0 for month in range(1, 13)})  # Year -> Month -> Submission Count
    first_year = datetime.now().year  # Initialize with the current year
    for subscription in subscriptions:
        if subscription.stripe_subscription_id is not None:
            invoices = get_invoices_by_subscription(subscription.stripe_subscription_id)
            if not invoices:
                continue

            for invoice in invoices.auto_paging_iter():
                if invoice.get("paid", False):  # Only consider paid invoices
                    created_date = datetime.fromtimestamp(invoice["created"])
                    year = created_date.year
                    month = created_date.month
                    yearly_monthly_revenue[year][month] += invoice.get("amount_paid", 0) / 100  # Convert cents to dollars
                    first_year = min(first_year, year)  # Update the first year if earlier

    # Step 3: Prepare data from the first year to the current year
    current_year = datetime.now().year
    for submission in form_submissions:
        year = submission.submission_date.year
        month = submission.submission_date.month
        yearly_monthly_submissions[year][month] += 1  # Increment submission count
        first_year = min(first_year, year)  # Update first year if earlier
        
        
        
    all_revenue_data = []
    
    all_submission_data = []

    submission_data = [yearly_monthly_submissions[year].get(month, 0) for month in range(1, 13)]
    all_submission_data.append({
            "year": year,
            "data": submission_data,  # Monthly revenue
           
        })
    
    for year in range(first_year, current_year + 1):
        data = [yearly_monthly_revenue[year].get(month, 0) for month in range(1, 13)]
        all_revenue_data.append({
            "year": year,
            "data": data
        })

    # Step 4: Build response
    response = {
        "all_revenue_data": all_revenue_data,
        "all_submission_data": all_submission_data
    }

    return Response(response, status=200)
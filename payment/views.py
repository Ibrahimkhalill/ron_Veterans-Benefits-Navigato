from django.shortcuts import render

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
from .models import Subscription
from authentications.models import UserProfile, CustomUser
from authentications.serializers import SubscriptionSerializer


# Set your Stripe secret key
stripe.api_key = ""

# Webhook secret (get this from your Stripe Dashboard)
endpoint_secret = ''



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    DOMAIN = "https://polite-engaging-mongrel.ngrok-free.app/api/payment"  # Replace with your actual domain
    # price_id = request.data.get("price_id")  # Stripe price ID

    user = request.user

    try:
        # Create the Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": "price_1RECRbALRymUd61p9Rcw4OzL",
                    "quantity": 1,
                }
            ],
            mode="subscription",
           
            success_url=f"{DOMAIN}/success/",
            cancel_url=f"{DOMAIN}/cancel/",
            metadata={  # Attach metadata to the session
                "user_id": str(user.id),  # Include the user ID for tracking
                "custom_note": "Tracking payment for subscription",
            },
        )

        return Response({"checkout_url": session.url}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


    
    
@api_view(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
   

    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return Response({"error": "Webhook signature failed"}, status=400)

    # Handle checkout completion (when a subscription is created)
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Retrieve customer and subscription ID
        metadata = session.get("metadata", {})

     
        user_id = metadata.get("user_id")
        stripe_subscription_id = session.get("subscription")
        user = get_object_or_404(CustomUser, id=user_id)

        # Fetch subscription details from Stripe
        stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)

        # Extract start and end dates
        current_period_start = datetime.fromtimestamp(stripe_subscription["current_period_start"])
        current_period_end = datetime.fromtimestamp(stripe_subscription["current_period_end"])

        # Update your Subscription model
        try:
            subscription = Subscription.objects.get(user=user)
            subscription.start_date = current_period_start
            subscription.end_date = current_period_end
            subscription.is_active = True
            subscription.plan = "premium"
            subscription.save()
            
        except Subscription.DoesNotExist:
            print("Subscription for customer not found")



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


# def get_invoices_by_subscription(subscription_id):
#     """
#     Fetch all invoices associated with a subscription.
#     """
#     try:
#         invoices = stripe.Invoice.list(subscription=subscription_id)
#         return invoices
#     except stripe.error.StripeError as e:
#         # Handle Stripe API errors
#         print(f"Stripe Error: {e}")
#         return None


# def get_total_revenue_by_subscription(subscription_id):
#     """
#     Calculate the total revenue for a specific subscription based on paid invoices.
#     """
#     invoices = get_invoices_by_subscription(subscription_id)
#     if not invoices:
#         return 0  # Return 0 if the Stripe API call fails

#     total_revenue = 0
#     for invoice in invoices.auto_paging_iter():
#         if invoice.get("paid", False):  # Safely access "paid" to avoid KeyError
#             total_revenue += invoice.get("amount_paid", 0) / 100  # Stripe amounts are in cents

#     return total_revenue


# @api_view(["GET"])
# def calculate_all_for_dashboard(request):
#     """
#     Calculate the revenue for all users and classify them into free and pro users.
#     """
#     # Step 1: Fetch all Stripe subscriptions
#     subscriptions = Subscription.objects.all()
#     if not subscriptions:
#         return Response({"error": "Failed to fetch subscriptions from Stripe"}, status=500)

#     # Step 2: Classify users
#     pro_user_count = Subscription.objects.filter(is_active=True).count()  # Count active users
#     free_user_count = Subscription.objects.filter(free_trial_end__isnull=False).count()

#     # Step 3: Calculate total revenue
#     total_revenue = 0
#     for subscription in subscriptions:
#         if subscription.stripe_subscription_id is not None:
#             subscription_revenue = get_total_revenue_by_subscription(subscription.stripe_subscription_id)
#             total_revenue += subscription_revenue

#     # Step 4: Build response
#     response = {
#         "free_user": free_user_count,
#         "pro_user": pro_user_count,
#         "total_revenue": round(total_revenue, 2),  # Ensure total revenue is rounded to 2 decimal places
#     }

#     return Response(response, status=200)


# @api_view(["GET"])
# def calculate_yearly_revenue(request):
#     """
#     Calculate monthly revenue starting from the first subscription year to the current year.
#     """
#     # Step 1: Fetch all subscriptions from the database
#     subscriptions = Subscription.objects.all()
#     if not subscriptions:
#         return Response({"error": "No subscriptions found"}, status=404)

#     # Step 2: Calculate revenue grouped by year and month
#     yearly_monthly_revenue = defaultdict(lambda: {month: 0 for month in range(1, 13)})  # Year -> Month -> Revenue

#     first_year = datetime.now().year  # Initialize with the current year
#     for subscription in subscriptions:
#         if subscription.stripe_subscription_id is not None:
#             invoices = get_invoices_by_subscription(subscription.stripe_subscription_id)
#             if not invoices:
#                 continue

#             for invoice in invoices.auto_paging_iter():
#                 if invoice.get("paid", False):  # Only consider paid invoices
#                     created_date = datetime.fromtimestamp(invoice["created"])
#                     year = created_date.year
#                     month = created_date.month
#                     yearly_monthly_revenue[year][month] += invoice.get("amount_paid", 0) / 100  # Convert cents to dollars
#                     first_year = min(first_year, year)  # Update the first year if earlier

#     # Step 3: Prepare data from the first year to the current year
#     current_year = datetime.now().year
#     all_revenue_data = []

#     for year in range(first_year, current_year + 1):
#         data = [yearly_monthly_revenue[year].get(month, 0) for month in range(1, 13)]
#         all_revenue_data.append({
#             "year": year,
#             "data": data
#         })

#     # Step 4: Build response
#     response = {
#         "all_revenue_data": all_revenue_data
#     }

#     return Response(response, status=200)
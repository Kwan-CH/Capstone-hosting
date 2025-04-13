from django.urls import path
from .views import *
#from .views import reward_points, recent_activity, profile

app_name = 'customer'

urlpatterns = [
    path('', homepage_customer, name='homepage-customer'), #Customer Homepage

    path('schedule_pickup/', schedule_pickup, name='schedule_pickup'), #Schedule Pickup
    path('redeem_rewards/', redeem_rewards_page, name='redeem_rewards_page'), #Reward Points page
    path('redeem_rewards/redeem_voucher/', redeem_voucher, name='redeem_rewards/redeem_voucher/'), #Redeem voucher function
    path('pickup_status/', pickup_status, name='pickup_status'), #Pickup Status

    path('user_profile/', user_profile, name='user_profile'), #Customer Profile
    path('edit_profile/', edit_profile, name='edit_profile'), # Edit customer profile
    path('edit_password/', edit_password, name='edit_password'), # Edit customer password

    path('waste_category/', waste_category, name='waste_category'), #Waste category page

    path('history_all/', history_all, name='history_all'), #Activity History
    path('history-device/', device_recycled, name='device_recycled'), #Activity History - Recycled Device
    path('history-voucher/', voucher_redeemed, name='voucher_redeemed'),  # Activity History - Voucher Redeemed


]
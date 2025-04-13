from django.urls import path
from .views import *

app_name = 'driver'
urlpatterns = [
    path('', homepage_driver, name='homepage-driver'),
    path('pickup_details/', pickup_details, name='pickup_details'), #Pickup Details
    path('update_pickup_status/<str:requestID>/', update_pickup_status, name='update_pickup_status'), #Update Pickup Status
    path('complete_pickup/', complete_pickup, name='complete_pickup'), #Complete Pickup
    path('update_complete_status/', update_complete_status, name='update_complete_status'), #Update Complete Pickup Status
    path('pickup_history/', pickup_history, name='pickup_history'), #Pickup History

    #------------------------Profile---------------------------------------
    path('user_profile/', user_profile, name='user_profile'), #Driver Profile
    path('edit_profile/', edit_profile, name='edit_profile'), #Edit customer profile
    path('edit_password/', edit_password, name='edit_password'), #Change password
]
from django.urls import path
from .views import *



app_name = 'operator'

urlpatterns = [
     path('', homepage_operator, name='homepage-operator'), #Operator Homepage

     path('create-driver-acc/', operator_create_acc_page, name='create_acc'),#Create Driver Account
     path('save_driver_account', save_driver_account, name='save_account'), #Save account

     path('manageReq/', manageReq, name='manageReq'), #Manage Requests
     path('manageReq/assign_driver_page/', assign_driver_page, name='manageReq/assign_driver_page/'), #Assign driver page
     path('manageReq/assign_driver_page/assign_driver/', assign_driver, name='manageReq/assign_driver_page/assign_driver/'), # Assign driver
     path('manageReq/reject_request/', reject_request, name='manageReq/reject_request/'), #Reject request

     path('reward_system/', reward_system, name='reward_system'), #Reward System
     path('add_reward/', add_reward, name='add_reward'), #Add Reward
     path('edit_reward/<str:voucherID>/', edit_reward, name='edit_reward'), #Edit Reward
     path('completed_request/', completed_request, name='completed_request')#Add Reward
]
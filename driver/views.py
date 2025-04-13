from django.shortcuts import render, redirect, get_object_or_404
from database.models import Driver, ScheduleRequest, PickedUpRequest, CompletedRequest, Customer
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import CharField, Value, When, Case
from django.db.models.functions import Concat
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
import re
from utilities.state_data import getState

import os
from dotenv import load_dotenv

load_dotenv()


states=getState.getState()

excluded_states = ["Kuala Lumpur", "Putrajaya", "Labuan"]

def homepage_driver(request):
    driverID = request.session.get("user_id")  # Get logged-in user's ID
    if not driverID:
        return redirect('customer:login')  # Redirect to login if not authenticated

    userInfo = Driver.objects.only('profile_picture').get(driverID=driverID) # Get user profile data

    return render(request, "driver/homepage-driver.html", {"profile": userInfo})

def pickup_details(request):
    driverID = request.session.get("user_id")
    # pickups = (ScheduleRequest.objects
    #            .annotate(address=Concat('street', Value(', '), 'postalCode',
    #                                     Value(', '), 'area', Value(', '), 'state', output_field=CharField()))
    #            .filter(driver_id=driverID, status="Approved").order_by('date', 'time')) # Get user profile data#Sort by closest date and time

    #Use use case for address formatting
    pickups = (
    ScheduleRequest.objects
    .annotate(
        address=Case(
            When(state__in=excluded_states,
                 then=Concat(
                     'street', Value(', '),
                     'postalCode', Value(', '),
                     'state',
                     output_field=CharField()
                 )),
            default=Concat(
                'street', Value(', '),
                'postalCode', Value(', '),
                'area', Value(', '),
                'state',
                output_field=CharField()
            ),
            output_field=CharField()
        )
    )
    .filter(driver_id=driverID, status="Approved")
    .order_by('date', 'time')  # Sort by closest date and time
    )

    userInfo = Driver.objects.only('profile_picture').get(driverID=driverID)
    return render(request, 'driver/pickupDetails.html', {'pickups': pickups, "profile": userInfo})

@require_POST
def update_pickup_status(request, requestID):
    try:
        pickUpRequest = ScheduleRequest.objects.get(requestID=requestID)
        pickUpRequest.status = "Picked Up"
        pickUpRequest.save()

        customer = Customer.objects.get(customerID=pickUpRequest.customer.customerID)
        customer.points += (pickUpRequest.category.pointsGiven * pickUpRequest.quantity)
        customer.save()

        PickedUpRequest.objects.create(requestID=pickUpRequest)

        messages.success(request, f"Pickup request {requestID} has been updated successfully!")
        return JsonResponse({'status': 'success'})
    except ScheduleRequest.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pickup not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def complete_pickup(request):
    driverID = request.session.get("user_id")
    # pickups = (ScheduleRequest.objects
    #            .annotate(address=Concat('street', Value(', '), 'postalCode',
    #                                     Value(', '), 'area', Value(', '), 'state', output_field=CharField()))
    #            .filter(driver_id=driverID, status="Picked Up").order_by('-date', '-time')) #Sort by closest date and time

    #Use use case for address formatting
    pickups = (
    ScheduleRequest.objects
    .annotate(
        address=Case(
            When(state__in=excluded_states,
                 then=Concat(
                     'street', Value(', '),
                     'postalCode', Value(', '),
                     'state',
                     output_field=CharField()
                 )),
            default=Concat(
                'street', Value(', '),
                'postalCode', Value(', '),
                'area', Value(', '),
                'state',
                output_field=CharField()
            ),
            output_field=CharField()
        )
    )
    .filter(driver_id=driverID, status="Picked Up")
    .order_by('-date', '-time')  # Sort by most recent pickups
    )

    userInfo = Driver.objects.only('profile_picture').get(driverID=driverID)
    return render(request, 'driver/completePick.html', {'pickups': pickups, "profile": userInfo})

@csrf_protect  # Allow AJAX to send requests
def update_complete_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            request_ids = data.get("request_ids", [])  # Get request IDs from AJAX

            if not request_ids:
                return JsonResponse({"success": False, "error": "No requests selected."}, status=400)

            # Update the status of selected requests
            requests_to_complete = ScheduleRequest.objects.filter(requestID__in=request_ids)
            requests_to_complete.update(status="Completed")
            for request in requests_to_complete:
                CompletedRequest.objects.get_or_create(requestID=request)

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

def pickup_history(request):
    driverID = request.session.get("user_id")
    # pickups = (ScheduleRequest.objects
    #            .annotate(address=Concat('street', Value(', '), 'postalCode',
    #                                     Value(', '), 'area', Value(', '), 'state', output_field=CharField()))
    #            .filter(driver_id=driverID, status="Completed").order_by('-date', '-time')) #Sort by closest date and time

    #Use use case for address formatting
    pickups = (
    ScheduleRequest.objects
    .annotate(
        address=Case(
            When(state__in=excluded_states,
                 then=Concat(
                     'street', Value(', '),
                     'postalCode', Value(', '),
                     'state',
                     output_field=CharField()
                 )),
            default=Concat(
                'street', Value(', '),
                'postalCode', Value(', '),
                'area', Value(', '),
                'state',
                output_field=CharField()
            ),
            output_field=CharField()
        )
    )
    .filter(driver_id=driverID, status="Completed")
    .order_by('-date', '-time')  # Sort by most recent pickups
)
    
    userInfo = Driver.objects.only('profile_picture').get(driverID=driverID)
    return render(request, 'driver/pickupHis.html', {"pickups": pickups, "profile": userInfo})


def user_profile(request):
    driverID = request.session.get("user_id")
    userInfo = Driver.objects.get(driverID=driverID)

    if request.method == 'POST' and request.FILES.get('profile_picture'):
        driverID = request.session.get("user_id")  # Get logged-in user
        userInfo = Driver.objects.get(driverID=driverID)
        

        # ✅ Only delete old picture IF a new one is uploaded
        if userInfo.profile_picture and userInfo.profile_picture.name != "profile_pics/default.jpg":
            userInfo.profile_picture.delete(save=False)

        # ✅ Save the new profile picture
        userInfo.profile_picture = request.FILES['profile_picture']
        userInfo.save()

        return JsonResponse({
            'new_profile_picture_url': userInfo.profile_picture.url
        })

    return render(request, "driver/userprofile-driver.html", {"profile": userInfo})


def edit_profile(request):
    driverID = request.session.get("user_id")
    userInfo = Driver.objects.get(driverID=driverID)

    if request.method == 'POST':
        new_name = request.POST.get('fullname')
        new_email = request.POST.get('email')
        new_phoneNumber = request.POST.get('contact_number')
        new_carplate = request.POST.get('carplatenumber')
        new_state = request.POST.get('state')
        new_area = request.POST.get('area')
        new_profile_pic = request.FILES.get("profile_picture")

        # Check if any field is empty
        if not new_name or not new_email or not new_phoneNumber or not new_carplate or not new_state :
            return render(request, 'driver/edituserprofile-driver.html', {
                'Invalid': True,
                'error_message': "All fields must be filled",
                'profile': userInfo,  # Pass back the profile details and state selection
                'states': states,
                "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        # Validate email
        if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$", new_email):
             return render(request, "driver/edituserprofile-driver.html", {
                "profile": userInfo,
                "Invalid": True,
                "states" : states,
                "error_message": "Invalid email format. Please enter a valid email.",
                 "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        # Validate Phone Number
        if not new_phoneNumber.isdigit() or not new_phoneNumber.startswith("01") or len(new_phoneNumber) not in [10,11]:
            return render(request, "driver/edituserprofile-driver.html", {
            "profile": userInfo,
            "phone_error": True,
            "states" : states,
            "API_KEY": os.getenv('GET_STATE_AREA_API')
        })

        # if Validate passes only update userinfo
        userInfo.name = new_name
        userInfo.email = new_email
        userInfo.phoneNumber = new_phoneNumber
        userInfo.plateNumber = new_carplate
        userInfo.stateCovered = new_state
        userInfo.areaCovered = new_area

        # ✅ Handle Profile Picture Update
        if new_profile_pic:
            # 🗑️ Delete old profile picture (if it's not the default)
            if userInfo.profile_picture and userInfo.profile_picture.name != "profile_pics/default.jpg":
                userInfo.profile_picture.delete(save=False)

            # 📸 Save new profile picture
            userInfo.profile_picture = new_profile_pic

        # ✅ Save updates
        userInfo.save()

        # update the corresponding data
        userInfo.save()
        return render(request, "driver/edituserprofile-driver.html", {
            "profile": userInfo,
            "update_success": True,
            "API_KEY": os.getenv('GET_STATE_AREA_API')
        })

    # reason to create a list at here, is to populate the option field while being able to set selected category
    return render(request, "driver/edituserprofile-driver.html", {
        "profile": userInfo,
        "states": states,
        "API_KEY": os.getenv('GET_STATE_AREA_API')
    })

#function for getting user address
def get_user_address(request):
    # Get the user_id from session
    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        # Fetch driver using session user_id
        driver = Driver.objects.get(driverID=user_id)
        return JsonResponse({"address": driver.address})
    except Driver.DoesNotExist:
        return JsonResponse({"error": "Address not found"}, status=404)



def edit_password(request):
    driverID = request.session.get("user_id")
    driver = Driver.objects.get(driverID=driverID)
    if request.method == "POST":
        current_password_input = request.POST['currentPassword']
        new_password = request.POST['newPassword']
        confirm_password = request.POST['confirmPassword']

        #Check if all field is entered
        if not current_password_input or not new_password or not confirm_password:
            return render(request, 'driver/editpassword-driver.html', {
                'Invalid': True,
                'error_message': "All fields must be filled"
            })

         # Check if the current password matches
        if driver.password != current_password_input:
            return render(request, 'driver/editpassword-driver.html', {
                'Invalid': True,
                'error_message': "Current password is incorrect"
            })

         # Check if new password matches confirm password
        if new_password != confirm_password:
            return render(request, 'driver/editpassword-driver.html', {
                'Invalid': True,
                'error_message': "New password and confirm password do not match"
            })

       
        # Then check if the password length is atleast 8 char
        if len(new_password) < 8:
            # messages.error(request, "Password must be at least 8 characters long")
            return render(request, 'driver/editpassword-driver.html',  {'Invalid': True, 'error_message': "Password must be at least 8 characters long"})


  # If all checks pass, update the password
        Driver.objects.filter(driverID=driverID).update(password=new_password)
        messages.success(request, "Password has been changed successfully")

        return render(request, "driver/editpassword-driver.html", {
            "profile": driver,
            "update_success": True
        })

    return render(request, 'driver/editpassword-driver.html', {"profile": driver})



def logout(request):
    request.session.flush()
    return redirect('e_waste: landing')

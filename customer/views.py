from django.contrib.admin.templatetags.admin_list import pagination
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from database.models import Customer, ScheduleRequest, ItemCategory, CustomerRedemption, Voucher
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db.models import CharField, Value, Case, When
from django.db.models.functions import Concat
from itertools import chain
from django.core.paginator import Paginator
import json, re
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils.timezone import now
from utilities.state_data import getState

import os
from dotenv import load_dotenv


load_dotenv()

states=getState.getState()

# states for dont have areas
excluded_states = ['Kuala Lumpur', 'Putrajaya', 'Labuan']


def homepage_customer(request):
    customerID = request.session.get("user_id")  # Get logged-in user's ID
    if not customerID:
        return redirect('customer:login')  # Redirect to login if not authenticated

    userInfo = Customer.objects.only('profile_picture').get(customerID=customerID)  # Get user profile data

    return render(request, "customer/homepage-customer.html", {"profile": userInfo})


@login_required
def pickup_status(request):
    customer_id = request.session.get('user_id')
    userInfo = Customer.objects.only('profile_picture').get(customerID=customer_id)  # Get user profile data
    if not customer_id:
        return redirect('login')

    # Get yesterday's date (24 hours ago)
    yesterday = now().date() - timedelta(days=1)

    # Filter requests that are NOT rejected and either:
    # - Have no completed request
    # - Have a completed request within the last 24 hours
    pickUpRequest = ScheduleRequest.objects.filter(
        customer__customerID=customer_id
    ).exclude(
        status="Rejected"
    ).exclude(
        completed_requests__completed_date__lt=yesterday  # Exclude if completed > 24 hours ago
    ).order_by('-trackingnumber')

    # pickUpRequest = ScheduleRequest.objects.filter(customer__customerID=customer_id).exclude(status="Rejected").order_by('-trackingnumber')

    pagination = Paginator(pickUpRequest, 5)
    page = request.GET.get('page')

    deliveries = pagination.get_page(page)

    if not deliveries.object_list:
        return render(request, 'customer/pickupStatus.html', {'Empty': True, "profile": userInfo})

    return render(request, 'customer/pickupStatus.html', {'deliveries': deliveries, "profile": userInfo})

@login_required
def schedule_pickup(request):
    customer_id = request.session.get("user_id")

    userInfo = Customer.objects.only('profile_picture').get(customerID=customer_id)  # Get user profile data
    if request.method == 'POST':
        category_id = request.POST.get('waste_type')
        quantity = request.POST.get('quantity_items').strip()
        weight = request.POST.get('quantity_weight')
        street = request.POST.get('street')
        # address = request.POST.get('street') #naming purpose
        postalCode = request.POST.get('postal_code')
        area = request.POST.get('area')
        stateSelected = request.POST.get('state')
        pickup_date = request.POST.get('pickup_date')
        pickup_time = request.POST.get('pickup_time')

        # Make Sure all fields are not empty
        required_fields = {
            'Waste Type': category_id,
            # 'Quantity': quantity,
            'Weight': weight,
            'Address': street,
            'State': stateSelected,
            'Postal Code': postalCode,
            # 'Area': area,
            'Pickup Date': pickup_date,
            'Pickup Time': pickup_time,
        }

        for field_name, value in required_fields.items():
            if not value:
                return render(request, 'customer/schedulePick.html', {
                    'categories': ItemCategory.objects.all(),
                    "profile": userInfo,
                    'submitted': False,
                    'states': states,
                    'error': f'{field_name} is required!',
                    "API_KEY": os.getenv('GET_STATE_AREA_API')
                })

        # 3. Special condition: If state is NOT Kuala Lumpur, Area is required
        excluded_states = ["Kuala Lumpur", "Putrajaya", "Labuan"]
        if stateSelected not in excluded_states and not area:
            return render(request, 'customer/schedulePick.html', {
                'categories': ItemCategory.objects.all(),
                "profile": userInfo,
                'submitted': False,
                'states': states,
                'error': 'Area is required for selected state!',
                "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        # Get the logged-in user
        if not customer_id:
            return redirect("login")  # Redirect to login if session expired

        #Validate Quantity
        # if not quantity:  # Check if quantity is provided
        #     return render(request, 'customer/schedulePick.html', {
        #         'categories': ItemCategory.objects.all(),
        #         "profile": userInfo,
        #         'submitted': False,  # Ensures no undefined variable usage
        #         'states': states,
        #         'error': 'Please enter quantity!',
        #         "API_KEY": os.getenv('GET_STATE_AREA_API')
        #     })

        if not quantity.isdigit() or not quantity:
            return render(request, 'customer/schedulePick.html', {
                'categories': ItemCategory.objects.all(),
                "profile": userInfo,
                'submitted': False,  # Ensures no undefined variable usage
                'states': states,
                'error': 'Please enter digits only for quantity!',
                "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        #Validate Postal Codes
        # if not len(postalCode) != 5:
        #     return render(request, 'customer/schedulePick.html', {
        #                 'categories': ItemCategory.objects.all(),
        #                 "profile": userInfo,
        #                 'submitted': False,  # Ensures no undefined variable usage
        #                 'states': states,
        #                 'error': 'Postal code should have 5 digits',
        #                 "API_KEY": os.getenv('GET_STATE_AREA_API')
        #             })
        # elif not postalCode.isdigit():
        #     print('posatl code  not digit')
        #     return render(request, 'customer/schedulePick.html', {
        #                 'categories': ItemCategory.objects.all(),
        #                 "profile": userInfo,
        #                 'submitted': False,  # Ensures no undefined variable usage
        #                 'states': states,
        #                 'error': 'Please enter digits only for postal code!',
        #                 "API_KEY": os.getenv('GET_STATE_AREA_API')
        #             })

        if not postalCode.isdigit() or len(postalCode) != 5 :
            return render(request, 'customer/schedulePick.html', {
                        'categories': ItemCategory.objects.all(),
                        "profile": userInfo,
                        'submitted': False,  # Ensures no undefined variable usage
                        'states': states,
                        'error': 'Please enter 5 digits only for postal code!',
                        "API_KEY": os.getenv('GET_STATE_AREA_API')
                    })

        try:
            customer = Customer.objects.get(customerID=customer_id)  # Fetch customer object
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found!")
            return redirect("login")

        try:
            category = ItemCategory.objects.get(categoryID=category_id)
        except ItemCategory.DoesNotExist:
            messages.error(request, "Invalid category selected.")
            return redirect('customer:schedule_pickup')

        # Create a new PickupRequest
        pickup_request = ScheduleRequest(
            customer=customer,
            category=category,
            quantity=quantity,
            weight=weight,
            street=street,
            postalCode=postalCode,
            area=area,
            state=stateSelected,
            date=pickup_date,
            time=pickup_time,
            status="Pending",
            driver=None,  # Driver will be assigned later
            operator=None  # Operator will be assigned later
        )
        pickup_request.trackingnumber = pickup_request.generate_tracking_number()
        print(pickup_request)
        pickup_request.save()

        tracking_number = pickup_request.trackingnumber  # Store tracking number

        messages.success(request, 'Pickup request submitted successfully!')
        # return redirect('customer:schedulePick.html')

        return render(request, 'customer/schedulePick.html', {
            'categories': ItemCategory.objects.all(),
            'submitted': True,
            'tracking_number': tracking_number,
            "profile": customer,
            'states':states,
            "API_KEY":os.getenv('GET_STATE_AREA_API')
        })

    # Handle GET request

    return render(request, 'customer/schedulePick.html', {
        'categories': ItemCategory.objects.all(),
        "profile": userInfo,
        'submitted': False,  # Ensures no undefined variable usage
        'states': states,
        "API_KEY": os.getenv('GET_STATE_AREA_API')
    })

def user_profile(request):
    customerID = request.session.get("user_id")
    # userInfo = (Customer.objects
    #             .annotate(address=Concat('street', Value(', '), 'postalCode',
    #                                      Value(', '), 'area', Value(', '), 'state', output_field=CharField()))
    #             .get(customerID=customerID))

    #Use Case to handle address formatting based on state [KL, Putrajaya, Labuan]
    userInfo = (
    Customer.objects
    .annotate(
        address=Case(
            When(state__in=excluded_states,
                 then=Concat('street', Value(', '), 'postalCode', Value(', '), 'state', output_field=CharField())),
            default=Concat('street', Value(', '), 'postalCode', Value(', '), 'area', Value(', '), 'state', output_field=CharField()),
            output_field=CharField()
        )
    )
    .get(customerID=customerID)
    )

    if request.method == 'POST' and request.FILES.get('profile_picture'):
        customerID = request.session.get("user_id")  # Get logged-in user
        userInfo = Customer.objects.get(customerID=customerID)

        # ✅ Only delete old picture IF a new one is uploaded
        if userInfo.profile_picture and userInfo.profile_picture.name != "profile_pics/default.jpg":
            userInfo.profile_picture.delete(save=False)

        # ✅ Save the new profile picture
        userInfo.profile_picture = request.FILES['profile_picture']
        userInfo.save()

        return JsonResponse({
            'new_profile_picture_url': userInfo.profile_picture.url
        })

    return render(request, "customer/userprofile-customer.html", {"profile": userInfo})

def edit_profile(request):
    customerID = request.session.get("user_id")
    userInfo = Customer.objects.get(customerID=customerID)

    if request.method == 'POST':
        new_name = request.POST.get('fullname')
        new_email = request.POST.get('email')
        new_phoneNumber = request.POST.get('contact_number')
        new_street = request.POST.get('street')
        new_postalCode = request.POST.get('postal_code')
        new_area = request.POST.get('area')
        new_state = request.POST.get('state')
        new_profile_pic = request.FILES.get("profile_picture")

        excluded_states = ["Kuala Lumpur", "Putrajaya", "Labuan"]

        # Check if any field is empty
        if (not new_name or not new_email or not new_phoneNumber or not new_street
                or not new_postalCode or not new_state) :
            return render(request, 'customer/edituserprofile-customer.html', {
                'Invalid': True,
                'error_message': "All fields must be filled",
                'profile': userInfo,  # Pass back the profile details and state selection
                'states': states,
                "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        # Validate email
        elif not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$", new_email):
             return render(request, "customer/edituserprofile-customer.html", {
                "profile": userInfo,
                "Invalid": True,
                "error_message": "Invalid email format. Please enter a valid email.",
                 'states': states,
                 "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        # Validate Phone Number
        elif not new_phoneNumber.isdigit() or not new_phoneNumber.startswith("01") or len(new_phoneNumber) not in [10,11]:
            return render(request, "customer/edituserprofile-customer.html", {
                "profile": userInfo,
                "phone_error": True,
                "states" : states,
                "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        elif new_state not in excluded_states and not new_area:
            return render(request, 'customer/edituserprofile-customer.html', {
                "profile": userInfo,
                "error_message": 'Please fill in the State and Area',
                "Invalid": True,
                "states" : states,
                "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        elif not new_postalCode.isdigit() or len(new_postalCode) != 5 :
            return render(request, "customer/edituserprofile-customer.html", {
                "profile": userInfo,
                "error_message": 'Please enter only 5 digits for postal code',
                "Invalid": True,
                "states" : states,
                "API_KEY": os.getenv('GET_STATE_AREA_API')
            })

        # elif len(new_postalCode) != 5 :
        #     return render(request, "customer/edituserprofile-customer.html", {
        #         "profile": userInfo,
        #         "error_message": 'Postal Code should have 5 digits',
        #         "Invalid": True,
        #         "states" : states,
        #         "API_KEY": os.getenv('GET_STATE_AREA_API')
        #     })


        # if Validate passes only update userinfo
        userInfo.name = new_name
        userInfo.email = new_email
        userInfo.phoneNumber = new_phoneNumber
        print("new_phoneNumber: ", new_phoneNumber)
        userInfo.street = new_street
        userInfo.postalCode = new_postalCode
        userInfo.area = new_area
        userInfo.state = new_state

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
        return render(request, "customer/edituserprofile-customer.html", {
            "profile": userInfo,
            "update_success": True,
            "API_KEY": os.getenv('GET_STATE_AREA_API')
        })

    # reason to create a list at here, is to populate the option field while being able to set selected category
    return render(request, "customer/edituserprofile-customer.html", {
        "profile": userInfo,
        "states": states,
        "API_KEY": os.getenv('GET_STATE_AREA_API')
    })



def edit_password(request):
    customerID = request.session.get("user_id")
    customer = Customer.objects.get(customerID=customerID)
    if request.method == "POST":
        current_password_input = request.POST['currentPassword']
        new_password = request.POST['newPassword']
        confirm_password = request.POST['confirmPassword']

        #Check if all field is entered
        if not current_password_input or not new_password or not confirm_password:
            return render(request, 'customer/editpassword-customer.html', {
                'Invalid': True,
                'error_message': "All fields must be filled",
                'profile': customer
            })

         # Check if the current password matches
        if customer.password != current_password_input:
            return render(request, 'customer/editpassword-customer.html', {
                'Invalid': True,
                'error_message': "Current password is incorrect",
                'profile': customer
            })

         # Check if new password matches confirm password
        if new_password != confirm_password:
            return render(request, 'customer/editpassword-customer.html', {
                'Invalid': True,
                'error_message': "New password and confirm password do not match",
                'profile': customer
            })

        #---------OLD-VERSION------
        # if customer.password == current_password_input and new_password == confirm_password:
        #     Customer.objects.filter(customerID=customerID).update(password=new_password)
        #     # messages.success(request, "Password has been changed successfully")
        #     return render(request, "customer/userprofile-customer.html", {"profile": customer, "update_success": True})

        # Then check if the password length is atleast 8 char
        if len(new_password) < 8:
            # messages.error(request, "Password must be at least 8 characters long")
            return render(request, 'customer/editpassword-customer.html', {
                'Invalid': True,
                'error_message': "Password must be at least 8 characters long",
                'profile': customer})


  # If all checks pass, update the password
        Customer.objects.filter(customerID=customerID).update(password=new_password)
        messages.success(request, "Password has been changed successfully")
        return render(request, "customer/editpassword-customer.html", {
            "profile": customer,
            "update_success": True
        })

        # messages.error(request, "Password does not match or is incorrect")
        # return render(request, 'customer/editpassword-customer.html', {'Invalid': True})

    return render(request, 'customer/editpassword-customer.html', {"profile": customer})


def waste_category(request):
    customerID = request.session.get('user_id')
    userInfo = Customer.objects.only('profile_picture').get(customerID=customerID)  # Get user profile data
    return render(request, 'customer/wasteCategory.html', {"profile": userInfo})

def history_all(request):
    customerID = request.session.get('user_id')
    userInfo = Customer.objects.only('profile_picture').get(customerID=customerID)  # Get user profile data
    # Get device recycling history
    # device_history = (ScheduleRequest.objects.filter(
    #                     # ~Q(status='Pending'),
    #                     Q(status='Completed') | Q(status='Rejected'),
    #                     customer__customerID=customerID)
    #                   .select_related('category')
    #                   .values('trackingnumber', 'category__itemType', 'date', 'quantity', 'status', 'rejectedReason__reason')
    #                   .annotate(total=F('quantity') * F('category__pointsGiven'))
    #                   .annotate(address=Concat('street', Value(', '), 'postalCode',
    #                                            Value(', '), 'area', Value(', '), 'state', output_field=CharField()))
    #                   .order_by('-date', '-time')  # Sort by date (latest first)
    #                   )

    # Use use case for address formatting
    device_history = (ScheduleRequest.objects.filter(
                    # ~Q(status='Pending'),
                    Q(status='Completed') | Q(status='Rejected'),
                    customer__customerID=customerID)
                    .select_related('category')
                    .values('trackingnumber', 'category__itemType', 'date', 'quantity', 'status', 'rejectedReason__reason')
                    .annotate(
                        total=F('quantity') * F('category__pointsGiven'),
                        address=Case(
                            When(
                                state__in=excluded_states,
                                then=Concat('street', Value(', '), 'postalCode', Value(', '), 'state', output_field=CharField())
                            ),
                            default=Concat('street', Value(', '), 'postalCode', Value(', '), 'area', Value(', '), 'state', output_field=CharField()),
                            output_field=CharField()
                        )
                    )
                    .order_by('-date', '-time')  # Sort by date (latest first)
                    )

    # Get voucher redemption history
    voucher_history = (CustomerRedemption.objects.filter(customer__customerID=customerID, status=False)
                       .select_related('voucher')
                       .values('voucher__voucherID', 'voucher__name', 'date', 'time', 'voucher__pointsRequired')
                       .order_by('-date', '-time')  # Sort by date (latest first, then by time)
                       )

    # Combine both lists
    combined_history = list(chain(device_history, voucher_history))

    # Sort by date (latest first)
    combined_history.sort(key=lambda x: x['date'], reverse=True)

    # Paginate combined history
    pagination = Paginator(combined_history, 4)  # 4 items per page
    page = request.GET.get('page')
    activities = pagination.get_page(page)

    # If no activity data available, show empty message
    if not activities.object_list:
        return render(request, 'customer/activityHis-All.html', {"Empty": True, "profile": userInfo})

    return render(request, 'customer/activityHis-All.html', {"activities": activities, "profile": userInfo})

def device_recycled(request):
    customerID = request.session.get('user_id')
    userInfo = Customer.objects.only('profile_picture').get(customerID=customerID)  # Get user profile data

    # select the pickup request that the customer made, while retrieve the item type based on categoryID
    # reason using small 'c' in customer is because it is not referring to the table but refer to the field itself
    # same goes to the select_relate(), it refers to the field not table

    # pickup_requests = (ScheduleRequest.objects.filter(
    #                     # ~Q(status='Pending'), ~Q functions to exclude condition specified
    #                     Q(status='Completed') | Q(status='Rejected'),
    #                     customer__customerID=customerID)
    #                    .select_related('category')
    #                    .values('trackingnumber', 'category__itemType', 'date', 'quantity', 'status', 'rejectedReason__reason')
    #                    .annotate(total=F('quantity') * F('category__pointsGiven')) #this here is to calculate the total points using F()
    #                    .annotate(address=Concat('street', Value(', '), 'postalCode',
    #                                             Value(', '), 'area', Value(', '), 'state', output_field=CharField()))
    #                    .order_by('-date', '-time') # order by date
    #                     )

    pickup_requests = (ScheduleRequest.objects.filter(
                    # ~Q(status='Pending'),
                    Q(status='Completed') | Q(status='Rejected'),
                    customer__customerID=customerID)
                    .select_related('category')
                    .values('trackingnumber', 'category__itemType', 'date', 'quantity', 'status', 'rejectedReason__reason')
                    .annotate(
                        total=F('quantity') * F('category__pointsGiven'),
                        address=Case(
                            When(
                                state__in=excluded_states,
                                then=Concat('street', Value(', '), 'postalCode', Value(', '), 'state', output_field=CharField())
                            ),
                            default=Concat('street', Value(', '), 'postalCode', Value(', '), 'area', Value(', '), 'state', output_field=CharField()),
                            output_field=CharField()
                        )
                    )
                    .order_by('-date', '-time')  # Sort by date (latest first)
                    )


    pagination = Paginator(pickup_requests, 4) # limit 4 data per page
    page = request.GET.get('page') #keep track on what page is the user in

    #some sort like put all data into the size we set and ready to be use in a loop
    devices = pagination.get_page(page)

    if not devices.object_list:
        return render(request, 'customer/activityHis-Device.html', {"Empty": True, "profile": userInfo})

    return render(request, 'customer/activityHis-Device.html', {"historyPages": devices, "profile": userInfo})

def voucher_redeemed(request):
    customerID = request.session.get('user_id')
    userInfo = Customer.objects.only('profile_picture').get(customerID=customerID)  # Get user profile data

    vouchers_redeemed = (CustomerRedemption.objects.filter(customer__customerID=customerID, status=False).select_related('voucher')
                         .values('voucher__voucherID', 'voucher__name', 'date', 'time', 'voucher__pointsRequired')
                         .order_by('-date', '-time')
                         )

    pagination = Paginator(vouchers_redeemed, 4)
    page = request.GET.get('page')

    vouchers = pagination.get_page(page)

    if not vouchers.object_list:
        return render(request, 'customer/activityHis-Point.html', {"Empty": True, "profile": userInfo})

    return render(request, 'customer/activityHis-Point.html', {'vouchers':vouchers, "profile": userInfo})

def logout(request):
    request.session.flush()
    return redirect('e-waste: landing')

def redeem_rewards_page(request): # need to add paginator in the future to consider the case of too much voucher
    customerID = request.session.get('user_id')
    userInfo = Customer.objects.only('profile_picture', 'points').get(customerID=customerID)  # Get user profile data
    # customerPoint = Customer.objects.filter(customerID=customerID).values_list('points', flat=True).first()

    vouchersAvailable = Voucher.objects.all().filter(quantity__gt=0).order_by('voucherID')
    pagination = Paginator(vouchersAvailable, 4)
    page = request.GET.get('page')

    vouchers = pagination.get_page(page)

    if not vouchers.object_list:
        return render(request, 'customer/redeemRewards.html', {"Empty": True, 'profile':userInfo})

    return render(request, 'customer/redeemRewards.html', {'vouchers':vouchers, 'profile':userInfo})

def redeem_voucher(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            voucherID = data.get("reward")
            points_required = data.get("points")

            customerID = request.session.get('user_id')
            customer = Customer.objects.get(customerID=customerID)
            voucher = Voucher.objects.get(voucherID=voucherID)

            # check if customer have enough points
            if customer.points < points_required:
                return JsonResponse({"success": False, "message": "Not enough points."}, status=400)

            customer.points -=points_required
            customer.save()
            voucher.quantity -= 1
            voucher.save()

            print("save pending")
            redemption = CustomerRedemption.objects.create(customer=customer, voucher=voucher, status=False)
            print("saved")
            redemption.save()
            return JsonResponse({"success": True, "message": "Voucher redeemed successfully!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)
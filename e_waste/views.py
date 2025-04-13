from django.shortcuts import redirect, render
from django.contrib import messages
from database.models import Customer, Driver, Operator
from dotenv import load_dotenv

from .utils import authenticate_user
from django.http import JsonResponse
from utilities.Email import emailAutomation
import requests

# random password generation
import secrets
import string
import  os
import dotenv

load_dotenv()

# ori version
# def signup(request):
#     # return render(request, 'e_waste/signup.html')
#     if request.method =='POST':
#         email = request.POST['email']
#         fullname = request.POST['fullname']
#         password = request.POST['password']
#         confirm_password = request.POST['confirm_password']
#         contact_number = request.POST['contact_number']
#         address = request.POST['address']
#         state = request.POST.get('state')

#         # Check if email already exists
#         if Customer.objects.filter(email=email).exists():
#             messages.error(request, 'Email address already exists.')
#             return redirect('signup')

#         if not state:
#             messages.error(request, "Please select your state.")
#             return redirect('e_waste/signup')

#         if password != confirm_password:
#             return render(request, "e_waste/signup.html", {"error": "Password do not match!"})

#         if len(password) < 8:
#             return render(request, "e_waste/signup.html", {"error": "Password is too short!"})

#         if not contact_number.isdigit():
#             return render(request, "e_waste/signup.html", {"error": "Invalid contact number!"})

#         new_user = Customer(email=email, name=fullname, password=password,phoneNumber=contact_number, address=address, state=state)
#         new_user.save()

#          #Store user in session
#         request.session['user_id'] = new_user.customerID
#         request.session['user_email'] = new_user.email
#         request.session['user_role'] = 'customer'

#         # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         #     return JsonResponse({'success': True})
#         # else:
#         #     return redirect('customer:homepage-customer')
#         # return redirect('customer:homepage-customer')
#     return render(request, 'e_waste/signup.html')

def signup(request):
    url = "https://api.countrystatecity.in/v1/countries/MY/states"

    headers = {
        'X-CSCAPI-KEY': os.getenv('GET_STATE_AREA_API')
    }

    response = requests.request("GET", url, headers=headers).json()
    states = {}
    for state in response:
        states[state.get('name')] = state.get('iso2')

    if request.method == 'POST':
        email = request.POST['email']
        fullname = request.POST['fullname']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        contact_number = request.POST['contact_number']
        street = request.POST['street']
        postalCode = request.POST['postal_code']
        area = request.POST.get('area')
        state = request.POST.get('state')

        if Customer.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email address already exists.'}, status=400)

        if not state:
            return JsonResponse({'success': False, 'error': 'Please select your state.'}, status=400)

        if password != confirm_password:
            return JsonResponse({'success': False, 'error': 'Passwords do not match.'}, status=400)

        if len(password) < 8:
            return JsonResponse({'success': False, 'error': 'Password is too short! Minimium 8 characters'}, status=400)

        if not contact_number.isdigit() or not contact_number.startswith("01") or len(contact_number) not in [10,11]:
            return JsonResponse({'success': False, 'error': 'Invalid contact number!'}, status=400)

        if not postalCode.isdigit() or len(postalCode)!=5 :
            return JsonResponse({'success': False, 'error': 'Invalid Postal Code!'}, status=400)

        new_user = Customer(
            email=email,
            name=fullname,
            password=password,
            phoneNumber=contact_number,
            street=street,
            postalCode=postalCode,
            area=area,
            state=state
        )

        new_user.save()

        request.session['user_id'] = new_user.customerID
        request.session['user_email'] = new_user.email
        request.session['user_role'] = 'customer'

        return JsonResponse({'success': True})

    return render(request, 'e_waste/signup.html', {'states':states, 'API_KEY':os.getenv('GET_STATE_AREA_API')})

def user_login(request):

    if request.method == 'POST':
        email = request.POST['email_input']
        password = request.POST['password']
        print(email)
        print(password)

        # Authenticate using the email field
        user = authenticate_user(email=email, password=password)
        print (user)

        if user is not None:
            # login(request, user)  # Logs the user in
            print(f"Logged in as {request.user}")

            # Check if the user is a Customer
            if Customer.objects.filter(email=email).exists():
                user_role = 'customer'
                user_obj = Customer.objects.get(email=email)
                userID = user_obj.customerID
                redirect_url = 'customer:homepage-customer'
            # Check if the user is a Driver
            elif Driver.objects.filter(email=email).exists():
                user_role = 'driver'
                user_obj = Driver.objects.get(email=email)
                userID = user_obj.driverID
                redirect_url = 'driver:homepage-driver'
            # Check if the user is an Operator
            elif Operator.objects.filter(email=email).exists():
                user_role = 'operator'
                user_obj = Operator.objects.get(email=email)
                userID = user_obj.operatorID
                redirect_url = 'operator:homepage-operator'

            # Store user details in session
            request.session['user_id'] = userID
            request.session['user_email'] = user_obj.email
            request.session['user_role'] = user_role
            return redirect(redirect_url)

        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'e_waste/login.html', {"Invalid":True})  # Redirect to login page

    return render(request, 'e_waste/login.html')  # Ensure GET requests return login page

def generatePassword():
    letters = string.ascii_letters

    digits = string.digits

    special_chars = string.punctuation

    selection_list = letters + digits + special_chars

    password_len = 10

    password = ''
    for i in range(password_len):
        password += ''.join(secrets.choice(selection_list))

    return password

def resetPassword(request):
    if request.method == 'POST':
        target = request.POST['email']
        customer = Customer.objects.filter(email=target).first()
        if customer:
            password = generatePassword()
            customer.password = password
            customer.save()
            # subject = 'Reset Password Request'
            # content = f'Your request to reset password has been received \nThis is your new password: {password}'
            emailAutomation.sendEmail('password_reset', target, context={'temp_password':password})
            return render(request, 'e_waste/resetpassword.html', {'Permission':True})
        else:
            return render(request, 'e_waste/resetpassword.html', {'Permission':False})
    return render(request, 'e_waste/resetpassword.html', {'Permission': None})

def landing(request):
    return render(request, 'e_waste/landing.html')


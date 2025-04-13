from database.models import Customer, Driver, Operator

def authenticate_user (email,password):
    try:
        user = Customer.objects.get(email=email)
        if user.password==password:
            return user
        return None

    except Customer.DoesNotExist:
        pass
    try:
        # Check if the user is a Driver
        user = Driver.objects.get(email=email)
        if user.password == password:
            return user
    except Driver.DoesNotExist:
        pass

    try:
        # Check if the user is an Operator
        user = Operator.objects.get(email=email)
        if user.password == password:
            return user
    except Operator.DoesNotExist:
        pass
    return None
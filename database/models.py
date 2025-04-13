from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import datetime
import time
# Create your models here.

class Customer (models.Model):
    customerID = models.CharField(primary_key=True, max_length=200)
    name = models.CharField(max_length=50)
    # age = models.IntegerField()
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=200)
    phoneNumber = models.CharField(max_length=15)
    street = models.CharField(max_length=255, null=True)
    postalCode = models.CharField(max_length=20, null=True)
    area = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50)
    points = models.IntegerField(blank = True, null = True, default=0)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # if not self.pk or Customer.objects.get(pk=self.pk).password != self.password:
        #     self.password = make_password(self.password)


        if not self.customerID:
            #get the last customer
            last_customer = Customer.objects.order_by('-customerID').first()
            print(last_customer)

            if last_customer:
                last_number = int(last_customer.customerID[1:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.customerID = f"C{new_number:04d}"

        super().save(*args, **kwargs)
        print(self.customerID)

    def __str__(self):
        return f"{self.customerID} {self.name} {self.email} {self.password}"

class Operator(models.Model):
    operatorID = models.CharField(primary_key=True, max_length=200)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.operatorID:
            #get the last customer
            last_operator = Operator.objects.orderby('-operatorID').first()

            if last_operator:
                last_number = int(last_operator.operatorID[1:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.operatorID = f"C{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operatorID} {self.name} {self.email} {self.password}"

class Driver(models.Model):
    driverID = models.CharField(primary_key=True, max_length=200)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=200)
    phoneNumber = models.CharField(max_length=50)
    # carType = models.CharField(max_length=50)
    plateNumber = models.CharField(max_length=50)
    areaCovered = models.CharField(max_length=20, null=True)
    stateCovered = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.driverID:
            #get the last customer
            last_driver = Driver.objects.order_by('-driverID').first()

            if last_driver:
                last_number = int(last_driver.driverID[1:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.driverID = f"D{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.driverID} {self.name} {self.email} {self.password}"

class ItemCategory (models.Model):
    categoryID = models.CharField(primary_key=True, max_length=50)
    itemType = models.CharField(max_length=50)
    pointsGiven = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.categoryID:
            #get the last customer
            last_category = ItemCategory.objects.order_by('-categoryID').first()

            if last_category:
                last_number = int(last_category.categoryID[1:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.categoryID = f"C{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.categoryID} {self.itemType}"

class Voucher(models.Model):
    voucherID = models.CharField(primary_key=True, max_length=200)
    name = models.CharField(max_length=150)
    # description = models.CharField(max_length=200)
    pointsRequired = models.IntegerField()
    # termsCondition = models.CharField(max_length=200)
    quantity = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.voucherID:
            #get the last customer
            last_voucher = Voucher.objects.order_by('-voucherID').first()

            if last_voucher:
                last_number = int(last_voucher.voucherID[1:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.voucherID = f"V{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.voucherID} {self.name}\tQuantity: {self.quantity}"

class CustomerRedemption(models.Model):
    redemptionID = models.CharField(primary_key=True, max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)
    status = models.BooleanField() # used status, if True = the voucher had been used vice versa

    def save(self, *args, **kwargs):
        if not self.redemptionID:
            #get the last customer
            last_redemption = CustomerRedemption.objects.order_by('-redemptionID').first()

            if last_redemption:
                last_number = int(last_redemption.redemptionID[1:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.redemptionID = f"R{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.redemptionID} {self.customer} {self.voucher} {self.date}"

class Reason(models.Model):
    reasonID = models.CharField(primary_key=True, max_length=255)
    reason = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.reasonID:
            last_reason = Reason.objects.order_by('-reasonID').first()

            if last_reason:
                last_number = int(last_reason.reasonID[2:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.reasonID = f"RE{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reasonID} Reason:{self.reason}"

class ScheduleRequest(models.Model):
    requestID = models.CharField(primary_key=True, max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    weight = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    street = models.CharField(max_length=255, null=True)
    postalCode = models.CharField(max_length=20, null=True)
    area = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=50, default="Pending")
    rejectedReason = models.ForeignKey(Reason, on_delete=models.CASCADE, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, null=True, blank=True)
    trackingnumber = models.CharField(max_length=200, unique=True)

    def generate_tracking_number(self):
        current_year = timezone.now().year
        prefix = f"#JAS{current_year}-"
        last_request = ScheduleRequest.objects.filter(trackingnumber__startswith=prefix).order_by('trackingnumber').last()
        if last_request:
            last_number = int(last_request.trackingnumber.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}{new_number:04d}"

    def save(self, *args, **kwargs):
        if not self.requestID:
            #get the last customer
            last_pickup = ScheduleRequest.objects.order_by('-requestID').first()

            if last_pickup:
                last_number = int(last_pickup.requestID[1:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.requestID = f"P{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.requestID} {self.customer} {self.date} {self.time} {self.trackingnumber}"

class CompletedRequest(models.Model):
    requestID = models.OneToOneField(ScheduleRequest, on_delete=models.CASCADE, related_name="completed_requests")
    completed_date = models.DateField(auto_now_add=True)
    completed_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requestID} {self.completed_date} {self.completed_time}"

class PickedUpRequest(models.Model):
    requestID =  models.OneToOneField(ScheduleRequest, on_delete=models.CASCADE,  related_name="pickedup_requests")
    pickedUp_date = models.DateField(auto_now_add=True)
    pickedUp_time = models.TimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.requestID} {self.pickedUp_date} {self.pickedUp_date}"
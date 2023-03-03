from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator
from ckeditor.fields import RichTextField
from datetime import datetime


STATE_CHOICES=(
    ('Barisal','Barisal'),
    ('Chittagong','Chittagong'),
    ('Dhaka','Dhaka'),
    ('Khulna','Khulna'),
    ('Rajshahi','Rajshahi'),
    ('Sylhet','Sylhet')
)

class Customer(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    zipcode = models.IntegerField()
    state=models.CharField(choices=STATE_CHOICES,max_length=200)

    def __str__(self):
        return str(self.id)

CATEGORY_CHOICES = (
    ('T', 'Tractor'),
    ('E', 'Engine'),
    ('GT', 'Gadening Tools'),
    ('FT', 'Farming Tools')
)

class Product(models.Model):
    title = models.CharField(max_length=200)
    selling_price = models.FloatField()
    description = RichTextField(blank=True,null=True)
    brand = models.CharField(max_length=200)
    category = models.CharField(choices = CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to = 'productimg')
    stock_available = models.BooleanField(default=True)

    def __str__(self):
        get_last_deal = OrderPlaced.objects.filter(product=self).last()
        if get_last_deal:
            get_expired = get_last_deal.End_date
            today = datetime.now().date()

            premium_valid_days = get_expired - today

            premium_valid_second = premium_valid_days.total_seconds()
            if premium_valid_second >= 0:
                self.stock_available = False
                self.save()
        else:
            pass
        return str(self.id)








class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    Start_date = models.CharField(max_length=255, default=datetime.now(), null=True, blank=True)
    End_date = models.CharField(max_length=255, default=datetime.now(), null=True, blank=True)
    Days = models.PositiveIntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def total_cost(self):
        return self.quantity * self.product.selling_price * self.Days

STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel')
)  

class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1) 
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    Start_date = models.DateField(default=datetime.now(), null=True, blank=True)
    End_date = models.DateField(default=datetime.now(), null=True, blank=True)
    Days = models.IntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        print('working')
        get_last_deal = OrderPlaced.objects.filter(product=self.product).last()
        if get_last_deal:
            print('fffffffffff')
            get_expired = get_last_deal.End_date
            today = datetime.now().date()

            premium_valid_days = get_expired - today

            premium_valid_second = premium_valid_days.total_seconds()
            print(int(premium_valid_second))
            if premium_valid_second >= 0:
                print('working22')
                self.product.stock_available = False
                self.product.save()
        else:
            pass

        return super(OrderPlaced, self).save(*args, **kwargs)

    @property
    def total_cost(self):
        return self.quantity * self.product.selling_price * self.Days

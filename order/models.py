from django.db import models
from account.models import Account
from store.models import Product, Variation

# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.payment_id

class Order(models.Model):
    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )
    user = models.ForeignKey(Account,on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    notes = models.CharField(max_length=100,blank=True)
    total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS,default='New')
    ip = models.CharField(max_length=20)
    is_ordered = models.BooleanField(default=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.order_number} - {self.user.first_name}"

    def customer_name(self):
        return f'{self.first_name} {self.last_name}'

    def customer_address(self):
        return f"{self.address_line_1}{' '+self.address_line_2 if self.address_line_2 else '' }"
class OrderProduct(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self) -> str:
        return f"{self.order.order_number} > {self.quantity} - {self.product.product_name} {self.created_at.isoformat()}"
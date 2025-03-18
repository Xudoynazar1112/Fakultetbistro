from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    chat_id = models.BigIntegerField(unique=True, null=False, blank=False)
    lang_id = models.IntegerField(null=True, blank=True, choices=((1, 'Uzbek'), (2, 'Russian')))
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} ({self.chat_id or self.username})"


class Category(models.Model):
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)

    def __str__(self):
        return self.name_uz

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    description_uz = models.TextField(null=True, blank=True)
    description_ru = models.TextField(null=True, blank=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='images/', default='images/default.jpg')

    def __str__(self):
        return self.name_uz

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.IntegerField(choices=[(1, "Pending"), (2, "Delivered"), (3, "Canceled")], default=1)  # 1: Pending
    payment_type = models.IntegerField(null=True, blank=True, choices=[(1, "Cash"), (2, "Payme"), (3, "Click")])  # 1: Cash, 2: Payme, 3: Click
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user}"

class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} x {self.product}"


class Comment(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[(1, "Pending"), (2, "Answered"), (3, "Ignored")], default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user}"

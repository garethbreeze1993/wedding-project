from django.db import models
from django.conf import settings
from django.shortcuts import reverse


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    brand = models.CharField(max_length=150)
    slug = models.SlugField()
    description = models.TextField()
    in_stock_quantity = models.IntegerField(default=1000)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('wedding_app:products', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('wedding_app:add-to-cart', kwargs={'slug': self.slug})

    def remove_from_cart_url(self):
        return reverse('wedding_app:remove-from-cart', kwargs={'slug': self.slug})


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.item.name + ' X' + str(self.quantity)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    orderitems = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username


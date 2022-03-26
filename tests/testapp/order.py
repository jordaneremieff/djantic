import factory
from django.db import models
from factory.django import DjangoModelFactory


class OrderUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)


class OrderUserProfile(models.Model):
    address = models.CharField(max_length=255)
    user = models.OneToOneField(OrderUser, on_delete=models.CASCADE, related_name='profile')


class Order(models.Model):
    total_price = models.DecimalField(max_digits=8, decimal_places=5, default=0)
    shipping_address = models.CharField(max_length=255)
    user = models.ForeignKey(
        OrderUser, on_delete=models.CASCADE, related_name="orders"
    )

    class Meta:
        ordering = ["total_price"]

    def __str__(self):
        return f'{self.order.id} - {self.name}'


class OrderItem(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=8, decimal_places=5, default=0)
    quantity = models.IntegerField(default=0)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f'{self.order.id} - {self.name}'


class OrderItemDetail(models.Model):
    name = models.CharField(max_length=30)
    value = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="details"
    )

    class Meta:
        ordering = ["order_item"]

    def __str__(self):
        return f'{self.order_item.id} - {self.name}'


class OrderItemDetailFactory(DjangoModelFactory):

    class Meta:
        model = OrderItemDetail


class OrderItemFactory(DjangoModelFactory):

    class Meta:
        model = OrderItem

    @factory.post_generation
    def details(self, create, details, **kwargs):
        if details is None:
            details = [OrderItemDetailFactory.create(order_item=self, **kwargs) for i in range(0, 2)]


class OrderFactory(DjangoModelFactory):

    class Meta:
        model = Order

    @factory.post_generation
    def items(self, create, items, **kwargs):
        if items is None:
            items = [OrderItemFactory.create(order=self, **kwargs)
                     for i in range(0, 2)]


class OrderUserProfileFactory(DjangoModelFactory):

    class Meta:
        model = OrderUserProfile


class OrderUserFactory(DjangoModelFactory):

    class Meta:
        model = OrderUser

    @factory.post_generation
    def orders(self, create, orders, **kwargs):
        if orders is None:
            orders = [OrderFactory.create(user=self, **kwargs) for i in range(0, 2)]

    @factory.post_generation
    def profile(self, create, profile, **kwargs):
        if profile is None:
            profile = OrderUserProfileFactory.create(user=self, **kwargs)

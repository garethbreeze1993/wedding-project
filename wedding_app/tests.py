import datetime
import pytz
from django.test import TestCase
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from wedding_app.models import Item, OrderItem, Order
from wedding_app.views import add_to_cart


def setup_user():
    User = get_user_model() # call the django user model via the get_user_model method
    return User.objects.create_superuser('test', email='test_user@gmail.com', password='test_pass') # create a user so I can login so I can get around permissions

def setup_user_2():
    User = get_user_model() # call the django user model via the get_user_model method
    return User.objects.create_superuser('new_user', email='new_user@gmail.com', password='new_pass') # create a user so I can login so I can get around permissions


class WeddingAppViewTests(TestCase):
    def setUp(self) -> None:
        for i in range(1, 4):
            Item.objects.create(
                name=f'item name_{i}', brand=f'item brand_{i}', in_stock_quantity=i,
                price=i, slug=slugify(f'item name_{i}'), description=f'Please add description{i}')
        user_1 = User.objects.create_superuser(username='test', email='test_user@gmail.com', password='test_pass')
        user_1.save()

    def test_add_to_cart_item_in_stock_quantity_is_zero(self):
        i = 5
        item_5 = Item.objects.create(name=f'item name_{i}', brand=f'item brand_{i}', in_stock_quantity=0,
                price=i, slug=slugify(f'item name_{i}'), description=f'Please add description{i}')
        slug = slugify(f'item name_{5}')
        response = self.client.get(reverse('wedding_app:add-to-cart', kwargs={'slug': slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:item-list'))

    def test_add_to_cart_order_not_exist_add_one_item(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        response = self.client.get(reverse('wedding_app:add-to-cart', kwargs={'slug': slug}))
        order_qs = Order.objects.all()
        item_obj = Item.objects.filter(slug=slug)
        self.assertEqual(len(order_qs), 1)
        self.assertEqual(order_qs[0].orderitems.all()[0].quantity, 1)
        order_obj = order_qs[0]
        self.assertEqual(order_obj.orderitems.all()[0].item.name, item_obj[0].name)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:item-list'))

    def test_add_to_cart_order_add_another_item_to_order(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        slug_2 = slugify(f'item name_{2}')
        item_obj = Item.objects.filter(slug=slug).first()
        order_item = OrderItem.objects.create(item=item_obj, quantity=1, user_id=1)
        order = Order.objects.create(user_id=1)
        order.orderitems.add(order_item)
        response = self.client.get(reverse('wedding_app:add-to-cart', kwargs={'slug': slug_2}))
        order_after_qs = Order.objects.all()
        order_after = order_after_qs.first()
        second_item_obj = Item.objects.filter(slug=slug_2).first()
        for index, o_item in enumerate(order_after.orderitems.all()):
            self.assertEqual(o_item.quantity, 1)
            if index == 0:
                self.assertEqual(o_item.item, item_obj)
            else:
                self.assertEqual(o_item.item, second_item_obj)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:item-list'))

    def test_add_to_cart_order_add_same_item_to_order(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        slug_2 = slugify(f'item name_{2}')
        item_obj = Item.objects.filter(slug=slug).first()
        order_item = OrderItem.objects.create(item=item_obj, quantity=1, user_id=1)
        order = Order.objects.create(user_id=1)
        order.orderitems.add(order_item)
        response = self.client.get(reverse('wedding_app:add-to-cart', kwargs={'slug': slug}))
        item_obj_after = Item.objects.filter(slug=slug).first()
        order_after_qs = Order.objects.all()
        order_after = order_after_qs.first()
        self.assertEqual(order_after.orderitems.first().quantity, 2)
        self.assertEqual(order_after.orderitems.first().item, item_obj)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:item-list'))
        self.assertEqual(item_obj_after.in_stock_quantity, 0)

    def test_home_page(self):
        login = self.client.login(username='test', password='test_pass')
        response = self.client.get(reverse('wedding_app:item-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name='home-page.html')

    def test_detail_page(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        item = Item.objects.filter(slug=slug).first()
        response = self.client.get(reverse('wedding_app:products', kwargs={'slug': slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response=response, template_name='product-page.html')
        self.assertEqual(response.context['item'], item)

    def test_checkout_page_no_orders(self):
        login = self.client.login(username='test', password='test_pass')
        response = self.client.get(reverse('wedding_app:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context[-1]['show_orders'])

    def test_checkout_page_orders_show(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        item_obj = Item.objects.filter(slug=slug).first()
        order_item = OrderItem.objects.create(item=item_obj, quantity=1, user_id=1)
        order = Order.objects.create(user_id=1)
        order.orderitems.add(order_item)
        response = self.client.get(reverse('wedding_app:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_orders'])
        self.assertEqual(response.context['orders'][0], order.orderitems.first())

    def test_remove_from_cart_no_active_order(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        response = self.client.get(reverse('wedding_app:remove-from-cart', kwargs={'slug': slug}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:item-list'))

    def test_remove_from_cart_item_not_in_cart(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        slug_2 = slugify(f'item name_{2}')
        item_obj = Item.objects.filter(slug=slug).first()
        order_item = OrderItem.objects.create(item=item_obj, quantity=2, user_id=1)
        order = Order.objects.create(user_id=1)
        order.orderitems.add(order_item)
        response = self.client.get(reverse('wedding_app:remove-from-cart', kwargs={'slug': slug_2}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:item-list'))
        self.assertEqual(order.orderitems.first(), order_item)

    def test_remove_from_cart_item_in_cart(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        item_obj = Item.objects.filter(slug=slug).first()
        order_item = OrderItem.objects.create(item=item_obj, quantity=1, user_id=1)
        order = Order.objects.create(user_id=1)
        order.orderitems.add(order_item)
        response = self.client.get(reverse('wedding_app:remove-from-cart', kwargs={'slug': slug}))
        item_obj_after = Item.objects.filter(slug=slug).first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:item-list'))
        self.assertFalse(order.orderitems.all())
        self.assertEqual(item_obj_after.in_stock_quantity, 2)

    def test_purchase_no_orders(self):
        login = self.client.login(username='test', password='test_pass')
        response = self.client.get(reverse('wedding_app:purchase'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:item-list'))

    def test_purchase_order_is_there(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        item_obj = Item.objects.filter(slug=slug).first()
        order_item = OrderItem.objects.create(item=item_obj, quantity=1, user_id=1)
        order = Order.objects.create(user_id=1)
        order.orderitems.add(order_item)
        response = self.client.get(reverse('wedding_app:purchase'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('wedding_app:purchased-gifts'))
        updated_order = Order.objects.filter(pk=1).first()
        order_item_updated = updated_order.orderitems.first()
        self.assertTrue(updated_order.ordered)
        self.assertTrue(order_item_updated.ordered)

    def test_puchased_gifts_no_orders_purchased(self):
        login = self.client.login(username='test', password='test_pass')
        response = self.client.get(reverse('wedding_app:purchased-gifts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order_items_list'], [])

    def test_puchased_gifts_purchased(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        item_obj = Item.objects.filter(slug=slug).first()
        ordered_date = datetime.datetime(2020, 1, 1, 11)
        now_aware = pytz.utc.localize(ordered_date)
        order_item = OrderItem.objects.create(item=item_obj, quantity=1, user_id=1, ordered=True)
        order = Order.objects.create(user_id=1, ordered=True, ordered_date=now_aware)
        order.orderitems.add(order_item)
        response = self.client.get(reverse('wedding_app:purchased-gifts'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['order_items_list'], zip)

    def test_generate_report_only_orders_not_purchased(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        item_obj = Item.objects.filter(slug=slug).first()
        order_item = OrderItem.objects.create(item=item_obj, quantity=1, user_id=1)
        order = Order.objects.create(user_id=1)
        order.orderitems.add(order_item)
        response = self.client.get(reverse('wedding_app:generate-report'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['orders_n_purchased'][0], order.orderitems.first())
        self.assertFalse(response.context['order_purchased'])

    def test_generate_report_both_orders_purchased_and_not_purchased(self):
        login = self.client.login(username='test', password='test_pass')
        slug = slugify(f'item name_{1}')
        item_obj = Item.objects.filter(slug=slug).first()
        ordered_date = datetime.datetime(2020, 1, 1, 11)
        now_aware = pytz.utc.localize(ordered_date)
        order_item = OrderItem.objects.create(item=item_obj, quantity=1, user_id=1, ordered=True)
        order = Order.objects.create(user_id=1, ordered_date=now_aware, ordered=True)
        slug_2 = slugify(f'item name_{2}')
        item_obj_2 = Item.objects.filter(slug=slug_2).first()
        order_item_2 = OrderItem.objects.create(item=item_obj_2, quantity=1, user_id=1)
        order_2 = Order.objects.create(user_id=1, ordered_date=now_aware)
        order.orderitems.add(order_item)
        order_2.orderitems.add(order_item_2)
        response = self.client.get(reverse('wedding_app:generate-report'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['orders_n_purchased'][0], order_2.orderitems.first())
        self.assertEqual(response.context['order_purchased'], {item_obj.name: 1})




from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Item, Order, OrderItem


class HomeView(ListView):
    model = Item
    template_name = 'home-page.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


def checkout_page(request):
    context = {'show_orders': False}
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_items = order.orderitems.filter(user=request.user)
        context['orders'] = order_items
        context['show_orders'] = True
        return render(request, 'checkout-page.html', context)
    else:
        return render(request, 'checkout-page.html', context)


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if item.in_stock_quantity < 1:
        messages.info(request, "This item is out of stock.")
        return redirect("wedding_app:item-list")
    else:
        item.in_stock_quantity -= 1
    item.save()
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item in order
        if order.orderitems.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("wedding_app:item-list")
        else:
            order.orderitems.add(order_item)
            messages.info(request, "This item was added to your cart")
            return redirect("wedding_app:item-list")
    else:
        order = Order.objects.create(user=request.user)
        order.orderitems.add(order_item)
        messages.info(request, "This item was added to your cart")
        return redirect("wedding_app:item-list")


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item_qs = OrderItem.objects.filter(user=request.user, item=item, ordered=False)
    quantity_of_opts = None
    if order_item_qs.exists():
        order_item = order_item_qs[0]
        quantity_of_opts = order_item.quantity

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user)[0]
            order.orderitems.remove(order_item)
            item.in_stock_quantity += quantity_of_opts
            item.save()
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("wedding_app:item-list")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("wedding_app:item-list")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("wedding_app:item-list")


def purchase(request):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_items = order.orderitems.all()
        for items in order_items:
            items.ordered = True
            items.save()
        order.ordered = True
        order.ordered_date = timezone.now()
        order.save()
        messages.info(request, "Your order has been processed")
        return redirect("wedding_app:purchased-gifts")

    else:
        messages.info(request, "You do not have an active order")
        return redirect("wedding_app:item-list")


def puchased_gifts(request):
    order_items_list = []
    order_date = []
    order_qs = Order.objects.filter(ordered=True, user=request.user)
    if order_qs.exists():
        for index, orders in enumerate(order_qs):
            order_items = orders.orderitems.filter(ordered=True)
            order_items_list.append(order_items)
            order_date.append(orders.ordered_date)
        final_list = zip(order_items_list, order_date)
        return render(request, 'purchased_gifts.html', {'order_items_list': final_list})
    else:
        return render(request, 'purchased_gifts.html', {'order_items_list': order_items_list})


def generate_report(request):
    orders_not_purchased = []
    orders_purchased = []
    order_qs_not_purchased = Order.objects.filter(ordered=False, user=request.user)
    if order_qs_not_purchased.exists():
        order = order_qs_not_purchased[0]
        orders_not_purchased_items = order.orderitems.filter(user=request.user)
        for i in orders_not_purchased_items:
            orders_not_purchased.append(i)
    else:
        pass
    order_qs_purchased = Order.objects.filter(ordered=True, user=request.user)
    if order_qs_purchased.exists():
        for index, orders in enumerate(order_qs_purchased):
            order_items = orders.orderitems.filter(ordered=True)
            orders_purchased.append(order_items)
        item_dict = {}
        for list_of_orderitems in orders_purchased:
            for o_item in list_of_orderitems:
                if o_item.item.name in item_dict:
                    value = item_dict[o_item.item.name]
                    value += o_item.quantity
                    item_dict[o_item.item.name] = value
                else:
                    item_dict[o_item.item.name] = o_item.quantity
        return render(request, 'report.html', context={'orders_n_purchased': orders_not_purchased,
                                                       'order_purchased': item_dict})
    else:
        return render(request, 'report.html',
                      context={'orders_n_purchased': orders_not_purchased, 'order_purchased': []})

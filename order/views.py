from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import datetime

from .forms import OrderForm
from .models import Order
from cart.models import CartItem
# Create your views here.


# @login_required(login_url='login')
def payment(request):
    return render(request,'order/payment.html')

@login_required(login_url='login')
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    count = cart_items.count()
    if count < 1:
        return redirect('store')
    total_order = 0
    quantity_order = 0

    for cart_item in cart_items:
        total_order += cart_item.quantity * cart_item.product.price
        quantity_order += cart_item.quantity
    tax_order = (total_order * 3) / 100
    total_order = total_order + tax_order

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order_data = Order()
            form_data = form.cleaned_data
            order_data.first_name = form_data['first_name']
            order_data.last_name = form_data['last_name']
            order_data.email = form_data['email']
            order_data.country = form_data['country']
            order_data.state = form_data['state']
            order_data.city = form_data['city']
            order_data.notes = form_data['notes']
            order_data.address_line_1 = form_data['address_line_1']
            order_data.address_line_2 = form_data['address_line_2']
            order_data.phone = form_data['phone']
            order_data.total = total_order
            order_data.tax = tax_order
            order_data.ip = request.META.get('REMOTE_ADDR')
            order_data.user = current_user
            order_data.save()

            order_number = f"{datetime.date.today().strftime('%Y%m%d')}{order_data.id}"
            order_data.order_number = order_number
            order_data.save()
            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'subtotal': total_order - tax_order,
                'tax': tax_order,
                'total': total_order

            }
            return render(request,'order/payment.html',context)
        return redirect('checkout')
    return redirect('checkout')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import datetime
import json

# email
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from cart.models import CartItem
# Create your views here.


# @login_required(login_url='login')
def payment(request):
    try:
        body = json.loads(request.body)
        order = Order.objects.get(user=request.user,is_ordered=False,order_number = body['orderId'])
        # create transaction in payment model
        payment = Payment(
            user = request.user,
            payment_id = body['transactionId'],
            payment_method = body['paymentMethod'],
            amount_paid = order.total,
            status = body['status']
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()
        # create products in order
        cart_items = CartItem.objects.filter(user=request.user)
        for cart_item in cart_items:
            product_variations = list(cart_item.variations.all())
            order_product = OrderProduct(
                order = order,
                user = request.user,
                payment = payment,
                product = cart_item.product,
                quantity = cart_item.quantity,
                product_price = cart_item.product.price,
                ordered = True
            )
            order_product.save()
            order_product.variations.set(product_variations)
            order_product.save()

            # update the stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()
            # clear cart items
            cart_item.delete()

        # send email
        mail_subject = 'Thank you for your purchase!'
        # email body
        message = render_to_string('order/order_confirmation_email.html',{
            'user': request.user,
            'order': order
        })
        request_email = EmailMessage(mail_subject,message,to=[order.email])
        request_email.send()

        # return a json to client
        data = {
            'orderNumber': order.order_number,
            'transactionId': payment.payment_id
        }
        return JsonResponse(data)
    except Exception as e:
        print('error')
        print(e)
        pass
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

@login_required(login_url='login')
def order_completed(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number)
        order_products = OrderProduct.objects.filter(order=order)
        payment = Payment.objects.get(payment_id=payment_id)
        subtotal = 0
        for product in order_products:
            subtotal += product.product_price * product.quantity
        tax = (subtotal * 3) / 100
        context = {
            'order': order,
            'products': order_products,
            'payment': payment,
            'subtotal': subtotal,
            'total': subtotal + tax,
            'tax': tax
        }
        return render(request,'order/order_completed.html', context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')
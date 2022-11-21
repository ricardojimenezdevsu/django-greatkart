from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from store.models import Product, Variation
from .models import Cart, CartItem

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
    
def add_cart(request, product_id):
    product_variation = []
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        # check for variations
        for item in request.POST:
            key = item
            value = request.POST[item]
            # validate if the variations are in the db
            try:
                variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass    
    else:
        cart_item = CartItem.objects.get(id=product_id)
        cart_item.quantity += 1
        cart_item.save()
        return redirect('cart')
    cart_id = _cart_id(request)
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = cart_id
        )
    cart.save()

    cart_iteme_exists = CartItem.objects.filter(product=product,quantity=1,cart=cart).exists()
    if cart_iteme_exists:
        cart_items = CartItem.objects.filter(product=product,quantity=1,cart=cart)
        ex_var_list = []
        id = []
        for item in cart_items:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in ex_var_list:
            # increase the quantity
            itemIndex = ex_var_list.index(product_variation)
            itemId = id[itemIndex]
            cart_item = CartItem.objects.get(product = product, id=itemId)
            cart_item.quantity += 1
            cart_item.variations.clear()
        else: 
            cart_item = CartItem.objects.create(
                cart = cart,
                product = product,
                quantity = 1
            )
        
    else:
        cart_item = CartItem.objects.create(
                cart = cart,
                product = product,
                quantity = 1
            )    
    cart_item.variations.add(*product_variation)
    
    cart_item.save()
    return redirect('cart')

def remove_cart(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    tax, grand_total = 0,0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)
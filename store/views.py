from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.db.models import Q

from .models import Product
from category.models import Category
from cart.views import _cart_id
from cart.models import CartItem

# Create your views here.
def _products_context_paginated(products, page=1):
    paginator = Paginator(products, 1)
    paged_products = paginator.get_page(page)
    product_count = products.count()
    return {
        'products': paged_products,
        'product_count': product_count
    }

def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
    context = _products_context_paginated(products, request.GET.get('page'))
    return render(request,'store/store.html', context)

def product_detail(request,category_slug, product_slug):
    is_in_cart = False
    try:
        product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        is_in_cart = CartItem.objects.filter(product=product,cart__cart_id=_cart_id(request)).exists()
    except Exception as e:
        raise e
    context = {
        'product': product,
        'is_in_cart': is_in_cart
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    
    if 'keyword' in request.GET and request.GET['keyword']:
        keyword = request.GET['keyword']
        products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
    else:
        return redirect('store')
    context = _products_context_paginated(products, request.GET.get('page'))    
    print(context)
    return render(request, 'store/store.html', context)

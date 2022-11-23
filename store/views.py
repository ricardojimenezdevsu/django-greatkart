from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.db.models import Q
from django.contrib import messages

from .models import Product, ReviewRating
from .forms import ReviewForm

from category.models import Category
from cart.views import _cart_id
from cart.models import CartItem
from order.models import OrderProduct

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
    try:
        order_product = OrderProduct.objects.filter(user__id=request.user.id,product__id=product.id).exists()
    except OrderProduct.DoesNotExist:
        order_product = None
    user_review = None
    if order_product:
        user_review = ReviewRating.objects.get(user__id=request.user.id,product__id=product.id,active=True)
    reviews = ReviewRating.objects.filter(product__id=product.id,active=True).order_by('-updated_at')
    context = {
        'product': product,
        'is_in_cart': is_in_cart,
        'order_product': order_product,
        'user_review': user_review,
        'reviews': reviews
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


def submit_review(request, product_id):
    current_url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(product__id=product_id,user__id=request.user.id)
            # update the old review with the form info
            form = ReviewForm(request.POST,instance=review)
            form.save()
            messages.success(request,'Your review has been updated!')
            return redirect(current_url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                # product = Product.objects.get(id=product_id)
                review = ReviewRating(
                    user = request.user,
                    product_id = product_id,
                    subject = form.cleaned_data['subject'],
                    review = form.cleaned_data['review'],
                    rating = form.cleaned_data['rating'],
                    ip = request.META.get('REMOTE_ADDR')
                )
                review.save()
                messages.success(request,'Your review has been created!')
                return redirect(current_url)
            messages.error(request,'Rating is required')

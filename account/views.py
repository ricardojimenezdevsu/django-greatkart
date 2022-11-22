"""A dummy docstring."""
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegistrationForm
from .models import Account
from cart.models import Cart, CartItem
from cart.views import _cart_id

# Create your views here.


def register(request):
    """A dummy docstring."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.phone_number = phone_number
            user.save()
            # user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            # email body
            message = render_to_string('account/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            request_email = EmailMessage(mail_subject,message,to=[email])
            request_email.send()
            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email.')
            return redirect('login/?command=verification&email='+email)
    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'account/register.html', context)


def login(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            # transfer cart items to user if 
            _update_cart(request,user)
            auth.login(request, user)
            messages.success(request,'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email/password')
            return redirect('login') 
    user = auth.get_user(request)
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'account/login.html')

def _update_cart(request, user):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
        if cart_items:
            user_cart_items = CartItem.objects.filter(user=user)
            ex_var_list = []
            id = []
            for item in user_cart_items:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            for cart_item in cart_items:
                product_variation = list(cart_item.variations.all())
                if product_variation in ex_var_list:
                    # increase the quantity
                    itemIndex = ex_var_list.index(product_variation)
                    itemId = id[itemIndex]
                    item = CartItem.objects.get(id=itemId)
                    item.quantity += cart_item.quantity
                    item.save()
                else:
                    cart_item.user = user
                    cart_item.save()
    except:
        pass
@login_required(login_url = 'login')
def logout(request):
    """A dummy docstring."""
    auth.logout(request)
    return redirect('login')

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Contratulations! Your account is now activated')
        return redirect('login')
    else:
        messages.error(request,'Invalid registration link')
        return redirect('register')


@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'account/dashboard.html')

def forgot_password(request):    
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset password'
            # email body
            message = render_to_string('account/reset_password_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            request_email = EmailMessage(mail_subject,message,to=[email])
            request_email.send()
            messages.success(request,'We have sent a email to reset your password')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist')
    return render(request, 'account/forgot_password.html')

def reset_password_validation(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        return redirect('reset_password')
    else:
        messages.error(request,'Link expired')
        return redirect('register')
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            messages.error(request,'Passwords are not the same')
            return redirect('reset_password')
        uid = request.session.get('uid')
        user = Account.objects.get(pk=uid)
        user.set_password(password)
        user.save()
        messages.success(request,'Your password was successfuly changed')
        return redirect('login')
    return render(request,'account/reset_password.html')
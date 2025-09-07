from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.db.models import Q, Count
from myshop import settings
from .forms import RegisterForm, LoginForm
from .models import Category, Product, Order, OrderItem, User
import stripe
import os
from django.conf import settings
CART_SESSION_KEY = 'cart'

# ======= Stripe API Key (test) =======
stripe.api_key = settings.STRIPE_SECRET_KEY
# ======= Cart helpers =======
def _get_cart(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    for pid, item in list(cart.items()):
        if isinstance(item, int):
            product = get_object_or_404(Product, id=int(pid))
            cart[pid] = {
                'title': product.title,
                'price': float(product.price),
                'quantity': item
            }
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True
    return cart

def _save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True

# ======= Homepage =======
def index(request):
    q = (request.GET.get("query") or "").strip()
    if q:
        products = Product.objects.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        ).order_by("-id")[:6]
    else:
        products = Product.objects.order_by("-id")[:3]
    return render(request, "store/index.html", {"products": products, "query": q})

# ======= All products =======
def all_products(request, slug=None):
    q = (request.GET.get("q") or "").strip()
    categories = Category.objects.all().order_by("name")
    active_category = None
    products = Product.objects.select_related("category").all()

    if slug:
        active_category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=active_category)

    if q:
        products = products.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )

    paginator = Paginator(products.order_by("-id"), 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "products": page_obj,
        "categories": categories,
        "active_category": active_category,
        "q": q,
    }
    return render(request, "store/all_products.html", context)

def category_view(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    products = cat.products.filter(is_active=True)
    return render(request, 'store/all_products.html', {
        'categories': Category.objects.all(),
        'products': products,
        'active_category': cat
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})

# ======= Cart =======
def cart_view(request):
    cart = _get_cart(request)
    items = []
    subtotal = Decimal('0')
    for pid, item in cart.items():
        p = get_object_or_404(Product, id=int(pid))
        quantity = int(item['quantity'])
        price = Decimal(item['price'])
        line_total = price * quantity
        items.append({'product': p, 'qty': quantity, 'line_total': line_total})
        subtotal += line_total
    return render(request, 'store/cart.html', {'items': items, 'subtotal': subtotal})

@login_required(login_url='/accounts/login/')
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = _get_cart(request)
    if str(product.id) in cart:
        cart[str(product.id)]['quantity'] += quantity
    else:
        cart[str(product.id)] = {'title': product.title, 'price': float(product.price), 'quantity': quantity}
    _save_cart(request, cart)
    return redirect('store:cart')

def cart_remove(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect('store:cart')

def cart_clear(request):
    _save_cart(request, {})
    return redirect('store:cart')

# ======= Checkout with Stripe =======
@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('store:index')

    items = []
    total = 0
    for pid, item in cart.items():
        p = get_object_or_404(Product, id=int(pid))
        quantity = int(item['quantity'])
        price = float(item['price'])
        line_total = price * quantity
        items.append({'product': p, 'qty': quantity, 'line_total': line_total})
        total += line_total

    if request.method == 'POST':
        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(total*100),  # cents
            currency='usd',
            metadata={'user_id': request.user.id}
        )

        # Save order as unpaid
        order = Order.objects.create(user=request.user, total=total, paid=False)
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['product'].price,
                quantity=item['qty']
            )

        # Return JSON to frontend
        return JsonResponse({
            'client_secret': intent.client_secret,
            'order_id': order.id
        })

    # For GET request
    return render(request, "store/checkout.html", {
        "items": items,
        "total": total,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    })



# ======= Payment success =======
@login_required
def payment_success(request, order_id):
    try:
        # Sirf order_id se fetch karo, user check temporarily remove kiya
        order = Order.objects.get(id=order_id)
        order.paid = True
        order.payment_id = request.GET.get('payment_intent', '')  # Stripe paymentIntent ID
        order.save()
        _save_cart(request, {})  # clear cart
        return render(request, 'store/payment_success.html', {'order': order})
    except Order.DoesNotExist:
        # Agar order nahi mila to home pe redirect
        return redirect('store:index')


# ======= Payment failed =======
@login_required
def payment_failed(request):
    return render(request, 'store/payment_failed.html')

# ======= Orders =======
@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})

@login_required
def secure_download(request, product_id):
    has_access = OrderItem.objects.filter(order__user=request.user, order__paid=True, product__id=product_id).exists()
    if not has_access:
        raise Http404("You do not have access to this file.")
    product = get_object_or_404(Product, id=product_id)
    if not product.file:
        raise Http404("File not found.")
    return FileResponse(product.file.open('rb'), as_attachment=True, filename=os.path.basename(product.file.name))

# ======= Auth & Profile =======
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm

@login_required
def profile(request):
    return render(request, 'store/orders.html', {'orders': Order.objects.filter(user=request.user)})

def search(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.filter(is_active=True)
    if q:
        products = products.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
    return render(request, 'store/index.html', {'categories': Category.objects.all(), 'products': products, 'query': q})

def about(request):
    return render(request, 'store/about.html')

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
@staff_member_required
def admin_dashboard(request):
    products_count = Product.objects.count()
    orders_count = Order.objects.count()
    users_count = User.objects.count()
    latest_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    orders_by_status = Order.objects.values('paid').annotate(total=Count('id')).order_by()
    context = {
        'products_count': products_count,
        'orders_count': orders_count,
        'users_count': users_count,
        'latest_orders': latest_orders,
        'orders_by_status': orders_by_status,
    }
    return render(request, 'store/admin_dashboard.html', context)

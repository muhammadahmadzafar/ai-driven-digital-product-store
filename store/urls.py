from django.urls import path # type: ignore
from . import views
from django.contrib.auth import views as auth_views # type: ignore
from django.views.generic.base import RedirectView # type: ignore

app_name = 'store'

urlpatterns = [
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Home & Products
    path('', views.index, name='index'),
    path('all-products/', views.all_products, name='all_products'),
    path('products/', RedirectView.as_view(pattern_name='store:all_products', permanent=True), name='products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_view, name='category'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),

    # Checkout & Payments
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    # Orders
    path('orders/', views.orders_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('download/<int:product_id>/', views.secure_download, name='secure_download'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='account_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),

    # Other
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
]

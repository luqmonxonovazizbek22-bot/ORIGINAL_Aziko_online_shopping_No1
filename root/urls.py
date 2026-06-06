from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from app.views import (
    AboutView,
    BlogView,
    CartView,
    CheckoutView,
    ContactView,
    IndexView,
    LoginView,
    ProductDetailView,
    ProductView,
    RegisterView,
    add_to_cart,
    ai_chat_api,
    ai_chat_page,
    logout_view,
    update_cart_item,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('product/', ProductView.as_view(), name='product'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/item/<int:item_id>/update/', update_cart_item, name='update_cart_item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),
    path('ai-chat/', ai_chat_page, name='ai_chat'),
    path('api/ai-chat/', ai_chat_api, name='ai_chat_api'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

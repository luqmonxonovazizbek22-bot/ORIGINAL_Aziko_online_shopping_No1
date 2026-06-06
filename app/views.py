import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView

from app.models import Cart, CartItem, ChatMessage, ChatSession, Contact, Order, OrderItem, Product, SupportTicket
from app.services.support_bot import build_answer


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured_products = Product.objects.filter(in_stock=True).order_by('-sold_count', '-review', '-created_at')[:4]
        context['featured_products'] = featured_products
        context['hero_stats'] = {
            'products_count': Product.objects.count(),
            'discount_count': Product.objects.filter(is_discount=True).count(),
            'popular_count': Product.objects.filter(sold_count__gt=0).count(),
        }
        context['category_cards'] = [
            {'name': 'Telefonlar', 'slug': 'telefon', 'icon': '📱', 'count': Product.objects.filter(category__icontains='telefon').count()},
            {'name': 'Quloqchinlar', 'slug': 'quloqchin', 'icon': '🎧', 'count': Product.objects.filter(category__icontains='quloqchin').count()},
            {'name': 'Krossovkalar', 'slug': 'krossovka', 'icon': '👟', 'count': Product.objects.filter(category__icontains='krossovka').count()},
            {'name': 'Noutbuklar', 'slug': 'noutbuk', 'icon': '💻', 'count': Product.objects.filter(category__icontains='noutbuk').count()},
        ]
        return context


class ContactView(TemplateView):
    template_name = 'contact.html'

    def post(self, request, *args, **kwargs):
        name = (request.POST.get('name') or '').strip()
        phone_number = (request.POST.get('phone_number') or request.POST.get('phone') or request.POST.get('email') or '').strip()
        subject = (request.POST.get('subject') or 'Saytdan xabar').strip()
        message = (request.POST.get('message') or '').strip()

        if not name or not phone_number or not message:
            messages.error(request, "Ism, telefon/email va xabar maydonlarini to'ldiring.")
            return redirect('contact')

        Contact.objects.create(
            name=name,
            phone_number=phone_number,
            subject=subject,
            message=message,
        )
        messages.success(request, "Xabaringiz qabul qilindi. Tez orada siz bilan bog'lanamiz.")
        return redirect('contact')


class ProductView(TemplateView):
    template_name = 'product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        search = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        sort = self.request.GET.get('sort', '').strip()

        if search:
            products = products.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search) |
                Q(color__icontains=search) |
                Q(sizes__icontains=search)
            )
        if category:
            products = products.filter(category__icontains=category)
        if sort == 'cheap':
            products = products.order_by('price')
        elif sort == 'expensive':
            products = products.order_by('-price')
        elif sort == 'discount':
            products = products.filter(is_discount=True).order_by('price')

        context['products'] = products.distinct()
        context['recommended_products'] = Product.objects.filter(in_stock=True).order_by('-sold_count', '-review', 'price')[:4]
        context['search'] = search
        context['current_category'] = category
        context['current_sort'] = sort
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product-detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        similar_products = Product.objects.filter(in_stock=True).exclude(pk=product.pk)
        if product.category:
            similar_products = similar_products.filter(
                Q(category__icontains=product.category) | Q(title__icontains=product.category)
            )
        context['similar_products'] = similar_products.order_by('-sold_count', '-review', 'price')[:4]
        return context


class CartView(TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = None
        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(user=self.request.user, checked_out=False).prefetch_related('items__product').first()
        context['cart'] = cart
        context['cart_items'] = cart.items.all() if cart else []
        context['cart_total'] = cart.total_price if cart else 0
        return context


class BlogView(TemplateView):
    template_name = 'blog.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class LoginView(TemplateView):
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        username_or_email = request.POST.get('username') or request.POST.get('email') or ''
        password = request.POST.get('password') or ''

        username = username_or_email
        if '@' in username_or_email:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                username = user_obj.username

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Login yoki parol noto'g'ri.")
            return redirect('login')

        login(request, user)
        messages.success(request, "Xush kelibsiz!")
        return redirect('index')


class RegisterView(TemplateView):
    template_name = 'register.html'

    def post(self, request, *args, **kwargs):
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not email or not password:
            messages.error(request, "Email va parolni to'ldiring.")
            return redirect('register')
        if password != password2:
            messages.error(request, "Parollar bir xil emas.")
            return redirect('register')
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Bu email bilan foydalanuvchi mavjud.")
            return redirect('register')

        first_name = full_name
        user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name)
        login(request, user)
        messages.success(request, "Akkaunt yaratildi.")
        return redirect('index')


class CheckoutView(TemplateView):
    template_name = 'checkout.html'
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Checkout uchun avval login qiling.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.filter(user=self.request.user, checked_out=False).prefetch_related('items__product').first()
        context['cart'] = cart
        context['cart_items'] = cart.items.all() if cart else []
        context['cart_total'] = cart.total_price if cart else 0
        return context

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user, checked_out=False).prefetch_related('items__product').first()
        if not cart or not cart.items.exists():
            messages.error(request, "Savatcha bo'sh.")
            return redirect('cart')

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name', request.user.get_full_name()),
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
                payment_type=request.POST.get('payment_type', 'Naqd'),
                status=Order.STATUS_PROCESSING,
                total_amount=cart.total_price,
            )
            for item in cart.items.select_related('product'):
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_title=item.product.title,
                    price=item.product.price,
                    quantity=item.quantity,
                )
                item.product.sold_count += item.quantity
                item.product.save(update_fields=['sold_count'])
            cart.checked_out = True
            cart.save(update_fields=['checked_out'])

        messages.success(request, f"Buyurtma #{order.id} qabul qilindi. AI chat orqali 'Buyurtmam qayerda?' deb so'rashingiz mumkin.")
        return redirect('cart')


def logout_view(request):
    logout(request)
    messages.success(request, "Akkauntdan chiqdingiz.")
    return redirect('index')


@require_POST
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.info(request, "Savatchaga qo'shish uchun avval login qiling.")
        return redirect('login')

    product = get_object_or_404(Product, pk=product_id, in_stock=True)
    cart, _ = Cart.objects.get_or_create(user=request.user, checked_out=False)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save(update_fields=['quantity'])
    messages.success(request, f"{product.title} savatchaga qo'shildi.")
    return redirect(request.POST.get('next') or 'product')


@require_POST
def update_cart_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect('login')
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user, cart__checked_out=False)
    action = request.POST.get('action')
    if action == 'plus':
        item.quantity += 1
        item.save(update_fields=['quantity'])
    elif action == 'minus':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save(update_fields=['quantity'])
    elif action == 'remove':
        item.delete()
    return redirect('cart')


@ensure_csrf_cookie
def ai_chat_page(request):
    return render(request, 'ai_chat.html')


def _get_chat_session(request):
    """AI chat uchun barqaror session qaytaradi.

    Eski bazada bir xil session_key bilan bir nechta ChatSession yozuvi qolib ketgan
    bo'lsa, get_or_create() MultipleObjectsReturned xatosini beradi. Shuning uchun
    avval filter().first() qilamiz, topilmasa yaratamiz.
    """
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key or ''
    user = request.user if request.user.is_authenticated else None

    chat_session = ChatSession.objects.filter(session_key=session_key).order_by('-updated_at').first()
    if chat_session is None:
        chat_session = ChatSession.objects.create(session_key=session_key, user=user)

    update_fields = []
    if user and chat_session.user_id != user.id:
        chat_session.user = user
        update_fields.append('user')
    if session_key and chat_session.session_key != session_key:
        chat_session.session_key = session_key
        update_fields.append('session_key')
    if update_fields:
        chat_session.save(update_fields=update_fields)

    return chat_session


def _product_payload(product):
    return {
        'id': product.id,
        'title': product.title,
        'price': product.price,
        'price_display': f"{product.price:,}".replace(',', ' ') + " so'm",
        'old_price': product.old_price or 0,
        'old_price_display': (f"{product.old_price:,}".replace(',', ' ') + " so'm") if product.old_price else '',
        'discount_percent': product.discount_percent,
        'sold_count': product.sold_count,
        'review': product.review,
        'url': reverse('product_detail', args=[product.id]),
        'add_to_cart_url': reverse('add_to_cart', args=[product.id]),
        'category': product.category,
        'color': product.color,
        'sizes': product.sizes,
        'image_url': product.image_url,
    }


def _take_unseen_operator_reply(chat_session):
    """Admin operator javobini chatga qaytaradi va qayta-qayta ko'rsatmaydi."""
    ticket = (
        SupportTicket.objects
        .filter(
            session=chat_session,
            status=SupportTicket.STATUS_ANSWERED,
            operator_reply__gt='',
            operator_reply_seen=False,
        )
        .order_by('updated_at')
        .first()
    )
    if not ticket:
        return None
    ticket.operator_reply_seen = True
    ticket.save(update_fields=['operator_reply_seen'])
    chat_session.needs_operator = False
    chat_session.save(update_fields=['needs_operator'])
    return ticket


@csrf_exempt
@require_POST
def ai_chat_api(request):
    """Frontend chat uchun JSON API.

    Local/dev loyihalarda CSRF cookie ba'zan eski kesh yoki boshqa sahifadan kelganda
    403 berib, foydalanuvchiga "AI ishlamayapti" bo'lib ko'rinadi. Shuning uchun
    bu endpoint CSRF'dan ozod qilindi, lekin faqat POST va JSON/Form data qabul qiladi.
    """
    try:
        if request.content_type and 'application/json' in request.content_type:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        else:
            payload = request.POST
    except Exception:
        payload = {}

    message = (payload.get('message') or '').strip()

    try:
        chat_session = _get_chat_session(request)

        if message:
            ChatMessage.objects.create(session=chat_session, role=ChatMessage.ROLE_USER, text=message, confidence=1)

        operator_ticket = _take_unseen_operator_reply(chat_session)
        if operator_ticket:
            answer = f"Operator javobi:\n{operator_ticket.operator_reply}"
            ChatMessage.objects.create(session=chat_session, role=ChatMessage.ROLE_OPERATOR, text=operator_ticket.operator_reply, confidence=1)
            return JsonResponse({
                'answer': answer,
                'confidence': 1,
                'needs_operator': False,
                'operator_reply': True,
                'products': [],
            })

        result = build_answer(message, user=request.user, chat_session=chat_session)

        ChatMessage.objects.create(session=chat_session, role=ChatMessage.ROLE_BOT, text=result.answer, confidence=result.confidence)

        update_fields = []
        if result.last_product_id and chat_session.last_product_id != result.last_product_id:
            chat_session.last_product_id = result.last_product_id
            update_fields.append('last_product')
        if result.needs_operator and not chat_session.needs_operator:
            chat_session.needs_operator = True
            update_fields.append('needs_operator')
        if update_fields:
            chat_session.save(update_fields=update_fields)

        if result.needs_operator and message:
            # Bir xil ochiq savolni ketma-ket ko'paytirib yubormaslik uchun avval tekshiramiz.
            existing_ticket = SupportTicket.objects.filter(
                session=chat_session,
                question=message,
                status=SupportTicket.STATUS_OPEN,
            ).first()
            if existing_ticket:
                existing_ticket.bot_answer = result.answer
                existing_ticket.topic = getattr(result, 'topic', 'general') or 'general'
                existing_ticket.confidence = result.confidence
                existing_ticket.save(update_fields=['bot_answer', 'topic', 'confidence', 'updated_at'])
            else:
                SupportTicket.objects.create(
                    session=chat_session,
                    question=message,
                    bot_answer=result.answer,
                    topic=getattr(result, 'topic', 'general') or 'general',
                    confidence=result.confidence,
                )

        products = [_product_payload(product) for product in (result.products or [])]

        return JsonResponse({
            'answer': result.answer,
            'confidence': result.confidence,
            'needs_operator': result.needs_operator,
            'topic': getattr(result, 'topic', 'general') or 'general',
            'products': products,
        })
    except Exception as exc:
        # API endi 500 HTML qaytarmaydi; frontend doim tushunarli JSON oladi.
        return JsonResponse({
            'answer': "Kechirasiz, AI javob berishda ichki xatolik bo'ldi. `python manage.py migrate` qilib, serverni qayta ishga tushiring.",
            'confidence': 0,
            'needs_operator': True,
            'products': [],
            'error': str(exc) if request.user.is_staff else '',
        }, status=200)

import os

from django.conf import settings
from django.db import models
from django.templatetags.static import static
from django.utils import timezone


class Contact(models.Model):
    name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=30)
    subject = models.CharField(max_length=160, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.phone_number}"


class Portfolio(models.Model):
    img = models.FileField(upload_to='portfolio/', blank=True)
    title = models.CharField(max_length=160)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateField(default=timezone.now)
    author = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.title


TITLE_IMAGE_RULES = {
    'qora krossovka urban step': 'products/black-sneakers-real.png',
    'qora airbass quloqchin': 'products/airbass-earbuds-real-v2.png',
    'oq minipods quloqchin': 'products/white-minipods-real.png',
    'iphone 16 pro': 'products/iphone-16-pro-gold-real.png',
    'samsung galaxy s25 ultra': 'products/samsung-galaxy-s25-ultra-real-v2.png',
    'macbook': 'products/macbook-real.png',
    "mikroto'lqinli pech": 'products/microwave-oven-real.png',
    'xiaomi redmi note 13': 'products/xiaomi-redmi-note-13-real-v2.png',
    'iphone 15': 'products/iphone-15-real.png',
    'samsung galaxy a55': 'products/samsung-galaxy-a55-real-v2.png',
    'asus vivobook 15': 'products/asus-vivobook-15-real.png',
    'lenovo ideapad 3': 'products/lenovo-ideapad-3-real.png',
    'hp pavilion gaming': 'products/hp-pavilion-gaming-real.png',
    'jbl tune 510bt': 'products/jbl-tune-510bt-real-v2.png',
    'samsung galaxy buds2': 'products/samsung-galaxy-buds2-real.png',
    'anker soundcore q20i': 'products/anker-soundcore-q20i-real-v2.png',
    'samsung crystal uhd 43': 'products/samsung-crystal-uhd-43-real.png',
    'lg oled evo c3 65': 'products/smart-tv-lg-real.png',
    'nike air max 90': 'products/nike-air-max-90-real.png',
    'adidas ultraboost 22': 'products/adidas-ultraboost-22-real.png',
    'reebok classic leather': 'products/reebok-classic-leather-real.png',
    'philips air fryer hd9200': 'products/microwave-oven-real.png',
    'bosch blender mmb2111m': 'products/bosch-blender-mmb2111m-real.png',
    'xiaomi smart air purifier 4': 'products/xiaomi-smart-air-purifier-4-real.png',
    'smart tv': 'products/smart-tv-lg-real.png',
}


PRODUCT_IMAGE_RULES = (
    (("iphone", "16"), "products/iphone-16-pro-real.png"),
    (("iphone", "15"), "products/iphone-16-pro-real.png"),
    (("iphone",), "products/iphone-16-pro-real.png"),
    (("samsung", "s25"), "products/samsung-galaxy-s25-ultra-real-v2.png"),
    (("galaxy", "s25"), "products/samsung-galaxy-s25-ultra-real-v2.png"),
    (("samsung", "a55"), "products/samsung-galaxy-a55-real-v2.png"),
    (("samsung", "galaxy"), "products/samsung-galaxy-s25-ultra-real-v2.png"),
    (("xiaomi",), "products/xiaomi-redmi-note-13-real-v2.png"),
    (("redmi",), "products/xiaomi-redmi-note-13-real-v2.png"),
    (("macbook",), "products/macbook-pro-real.png"),
    (("asus",), "products/macbook-pro-real.png"),
    (("lenovo",), "products/macbook-pro-real.png"),
    (("hp", "pavilion"), "products/macbook-pro-real.png"),
    (("smart tv",), "products/smart-tv-lg-real.png"),
    (("televizor",), "products/smart-tv-lg-real.png"),
    (("samsung", "crystal"), "products/smart-tv-lg-real.png"),
    (("lg", "oled"), "products/smart-tv-lg-real.png"),
    (("mikro", "pech"), "products/microwave-oven-real.png"),
    (("air fryer",), "products/microwave-oven-real.png"),
    (("blender",), "products/microwave-oven-real.png"),
    (("purifier",), "products/microwave-oven-real.png"),
    (("krossovka",), "products/black-sneakers-real.png"),
    (("sneaker",), "products/black-sneakers-real.png"),
    (("nike",), "products/black-sneakers-real.png"),
    (("adidas",), "products/black-sneakers-real.png"),
    (("reebok",), "products/black-sneakers-real.png"),
    (("jbl",), "products/jbl-tune-510bt-real-v2.png"),
    (("soundcore",), "products/anker-soundcore-q20i-real-v2.png"),
    (("anker",), "products/anker-soundcore-q20i-real-v2.png"),
    (("galaxy", "buds"), "products/white-minipods-real.png"),
    (("airbass",), "products/black-earbuds-real.png"),
    (("minipods",), "products/white-minipods-real.png"),
    (("quloqchin",), "products/black-earbuds-real.png"),
)


def guess_product_image(title='', category='', color=''):
    """Mahsulot nomiga qarab local media ichidagi eng mos rasmni tanlaydi.

    Eslatma: "oq" so'zini oddiy substring sifatida tekshirmaymiz, chunki
    "quloqchin" so'zi ichida ham "oq" harflari ketma-ket keladi.
    """
    title_text = (title or '').lower()
    category_text = (category or '').lower()
    color_text = (color or '').lower().strip()
    text = f"{title_text} {category_text} {color_text}"
    normalized = f" {text.replace('-', ' ').replace('_', ' ')} "

    exact_title_match = TITLE_IMAGE_RULES.get(title_text.strip())
    if exact_title_match:
        return exact_title_match

    if 'minipods' in text or ('quloqchin' in text and (color_text == 'oq' or ' white ' in normalized or ' oq ' in normalized)):
        return 'products/white-minipods-real.png'

    # Maishiy texnika nomlari telefon brandlari bilan to'qnashsa ham, avval maxsus mahsulot rasmini tekshiramiz.
    if 'blender' in text:
        return 'products/bosch-blender-mmb2111m-real.png'
    if 'purifier' in text:
        return 'products/xiaomi-smart-air-purifier-4-real.png'
    if category_text.strip() == 'maishiy texnika' or any(keyword in text for keyword in ('air fryer', 'mikro', 'pech')):
        return 'products/microwave-oven-real.png'

    for keywords, image_path in PRODUCT_IMAGE_RULES:
        if all(keyword in text for keyword in keywords):
            return image_path

    category_map = {
        'telefon': 'products/iphone-16-pro-gold-real.png',
        'quloqchin': 'products/black-earbuds-real.png',
        'krossovka': 'products/black-sneakers-real.png',
        'noutbuk': 'products/macbook-real.png',
        'televizor': 'products/smart-tv-lg-real.png',
        'maishiy texnika': 'products/microwave-oven-real.png',
    }
    return category_map.get(category_text.strip(), '')


class Product(models.Model):
    img = models.FileField(upload_to='products/', blank=True)
    title = models.CharField(max_length=180)
    review = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    old_price = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=120, blank=True)

    # AI tavsiya tizimi uchun qo'shimcha maydonlar
    category = models.CharField(max_length=80, default='general', db_index=True)
    color = models.CharField(max_length=80, blank=True, default='')
    sizes = models.CharField(max_length=180, blank=True, default='', help_text="Masalan: 39, 40, 41 yoki S, M, L")
    in_stock = models.BooleanField(default=True)
    is_discount = models.BooleanField(default=False)
    sold_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-sold_count', '-review', '-created_at']

    def __str__(self):
        return self.title

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) * 100 / self.old_price)
        return 0

    def save(self, *args, **kwargs):
        # Agar admin/baza orqali mahsulot rasmi berilmagan bo'lsa yoki eski svg biriktirilgan bo'lsa,
        # nomi va kategoriyasiga mos real rasm biriktiriladi.
        current_name = getattr(self.img, 'name', '') if self.img else ''
        guessed = guess_product_image(self.title, self.category, self.color)
        should_replace = (not self.img) or str(current_name).lower().endswith('.svg')
        if guessed and TITLE_IMAGE_RULES.get((self.title or '').lower().strip()) and str(current_name) != guessed:
            should_replace = True
        if should_replace and guessed:
            self.img = guessed
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        """Mahsulot rasmi topilmasa ham sayt buzilmasin: avval real media, keyin nomga mos rasm, oxirida placeholder."""
        placeholder_map = {
            'telefon': 'images/placeholders/phone.svg',
            'quloqchin': 'images/placeholders/earbuds.svg',
            'krossovka': 'images/placeholders/sneakers.svg',
            'noutbuk': 'images/placeholders/laptop.svg',
            'televizor': 'images/placeholders/tv.svg',
            'maishiy texnika': 'images/placeholders/appliance.svg',
            'general': 'images/placeholders/default.svg',
        }

        def media_url_if_exists(relative_path):
            if not relative_path:
                return ''
            relative_path = str(relative_path).replace('\\', '/').lstrip('/')

            preferred_paths = []
            if relative_path.lower().endswith('.svg'):
                preferred_paths.append(relative_path[:-4] + '-real.png')
            preferred_paths.append(relative_path)

            for preferred_path in preferred_paths:
                candidates = [
                    os.path.join(settings.MEDIA_ROOT, preferred_path),
                    os.path.join(settings.BASE_DIR, 'media', preferred_path),
                ]
                basename = os.path.basename(preferred_path)
                if basename:
                    candidates.append(os.path.join(settings.MEDIA_ROOT, 'products', basename))
                for candidate in candidates:
                    if os.path.exists(candidate):
                        rel = os.path.relpath(candidate, settings.MEDIA_ROOT).replace('\\', '/')
                        return settings.MEDIA_URL + rel
            return ''

        if self.img and getattr(self.img, 'name', ''):
            found_url = media_url_if_exists(self.img.name)
            if found_url:
                return found_url

        guessed = guess_product_image(self.title, self.category, self.color)
        found_url = media_url_if_exists(guessed)
        if found_url:
            return found_url

        return static(placeholder_map.get(self.category, 'images/placeholders/default.svg'))


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    checked_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.pk} - {self.user}"

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.select_related('product'))

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.select_related('product'))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_PROCESSING = 'processing'
    STATUS_DELIVERING = 'delivering'
    STATUS_DONE = 'done'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Yangi'),
        (STATUS_PROCESSING, 'Tayyorlanmoqda'),
        (STATUS_DELIVERING, 'Yetkazib berilmoqda'),
        (STATUS_DONE, 'Yetkazildi'),
        (STATUS_CANCELLED, 'Bekor qilindi'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    payment_type = models.CharField(max_length=60, default='Naqd')
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_NEW, db_index=True)
    total_amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Buyurtma #{self.pk} - {self.get_status_display()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_title = models.CharField(max_length=180)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_title} x {self.quantity}"


class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_sessions')
    session_key = models.CharField(max_length=80, blank=True, db_index=True)
    last_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    needs_operator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        owner = self.user if self.user_id else self.session_key or 'anonymous'
        return f"Chat - {owner}"


class ChatMessage(models.Model):
    ROLE_USER = 'user'
    ROLE_BOT = 'bot'
    ROLE_OPERATOR = 'operator'
    ROLE_CHOICES = [
        (ROLE_USER, 'Foydalanuvchi'),
        (ROLE_BOT, 'Bot'),
        (ROLE_OPERATOR, 'Operator'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    text = models.TextField()
    confidence = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_role_display()}: {self.text[:50]}"


class SupportTicket(models.Model):
    STATUS_OPEN = 'open'
    STATUS_ANSWERED = 'answered'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Ochiq'),
        (STATUS_ANSWERED, 'Javob berilgan'),
        (STATUS_CLOSED, 'Yopilgan'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='tickets')
    question = models.TextField()
    bot_answer = models.TextField(blank=True)
    operator_reply = models.TextField(blank=True)
    operator_reply_seen = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN, db_index=True)
    topic = models.CharField(max_length=60, blank=True, default='general', db_index=True)
    confidence = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.pk} - {self.get_status_display()}"

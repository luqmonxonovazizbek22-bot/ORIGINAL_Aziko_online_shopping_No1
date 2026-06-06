# AI support, orders and product recommendation fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_ai_products(apps, schema_editor):
    Product = apps.get_model('app', 'Product')

    def upsert(title, defaults):
        obj = Product.objects.filter(title__iexact=title).first()
        if obj:
            for key, value in defaults.items():
                setattr(obj, key, value)
            obj.save()
        else:
            Product.objects.create(title=title, **defaults)

    # Mavjud mahsulotlarni AI qidiruv uchun kategoriyalab qo'yamiz.
    for product in Product.objects.all():
        title = (product.title or '').lower()
        description = (product.description or '').lower()
        text = title + ' ' + description
        if any(word in text for word in ['iphone', 'samsung', 'galaxy', 'smartfon', 'phone']):
            product.category = 'telefon'
            product.color = product.color or 'qora'
            product.sizes = product.sizes or '128GB, 256GB, 512GB'
        elif any(word in text for word in ['macbook', 'noutbuk', 'ноутбук']):
            product.category = 'noutbuk'
            product.color = product.color or 'kulrang'
            product.sizes = product.sizes or '14 dyuym, 16 dyuym'
        elif any(word in text for word in ['tv', 'televizor', 'телевизор']):
            product.category = 'televizor'
            product.sizes = product.sizes or '55 dyuym'
        elif any(word in text for word in ['pech', 'mikro']):
            product.category = 'maishiy texnika'
        product.in_stock = True
        product.sold_count = product.sold_count or product.review or 5
        product.save()

    upsert('Qora krossovka Urban Step', {
        'img': '',
        'review': 5,
        'description': "Yengil, kundalik kiyishga qulay qora krossovka. Sport va casual obraz uchun mos.",
        'price': 449000,
        'old_price': 529000,
        'author': 'AZIKO MARKET',
        'category': 'krossovka',
        'color': 'qora',
        'sizes': '39, 40, 41, 42, 43',
        'in_stock': True,
        'is_discount': True,
        'sold_count': 78,
    })
    upsert('Qora AirBass quloqchin', {
        'img': '',
        'review': 5,
        'description': "Telefon uchun Bluetooth quloqchin, shovqinni kamaytirish va uzoq batareya.",
        'price': 299000,
        'old_price': 399000,
        'author': 'AZIKO MARKET',
        'category': 'quloqchin',
        'color': 'qora',
        'sizes': 'universal',
        'in_stock': True,
        'is_discount': True,
        'sold_count': 120,
    })
    upsert('Oq MiniPods quloqchin', {
        'img': '',
        'review': 4,
        'description': "iPhone va Android telefonlar uchun yengil simsiz quloqchin.",
        'price': 219000,
        'old_price': None,
        'author': 'AZIKO MARKET',
        'category': 'quloqchin',
        'color': 'oq',
        'sizes': 'universal',
        'in_stock': True,
        'is_discount': False,
        'sold_count': 64,
    })


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(db_index=True, default='general', max_length=80),
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.CharField(blank=True, default='', help_text='Masalan: 39, 40, 41 yoki S, M, L', max_length=180),
        ),
        migrations.AddField(
            model_name='product',
            name='in_stock',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_discount',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='sold_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=160)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('payment_type', models.CharField(default='Naqd', max_length=60)),
                ('status', models.CharField(choices=[('new', 'Yangi'), ('processing', 'Tayyorlanmoqda'), ('delivering', 'Yetkazib berilmoqda'), ('done', 'Yetkazildi'), ('cancelled', 'Bekor qilindi')], db_index=True, default='new', max_length=24)),
                ('total_amount', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=80)),
                ('needs_operator', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_sessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_title', models.CharField(max_length=180)),
                ('price', models.PositiveIntegerField(default=0)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.product')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'Foydalanuvchi'), ('bot', 'Bot'), ('operator', 'Operator')], max_length=20)),
                ('text', models.TextField()),
                ('confidence', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='app.chatsession')),
            ],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='SupportTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('bot_answer', models.TextField(blank=True)),
                ('operator_reply', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('open', 'Ochiq'), ('answered', 'Javob berilgan'), ('closed', 'Yopilgan')], db_index=True, default='open', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='app.chatsession')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.RunPython(seed_ai_products, migrations.RunPython.noop),
    ]

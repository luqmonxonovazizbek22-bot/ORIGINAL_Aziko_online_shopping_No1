from django.db import migrations


DEMO_PRODUCTS = [
    {
        'title': 'Iphone 16 pro',
        'img': 'products/iphone-16-pro.svg',
        'review': 5,
        'description': "Apple iPhone 16 Pro — premium smartfon. Kuchli kamera, tezkor chip, sifatli displey va stabil ishlashi bilan foto, video, o'qish, ish va kundalik foydalanish uchun mos. Xotira variantlari: 128GB, 256GB, 512GB. Premium telefon izlayotganlar uchun yaxshi tanlov.",
        'price': 19322600,
        'old_price': 19990000,
        'author': 'AZIKO MARKET',
        'category': 'telefon',
        'color': 'qora',
        'sizes': '128GB, 256GB, 512GB',
        'in_stock': True,
        'is_discount': True,
        'sold_count': 87,
    },
    {
        'title': 'Samsung Galaxy s25 ultra',
        'img': 'products/samsung-s25-ultra.svg',
        'review': 5,
        'description': "Samsung Galaxy S25 Ultra — Android flagman. Katta ekran, kuchli kamera, uzoq batareya va tezkor ishlashi bilan o'yin, foto/video, ish va multimedia uchun mos. iPhone bilan taqqoslaganda Android erkinligi va katta ekran tarafdan kuchli.",
        'price': 14090000,
        'old_price': 14990000,
        'author': 'AZIKO MARKET',
        'category': 'telefon',
        'color': 'qora',
        'sizes': '128GB, 256GB, 512GB',
        'in_stock': True,
        'is_discount': True,
        'sold_count': 92,
    },
    {
        'title': 'MacBook',
        'img': 'products/macbook-pro.svg',
        'review': 5,
        'description': "MacBook — o'qish, ish, dizayn, dasturlash va kontent yaratish uchun kuchli noutbuk. Yengil korpus, tez ishlash, sifatli ekran va uzoq batareya bilan sahna prezentatsiyasi, ofis va kreativ ishlar uchun qulay.",
        'price': 55000000,
        'old_price': None,
        'author': 'AZIKO MARKET',
        'category': 'noutbuk',
        'color': 'kulrang',
        'sizes': '14 dyuym, 16 dyuym',
        'in_stock': True,
        'is_discount': False,
        'sold_count': 31,
    },
    {
        'title': 'Smart TV',
        'img': 'products/smart-tv-lg.svg',
        'review': 4,
        'description': "Smart TV — 55 dyuymli katta ekranli televizor. YouTube, kino, serial, sport va streaming ko'rish uchun qulay. Uyda katta ekranda sifatli ko'ngilochar kontent ko'rishni xohlaganlar uchun mos variant.",
        'price': 6100000,
        'old_price': 6900000,
        'author': 'AZIKO MARKET',
        'category': 'televizor',
        'color': 'qora',
        'sizes': '55 dyuym',
        'in_stock': True,
        'is_discount': True,
        'sold_count': 45,
    },
    {
        'title': "Mikroto'lqinli Pech",
        'img': 'products/microwave-oven.svg',
        'review': 4,
        'description': "Mikroto'lqinli pech — oshxona uchun tez isitish, ovqatni muzdan tushirish va kundalik qulaylik yaratish uchun kerakli maishiy texnika. 20L hajm uy sharoiti uchun yetarli va ixcham.",
        'price': 1200000,
        'old_price': 1390000,
        'author': 'AZIKO MARKET',
        'category': 'maishiy texnika',
        'color': 'oq',
        'sizes': '20L',
        'in_stock': True,
        'is_discount': True,
        'sold_count': 53,
    },
    {
        'title': 'Qora krossovka Urban Step',
        'img': 'products/black-sneakers.svg',
        'review': 5,
        'description': "Qora krossovka Urban Step — kundalik yurish, sport uslubi va casual kiyimlar uchun mos. Qora rang deyarli barcha kiyimlarga tushadi, yengil taglik esa uzoq yurishda qulaylik beradi. Razmerlar: 39–43.",
        'price': 449000,
        'old_price': 529000,
        'author': 'AZIKO MARKET',
        'category': 'krossovka',
        'color': 'qora',
        'sizes': '39, 40, 41, 42, 43',
        'in_stock': True,
        'is_discount': True,
        'sold_count': 78,
    },
    {
        'title': 'Qora AirBass quloqchin',
        'img': 'products/black-earbuds.svg',
        'review': 5,
        'description': "Qora AirBass quloqchin — Bluetooth simsiz quloqchin. Telefon bilan musiqa eshitish, video ko'rish va qo'ng'iroq qilish uchun mos. Qora rang zamonaviy ko'rinadi, narxi ham byudjetga mos. Shovqinni kamaytirish va uzoq batareya afzalligi bor.",
        'price': 299000,
        'old_price': 399000,
        'author': 'AZIKO MARKET',
        'category': 'quloqchin',
        'color': 'qora',
        'sizes': 'universal',
        'in_stock': True,
        'is_discount': True,
        'sold_count': 120,
    },
    {
        'title': 'Oq MiniPods quloqchin',
        'img': 'products/white-minipods.svg',
        'review': 4,
        'description': "Oq MiniPods quloqchin — iPhone va Android uchun yengil simsiz quloqchin. Kundalik qo'ng'iroq, dars, video va musiqa uchun mos. Arzonroq, ixcham va universal variant izlaganlar uchun yaxshi tanlov.",
        'price': 199000,
        'old_price': None,
        'author': 'AZIKO MARKET',
        'category': 'quloqchin',
        'color': 'oq',
        'sizes': 'universal',
        'in_stock': True,
        'is_discount': False,
        'sold_count': 64,
    },
]


def seed_products(apps, schema_editor):
    Product = apps.get_model('app', 'Product')
    for data in DEMO_PRODUCTS:
        obj = Product.objects.filter(title__iexact=data['title']).first()
        if obj is None:
            Product.objects.create(**data)
            continue
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0003_alter_product_options_alter_contact_name_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_products, migrations.RunPython.noop),
    ]

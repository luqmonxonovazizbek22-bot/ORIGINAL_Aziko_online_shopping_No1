from django.core.management.base import BaseCommand

from app.models import Product, guess_product_image


class Command(BaseCommand):
    help = "Mahsulot nomi/kategoriyasiga qarab yetishmayotgan product rasmlarini avtomatik biriktiradi."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Barcha mahsulotlarning rasm yo‘lini qayta hisoblab yozadi.',
        )

    def handle(self, *args, **options):
        force = options['force']
        updated = 0
        skipped = 0

        for product in Product.objects.all():
            guessed = guess_product_image(product.title, product.category, product.color)
            if not guessed:
                skipped += 1
                continue

            if force or not product.img:
                if product.img != guessed:
                    product.img = guessed
                    product.save(update_fields=['img'])
                    updated += 1
                else:
                    skipped += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"Tayyor: {updated} ta mahsulot rasmi yangilandi, {skipped} ta o‘tkazildi."))

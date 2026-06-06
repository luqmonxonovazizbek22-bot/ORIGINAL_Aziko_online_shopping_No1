import re
from dataclasses import dataclass
from typing import Optional

from django.db.models import Q
from django.urls import reverse

from app.models import CartItem, Order, Product


COLORS = {
    "qora": ["qora", "black", "черный", "чёрный", "темный", "тёмный"],
    "oq": ["oq", "white", "белый", "белая"],
    "ko'k": ["ko'k", "kok", "blue", "синий", "синяя", "голубой"],
    "qizil": ["qizil", "red", "красный", "красная"],
    "yashil": ["yashil", "green", "зеленый", "зелёный"],
    "kulrang": ["kulrang", "gray", "grey", "серый", "серебристый", "silver"],
}

CATEGORY_KEYWORDS = {
    # Tartib muhim: "telefon uchun quloqchin" so'rovida asosiy mahsulot quloqchin bo'lishi kerak.
    "quloqchin": [
        "quloqchin", "naushnik", "airpods", "earbuds", "headphone", "earphone",
        "наушник", "наушники", "гарнитура", "jbl", "anker", "soundcore",
        "buds", "pods", "minipods", "airbass",
    ],
    "krossovka": [
        "krossovka", "oyoq kiyim", "poyabzal", "sneaker", "sneakers",
        "кроссовк", "обувь", "ботинка", "nike", "adidas", "reebok",
        "puma", "new balance", "oyoq", "tufli",
    ],
    "telefon": [
        "telefon", "phone", "iphone", "ayfon", "samsung", "galaxy",
        "smartfon", "смартфон", "телефон", "айфон", "xiaomi", "redmi",
        "huawei", "realme", "oppo", "oneplus", "pixel",
    ],
    "noutbuk": [
        "noutbuk", "laptop", "macbook", "notebook", "ноутбук", "макбук",
        "компьютер", "asus", "lenovo", "hp", "dell", "acer", "vivobook",
        "ideapad", "thinkpad", "pavilion", "gaming laptop",
    ],
    "televizor": [
        "tv", "televizor", "smart tv", "телевизор", "samsung tv", "lg tv",
        "oled", "qled", "uhd", "4k tv", "55 dyuym", "43 dyuym", "65 dyuym",
    ],
    "maishiy texnika": [
        "pech", "mikroto", "mikroto'lqinli", "changyutgich", "muzlatkich",
        "texnika", "maishiy", "печь", "микроволновка", "пылесос", "холодильник",
        "blender", "fryer", "air fryer", "purifier", "havo tozalagich",
        "bosch", "philips", "xiaomi texnika",
    ],
}

FAQ_ANSWERS = [
    (
        ["yetkazib", "dostavka", "delivery", "necha kunda", "olib kel", "доставка", "доставят"],
        "Yetkazib berish odatda Toshkent bo'yicha 1-2 kun, viloyatlarga 2-5 ish kuni ichida amalga oshiriladi. Aniq muddat mahsulot, manzil va kuryer yuklamasiga qarab o'zgaradi.",
        "delivery",
    ),
    (
        ["qaytar", "return", "almash", "vozvrat", "возврат", "обмен"],
        "Ha, mahsulotni qabul qilgandan keyin qadoq, chek va mahsulot holati saqlangan bo'lsa, 14 kun ichida qaytarish yoki almashtirish bo'yicha murojaat qilishingiz mumkin.",
        "return_policy",
    ),
    (
        ["to'lov", "tolov", "naqd", "click", "payme", "karta", "payment", "оплата", "налич", "картой"],
        "To'lov usullari: naqd, karta, Click va Payme. Checkout sahifasida kerakli to'lov turini tanlashingiz mumkin.",
        "payment",
    ),
    (
        ["kafolat", "garantiya", "warranty", "гарантия"],
        "Kafolat muddati mahsulot turiga bog'liq. Elektronika mahsulotlarida odatda kafolat taloni yoki ishlab chiqaruvchi kafolati bo'ladi.",
        "warranty",
    ),
    (
        ["operator", "odam bilan gaplash", "admin", "consultant", "konsultant", "менеджер", "оператор"],
        "Albatta. Bu so'rovni operator uchun belgiladim. Admin panelda savolingiz ko'rinadi va operator qo'lda javob yozishi mumkin.",
        "operator",
    ),
    (
        ["bog'lanish", "aloqa", "kontakt", "contact", "связь", "контакт", "telefon raqam"],
        "Bog'lanish uchun: +998 90 000 00 00 yoki hello@azikomarket.uz. Contact sahifasi orqali ham yozishingiz mumkin.",
        "contact",
    ),
]

THANKS_WORDS = ["rahmat", "thank", "thanks", "spasibo", "спасибо", "katta rahmat", "raxmat"]
GREETING_WORDS = ["salom", "assalom", "assalomu alaykum", "hello", "hi", "privet", "привет", "здравствуйте", "добрый"]
CAPABILITY_WORDS = [
    "nima qila olasan", "nima qilasan", "help", "yordam", "qanday yordam",
    "what can you do", "что умеешь", "что можешь", "помощь", "imkoniyat",
]
COMPARE_WORDS = ["taqqosla", "solishtir", "compare", "farqi", "qaysi yaxshi", "сравни", "сравнение", "отличие", "лучше"]
DETAIL_WORDS = ["shu mahsulot", "bu mahsulot", "batafsil", "detail", "характеристика", "подробнее", "ma'lumot", "malumot", "расскажи", "описание"]
SIMILAR_WORDS = ["o'xshash", "oxshash", "shunga o'xshash", "alternativ", "alternativa", "similar", "похож", "аналог", "замена"]
PERSONAL_WORDS = ["men uchun", "menga mos", "personal", "shaxsiy", "qiziqishim", "qiziqishiga qarab", "oldingi xarid", "прошл", "подбери", "мне подходит", "для меня"]
DISCOUNT_WORDS = ["chegirma", "aksiya", "discount", "sale", "скидка", "акция", "arzonlashtirilgan"]
POPULAR_WORDS = ["eng ko'p sotilgan", "kop sotilgan", "ko'p sotilgan", "mashhur", "popular", "top", "best", "хит", "популяр", "самый продаваемый"]
PRODUCT_INTENT_WORDS = [
    "kerak", "tavsiya", "topib ber", "qidir", "bor", "mahsulot", "narx", "arzon", "qimmat",
    "chegirma", "aksiya", "sotilgan", "telefon", "quloqchin", "krossovka", "noutbuk", "tv", "pech",
    "olmoqchiman", "tanla", "ko'rsat", "korsat", "qancha", "necha pul", "variant", "modellari",
    "best", "top", "recommend", "find", "show", "price", "cheap", "expensive",
    "подбери", "посоветуй", "товар", "цена", "скидка", "нужен", "нужна", "нужно",
    "найди", "покажи", "есть", "купить", "дешев", "дорог", "вариант",
    # Brand names
    "iphone", "samsung", "xiaomi", "apple", "macbook", "asus", "lenovo", "hp", "jbl", "anker",
    "nike", "adidas", "reebok", "puma", "lg", "bosch", "philips",
    # More Uzbek
    "olib berchi", "sotib olmoqchi", "izlayapman", "kerakli", "qaysi",
    "redmi", "galaxy", "buds", "airpods", "ultraboost", "air max",
]

CASUAL_ANSWERS = [
    (["nima gap", "qalesan", "qalaysan", "yaxshimisan", "как дела", "как ты"],
     "Yaxshi, rahmat 😊 Men tayyorman: mahsulot topib beraman, narx solishtiraman, tavsiya qilaman yoki buyurtma holatini tushuntiraman."),
    (["isming", "kimsan", "kim san", "как тебя зовут", "кто ты"],
     "Men AZIKO MARKET AI yordamchisiman. Vazifam — online do'konda mahsulot tavsiya qilish, o'xshash mahsulot topish va mijoz savollariga tez javob berish."),
    (["hazil", "joke", "анекдот"],
     "Mayli 😄 Online do'kondagi eng chaqqon narsa nima? Savatcha — bir bosishda to'lib qoladi! Endi xohlasangiz, sizga mahsulot ham tanlab beraman."),
    (["assistent", "assistant", "ai", "бот", "робот"],
     "Ha, men AI yordamchiman. Savolingizni erkin yozing: masalan, '1 mln so'mgacha telefon kerak', 'qora quloqchin bormi?' yoki 'qaysi biri yaxshi?'."),
]


@dataclass
class BotResult:
    answer: str
    confidence: float = 0.0
    products: Optional[list] = None
    last_product_id: Optional[int] = None
    needs_operator: bool = False
    topic: str = "general"


def normalize(text: str) -> str:
    return (
        (text or "")
        .lower()
        .replace("ʻ", "'")
        .replace("’", "'")
        .replace("`", "'")
        .replace("ё", "е")
        .strip()
    )


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zа-я0-9']+", normalize(text), flags=re.IGNORECASE)


def keyword_found(text: str, keyword: str) -> bool:
    text_norm = normalize(text)
    keyword_norm = normalize(keyword)
    if not keyword_norm:
        return False

    tokens = set(tokenize(text_norm))

    # Juda qisqa so'zlar faqat to'liq token bo'lsa ishlaydi.
    # Masalan: "hi" so'zi "quloqchin" ichidan topilib ketmasligi kerak.
    if len(keyword_norm) <= 3 and " " not in keyword_norm:
        return keyword_norm in tokens

    if " " in keyword_norm:
        return keyword_norm in text_norm

    return keyword_norm in tokens or any(token.startswith(keyword_norm) for token in tokens)


def any_keyword(text: str, keywords: list[str]) -> bool:
    return any(keyword_found(text, keyword) for keyword in keywords)


def parse_price(text: str) -> Optional[int]:
    text = normalize(text).replace(",", ".")
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:mln|million|млн)",
        r"(\d+(?:\.\d+)?)\s*(?:ming|минг|тыс|k)",
        r"(\d{5,})",
    ]
    for idx, pattern in enumerate(patterns):
        match = re.search(pattern, text)
        if not match:
            continue
        number = float(match.group(1))
        if idx == 0:
            return int(number * 1_000_000)
        if idx == 1:
            return int(number * 1_000)
        return int(number)
    return None


def detect_price_mode(text: str) -> str:
    text = normalize(text)
    if any_keyword(text, ["gacha", "oshmasin", "dan kam", "до", "не дороже", "максимум", "max", "maximum"]):
        return "max"
    if any_keyword(text, ["dan qimmat", "yuqori", "от", "дороже", "minimum", "min"]):
        return "min"
    return "max"


def detect_color(text: str) -> str:
    for canonical, words in COLORS.items():
        if any_keyword(text, words):
            return canonical
    return ""


def detect_category(text: str) -> str:
    for category, words in CATEGORY_KEYWORDS.items():
        if any_keyword(text, words):
            return category
    return ""


def money(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " so'm"


def product_link(product: Product) -> str:
    try:
        return reverse("product_detail", args=[product.pk])
    except Exception:
        return "/product/"


def product_text(product: Product) -> str:
    return normalize(" ".join([
        product.title or "",
        product.description or "",
        product.category or "",
        product.color or "",
        product.sizes or "",
    ]))


def _user_interest_categories(user=None, chat_session=None) -> list[str]:
    categories: list[str] = []
    if chat_session and chat_session.last_product_id and chat_session.last_product and chat_session.last_product.category:
        categories.append(chat_session.last_product.category)

    if user and getattr(user, "is_authenticated", False):
        cart_items = CartItem.objects.filter(
            cart__user=user,
            cart__checked_out=False,
        ).select_related("product").order_by("-updated_at")[:8]
        categories.extend(item.product.category for item in cart_items if item.product and item.product.category)

        orders = Order.objects.filter(user=user).prefetch_related("items__product")[:5]
        for order in orders:
            for item in order.items.all():
                if item.product and item.product.category:
                    categories.append(item.product.category)

    unique = []
    for category in categories:
        if category and category not in unique:
            unique.append(category)
    return unique


def _rank_products(products, text: str = "", user=None, chat_session=None, strict_budget: bool = True):
    text_norm = normalize(text)
    tokens = [token for token in tokenize(text_norm) if len(token) > 2]
    price_value = parse_price(text_norm)
    price_mode = detect_price_mode(text_norm)
    color = detect_color(text_norm)
    category = detect_category(text_norm)
    interest_categories = _user_interest_categories(user, chat_session)
    wants_discount = any_keyword(text_norm, DISCOUNT_WORDS) or any_keyword(text_norm, ["arzon", "cheap", "дешев"])
    wants_popular = any_keyword(text_norm, POPULAR_WORDS)

    ranked = []
    for product in products:
        if not product.in_stock:
            continue
        p_text = product_text(product)
        p_category = normalize(product.category or '')
        p_title = normalize(product.title or '')

        # Kategoriya filtri tavsif ichidagi tasodifiy so'zga emas, asosan category/title ga qaraydi.
        # Masalan quloqchin tavsifida "telefon uchun" borligi uni telefon sifatida chiqarib yubormasligi kerak.
        if category and category not in p_category and category not in p_title:
            continue
        if color and color not in p_text:
            continue
        if price_value:
            if price_mode == "max":
                limit = price_value if strict_budget else int(price_value * 1.25)
                if product.price > limit:
                    continue
            elif price_mode == "min" and product.price < price_value:
                continue

        score = 0
        if category and (category in p_category or category in p_title):
            score += 45
        if color and color in p_text:
            score += 28
        if price_value:
            if price_mode == "max":
                if product.price <= price_value:
                    score += 34
                    score += max(0, 12 - int((price_value - product.price) / max(price_value, 1) * 12))
                else:
                    score += 6
            else:
                if product.price >= price_value:
                    score += 24
        if wants_discount and (product.is_discount or product.discount_percent):
            score += 30
        if wants_discount and product.old_price and product.old_price > product.price:
            score += product.discount_percent
        if wants_popular:
            score += min(product.sold_count, 150) // 4 + product.review * 2
        if product.category in interest_categories:
            score += 20
        for token in tokens:
            if token in p_title:
                score += 10
            elif token in p_text:
                score += 4
        score += min(product.review, 5) * 3
        score += min(product.sold_count, 200) / 10
        if product.is_discount:
            score += 4

        ranked.append((score, product.price, -product.sold_count, product))

    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [product for _, _, _, product in ranked]


def find_products(text: str, user=None, chat_session=None):
    all_products = Product.objects.filter(in_stock=True)

    if any_keyword(text, DISCOUNT_WORDS):
        all_products = all_products.filter(Q(is_discount=True) | Q(old_price__gt=0))
    if any_keyword(text, POPULAR_WORDS):
        all_products = all_products.order_by("-sold_count", "-review", "price")

    products = _rank_products(all_products, text, user=user, chat_session=chat_session, strict_budget=True)[:5]
    relaxed = False
    if not products and parse_price(text):
        products = _rank_products(Product.objects.filter(in_stock=True), text, user=user, chat_session=chat_session, strict_budget=False)[:5]
        relaxed = bool(products)

    price_value = parse_price(text)
    color = detect_color(text)
    category = detect_category(text)
    return products, price_value, color, category, relaxed


def format_products(products):
    lines = []
    for product in products:
        extra = []
        if product.color:
            extra.append(f"rang: {product.color}")
        if product.sizes:
            extra.append(f"variant: {product.sizes}")
        if product.discount_percent:
            extra.append(f"chegirma: {product.discount_percent}%")
        if product.sold_count:
            extra.append(f"sotilgan: {product.sold_count} ta")
        suffix = f" ({', '.join(extra)})" if extra else ""
        lines.append(f"• {product.title} — {money(product.price)}{suffix}")
    return "\n".join(lines)


def answer_order_status(user) -> BotResult:
    if not user or not user.is_authenticated:
        return BotResult(
            "Buyurtma holatini tekshirish uchun avval saytga login qiling. Login qilganingizdan keyin: 'Buyurtmam qayerda?' deb yozsangiz, oxirgi buyurtmangizni Order modelidan topib beraman.",
            confidence=0.86,
            topic="order_status",
        )

    order = Order.objects.filter(user=user).prefetch_related("items").first()
    if not order:
        return BotResult(
            "Sizda hali buyurtma topilmadi. Mahsulotni savatchaga qo'shib checkout qilsangiz, keyin shu yerdan holatini ko'ra olasiz.",
            confidence=0.85,
            topic="order_status",
        )

    item_names = ", ".join(item.product_title for item in order.items.all()[:3]) or "mahsulotlar"
    status_explain = {
        "new": "qabul qilindi",
        "processing": "tayyorlanmoqda",
        "delivering": "yetkazib berish jarayonida",
        "done": "yetkazib berilgan",
        "cancelled": "bekor qilingan",
    }.get(order.status, order.get_status_display())
    return BotResult(
        f"Oxirgi buyurtmangiz: #{order.id}. Holati: {order.get_status_display()} — {status_explain}. Jami: {money(order.total_amount)}. Mahsulotlar: {item_names}.",
        confidence=0.96,
        topic="order_status",
    )


def _find_named_products(text: str):
    text_norm = normalize(text)
    tokens = [token for token in tokenize(text_norm) if len(token) > 2]
    results = []
    for product in Product.objects.filter(in_stock=True):
        score = 0
        title = normalize(product.title)
        p_text = product_text(product)
        if title and title in text_norm:
            score += 30
        for token in tokens:
            if token in title:
                score += 7
            elif token in p_text:
                score += 2
        if score:
            results.append((score, product.price, -product.sold_count, product))
    results.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [product for _, _, _, product in results[:5]]


def _similar_products(product: Product, limit: int = 5):
    candidates = Product.objects.filter(in_stock=True).exclude(pk=product.pk)
    if product.category:
        candidates = candidates.filter(Q(category__icontains=product.category) | Q(title__icontains=product.category))
    ranked = []
    for candidate in candidates:
        diff = abs(candidate.price - product.price)
        score = candidate.review * 5 + min(candidate.sold_count, 100)
        if candidate.color and product.color and candidate.color == product.color:
            score += 12
        if product.price:
            score -= diff / max(product.price, 1) * 10
        ranked.append((score, candidate.price, -candidate.sold_count, candidate))
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [product for _, _, _, product in ranked[:limit]]


def answer_size(text: str, chat_session=None) -> BotResult:
    products = _find_named_products(text)
    product = products[0] if products else None

    if not product and chat_session and chat_session.last_product_id:
        product = chat_session.last_product

    if not product:
        return BotResult(
            "Qaysi mahsulot o'lchami yoki varianti kerak? Mahsulot nomini yozing, masalan: 'Qora krossovka o'lchami bormi?'.",
            confidence=0.75,
            topic="size",
        )

    if product.sizes:
        return BotResult(
            f"{product.title} uchun mavjud variant/o'lchamlar: {product.sizes}. Narxi: {money(product.price)}.",
            confidence=0.94,
            last_product_id=product.id,
            products=[product],
            topic="size",
        )
    return BotResult(
        f"{product.title} bo'yicha o'lcham/variant ma'lumoti bazada kiritilmagan. Operator aniqlab berishi uchun so'rov qoldirdim.",
        confidence=0.45,
        last_product_id=product.id,
        needs_operator=True,
        products=[product],
        topic="size",
    )


def answer_capabilities() -> BotResult:
    return BotResult(
        "Men online do'kon uchun AI tavsiya tizimiman: mahsulotlarni qiziqishingizga qarab tanlayman, o'xshash mahsulotlarni ko'rsataman, narx/rang/kategoriya/chegirma bo'yicha aqlli qidiraman, eng ko'p sotilgan mahsulotlarni chiqaraman, buyurtma holatini tekshiraman, to'lov/yetkazib berish/qaytarish savollariga javob beraman va kerak bo'lsa operatorga ulayman. Ovozli yozish uchun mikrofon tugmasini bosing.",
        confidence=0.96,
        topic="capabilities",
    )


def answer_product_details(text: str, chat_session=None) -> BotResult:
    products = _find_named_products(text)
    product = products[0] if products else None
    if not product and chat_session and chat_session.last_product_id:
        product = chat_session.last_product
    if not product:
        return BotResult(
            "Qaysi mahsulot haqida bilmoqchisiz? Nomini yozing yoki men sizga tavsiya ham bera olaman.",
            confidence=0.62,
            topic="product_detail",
        )
    extras = []
    if product.color:
        extras.append(f"Rangi: {product.color}")
    if product.sizes:
        extras.append(f"Variantlari: {product.sizes}")
    extras.append(f"Kategoriya: {product.category}")
    extras.append(f"Holati: {'omborda bor' if product.in_stock else 'omborda yoq'}")
    if product.discount_percent:
        extras.append(f"Chegirma: {product.discount_percent}%")
    similar = _similar_products(product, limit=3)
    similar_text = f"\nO'xshashlari:\n{format_products(similar)}" if similar else ""
    return BotResult(
        f"{product.title} haqida qisqacha: {product.description or 'Qisqa tavsif kiritilmagan.'}\nNarxi: {money(product.price)}. {' | '.join(extras)}. Batafsil: {product_link(product)}{similar_text}",
        confidence=0.9,
        products=[product] + similar,
        last_product_id=product.id,
        topic="product_detail",
    )


def answer_compare(text: str) -> Optional[BotResult]:
    if not any_keyword(text, COMPARE_WORDS):
        return None
    products = _find_named_products(text)
    if len(products) < 2:
        return BotResult(
            "Taqqoslash uchun 2 ta mahsulot nomini yozing. Masalan: 'iPhone 16 Pro va Samsung Galaxy S25 Ultra ni taqqosla'.",
            confidence=0.62,
            topic="compare",
        )
    a, b = products[:2]
    cheaper = a if a.price < b.price else b
    rating_winner = a if a.review >= b.review else b
    popular = a if a.sold_count >= b.sold_count else b
    return BotResult(
        f"Taqqoslash:\n• {a.title} — {money(a.price)}, ★ {a.review}, sotilgan: {a.sold_count}, kategoriya: {a.category}\n• {b.title} — {money(b.price)}, ★ {b.review}, sotilgan: {b.sold_count}, kategoriya: {b.category}\nArzonroq variant: {cheaper.title}. Review bo'yicha kuchliroq tanlov: {rating_winner.title}. Sotuv bo'yicha mashhurrog'i: {popular.title}. Maqsadingiz va byudjetingizni yozsangiz, aniqroq tavsiya beraman.",
        confidence=0.88,
        products=[a, b],
        last_product_id=rating_winner.id,
        topic="compare",
    )


def answer_similar(text: str, chat_session=None) -> Optional[BotResult]:
    if not any_keyword(text, SIMILAR_WORDS):
        return None
    products = _find_named_products(text)
    product = products[0] if products else None
    if not product and chat_session and chat_session.last_product_id:
        product = chat_session.last_product
    if not product:
        found, _, _, _, _ = find_products(text, chat_session=chat_session)
        if found:
            top = found[0]
            return BotResult(
                f"Mana o'xshash variantlar:\n{format_products(found)}\n\nEng mos tanlov: {top.title}. Batafsil: {product_link(top)}",
                confidence=0.82,
                products=found,
                last_product_id=top.id,
                topic="similar_products",
            )
        return BotResult("Qaysi mahsulotga o'xshash variant kerak? Mahsulot nomini yozing.", confidence=0.6, topic="similar_products")
    similar = _similar_products(product)
    if not similar:
        return BotResult(f"{product.title} uchun hozir o'xshash mahsulot topilmadi.", confidence=0.5, products=[product], last_product_id=product.id, topic="similar_products")
    return BotResult(
        f"{product.title} ga o'xshash mahsulotlar:\n{format_products(similar)}\n\nEng yaqin variant: {similar[0].title}. Batafsil: {product_link(similar[0])}",
        confidence=0.88,
        products=similar,
        last_product_id=similar[0].id,
        topic="similar_products",
    )


def answer_personal_recommendation(user=None, chat_session=None, text: str = "") -> BotResult:
    # Agar foydalanuvchi "men uchun quloqchin" deb aniq kategoriya yozsa, personal flow shu kategoriyani ham hisobga oladi.
    category = detect_category(text)
    price_value = parse_price(text)
    color = detect_color(text)
    if category or price_value or color:
        products, _, _, _, relaxed = find_products(text, user=user, chat_session=chat_session)
        if products:
            top = products[0]
            intro = "Siz yozgan ehtiyojga qarab shaxsiy tavsiyalar"
            if relaxed:
                intro = "Byudjetga juda yaqin shaxsiy tavsiyalar"
            return BotResult(
                f"{intro}:\n{format_products(products)}\n\nEng mos tanlov: {top.title}. Nega? Narxi, kategoriya mosligi, review va sotilgan soni bo'yicha yaxshi ko'rindi. Batafsil: {product_link(top)}",
                confidence=0.91,
                products=products,
                last_product_id=top.id,
                topic="personal_recommendation",
            )

    interests = _user_interest_categories(user, chat_session)
    qs = Product.objects.filter(in_stock=True)
    if interests:
        q = Q()
        for category_name in interests:
            q |= Q(category__icontains=category_name)
        products = list(qs.filter(q).order_by("-sold_count", "-review", "price")[:5])
        intro = "Siz ko'rgan, savatchaga qo'shgan yoki oldin xarid qilgan mahsulotlaringizga qarab tavsiyalar"
    else:
        products = list(qs.order_by("-sold_count", "-review", "price")[:5])
        intro = "Hozircha shaxsiy xarid tarixi kam, shuning uchun eng mashhur tavsiyalar"
    if not products:
        return BotResult("Tavsiya qilish uchun hali mahsulotlar bazada topilmadi.", confidence=0.35, needs_operator=True, topic="personal_recommendation")
    top = products[0]
    return BotResult(
        f"{intro}:\n{format_products(products)}\n\nEng mos tanlov: {top.title}. Batafsil: {product_link(top)}",
        confidence=0.9,
        products=products,
        last_product_id=top.id,
        topic="personal_recommendation",
    )


def answer_discounts(text: str) -> Optional[BotResult]:
    if not any_keyword(text, DISCOUNT_WORDS):
        return None
    products = list(Product.objects.filter(in_stock=True).filter(Q(is_discount=True) | Q(old_price__gt=0)).order_by("price", "-review")[:5])
    if not products:
        return BotResult("Hozircha bazada chegirmadagi mahsulot topilmadi. Operatorga so'rov qoldirdim, yangi aksiya bo'lsa aniqlab beradi.", confidence=0.45, needs_operator=True, topic="discounts")
    top = products[0]
    return BotResult(
        f"Hozirgi chegirmadagi mahsulotlar:\n{format_products(products)}\n\nEng yaxshi narxli variant: {top.title}. Batafsil: {product_link(top)}",
        confidence=0.91,
        products=products,
        last_product_id=top.id,
        topic="discounts",
    )


def answer_popular(text: str) -> Optional[BotResult]:
    if not any_keyword(text, POPULAR_WORDS):
        return None
    category = detect_category(text)
    qs = Product.objects.filter(in_stock=True)
    if category:
        qs = qs.filter(Q(category__icontains=category) | Q(title__icontains=category))
    products = list(qs.order_by("-sold_count", "-review", "price")[:5])
    if not products:
        return BotResult("Eng ko'p sotilgan mahsulotlarni chiqarish uchun bazada sold_count ma'lumoti topilmadi.", confidence=0.5, topic="popular")
    top = products[0]
    intro = f"Eng ko'p sotilgan {category} mahsulotlari" if category else "Eng ko'p sotilgan mahsulotlar"
    return BotResult(
        f"{intro}:\n{format_products(products)}\n\nTop variant: {top.title}. Batafsil: {product_link(top)}",
        confidence=0.92,
        products=products,
        last_product_id=top.id,
        topic="popular",
    )


def answer_casual_or_general(text: str) -> Optional[BotResult]:
    for keywords, answer in CASUAL_ANSWERS:
        if any_keyword(text, keywords):
            return BotResult(answer, confidence=0.82, topic="small_talk")

    if any_keyword(text, ["salomatlik", "doctor", "vrach", "врач", "юрист", "advokat", "pul ishlash", "кредит"]):
        return BotResult(
            "Bu savol do'kon mavzusidan tashqarida. Men aniq mutaxassis o'rnini bosmayman, lekin online xarid, mahsulot tanlash, narx va buyurtma bo'yicha bemalol yordam beraman.",
            confidence=0.55,
            topic="out_of_scope",
        )

    return None


def answer_general_shop_question(text: str) -> Optional[BotResult]:
    if any_keyword(text, ["online do'kon", "internet magazin", "ecommerce", "e-commerce", "ai tavsiya", "recommendation system"]):
        return BotResult(
            "Bu loyiha AI-powered e-commerce recommendation system sifatida ishlaydi: Django mahsulot, savat, checkout, foydalanuvchi va buyurtmalarni boshqaradi; AI esa mahsulot tavsiya qiladi, o'xshash mahsulotlarni topadi, qidiruvni aqlliroq qiladi va support savollariga javob beradi.",
            confidence=0.9,
            topic="project_info",
        )
    return None



# --- MARKAZIY AI KNOWLEDGE BASE: ChatGPT'ga o'xshashroq, lekin loyiha ichida offline ishlaydi ---
PROJECT_FACTS = {
    "name": "Aziko Market",
    "type": "AI-powered e-commerce recommendation system",
    "stack": "Django, SQLite, HTML, CSS, JavaScript",
    "goal": "foydalanuvchiga mahsulotni tez topish, savatga qo'shish, buyurtma qilish va AI yordamchi orqali maslahat olishni qulaylashtirish",
}

CATEGORY_GUIDES = {
    "telefon": (
        "Telefon tanlashda 5 ta narsaga qarang: 1) protsessor va tezlik, 2) kamera sifati, "
        "3) xotira hajmi, 4) batareya, 5) narx. Agar premium va kamera kerak bo'lsa iPhone/Samsung flagmanlari yaxshi. "
        "Agar narx muhim bo'lsa, byudjetingizni yozing — men bazadagi mos telefonlarni chiqarib beraman."
    ),
    "quloqchin": (
        "Quloqchin tanlashda ovoz sifati, mikrofon, batareya, quloqqa qulayligi va telefon bilan mosligini tekshirish kerak. "
        "Sport yoki ko'chada ishlatish uchun quloqqa mahkam turadigan model yaxshi; qo'ng'iroq uchun mikrofon sifati muhim."
    ),
    "noutbuk": (
        "Noutbuk tanlashda CPU, RAM, SSD, ekran va batareyaga qarang. O'qish/ofis uchun yengil noutbuk yetadi, "
        "dizayn, montaj yoki dasturlash uchun kuchliroq protsessor va kamida 16GB RAM yaxshi tanlov bo'ladi."
    ),
    "televizor": (
        "Televizor tanlashda ekran o'lchami, smart funksiyalar, ruxsat, tovush va kafolatga qarang. Katta xona uchun 55 dyuym va undan yuqori, "
        "kichik xona uchun esa ixchamroq model qulay."
    ),
    "krossovka": (
        "Krossovka tanlashda razmer, taglik qulayligi, material, rang va kundalik kiyimga mosligiga qarang. "
        "Agar uzoq yurish uchun kerak bo'lsa, yumshoq taglik va to'g'ri razmer eng muhim."
    ),
    "maishiy texnika": (
        "Maishiy texnika tanlashda quvvat, hajm, energiya sarfi, kafolat va uy sharoitiga mosligini tekshirish kerak. "
        "Kichik oshxona uchun ixcham, katta oila uchun hajmi kattaroq model qulay."
    ),
}

PRESENTATION_SCRIPT = (
    "Prezentatsiyada shunday aytishingiz mumkin: Aziko Market — bu Django asosida yaratilgan online do'kon. "
    "Unda foydalanuvchi mahsulotlarni ko'radi, qidiradi, savatga qo'shadi va buyurtma beradi. Eng muhim qismi — AI yordamchi: "
    "u mahsulotlarni narx, kategoriya, rang, chegirma va mashhurlik bo'yicha tavsiya qiladi, buyurtma holatini tekshiradi va FAQ savollariga javob beradi. "
    "Demo uchun avval bosh sahifa, keyin mahsulotlar, keyin savat/checkout, oxirida AI chatni ko'rsating."
)

SHOP_POLICIES_EXTENDED = {
    "how_to_buy": (
        "Xarid qilish tartibi: 1) mahsulotni tanlang, 2) batafsil sahifasini oching, 3) 'Savatga qo'shish' tugmasini bosing, "
        "4) cart sahifasida mahsulotni tekshiring, 5) checkout sahifasida ism, telefon, manzil va to'lov turini kiriting."
    ),
    "cart": (
        "Savatcha siz tanlagan mahsulotlarni vaqtincha saqlaydi. U yerda mahsulot miqdorini oshirish, kamaytirish yoki olib tashlash mumkin. "
        "Checkout qilish uchun foydalanuvchi login qilgan bo'lishi kerak."
    ),
    "login": (
        "Login/register foydalanuvchini tanib olish uchun kerak. Shunda savatcha, buyurtma va AI buyurtma statusini tekshirish funksiyalari to'g'ri ishlaydi."
    ),
    "security": (
        "Sayt shaxsiy ma'lumotlar bilan ehtiyotkor ishlashi kerak: parollar Django auth tizimida hash ko'rinishida saqlanadi, checkout ma'lumotlari esa buyurtmani yetkazish uchun ishlatiladi."
    ),
    "future": (
        "Kelajakda loyihaga online to'lov, Telegram notification, yetkazib berish tracking, real AI API, foydalanuvchi xarid tarixiga qarab yanada kuchli tavsiya tizimi qo'shish mumkin."
    ),
}

GENERAL_KNOWLEDGE = [
    (
        ["django", "framework", "backend", "бекенд", "бэкенд"],
        "Django — Python'da yozilgan kuchli backend framework. Bu loyihada Django mahsulotlar, foydalanuvchilar, savat, buyurtma, admin panel va AI chat API qismlarini boshqaradi.",
        "django_info",
    ),
    (
        ["database", "baza", "sqlite", "ma'lumotlar bazasi", "malumotlar bazasi", "база", "бд"],
        "Bu loyiha ma'lumotlarni SQLite database'da saqlaydi: mahsulotlar, foydalanuvchilar, savat, buyurtmalar, chat xabarlari va support ticketlar bazada turadi.",
        "database_info",
    ),
    (
        ["frontend", "html", "css", "javascript", "дизайн", "фронтенд"],
        "Frontend qismida HTML, CSS va JavaScript ishlatilgan. HTML sahifa tuzilishini, CSS dizaynni, JavaScript esa AI chat, voice input va interaktiv tugmalarni boshqaradi.",
        "frontend_info",
    ),
    (
        ["admin panel", "admin", "operator panel", "админ", "админка"],
        "Admin panel orqali mahsulot qo'shish, narx/rasm/kategoriya tahrirlash, buyurtmalarni ko'rish, contact xabarlarni tekshirish va support ticketlarga javob berish mumkin.",
        "admin_info",
    ),
    (
        ["ai qanday ishlaydi", "ai qanaqa ishlaydi", "tavsiya tizimi", "recommendation", "рекомендац", "как работает ai"],
        "AI yordamchi foydalanuvchi matnidan kategoriya, rang, narx, chegirma va mahsulot nomini ajratadi. Keyin Django database'dagi Product modelidan mos mahsulotlarni topib, eng mos variantlarni reyting, sotuv soni va narx bo'yicha tartiblaydi.",
        "ai_logic",
    ),
    (
        ["iphone nima", "iphone haqida", "apple haqida", "ios nima"],
        "iPhone — Apple kompaniyasi ishlab chiqaradigan premium smartfon seriyasi. iOS operatsion tizimida ishlaydi. Yuqori kamera sifati, tezkor ishlash va uzoq qo'llab-quvvatlash bilan mashhur. Bazamizda iPhone 15 va iPhone 16 Pro mavjud.",
        "iphone_info",
    ),
    (
        ["samsung nima", "samsung haqida", "galaxy nima"],
        "Samsung — dunyo bo'yicha eng mashhur Android smartfon ishlab chiqaruvchisi. Galaxy seriyasi (S, A, Note) turli narx segmentlari uchun mavjud. Bazamizda Samsung Galaxy S25 Ultra va Galaxy A55 bor.",
        "samsung_info",
    ),
    (
        ["xiaomi nima", "redmi nima", "xiaomi haqida"],
        "Xiaomi — Xitoy smartfon va texnologiya kompaniyasi. Arzon narxda sifatli mahsulot taklif etishi bilan mashhur. Redmi seriyasi byudjet uchun, Mi va Poco seriyasi o'rta va yuqori segment uchun. Bazamizda Xiaomi Redmi Note 13 mavjud.",
        "xiaomi_info",
    ),
    (
        ["nike nima", "adidas nima", "reebok nima", "krossovka brend"],
        "Nike, Adidas, Reebok — dunyo mashhur krossovka brendlari. Nike Air Max, Adidas Ultraboost, Reebok Classic eng mashhur modellari. Bazamizda ushbu brendlarning bir nechta modeli mavjud.",
        "brand_info",
    ),
]


def _products_count_text() -> str:
    total = Product.objects.count()
    in_stock = Product.objects.filter(in_stock=True).count()
    discounts = Product.objects.filter(Q(is_discount=True) | Q(old_price__gt=0)).count()
    categories = sorted(set(Product.objects.exclude(category='').values_list('category', flat=True)))
    category_text = ", ".join(categories) if categories else "kategoriya kiritilmagan"
    return f"Bazadagi umumiy mahsulotlar: {total} ta. Omborda borlari: {in_stock} ta. Chegirmadagilar: {discounts} ta. Kategoriyalar: {category_text}."


def answer_project_info(text: str) -> Optional[BotResult]:
    if any_keyword(text, [
        "aziko", "loyiha haqida", "proyekt haqida", "sayt haqida", "market haqida", "aziko market nima",
        "nima loyiha", "цель проекта", "о проекте", "что это за проект", "about project",
    ]):
        return BotResult(
            f"{PROJECT_FACTS['name']} — {PROJECT_FACTS['type']}. Asosiy maqsadi: {PROJECT_FACTS['goal']}. "
            f"Texnologiyalar: {PROJECT_FACTS['stack']}. Saytda mahsulotlar, qidiruv, product detail, savat, checkout, login/register, contact va AI support qismlari bor. "
            f"AI yordamchi foydalanuvchiga mahsulot tavsiya qiladi, narx bo'yicha qidiradi, buyurtma holatini tushuntiradi va operatorga ticket ochishi mumkin. {_products_count_text()}",
            confidence=0.94,
            topic="project_info",
        )
    return None


def answer_presentation_question(text: str) -> Optional[BotResult]:
    if any_keyword(text, ["prezentatsiya", "taqdimot", "sahnada", "himoya", "выступ", "презентац"]):
        return BotResult(PRESENTATION_SCRIPT, confidence=0.93, topic="presentation_help")
    return None


def answer_catalog(text: str) -> Optional[BotResult]:
    if not any_keyword(text, [
        "hamma mahsulot", "barcha mahsulot", "katalog", "narxlar", "price list", "прайс", "каталог", "все товары", "nimalar bor", "qanday mahsulotlar bor",
    ]):
        return None
    products = list(Product.objects.filter(in_stock=True).order_by('category', 'price'))
    if not products:
        return BotResult("Hozircha katalogda mahsulot yo'q.", confidence=0.4, needs_operator=True, topic="catalog")
    return BotResult(
        f"Aziko Market katalogida hozir quyidagi mahsulotlar bor:\n{format_products(products)}\n\n{_products_count_text()} Xohlasangiz, kategoriya yoki byudjet yozing — men eng moslarini ajratib beraman.",
        confidence=0.92,
        products=products[:6],
        last_product_id=products[0].id if products else None,
        topic="catalog",
    )


def answer_category_guide(text: str) -> Optional[BotResult]:
    category = detect_category(text)
    wants_guide = any_keyword(text, [
        "qanday tanlash", "qanaqa tanlash", "tanlashda", "maslahat", "tushuntir", "qaysi yaxshi", "nima farqi", "qanday olish",
        "как выбрать", "совет", "объясни", "что лучше", "подскажи",
    ])
    if category and wants_guide:
        products, *_ = find_products(category)
        product_part = ""
        if products:
            product_part = f"\n\nBazadagi mos variantlar:\n{format_products(products[:4])}"
        return BotResult(
            f"{CATEGORY_GUIDES.get(category, 'Bu kategoriya bo‘yicha narx, sifat, kafolat va ehtiyojingizga qarab tanlash kerak.')}"
            f"{product_part}",
            confidence=0.9,
            products=products[:4] if products else [],
            last_product_id=products[0].id if products else None,
            topic="category_guide",
        )
    return None


def answer_shop_process(text: str) -> Optional[BotResult]:
    checks = [
        (["qanday sotib", "qanday xarid", "buyurtma qilish", "zakaz qilish", "заказать", "как купить", "checkout"], "how_to_buy"),
        (["savat", "cart", "korzina", "корзина"], "cart"),
        (["login", "register", "ro'yxatdan", "royxatdan", "akkaunt", "пароль", "регистрац"], "login"),
        (["xavfsiz", "security", "parol", "shaxsiy ma'lumot", "личные данные", "безопас"], "security"),
        (["kelajak", "future", "yana nima qo'sh", "nima qo'shsa", "развитие", "будущ"], "future"),
    ]
    for keywords, key in checks:
        if any_keyword(text, keywords):
            return BotResult(SHOP_POLICIES_EXTENDED[key], confidence=0.9, topic=key)
    return None


def answer_general_knowledge(text: str) -> Optional[BotResult]:
    for keywords, answer, topic in GENERAL_KNOWLEDGE:
        if any_keyword(text, keywords):
            return BotResult(answer, confidence=0.88, topic=topic)
    return None


def answer_smart_general(text: str) -> Optional[BotResult]:
    """Do'konga yaqin umumiy savollarga ham bo'sh qolmasdan javob beradi."""
    if any_keyword(text, ["qimmatmi", "nega qimmat", "arzonmi", "narxi yaxshi", "стоит ли", "выгодно", "дорого"]):
        products = _find_named_products(text)
        if products:
            product = products[0]
            explanation = ""
            if product.discount_percent:
                explanation = f" Hozir {product.discount_percent}% chegirma bor, shuning uchun eski narxiga qaraganda foydaliroq."
            return BotResult(
                f"{product.title} narxi {money(product.price)}.{explanation} Qiymatini baholashda kategoriya, review, sotilgan soni va sizga kerak bo'lgan xususiyatlarni solishtirish kerak. Xohlasangiz, men unga o'xshash arzonroq variantlarni ham chiqaraman.",
                confidence=0.82,
                products=products[:3],
                last_product_id=product.id,
                topic="price_explain",
            )
        return BotResult("Narxni baholash uchun mahsulot nomini yozing. Masalan: 'iPhone 16 Pro qimmatmi?' yoki '299 minggacha quloqchin bormi?'.", confidence=0.65, topic="price_explain")

    if any_keyword(text, ["sovg'a", "sovga", "podarka", "подарок", "tug'ilgan kun", "день рождения"]):
        products = list(Product.objects.filter(in_stock=True).order_by('-review', 'price')[:5])
        return BotResult(
            f"Sovg'a uchun yaxshi variantlar: quloqchin, smartfon aksessuari, krossovka yoki maishiy texnika. Bazadan tavsiya:\n{format_products(products)}\n\nKimga sovg'a qilmoqchisiz va byudjet qancha? Shuni yozsangiz aniqroq tanlab beraman.",
            confidence=0.86,
            products=products,
            last_product_id=products[0].id if products else None,
            topic="gift_ideas",
        )

    if any_keyword(text, ["talaba", "o'quvchi", "student", "учеб", "ученик", "maktab", "univer"]):
        products = list(Product.objects.filter(in_stock=True).filter(Q(category__icontains='noutbuk') | Q(category__icontains='quloqchin') | Q(category__icontains='telefon')).order_by('price')[:5])
        return BotResult(
            f"O'qish uchun eng kerakli mahsulotlar: telefon, quloqchin va noutbuk. Talaba uchun narx/foyda muhim, shuning uchun avval byudjetni belgilash kerak. Bazadagi mos variantlar:\n{format_products(products)}",
            confidence=0.84,
            products=products,
            last_product_id=products[0].id if products else None,
            topic="student_recommendation",
        )

    return None


def answer_fallback_chatgpt_style(text: str) -> BotResult:
    """Butunlay notanish savolda ham AI jim qolmasin; foydalanuvchini foydali yo'nalishga olib keladi."""
    products = list(Product.objects.filter(in_stock=True).order_by('-sold_count', '-review', 'price')[:3])
    product_text_block = f"\n\nHozircha sizga shularni tavsiya qila olaman:\n{format_products(products)}" if products else ""
    return BotResult(
        "Savolingizni qabul qildim. Men Aziko Market ichida eng yaxshi ishlaydigan yo'nalishlarim: mahsulot tavsiya qilish, narx bo'yicha qidirish, solishtirish, savat/checkoutni tushuntirish, buyurtma statusi, yetkazib berish, to'lov va loyiha haqida ma'lumot berish. "
        "Savolingizni biroz aniqroq yozsangiz, men bazadan mos mahsulotlarni ham chiqarib beraman. Masalan: '500 minggacha quloqchin', 'telefon tavsiya qil', 'Django nima uchun ishlatilgan?', 'prezentatsiyada nima deyish kerak?'."
        f"{product_text_block}",
        confidence=0.55,
        products=products,
        last_product_id=products[0].id if products else None,
        needs_operator=False,
        topic="smart_fallback",
    )

def build_answer(message: str, user=None, chat_session=None) -> BotResult:
    text = normalize(message)

    if not text:
        return BotResult("Savolingizni yozing. Men mahsulot topish, buyurtma holatini tekshirish, loyiha haqida ma'lumot berish va shopping bo'yicha yordam beraman.", confidence=0.5, topic="empty")

    # Buyurtma/status savoli greetingdan oldin tekshiriladi: "salom buyurtmam qayerda" bo'lsa status qaytsin.
    if any_keyword(text, ["buyurtma", "zakaz", "order", "qayerda", "holati", "status", "заказ", "статус"]):
        return answer_order_status(user)

    if any_keyword(text, THANKS_WORDS):
        return BotResult("Arzimaydi 😊 Yana xohlagan savolingizni yozavering — mahsulot topib, tushuntirib, taqqoslab yoki loyiha haqida ma'lumot berib yordam beraman.", confidence=0.88, topic="thanks")

    if any_keyword(text, CAPABILITY_WORDS):
        return answer_capabilities()

    # Loyiha, prezentatsiya va texnologiya haqida ko'proq ma'lumot berish.
    for general_handler in (
        answer_presentation_question,
        answer_project_info,
        answer_catalog,
        answer_shop_process,
        answer_general_knowledge,
        answer_category_guide,
        answer_smart_general,
    ):
        general_result = general_handler(text)
        if general_result:
            return general_result

    compare_result = answer_compare(text)
    if compare_result:
        return compare_result

    similar_result = answer_similar(text, chat_session)
    if similar_result:
        return similar_result

    if any_keyword(text, ["o'lcham", "olcham", "razmer", "размер", "size", "variant"]):
        return answer_size(text, chat_session)

    for keywords, answer, topic in FAQ_ANSWERS:
        if any_keyword(text, keywords):
            needs_operator = topic == "operator"
            return BotResult(answer, confidence=0.92, needs_operator=needs_operator, topic=topic)

    if any_keyword(text, GREETING_WORDS):
        # Agar salom bilan birga mahsulot ham so'ralgan bo'lsa, pastdagi product flow ishlasin.
        if not any_keyword(text, PRODUCT_INTENT_WORDS) and not detect_category(text):
            return BotResult(
                "Salom! Men AZIKO MARKET AI yordamchisiman. Menga mahsulot turi, rang, byudjet yoki savolingizni yozing — masalan: 'Menga 500 ming so'mgacha qora krossovka kerak'. Shuningdek, loyiha, Django, AI tavsiya tizimi yoki prezentatsiya haqida ham tushuntirib bera olaman.",
                confidence=0.9,
                topic="greeting",
            )

    casual_result = answer_casual_or_general(text)
    if casual_result:
        return casual_result

    if any_keyword(text, DETAIL_WORDS):
        return answer_product_details(text, chat_session)

    if any_keyword(text, PERSONAL_WORDS):
        return answer_personal_recommendation(user, chat_session, text)

    discount_result = answer_discounts(text)
    if discount_result:
        return discount_result

    popular_result = answer_popular(text)
    if popular_result:
        return popular_result

    general_result = answer_general_shop_question(text)
    if general_result:
        return general_result

    is_product_question = any_keyword(text, PRODUCT_INTENT_WORDS)
    products, price_value, color, category, relaxed = find_products(text, user=user, chat_session=chat_session)
    has_product_filter = bool(price_value or color or category or any_keyword(text, DISCOUNT_WORDS + POPULAR_WORDS + ["arzon", "qimmat", "дешев", "дорог"]))

    if is_product_question or has_product_filter:
        if products:
            details = []
            if price_value:
                details.append(f"narx {money(price_value)} {'dan yuqori' if detect_price_mode(text) == 'min' else 'gacha'}" + ("ga yaqin" if relaxed else ""))
            if color:
                details.append(f"rang {color}")
            if category:
                details.append(f"kategoriya {category}")
            if any_keyword(text, DISCOUNT_WORDS):
                details.append("chegirma")
            if any_keyword(text, POPULAR_WORDS):
                details.append("ko'p sotilgan")
            intro = "Sizga mos variantlar" + (f" ({', '.join(details)})" if details else "") + ":"
            if relaxed:
                intro = "Aniq byudjetga to'liq sig'adigan mahsulot kam, lekin eng yaqin variantlar:"
            top = products[0]
            extra_tip = "\n\nMaslahat: mahsulotni tanlashda narx, review, sotilgan soni, rang/variant va kafolatga qarang."
            return BotResult(
                f"{intro}\n{format_products(products)}\n\nEng mos tanlov: {top.title}. Batafsil ko'rish: {product_link(top)}{extra_tip}",
                confidence=0.9,
                products=products,
                last_product_id=top.id,
                topic="product_recommendation",
            )
        return BotResult(
            "Hozir bazadan aynan mos mahsulot topilmadi. Narx diapazonini kengaytiring yoki boshqa kategoriya/rang yozing. Masalan: '300 minggacha quloqchin' yoki 'qora krossovka'. Kerak bo'lsa operator ham aniqlab berishi mumkin.",
            confidence=0.45,
            needs_operator=True,
            topic="unanswered_product",
        )

    # Oldingi versiyada bu joyda ko'p savollar operatorga ketardi. Endi AI ko'proq savolga javob qaytaradi.
    return answer_fallback_chatgpt_style(text)


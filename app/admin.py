from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Count

from .models import (
    Cart,
    CartItem,
    ChatMessage,
    ChatSession,
    Contact,
    Order,
    OrderItem,
    Portfolio,
    Product,
    SupportTicket,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'category', 'price', 'old_price', 'discount_percent', 'color', 'sizes', 'in_stock', 'is_discount', 'sold_count', 'review')
    list_filter = ('category', 'in_stock', 'is_discount', 'color')
    search_fields = ('title', 'description', 'category', 'color', 'sizes')
    list_editable = ('price', 'old_price', 'in_stock', 'is_discount', 'sold_count')
    ordering = ('-sold_count', '-review', 'price')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if not obj or not obj.pk:
            return '-'
        return format_html('<img src="{}" style="width:64px;height:54px;object-fit:cover;border-radius:10px;border:1px solid #ddd;" />', obj.image_url)
    image_preview.short_description = 'Rasm'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'checked_out', 'total_quantity', 'total_price', 'updated_at')
    list_filter = ('checked_out',)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'phone', 'status', 'payment_type', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = ('full_name', 'phone', 'address', 'user__username', 'user__email')
    list_editable = ('status',)
    inlines = [OrderItemInline]


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'text', 'confidence', 'created_at')
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'short_session_key', 'needs_operator', 'messages_count', 'open_tickets_count', 'last_user_question', 'updated_at')
    list_filter = ('needs_operator', 'created_at', 'updated_at')
    search_fields = ('session_key', 'user__username', 'user__email', 'messages__text')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ChatMessageInline]
    actions = ('mark_needs_operator', 'mark_operator_done')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_messages_count=Count('messages', distinct=True), _tickets_count=Count('tickets', distinct=True))

    def short_session_key(self, obj):
        return (obj.session_key or 'anonymous')[:18]
    short_session_key.short_description = 'Session'

    def messages_count(self, obj):
        return getattr(obj, '_messages_count', obj.messages.count())
    messages_count.short_description = 'Xabarlar'

    def open_tickets_count(self, obj):
        return obj.tickets.filter(status=SupportTicket.STATUS_OPEN).count()
    open_tickets_count.short_description = 'Ochiq ticket'

    def last_user_question(self, obj):
        msg = obj.messages.filter(role=ChatMessage.ROLE_USER).order_by('-created_at').first()
        return (msg.text[:90] + '...') if msg and len(msg.text) > 90 else (msg.text if msg else '-')
    last_user_question.short_description = 'Oxirgi savol'

    @admin.action(description="Operator kerak deb belgilash")
    def mark_needs_operator(self, request, queryset):
        updated = queryset.update(needs_operator=True)
        self.message_user(request, f"{updated} ta chat operatorga belgilandi.", messages.SUCCESS)

    @admin.action(description="Operator ishi tugadi deb belgilash")
    def mark_operator_done(self, request, queryset):
        updated = queryset.update(needs_operator=False)
        self.message_user(request, f"{updated} ta chat yopildi.", messages.SUCCESS)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'short_text', 'confidence', 'created_at')
    list_filter = ('role', 'created_at', 'confidence')
    search_fields = ('text', 'session__session_key', 'session__user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('session', 'role', 'text', 'confidence', 'created_at')

    def short_text(self, obj):
        return obj.text[:100]
    short_text.short_description = 'Xabar'


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'topic', 'confidence', 'session', 'short_question', 'has_operator_reply', 'operator_reply_seen', 'created_at', 'updated_at')
    list_filter = ('status', 'topic', 'operator_reply_seen', 'created_at', 'updated_at')
    search_fields = ('question', 'bot_answer', 'operator_reply', 'session__user__username', 'session__user__email')
    list_editable = ('status',)
    readonly_fields = ('session', 'question', 'bot_answer', 'topic', 'confidence', 'operator_reply_seen', 'created_at', 'updated_at')
    fields = ('session', 'status', 'topic', 'confidence', 'question', 'bot_answer', 'operator_reply', 'operator_reply_seen', 'created_at', 'updated_at')
    actions = ('mark_answered', 'mark_closed', 'mark_open')
    date_hierarchy = 'created_at'

    def short_question(self, obj):
        return obj.question[:100]
    short_question.short_description = 'Savol'

    def has_operator_reply(self, obj):
        return bool(obj.operator_reply)
    has_operator_reply.boolean = True
    has_operator_reply.short_description = 'Operator javobi'

    def save_model(self, request, obj, form, change):
        old_reply = ''
        if change and obj.pk:
            old = SupportTicket.objects.filter(pk=obj.pk).first()
            old_reply = old.operator_reply if old else ''

        if obj.operator_reply and obj.status == SupportTicket.STATUS_OPEN:
            obj.status = SupportTicket.STATUS_ANSWERED

        if obj.operator_reply and obj.operator_reply != old_reply:
            obj.operator_reply_seen = False

        super().save_model(request, obj, form, change)

        if obj.operator_reply and obj.operator_reply != old_reply:
            ChatMessage.objects.create(
                session=obj.session,
                role=ChatMessage.ROLE_OPERATOR,
                text=obj.operator_reply,
                confidence=1,
            )
            obj.session.needs_operator = False
            obj.session.save(update_fields=['needs_operator'])
            self.message_user(request, "Operator javobi chatga qo'shildi. Foydalanuvchi keyingi xabarida javobni ko'radi.", messages.SUCCESS)

    @admin.action(description="Tanlangan ticketlarni javob berilgan qilish")
    def mark_answered(self, request, queryset):
        updated = queryset.update(status=SupportTicket.STATUS_ANSWERED)
        self.message_user(request, f"{updated} ta ticket javob berilgan qilindi.", messages.SUCCESS)

    @admin.action(description="Tanlangan ticketlarni yopish")
    def mark_closed(self, request, queryset):
        updated = queryset.update(status=SupportTicket.STATUS_CLOSED)
        self.message_user(request, f"{updated} ta ticket yopildi.", messages.SUCCESS)

    @admin.action(description="Tanlangan ticketlarni ochiq qilish")
    def mark_open(self, request, queryset):
        updated = queryset.update(status=SupportTicket.STATUS_OPEN)
        self.message_user(request, f"{updated} ta ticket qayta ochildi.", messages.SUCCESS)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'subject')
    search_fields = ('name', 'phone_number', 'subject', 'message')


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'description', 'author')

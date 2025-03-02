# bot/handlers/db_handlers.py
from django.utils import timezone
from asgiref.sync import sync_to_async
from ..models import CustomUser, Category, Product, Order, OrderProduct, Comment

async def get_or_create_user(chat_id):
    return await sync_to_async(CustomUser.objects.get_or_create)(chat_id=chat_id, defaults={'username': str(chat_id)})

async def get_user(chat_id):
    return await sync_to_async(CustomUser.objects.get)(chat_id=chat_id)

async def save_user(user):
    await sync_to_async(user.save)()

async def get_categories():
    return await sync_to_async(list)(Category.objects.all())  # Simply fetch all categories, no parent filter

async def get_products_by_category(category_id):
    return await sync_to_async(list)(Product.objects.filter(category_id=category_id))

async def get_product(product_id):
    return await sync_to_async(Product.objects.get)(id=product_id)

async def create_order(user, carts, status, payment_type, longitude, latitude):
    order = await sync_to_async(Order.objects.create)(
        user=user,
        status=status,
        payment_type=payment_type,
        longitude=longitude,
        latitude=latitude,
        created_at=timezone.now()
    )
    for product_id, amount in carts.items():
        await sync_to_async(OrderProduct.objects.create)(
            order=order,
            product_id=product_id,
            amount=amount,
            created_at=timezone.now()
        )
    return order

async def get_my_order_pending(chat_id):
    return await sync_to_async(list)(Order.objects.filter(user__chat_id=chat_id, status=1))

async def get_my_order_delivered(chat_id):
    return await sync_to_async(list)(Order.objects.filter(user__chat_id=chat_id, status=2))

async def get_my_order_canceled(chat_id):
    return await sync_to_async(list)(Order.objects.filter(user__chat_id=chat_id, status=3))

async def get_order_products(order):
    return await sync_to_async(list)(OrderProduct.objects.filter(order=order))

async def cancel_order(order_id):
    order = await sync_to_async(Order.objects.get)(id=order_id)
    order.status = 3  # Set status to canceled
    await sync_to_async(order.save)()
    return order

async def save_comment(message, user, ):
    comment = await sync_to_async(Comment.objects.create)(
        user=user,
        message=message,
        status=1,  # "Pending"
    )
    return comment
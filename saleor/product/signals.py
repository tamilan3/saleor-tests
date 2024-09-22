from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..product.models import ProductVariantChannelListing
from ..channel.models import Channel
from ..core.tasks import delete_from_storage_task


def delete_background_image(sender, instance, **kwargs):
    if img := instance.background_image:
        delete_from_storage_task.delay(img.name)


def delete_digital_content_file(sender, instance, **kwargs):
    if file := instance.content_file:
        delete_from_storage_task.delay(file.name)


def delete_product_media_image(sender, instance, **kwargs):
    if file := instance.image:
        delete_from_storage_task.delay(file.name)


@receiver(post_save, sender=ProductVariantChannelListing)
def product_variant_channel_listing_post_save(sender, instance, created, **kwargs):
    CURRENCY = "USD"
    CURRENCY_SYMBOL = "$"
    SLUG = "default-channel"
    CURRENCY_VALUE = Decimal('0.0130')  # Use Decimal for precision

    if created and instance.currency == "INR":
        try:
            channel = Channel.objects.filter(slug=SLUG, currency_code=CURRENCY).first()
            new_instance = ProductVariantChannelListing.objects.update_or_create(
                variant=instance.variant,
                channel=channel,
                price_amount=(instance.price_amount * CURRENCY_VALUE).quantize(Decimal('0.01')),
                cost_price_amount=(instance.cost_price_amount * CURRENCY_VALUE).quantize(Decimal('0.01')),
                currency=CURRENCY
            )
            print(f'New instance created: {new_instance}')
        except Exception as e:
            print(f'Error creating new instance: {e}')
        



@receiver(post_save, sender=ProductVariantChannelListing)
def product_variant_channel_listing_post_save_receiver(sender, instance, created, **kwargs):
    product_variant_channel_listing_post_save(sender, instance, created, **kwargs)



 

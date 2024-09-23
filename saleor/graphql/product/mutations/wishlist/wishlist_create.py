import graphene
from django.core.exceptions import ValidationError

from saleor.core.tracing import traced_atomic_transaction
from saleor.graphql.channel import ChannelContext
from saleor.graphql.core.validators import validate_slug_and_generate_if_needed
from saleor.product.error_codes import WishlistErrorCode
from saleor.product.search import PRODUCTS_BATCH_SIZE
from saleor.product.tasks import collection_product_updated_task
from .....permission.enums import ProductPermissions
from .....product import models
from ....core import ResolveInfo
from ....core.doc_category import DOC_CATEGORY_WISHLIST
from ....core.mutations import ModelMutation
from ....core.types import BaseInputObjectType, ProductError, NonNullList
from ...types.wishlists import Wishlist


class WishlistInput(BaseInputObjectType):
    slug = graphene.String(description="Wishlist slug.")
    user = graphene.ID(
        description="Customer associated with the wishlist.", name="user"
    )
    products = NonNullList(
        graphene.ID,
        description="List of products to be added to the Wishlist.",
        name="products",
    )

    class Meta:
        doc_category = DOC_CATEGORY_WISHLIST

    

class WishlistCreate(ModelMutation):
    class Arguments:
        input = WishlistInput(
            required=True, description="Fields required to create a Wishlist."
        )

    class Meta:
        description = "Creates a new wishlist."
        model = models.Wishlist
        object_type = Wishlist
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ProductError
        error_type_field = "product_errors"
        support_meta_field = True
        support_private_meta_field = True

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        if info.context.user and not info.context.user.is_authenticated:
            raise ValidationError("User must be authenticated to create a wishlist.")
        cleaned_input["user"] = info.context.user
        cls.cleaned_input = cleaned_input
        return cls.cleaned_input
    
    @classmethod
    def save(cls, info: ResolveInfo, instance, cleaned_input):  
        instance.search_index_dirty = True
        instance.save()
        cls._save_m2m(info, instance, cleaned_input)
    
    @classmethod
    def _save_m2m(cls, info: ResolveInfo, instance, cleaned_data):
        products = cleaned_data.get("products", None)
        if products is not None:
            instance.products.set(products)

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **kwargs):
    
        response = super().perform_mutation(_root, info, **kwargs)
        wishlist = getattr(response, cls._meta.return_field_name)

        # Wrap product instance with ChannelContext in response
        setattr(
            response,
            cls._meta.return_field_name,
            ChannelContext(node=wishlist, channel_slug=None),
        )
        return response
       

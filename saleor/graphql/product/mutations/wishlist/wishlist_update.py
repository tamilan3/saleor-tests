import graphene 
from django.core.exceptions import ValidationError
from .....permission.enums import ProductPermissions
from .....product import models
from ....core import ResolveInfo
from ....core.types import BaseInputObjectType, ProductError, NonNullList
from ...types.wishlists import Wishlist
from .wishlist_create import WishlistCreate, WishlistInput
from ....core.doc_category import DOC_CATEGORY_WISHLIST


class WishlistUpdate(WishlistCreate):
    class Arguments:
        id = graphene.ID(required=False, description="ID of a Tag to update.")
        input = WishlistInput(
            required=True, description="Fields required to update a product."
        )

    class Meta:
        description = "Creates a new Wishlist."
        model = models.Wishlist
        object_type = Wishlist
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ProductError
        error_type_field = "product_errors"


    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        if info.context.user and not info.context.user.is_authenticated:
            raise ValidationError("User must be authenticated to create a wishlist.")
        return cleaned_input
    
    @classmethod
    def _save_m2m(cls, _info: ResolveInfo, instance, cleaned_data):
        products = cleaned_data.get("products", None)
        if products is not None:
            instance.products.set(products)

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root, info, **data)
        return response
import graphene 
from django.core.exceptions import ValidationError
from .....permission.enums import ProductPermissions
from ....core.mutations import ModelWithExtRefMutation
from .....product import models
from ....core import ResolveInfo
from ....core.types import BaseInputObjectType, ProductError, NonNullList
from ...types import wishlists
from .wishlist_create import WishlistCreate, WishlistInput
from ....core.doc_category import DOC_CATEGORY_WISHLIST


class WishlistInput(BaseInputObjectType):
    id = graphene.GlobalID(required=True, description="The ID of the Wishlist.")
    products = NonNullList(graphene.String, description="Product IDs.")

    class Meta:
        doc_category = DOC_CATEGORY_WISHLIST


class WishlistUpdate(WishlistCreate,ModelWithExtRefMutation):
    class Arguments:
        id = graphene.ID(required=False, description="ID of a Tag to update.")
        input = WishlistInput(
            required=True, description="Fields required to update a product."
        )

    class Meta:
        description = "Creates a new Wishlist."
        model = models.Wishlist
        object_type = wishlists
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
        return cleaned_input
    
    @classmethod
    def save(cls, info: ResolveInfo, instance, cleaned_input):
        instance.search_index_dirty = True
        instance.save()
    
    @classmethod
    def _save_m2m(cls, _info: ResolveInfo, instance, cleaned_data):
        products = cleaned_data.get("products", None)
        if products is not None:
            instance.products.set(products)

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root, info, **data)
        return response
import graphene
from django.core.exceptions import ValidationError
from .....permission.enums import ProductPermissions
from .....product import models
from ....core import ResolveInfo
from ....core.doc_category import DOC_CATEGORY_WISHLIST
from ....core.mutations import ModelMutation
from ....core.types import BaseInputObjectType, ProductError, NonNullList
from ...types.wishlists import Wishlist


class WishlistInput(BaseInputObjectType):
    user = graphene.ID(
        description="Customer associated with the draft order.", name="user"
    )
    products = graphene.ID(
        description="List of products to be added to the collection.",name=""
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

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        if info.context.user and not info.context.user.is_authenticated:
            raise ValidationError("User must be authenticated to create a wishlist.")
        cleaned_input["user"] = info.context.user
        return cleaned_input
    
    @classmethod
    def save(cls, info: ResolveInfo, instance, cleaned_input):
        instance.search_index_dirty = True
        instance.save()
    
    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root, info, **data)
        return response
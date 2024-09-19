import graphene
from graphene import relay

from ....product import models
from ...core.connection import CountableConnection
from ...core.fields import FilterConnectionField
from ...core.doc_category import DOC_CATEGORY_PRODUCTS
from ...core.descriptions import (
    ADDED_IN_314,
    PREVIEW_FEATURE,
)
from ....permission.enums import (
    AccountPermissions
)
from ....permission.auth_filters import AuthorizationFilters
from ...core.federation import federated_entity
from ..sorters import ProductOrder
from .products import ProductCountableConnection
from ..filters import ProductFilterInput, ProductWhereInput
from ...account.types import User
from ...core.types import ModelObjectType

@federated_entity("id")
class Wishlist(ModelObjectType[models.Wishlist]):
    id = graphene.GlobalID(required=True, description="The ID of the Wishlist.")
    user = graphene.Field(
        User,
        description=(
            "User who performed the action. Requires of of the following "
            f"permissions: {AccountPermissions.MANAGE_USERS.name}, "
            f"{AccountPermissions.MANAGE_STAFF.name}, "
            f"{AuthorizationFilters.OWNER.name}."
        ),
    )
    products = FilterConnectionField(
        ProductCountableConnection,
        filter=ProductFilterInput(description="Filtering options for products."),
        where=ProductWhereInput(
            description="Filtering options for products."
            + ADDED_IN_314
            + PREVIEW_FEATURE
        ),
        sort_by=ProductOrder(description="Sort products."),
        description="List of products in this collection.",
    )

    class Meta:
        description = "Represents a wishlist of products for a user."
        interfaces = [relay.Node]
        model = models.Wishlist

class WishlistCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_PRODUCTS
        node = Wishlist
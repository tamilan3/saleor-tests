from typing import Optional
import graphene
from graphene import relay

from saleor.graphql.channel import ChannelContext
from saleor.graphql.channel.types import ChannelContextTypeWithMetadata
from saleor.graphql.core.types.model import ModelObjectType
from saleor.graphql.product.dataloaders.products import WishListByIdLoader
from saleor.graphql.product.types.products import Product
from saleor.permission.auth_filters import AuthorizationFilters

from ....product import models
from ...core.connection import CountableConnection
from ...core.doc_category import DOC_CATEGORY_PRODUCTS
from ....permission.enums import AccountPermissions
from ...core.federation import federated_entity
from ...account.types import User
@federated_entity("id")
class Wishlist(ModelObjectType[models.Product]):
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
    products = graphene.Field(
        Product, required=True, description="preduct of the Wishlist."
    )

    class Meta:
        description = "Represents a wishlist of products for a user."
        interfaces = (relay.Node,)
        model = models.Wishlist

    @staticmethod
    def resolve_products(root: models.Wishlist, info):
        return root.products
    
        
        
class WishlistCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_PRODUCTS
        node = Wishlist
import graphene
from graphene import relay

from ....product import models
from ...core.connection import CountableConnection
from ...core.doc_category import DOC_CATEGORY_PRODUCTS
from ...core.types import ModelObjectType
from ...meta.types import ObjectWithMetadata, NonNullList
from ...account.types import User

class Wishlist(ModelObjectType[models.Wishlist]):
    id = graphene.GlobalID(required=True, description="The ID of the Wishlist.")
    user = graphene.Field(User, description="The user associated with the wishlist.")
    products = NonNullList("saleor.graphql.product.types.products")

    class Meta:
        description = "Represents a wishlist of products for a user."
        interfaces = [relay.Node, ObjectWithMetadata]
        model = models.Wishlist

class WishlistCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_PRODUCTS
        node = Wishlist
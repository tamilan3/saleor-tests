from typing import Optional
import graphene
from graphene import relay

from saleor.graphql.channel.dataloaders import ChannelBySlugLoader
from saleor.graphql.core import ResolveInfo
from saleor.graphql.core.context import get_database_connection_name
from saleor.graphql.core.descriptions import ADDED_IN_314, PREVIEW_FEATURE
from saleor.graphql.core.federation.entities import federated_entity
from saleor.graphql.core.fields import FilterConnectionField
from saleor.graphql.meta.types import ObjectWithMetadata
from saleor.graphql.product.filters import ProductFilterInput, ProductWhereInput
from saleor.graphql.product.sorters import ProductOrder
from saleor.graphql.product.utils import check_for_sorting_by_rank
from saleor.graphql.utils import get_user_or_app_from_context
from saleor.product.search import search_products

from ...channel import ChannelContext, ChannelQsContext
from saleor.graphql.channel.types import ChannelContextType, ChannelContextTypeWithMetadata
from saleor.graphql.product.types.products import ProductCountableConnection

from ....product import models
from ...core.connection import CountableConnection, create_connection_slice, filter_connection_queryset
from ...core.doc_category import DOC_CATEGORY_PRODUCTS
from ...account.types import User



@federated_entity("id Wishlist")
class Wishlist(ChannelContextTypeWithMetadata[models.Wishlist]):
    id = graphene.GlobalID(required=True, description="The ID of the Wishlist.")
    user = graphene.Field(User, description="user of this wishlist")
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
        default_resolver = ChannelContextType.resolver_with_context
        description = "Represents a collection of products."
        interfaces = [relay.Node, ObjectWithMetadata]
        model = models.Wishlist

    @staticmethod
    def resolve_channel(root: ChannelContext[models.Product], _info):
        return root.channel_slug
    
    @staticmethod
    def resolve_user(root: ChannelContext[models.Wishlist], _info: ResolveInfo):
        return root.node.user

    @staticmethod
    def resolve_products(
        root: ChannelContext[models.Wishlist], info: ResolveInfo, **kwargs
    ):
        check_for_sorting_by_rank(info, kwargs)
        search = kwargs.get("search")

        requestor = get_user_or_app_from_context(info.context)
        limited_channel_access = False if root.channel_slug is None else True

        def _resolve_products(channel):
            
            qs = root.node.products.using(
                get_database_connection_name(info.context)
            ).visible_to_user(requestor, channel, limited_channel_access)

            if search:
                qs = ChannelQsContext(
                    qs=search_products(qs.qs, search), channel_slug=root.channel_slug
                )
            else:
                qs = ChannelQsContext(qs=qs, channel_slug=root.channel_slug)

            kwargs["channel"] = root.channel_slug
            qs = filter_connection_queryset(
                qs, kwargs, allow_replica=info.context.allow_replica
            )
            return create_connection_slice(qs, info, kwargs, ProductCountableConnection)

        if root.channel_slug:
            return (
                ChannelBySlugLoader(info.context)
                .load(str(root.channel_slug))
                .then(_resolve_products)
            )
        else:
            return _resolve_products(None)
        
    
        
        
class WishlistCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_PRODUCTS
        node = Wishlist
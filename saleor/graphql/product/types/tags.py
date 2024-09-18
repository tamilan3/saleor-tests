import graphene
from graphene import relay

from ....product import models
from ...core.connection import CountableConnection
from ...core.doc_category import DOC_CATEGORY_PRODUCTS
from ...core.federation import federated_entity
from ...core.types import ModelObjectType
from ...meta.types import ObjectWithMetadata


@federated_entity("id")
class Tag(ModelObjectType[models.Tag]):
    id = graphene.GlobalID(required=True, description="The ID of the category.")
    name = graphene.String(required=True, description="Name of category")
    slug = graphene.String(required=True, description="Slug of the category.")

    class Meta:
        description = (
            "Represents a single category of products. Categories allow to organize "
            "products in a tree-hierarchies which can be used for navigation in the "
            "storefront."
        )
        interfaces = [relay.Node, ObjectWithMetadata]
        model = models.Tag


class TagCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_PRODUCTS
        node = Tag
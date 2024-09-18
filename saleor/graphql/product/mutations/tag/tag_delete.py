import graphene
from django.db.models.expressions import Exists, OuterRef

from .....core.tracing import traced_atomic_transaction
from .....permission.enums import ProductPermissions
from .....product import models
from ....app.dataloaders import get_app_promise
from ....channel import ChannelContext
from ....core import ResolveInfo
from ....core.descriptions import ADDED_IN_310
from ....core.mutations import ModelDeleteMutation, ModelWithExtRefMutation
from ....core.types import ProductError
from ...types import Tag


class TagDelete(ModelDeleteMutation, ModelWithExtRefMutation):
    class Arguments:
        id = graphene.ID(required=False, description="ID of a Tag to delete.")
        external_reference = graphene.String(
            required=False,
            description=f"External ID of a Tag to delete. {ADDED_IN_310}",
        )

    class Meta:
        description = "Deletes a Tag."
        model = models.Tag
        object_type = Tag
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ProductError
        error_type_field = "product_errors"

    @classmethod
    def success_response(cls, instance):
        instance = ChannelContext(node=instance, channel_slug=None)
        return super().success_response(instance)

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, external_reference=None, id=None
    ):
        instance = cls.get_instance(info, external_reference=external_reference, id=id)
        with traced_atomic_transaction():
            # Remove the tag from all products before deleting
            models.Product.tags.through.objects.filter(tag=instance).delete()
            
            response = super().perform_mutation(
                _root, info, external_reference=external_reference, id=id
            )

        return response

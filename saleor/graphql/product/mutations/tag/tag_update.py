import graphene
from .....permission.enums import ProductPermissions
from .....product import models
from ....core import ResolveInfo
from ....core.mutations import ModelWithExtRefMutation
from ....core.types.common import ProductError
from ....plugins.dataloaders import get_plugin_manager_promise
from ...types import Tag
from .tag_create import TagCreate, TagInput


class TagUpdate(TagCreate, ModelWithExtRefMutation):
    class Arguments:
        id = graphene.ID(required=False, description="ID of a Tag to update.")
        input = TagInput(
            required=True, description="Fields required to update a product."
        )

    class Meta:
        description = "Updates an existing tag."
        model = models.Tag
        object_type = Tag
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ProductError
        error_type_field = "product_errors"
        support_meta_field = True
        support_private_meta_field = True

    @classmethod
    def post_save_action(cls, info: ResolveInfo, instance, cleaned_input):
        manager = get_plugin_manager_promise(info.context).get()
        cls.call_event(manager.product_updated, instance)


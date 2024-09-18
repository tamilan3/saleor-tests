import graphene
from django.core.exceptions import ValidationError

from .....permission.enums import ProductPermissions
from .....product import models
from .....product.error_codes import ProductErrorCode
from ....core import ResolveInfo
from ....core.doc_category import DOC_CATEGORY_TAG
from ....core.mutations import ModelMutation
from ....core.types import BaseInputObjectType, ProductError
from ....core.validators import validate_slug_and_generate_if_needed
from ...types import Tag
from ....channel import ChannelContext


class TagInput(BaseInputObjectType):
    name = graphene.String(description="Tag name.")
    slug = graphene.String(description="Tag slug.")
    class Meta:
        doc_category = DOC_CATEGORY_TAG


class TagCreate(ModelMutation):
    class Arguments:
        input = TagInput(
            required=True, description="Fields required to create a Tag."
        )

    class Meta:
        description = "Creates a new Tag."
        model = models.Tag
        object_type = Tag
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ProductError
        error_type_field = "product_errors"
        support_meta_field = True
        support_private_meta_field = True

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)
        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "name", cleaned_input
            )
        except ValidationError as error:
            error.code = ProductErrorCode.REQUIRED.value
            raise ValidationError({"slug": error})

        return cleaned_input

    @classmethod
    def save(cls, info: ResolveInfo, instance, cleaned_input):
        instance.search_index_dirty = True
        instance.save()

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        response = super().perform_mutation(_root, info, **data)
        return response
from tempfile import NamedTemporaryFile

import pytest
from testapp.models import Attachment

from djantic import ModelSchema


@pytest.mark.django_db
def test_image_field_schema():
    class AttachmentSchema(ModelSchema):
        class Config:
            model = Attachment

    image_file = NamedTemporaryFile(suffix=".jpg")
    attachment = Attachment.objects.create(
        description="My image upload",
        image=image_file.name,
    )

    assert AttachmentSchema.schema() == {
        "title": "AttachmentSchema",
        "description": "Attachment(id, description, image)",
        "type": "object",
        "properties": {
            "id": {"title": "Id", "description": "id", "type": "integer"},
            "description": {
                "title": "Description",
                "description": "description",
                "maxLength": 255,
                "type": "string",
            },
            "image": {
                "title": "Image",
                "description": "image",
                "maxLength": 100,
                "type": "string",
            },
        },
        "required": ["description"],
    }

    assert AttachmentSchema.from_django(attachment).dict() == {
        "id": attachment.id,
        "description": attachment.description,
        "image": attachment.image.name,
    }

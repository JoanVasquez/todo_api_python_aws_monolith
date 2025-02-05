from django.forms.models import model_to_dict


def serialize_instance(instance) -> dict:
    """
    Serialize a Django model instance to a dict.
    """
    return model_to_dict(instance)


def deserialize_instance(model_class, data: dict):
    """
    Re-create a Django model instance from a dict.
    Note: This does not mark the instance as “loaded” from the database.
    """
    return model_class(**data)

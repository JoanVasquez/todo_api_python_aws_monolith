# test_serialization.py

from django.db import models
from django.test import TestCase

from core.utils.model_serializers import (deserialize_instance,
                                          serialize_instance)


# Define a dummy model for testing.
# (If you already have a model to test against, you can use that one.)
class DummyModel(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True)

    class Meta:
        # This is needed if your test file is not in an installed app.
        app_label = "myapp"


class SerializationTest(TestCase):

    def setUp(self):
        # Create a DummyModel instance (without saving to the database)
        self.instance = DummyModel(name="John Doe", age=25)

    def test_serialize_instance(self):
        """
        Test that serialize_instance returns a dict with the correct fields.
        Note: For an unsaved instance, the primary key field is None.
        """
        data = serialize_instance(self.instance)
        expected_data = {
            "id": None,  # Django sets id to None for unsaved instances
            "name": "John Doe",
            "age": 25,
        }
        self.assertEqual(data, expected_data)

    def test_deserialize_instance(self):
        """
        Test that deserialize_instance creates an instance with the correct
        attributes.
        """
        data = {
            "name": "Jane Smith",
            "age": 30,
        }
        instance = deserialize_instance(DummyModel, data)
        self.assertIsInstance(instance, DummyModel)
        self.assertEqual(instance.name, "Jane Smith")
        self.assertEqual(instance.age, 30)

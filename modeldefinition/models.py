from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from ordered_model.models import OrderedModel
from django.core.exceptions import ValidationError
from model_utils import Choices
#from treebeard.mp_tree import MP_Node
from treenode.models import TreeNodeModel

'''
To do:
 - inherit from TimeStampedModel
 - implement Referenced Variable (lookup by class & property)
 - implement ChoiceValue out of selected class + field (key, value)
 - implement Unit for NumericValue (via subclass or additional features)
 - add existing fields to (other) classes
'''


'''
class ValuePointer(AbstractValue):
    value_reference = models.ForeignKey(
        'DynamicObject', on_delete=models.CASCADE, null=True, blank=True, related_name='valuepointers')

    def __str__(self):
        return f"{self.value_reference}"

# Lookup Value by Class, Field
# Job src=C: (viele jobs, welcher?)
# Task ref src = (Job src)

'''

class Property(PolymorphicModel):
    name = models.CharField(max_length=255, blank=False,
                            null=False)
    element = models.ForeignKey(
        'Element', on_delete=models.CASCADE, related_name='properties')

    class Meta:
        verbose_name_plural = "properties"
        unique_together = (("name", "element"),)

    def __str__(self):
        instance = self.get_real_instance()
        if self.__str__ != instance.__str__:
            return str(self.get_real_instance())
        return str(super())


class ValueObject(Property):
    value_class = models.ForeignKey(
        'Element', on_delete=models.CASCADE, related_name='class_set', limit_choices_to=models.Q(model_type='Class'))
    value = models.ForeignKey(
        'Element', on_delete=models.CASCADE, related_name='object_set', limit_choices_to=models.Q(model_type='Object'))

    def __str__(self):
        return f"{self.value}"


class ValueNumber(Property):
    value = models.FloatField()

    def __str__(self):
        return f"{self.name} = {self.value} ({self.polymorphic_ctype})"


class ValueString(Property):
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} = {self.value} ({self.polymorphic_ctype})"


# class ValueImage(Property):
#    value = models.ImageField(upload_to='temp')


class Element(TreeNodeModel):
    TYPES = Choices('Namespace', 'Class', 'Object')

    name = models.CharField(max_length=255, blank=False,
                            null=False, unique=True)
    model_type = models.CharField(
        choices=TYPES, default=TYPES.Object, max_length=100)
    treenode_display_field = 'name'

    def __str__(self):
        if self.parent:
            return f"{self.name} (Type: {self.model_type}; Parent: {self.parent.name})"
        return f"{self.name} (Type: {self.model_type})"


'''
Notes:
 - Why not Treebeared: parent field can not be used as autocomplete field (field not in db), AL_Node has parent, but UI very poor
 - Why not django-MPTT: Draggable Admin only for < 1000 items. Cannot close unneccessary nodes. UI primitive, but functional.
'''
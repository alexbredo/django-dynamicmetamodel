from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from ordered_model.models import OrderedModel
from django.core.exceptions import ValidationError
from model_utils import Choices

'''
To do:
 - inherit from TimeStampedModel
 - implement Referenced Variable (lookup by class & property)
 - implement ChoiceValue out of selected class + field (key, value)
 - implement Unit for NumericValue (via subclass or additional features)
 - add existing fields to (other) classes
'''


class DynamicClass(PolymorphicModel):
    name = models.CharField(max_length=255, blank=False,
                            null=False, unique=True)

    class Meta:
        verbose_name_plural = "dynamic classes"

    def __str__(self):
        return self.name


class Field(PolymorphicModel):
    dynamic_class = models.ForeignKey(
        'DynamicClass', on_delete=models.CASCADE, related_name='classfields')
    name = models.CharField(max_length=255, blank=False,
                            null=False)

    class Meta:
        unique_together = ('name', 'dynamic_class', )
        ordering = ('name', 'dynamic_class')
        indexes = [
            models.Index(fields=['dynamic_class', 'name']),
        ]

    def __str__(self):
        if self.dynamic_class:
            return f'{self.name} ({self.dynamic_class.name})'
        return f'{self.name} (Global)'


class FieldValue(Field):
    value = models.ForeignKey(
        'AbstractValue', on_delete=models.CASCADE, related_name='fieldvalues')


class FieldCustom(Field):
    limit = models.Q(app_label='modeldefinition', model__startswith='value') & \
        ~models.Q(app_label='modeldefinition', model='value')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, limit_choices_to=limit)
    default_value = models.ForeignKey(
        'AbstractValue', on_delete=models.SET_NULL, null=True, blank=True)
    # result möglicherweise nicht unbedingt notwendig!
    #CONSTRAINTS = Choices('required', 'optional', 'result')

    # constraint = models.CharField(
    #    choices=CONSTRAINTS, default=CONSTRAINTS.required, max_length=100)


class DynamicObject(models.Model):
    dynamic_class = models.ForeignKey(
        'DynamicClass', on_delete=models.CASCADE, null=False)
    elements = models.ManyToManyField(
        'Field', through='AbstractValue', through_fields=('element', 'field'))

    def __str__(self):
        return f'{self.dynamic_class.name}-Object-{self.pk}'


class AbstractValue(PolymorphicModel):
    element = models.ForeignKey(
        'DynamicObject', on_delete=models.CASCADE, null=True, blank=True)
    # todo: limit_choices_to=get_contenttype_choices
    field = models.ForeignKey(
        'Field', on_delete=models.PROTECT, null=True, blank=True)
    # Problem: ValueNumber benötigt {element, field}, sonst sinnlos (da keinerlei Zugehörigkeit)

    class Meta:
        # abstract = True # could not register with admin, if abstract
        unique_together = ('element', 'field', )

    def __str__(self):
        instance = self.get_real_instance()
        if self.__str__ != instance.__str__:
            return str(self.get_real_instance())
        return str(super())

    '''
    @staticmethod
    def get_contenttype_choices():
        for cls in AbstractValue.__subclasses__():
            print(cls)

        query_a = Field.objects.filter(field_type=ContentType.objects.get_for_model(AbstractValue).model)
        return { 'fields': query_a }
    '''


'''
class SimpleValue(AbstractValue):
    pass
'''


class ValuePointer(AbstractValue):
    value_reference = models.ForeignKey(
        'DynamicObject', on_delete=models.CASCADE, null=True, blank=True, related_name='valuepointers')

    def __str__(self):
        return f"{self.value_reference}"

# Lookup Value by Class, Field
# Job src=C: (viele jobs, welcher?)
# Task ref src = (Job src)


class ValueNumber(AbstractValue):
    value = models.FloatField()

    def __str__(self):
        return f"{self.value}"


class ValueString(AbstractValue):
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.field.name} ({self.element}) = {self.value}"


# class ValueFloat(AbstractValue):
#    value = models.FloatField()


# class ValueImage(AbstractValue):
#    value = models.ImageField(upload_to='temp')


###############################################################################################################
""" class Task(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    params = models.ManyToManyField(Field, through='TaskParameter', through_fields=('task', 'field'))

    def __str__(self):
        return self.name """


""" class TaskParameter(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, null=False)
    # filtern: nach variablen, die zur spezifischen "DynamicClass" gehören

    class Meta:
        unique_together = ('task', 'field',)

    def __str__(self):
        return f'{self.task.name}-{self.field.name}' """


""" class JobTemplate(DynamicClass):
    tasks = models.ManyToManyField(Task, through='JobTemplateTask', through_fields=('job_template', 'task'))
    
    def __str__(self):
        return self.name 
    
    def get_required_fields(self):
        fields = list()
        for task in self.tasks.all():
            for param in task.params.filter(taskparameter__category=1):
                fields.append(param.name)
        return set(fields)
"""


""" class JobTemplateTask(OrderedModel):
    job_template = models.ForeignKey('JobTemplate', on_delete=models.CASCADE, null=False)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=False)
    order_with_respect_to = 'job_template'

    class Meta(OrderedModel.Meta):
        ordering = ('job_template', 'order')

    def __str__(self):
        return f'{self.job_template.name}-{self.task.name}' """


""" class Job(DynamicObject):
    # Instance / Object
    #job_template = models.ForeignKey(JobTemplate, on_delete=models.PROTECT, null=False) 
    #values = models.ManyToManyField(Field, through='AbstractValue', through_fields=('job', 'field'))
    class Meta:
            proxy = True """


class Property(models.Model):
    limit = models.Q(app_label='modeldefinition', model__startswith='value') & \
        ~models.Q(app_label='modeldefinition', model='value')

    name = models.CharField(max_length=255, blank=False,
                            null=False, unique=True)
    element = models.ForeignKey(
        'Element', on_delete=models.CASCADE, related_name='properties')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, limit_choices_to=limit)
    # value

    class Meta:
        verbose_name_plural = "properties"


class Element(models.Model):
    TYPES = Choices('Namespace', 'Class', 'Object')

    name = models.CharField(max_length=255, blank=False,
                            null=False, unique=True)
    model_type = models.CharField(
        choices=TYPES, default=TYPES.Object, max_length=100)
    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE, related_name='children')

    class Meta:
        ordering = ('name', )

    def __str__(self):
        if self.parent:
            return f"{self.name} (Type: {self.model_type}; Parent: {self.parent.name})"
        return f"{self.name} (Type: {self.model_type})"


class Eigenschaft(models.Model):
    name = models.CharField(max_length=255, blank=False,
                            null=False, unique=True)
    element = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name='properties')
        
    class Meta:
        verbose_name_plural = "eigenschaften"


from treebeard.mp_tree import MP_Node
#from relativity.treebeard import MP_Descendants, MP_Subtree
class Category(MP_Node):
    name = models.CharField(max_length=30)
    node_order_by = ['name']

    #descendants = MP_Descendants()
    #subtree = MP_Subtree()

    def __str__(self):
        return self.name

# https://django-treebeard.readthedocs.io/en/latest/admin.html
# https://github.com/alexhill/django-relativity 
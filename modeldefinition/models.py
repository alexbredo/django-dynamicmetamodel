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
 - Problemstellung: 
'''


class DynamicClass(PolymorphicModel):
    name = models.CharField(max_length=255, blank=False,
                            null=False, unique=True)

    class Meta:
        verbose_name_plural = "dynamic classes"

    def __str__(self):
        return self.name


class Field(models.Model):
    # result möglicherweise nicht unbedingt notwendig!
    CONSTRAINTS = Choices('required', 'optional', 'result')

    name = models.CharField(max_length=255, blank=False,
                            null=False)
    constraint = models.CharField(
        choices=CONSTRAINTS, default=CONSTRAINTS.required, max_length=100)

    limit = models.Q(app_label='modeldefinition', model__startswith='value') & \
        ~models.Q(app_label='modeldefinition', model='value')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="fields", limit_choices_to=limit)
    dynamic_class = models.ForeignKey(
        'DynamicClass', on_delete=models.CASCADE, null=True, blank=True, related_name='required_fields')

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
        #abstract = True # could not register with admin, if abstract
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

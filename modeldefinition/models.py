from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from ordered_model.models import OrderedModel
from django.core.exceptions import ValidationError


# Field von contenttype erben??
class CustomField(models.Model):
    # evtl nur pro namespace - nicht global?
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    limit = models.Q(app_label='modeldefinition', model='numbervalue') | \
            models.Q(app_label='modeldefinition', model='stringvalue')
    field_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="fields", limit_choices_to=limit)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

'''
class Namespace(models.Model):
    # Sozusagen eine Tabelle
    name = models.CharField(max_length=255)
    #valid = models.ManyToManyField(CustomField)

    def __str__(self):
        return self.name
    # todo: required fields check


class Record(models.Model):
    # Sozusagen eine Zeile in der Tabelle 
    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE, null=False)
    values = models.ManyToManyField(CustomField, through='AbstractValue', through_fields=('record', 'field'))


def get_contenttype_choices():
    for cls in AbstractValue.__subclasses__():
        print(cls)

    query_a = CustomField.objects.filter(field_type=ContentType.objects.get_for_model(AbstractValue).model)
    return { 'fields': query_a }
'''

class AbstractValue(PolymorphicModel):
    job = models.ForeignKey('Job', on_delete=models.CASCADE, null=False) 
    # record = models.ForeignKey(Record, on_delete=models.CASCADE, null=False)
    field = models.ForeignKey(CustomField, on_delete=models.PROTECT, null=False)  # todo: limit_choices_to=get_contenttype_choices

    class Meta:
        unique_together = ('job', 'field',)
        # abstract = True
        # Geht nicht, weil dann das Model im Admin nicht registriert werden kann
        # Ist aber nicht schlimm, da im Admin nur bestimmte Typen erlaubt werden

    def __str__(self):
        instance = self.get_real_instance()
        if self.__str__ != instance.__str__:
            return str(self.get_real_instance())
        return str(super())


class NumberValue(AbstractValue):
    value = models.FloatField()
    # Unit
    def __init__(self, *args, **kwargs):
        super(NumberValue, self).__init__(*args, **kwargs)
        #print("###############")
        #print(super().__dict__)
        #self.field.limit_choices_to = { 'field_type': 'number value' }

    def __str__(self):
        return f"{self.value}"


class StringValue(AbstractValue):
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.value}"

# todo ChoiceValue out of selected namespace + field 
# Evtl. TupleChoiceValue (index + name)



###############################################################################################################

class Task(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    params = models.ManyToManyField(CustomField, through='TaskParameter', through_fields=('task', 'field'))

    def __str__(self):
        return self.name


class TaskParameter(models.Model):
    PARAMETER_TYPES = (
        (1, 'required parameter'),
        (100, 'optional parameter'),
        (1000, 'result'),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE, null=False)
    category = models.PositiveIntegerField(default=1, choices=PARAMETER_TYPES)

    class Meta:
        unique_together = ('task', 'field',)

    def __str__(self):
        return f'{self.task.name}-{self.field.name}'


class JobTemplate(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    tasks = models.ManyToManyField(Task, through='JobTemplateTask', through_fields=('job_template', 'task'))
    
    def __str__(self):
        fields = list()
        for task in self.tasks.all():
            for param in task.params.filter(taskparameter__category=1):
                fields.append(param.name)
        fields_str = ', '.join(set(fields))
        return f'{self.name} ({fields_str})'


class JobTemplateTask(OrderedModel):
    job_template = models.ForeignKey(JobTemplate, on_delete=models.CASCADE, null=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)
    order_with_respect_to = 'job_template'

    class Meta(OrderedModel.Meta):
        ordering = ('job_template', 'order')

    def __str__(self):
        return f'{self.job_template.name}-{self.task.name}'


class Job(models.Model):
    job_template = models.ForeignKey(JobTemplate, on_delete=models.PROTECT, null=False) 
    values = models.ManyToManyField(CustomField, through='AbstractValue', through_fields=('job', 'field'))
    '''
    def clean_fields(self, exclude=None):
        print(self.values)
        raise ValidationError('Wrong fields specified. Field missing: ...')
        return super().clean_fields(exclude)

    def clean(self):
        for x in self.values.all():
            print(x)

        raise ValidationError('Wrong fields specified. Field missing: ...')
        return super().clean()
    '''
# CustomField

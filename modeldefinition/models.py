from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from ordered_model.models import OrderedModel
from django.core.exceptions import ValidationError
from model_utils import Choices
#from model_utils.managers import InheritanceManager


# Idee: clean in dem modell aufrufen, wo es validiert werden soll

# inherit from TimeStampedModel

class DynamicClass(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    related = models.ManyToManyField('self', symmetrical=True)
    # required_variables (related name)
    # many tasks (task is another class) select

    class Meta:
        verbose_name_plural = "dynamic classes"

    def __str__(self):
        return self.name


class DynamicVariable(models.Model):
    CONSTRAINTS = Choices('required', 'optional', 'result') # result möglicherweise nicht unbedingt notwendig!

    dynamic_class = models.ForeignKey('DynamicClass', on_delete=models.CASCADE, null=False, related_name='required_variables')
    name = models.CharField(max_length=255, blank=False, null=False)
    # Limit to all subclasses of Value (value* ?)
    limit = models.Q(app_label='modeldefinition', model__startswith='value') & \
        ~models.Q(app_label='modeldefinition', model='value')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="fields", limit_choices_to=limit)
    constraint = models.CharField(choices=CONSTRAINTS, default=CONSTRAINTS.required, max_length=100)

    class Meta:
        unique_together = ('name', 'dynamic_class', )
        ordering = ('dynamic_class', 'name', )
        indexes = [
            models.Index(fields=['dynamic_class', 'name']),
        ]

    def __str__(self):
        return f'{self.name} ({self.dynamic_class.name})'


#class ObjectVariable(models.Model):
#    dynamic_object = models.ForeignKey('DynamicObject', on_delete=models.CASCADE, null=False)
#    dynamic_variable = models.ForeignKey('DynamicVariable', on_delete=models.CASCADE, null=False)
#    value = models.ForeignKey('Value', on_delete=models.CASCADE, null=False)


class DynamicObject(models.Model):
    dynamic_class = models.ForeignKey('DynamicClass', on_delete=models.CASCADE, null=False)
    variables = models.ManyToManyField('DynamicVariable', through='Value', through_fields=('dynamic_object', 'dynamic_variable'))

    def __str__(self):
        return f'{self.dynamic_class.name}-Object-{self.id}'


class Value(PolymorphicModel):
    dynamic_object = models.ForeignKey('DynamicObject', on_delete=models.CASCADE, null=False) # vorher: job
    dynamic_variable = models.ForeignKey('DynamicVariable', on_delete=models.PROTECT, null=False)  # todo: limit_choices_to=get_contenttype_choices
    #objects = InheritanceManager()

    class Meta:
        unique_together = ('dynamic_object', 'dynamic_variable',)
        # abstract = True
        # Geht nicht, weil dann das Model im Admin nicht registriert werden kann
        # Ist aber nicht schlimm, da im Admin nur bestimmte Typen erlaubt werden

    def __str__(self):
        instance = self.get_real_instance()
        if self.__str__ != instance.__str__:
            return str(self.get_real_instance())
        return str(super())
    
    '''
    @staticmethod
    def get_contenttype_choices():
        for cls in Value.__subclasses__():
            print(cls)

        query_a = DynamicVariable.objects.filter(field_type=ContentType.objects.get_for_model(Value).model)
        return { 'fields': query_a }
    '''

class ValueNumber(Value):
    value = models.FloatField()
    
    def __init__(self, *args, **kwargs):
        super(ValueNumber, self).__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.value}"


class ValueString(Value):
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.value}"


class ValueObject(Value):
    value = models.ForeignKey('DynamicObject', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.value}"


#class ValueFloat(Value):
#    value = models.FloatField()


#class ValueImage(Value):
#    value = models.ImageField(upload_to='temp')

# todo ChoiceValue out of selected namespace + field 
# Evtl. TupleChoiceValue (index + name), List, Object



###############################################################################################################

class Task(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    params = models.ManyToManyField(DynamicVariable, through='TaskParameter', through_fields=('task', 'field'))

    def __str__(self):
        return self.name


class TaskParameter(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False)
    field = models.ForeignKey(DynamicVariable, on_delete=models.CASCADE, null=False)
    # filtern: nach variablen, die zur spezifischen "DynamicClass" gehören

    class Meta:
        unique_together = ('task', 'field',)

    def __str__(self):
        return f'{self.task.name}-{self.field.name}'


class JobTemplate(DynamicClass):
    tasks = models.ManyToManyField(Task, through='JobTemplateTask', through_fields=('job_template', 'task'))
    
    def __str__(self):
        return self.name

    '''
    def get_required_fields(self):
        fields = list()
        for task in self.tasks.all():
            for param in task.params.filter(taskparameter__category=1):
                fields.append(param.name)
        return set(fields)
    '''


class JobTemplateTask(OrderedModel):
    job_template = models.ForeignKey('JobTemplate', on_delete=models.CASCADE, null=False)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=False)
    order_with_respect_to = 'job_template'

    class Meta(OrderedModel.Meta):
        ordering = ('job_template', 'order')

    def __str__(self):
        return f'{self.job_template.name}-{self.task.name}'


class Job(DynamicObject):
    # Instance / Object
    #job_template = models.ForeignKey(JobTemplate, on_delete=models.PROTECT, null=False) 
    #values = models.ManyToManyField(DynamicVariable, through='Value', through_fields=('job', 'field'))
    class Meta:
            proxy = True
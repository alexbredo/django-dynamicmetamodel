from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


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


class Namespace(models.Model):
    ''' Sozusagen eine Tabelle '''
    name = models.CharField(max_length=255)
    #valid = models.ManyToManyField(CustomField)

    def __str__(self):
        return self.name
    # todo: required fields check


class Record(models.Model):
    ''' Sozusagen eine Zeile in der Tabelle '''
    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE, null=False)
    values = models.ManyToManyField(CustomField, through='AbstractValue', through_fields=('record', 'field'))


def get_contenttype_choices():
    for cls in AbstractValue.__subclasses__():
        print(cls)

    query_a = CustomField.objects.filter(field_type=ContentType.objects.get_for_model(AbstractValue).model)
    return { 'fields': query_a }


class AbstractValue(PolymorphicModel):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, null=False)
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE, null=False)  # todo: limit_choices_to=get_contenttype_choices

    class Meta:
        unique_together = ('record', 'field',)
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
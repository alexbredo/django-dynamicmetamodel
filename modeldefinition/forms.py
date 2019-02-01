from modeldefinition import models
from django.core.exceptions import ValidationError
from django import forms


class ValueNumberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = models.FieldCustom.objects.filter(
            content_type__model='valuenumber')


class ValueStringForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = models.FieldCustom.objects.filter(
            content_type__model='valuestring')


class ValueObjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = models.FieldCustom.objects.filter(
            content_type__model='valueobject')


class ValuePointerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = models.FieldCustom.objects.filter(
            content_type__model='valuepointer')
from . import models
from django.core.exceptions import ValidationError
from django import forms


class ValueNumberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dynamic_variable'].queryset = models.DynamicVariable.objects.filter(content_type__model='valuenumber')
        

class ValueStringForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dynamic_variable'].queryset = models.DynamicVariable.objects.filter(content_type__model='valuestring')


class ValueObjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dynamic_variable'].queryset = models.DynamicVariable.objects.filter(content_type__model='valueobject')


class ValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

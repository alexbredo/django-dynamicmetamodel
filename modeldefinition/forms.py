from . import models


from django import forms
class NumberValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = models.CustomField.objects.filter(field_type__model='numbervalue')


from django import forms
class StringValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = models.CustomField.objects.filter(field_type__model='stringvalue')
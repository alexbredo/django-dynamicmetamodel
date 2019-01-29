from . import models
from django.core.exceptions import ValidationError
from django import forms


class NumberValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = models.CustomField.objects.filter(field_type__model='numbervalue')


class StringValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = models.CustomField.objects.filter(field_type__model='stringvalue')

    #def clean_field(self):
        #print(self.cleaned_data['field'])
    #    raise ValidationError('Draft entries may not have a publication date.')

class JobForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        #print(self.__dict__)

    def clean(self):
        print(self.cleaned_data)
        values = self.cleaned_data.get('values')
            
        raise ValidationError("The word has a different language")
        return self.cleaned_data
        
# ugly example: https://gist.github.com/vero4karu/1c065cb54baef2da79c2

'''
https://github.com/django-oscar/django-oscar/issues/1743
class ProductAttributeValueFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(ProductAttributeValueFormSet, self).__init__(*args, **kwargs)
        # This return initial [{'attribute' initial}, {..}, {..}]
        self.initial = [{'attribute': a} for a in obj.category.attributes.all()]
        # Now we need to make a queryset to each field of each form inline
        self.queryset = [{'value_option' .. }, { .. }]
'''
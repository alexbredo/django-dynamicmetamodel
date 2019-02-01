from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter, PolymorphicInlineSupportMixin, StackedPolymorphicInline
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin
from django.forms.models import BaseInlineFormSet
from polymorphic.formsets import BasePolymorphicInlineFormSet
from . import models
from . import forms


class FieldInline(StackedPolymorphicInline):
    class FieldValueInline(StackedPolymorphicInline.Child):
        model = models.FieldValue
        #autocomplete_fields = ['value']
        #form = forms.ValueStringForm

    class FieldCustomInline(StackedPolymorphicInline.Child):
        model = models.FieldCustom
        #form = forms.ValuePointerForm

    model = models.Field
    child_inlines = (
        FieldCustomInline,
        FieldValueInline
    )


""" class FieldInlineAdmin(admin.TabularInline):
    model = models.Field
    extra = 0 """


@admin.register(models.DynamicClass)
class DynamicClassAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = [FieldInline]  
    # filter_horizontal = ('related',)


class ValueInlineFormset(BasePolymorphicInlineFormSet): # BaseInlineFormSet
    def clean(self):
        #if any(self.errors):
        #    # Don't bother validating the formset unless each form is valid on its own
        #    return

        print('FIRE---------------FIRE')
        #form_fields = [form.cleaned_data['field'] for form in self.forms]

        # Check 1: Missing fields
        #missing = models.Field.objects.filter(dynamic_class=self.instance.dynamic_class).exclude(name__in=form_fields)
        #missing_str = ', '.join([f'{field.name} ({field.content_type})' for field in missing])
        #print (missing)

        # Check 2: Too many fields
        #too_many = models.Field.objects.filter(dynamic_class=self.instance.dynamic_class).filter(name__in=form_fields)
        #print(too_many)
        # todo
        #raise forms.ValidationError("Missing fields: " + missing_str)


class ValueInline(StackedPolymorphicInline):
    class ValueNumberInline(StackedPolymorphicInline.Child):
        model = models.ValueNumber
        form = forms.ValueNumberForm

    class ValueStringInline(StackedPolymorphicInline.Child):
        model = models.ValueString
        form = forms.ValueStringForm

    class ValuePointerInline(StackedPolymorphicInline.Child):
        model = models.ValuePointer
        form = forms.ValuePointerForm
        autocomplete_fields = ['value_reference']

    model = models.AbstractValue
    child_inlines = (
        ValueNumberInline,
        ValueStringInline,
        ValuePointerInline
    )
    formset = ValueInlineFormset


@admin.register(models.DynamicObject)
class DynamicObjectAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = [ValueInline] 
    list_display = ("id", "dynamic_class")
    extra = 0
    base_model = models.DynamicObject
    child_models = (models.ValueNumber, models.ValueString, models.ValuePointer)
    list_display = ('id', 'dynamic_class', '__str__')
    #list_filter = (PolymorphicChildModelFilter,)
    search_fields = ['id', 'dynamic_class', '__str__']


@admin.register(models.ValueNumber)
class ValueNumberAdmin(PolymorphicChildModelAdmin):
    base_model = models.ValueNumber
    show_in_index = False
    form = forms.ValueNumberForm


@admin.register(models.ValueString)
class ValueStringAdmin(PolymorphicChildModelAdmin):
    base_model = models.ValueString
    show_in_index = False
    form = forms.ValueStringForm 


@admin.register(models.ValuePointer)
class ValuePointerAdmin(PolymorphicChildModelAdmin):
    base_model = models.ValuePointer
    show_in_index = False
    form = forms.ValuePointerForm 
    autocomplete_fields = ['value_reference']


#@admin.register(models.ValueObject)
#class ValueObjectAdmin(PolymorphicChildModelAdmin):
#    base_model = models.ValueObject
#    show_in_index = False
#    form = forms.ValueObjectForm


@admin.register(models.AbstractValue)
class ValueParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.AbstractValue
    child_models = (models.ValueNumber, models.ValueString, models.ValuePointer)
    list_display = ('id', 'element', 'field', 'polymorphic_ctype', '__str__')
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ['field__name']


@admin.register(models.FieldCustom)
class FieldCustomAdmin(PolymorphicChildModelAdmin):
    base_model = models.FieldCustom
    show_in_index = False


@admin.register(models.FieldValue)
class FieldValueAdmin(PolymorphicChildModelAdmin):
    base_model = models.FieldValue
    show_in_index = False


@admin.register(models.Field)
class FieldParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.Field
    child_models = (models.FieldCustom, models.FieldValue)
    list_display = ('id', 'name', 'dynamic_class', 'polymorphic_ctype', )
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ['name', 'dynamic_class__name']
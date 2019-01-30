from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter, PolymorphicInlineSupportMixin, StackedPolymorphicInline
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin
from django.forms.models import BaseInlineFormSet
from polymorphic.formsets import BasePolymorphicInlineFormSet
#from .models import Value, ValueNumber, ValueString, DynamicVariable, Record, Namespace
from . import models
from . import forms


class DynamicVariableInline(admin.TabularInline):
    model = models.DynamicVariable
    extra = 0


@admin.register(models.DynamicClass)
class DynamicClassAdmin(admin.ModelAdmin):
    inlines = [DynamicVariableInline]  
    filter_horizontal = ('related',)


@admin.register(models.DynamicVariable)
class DynamicVariableAdmin(admin.ModelAdmin):
    list_display = ('dynamic_class', 'name', 'content_type', 'constraint', ) 
    list_filter = ('content_type', 'constraint', )
    search_fields = ('name', 'content_type__model', 'dynamic_class__name', )


class ValueInlineFormset(BasePolymorphicInlineFormSet): # BaseInlineFormSet
    def clean(self):
        #if any(self.errors):
        #    # Don't bother validating the formset unless each form is valid on its own
        #    return

        print('FIRE---------------FIRE')
        form_fields = [form.cleaned_data['dynamic_variable'] for form in self.forms]

        # Check 1: Missing fields
        missing = models.DynamicVariable.objects.filter(dynamic_class=self.instance.dynamic_class).exclude(name__in=form_fields)
        missing_str = ', '.join([f'{field.name} ({field.content_type})' for field in missing])
        print (missing)

        # Check 2: Too many fields
        too_many = models.DynamicVariable.objects.filter(dynamic_class=self.instance.dynamic_class).filter(name__in=form_fields)
        print(too_many)
        # todo
        #raise forms.ValidationError("Missing fields: " + missing_str)


class ValueInline(StackedPolymorphicInline):
    class ValueNumberInline(StackedPolymorphicInline.Child):
        model = models.ValueNumber
        form = forms.ValueNumberForm

    class ValueStringInline(StackedPolymorphicInline.Child):
        model = models.ValueString
        form = forms.ValueStringForm

    class ValueObjectInline(StackedPolymorphicInline.Child):
        model = models.ValueObject
        form = forms.ValueObjectForm

    model = models.Value
    child_inlines = (
        ValueNumberInline,
        ValueStringInline,
        ValueObjectInline
    )
    formset = ValueInlineFormset

#class ObjectVariableInline(admin.TabularInline):
#    model = models.ObjectVariable
#    extra = 0


@admin.register(models.DynamicObject)
class DynamicObjectAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = [ValueInline] 
    list_display = ("id", "dynamic_class")
    extra = 0


class TaskParametersInline(admin.TabularInline):
    model = models.TaskParameter
    extra = 0


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [TaskParametersInline, ]
    


class JobTemplateTabularInline(OrderedTabularInline):
    model = models.JobTemplateTask
    fields = ('task', 'order', 'move_up_down_links',)
    readonly_fields = ('order', 'move_up_down_links',)
    extra = 1
    ordering = ('order',)


@admin.register(models.JobTemplate)
class JobTemplateAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ('name', )
    inlines = (JobTemplateTabularInline, )


@admin.register(models.JobTemplateTask)
class JobTemplateTaskAdmin(admin.ModelAdmin):
    pass   


@admin.register(models.Job)
class JobAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    list_display = ("id", "dynamic_class")
    inlines = (ValueInline,)
    extra = 0

# Im Job sollen nur die Felder angezeigt werden, die der Task auch benötigt.
# Andere Überlegeung: die Felder, die im JobTemplate () definiert werden. 


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


@admin.register(models.ValueObject)
class ValueObjectAdmin(PolymorphicChildModelAdmin):
    base_model = models.ValueObject
    show_in_index = False
    form = forms.ValueObjectForm


@admin.register(models.Value)
class ValueParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = models.Value
    child_models = (models.ValueNumber, models.ValueString)
    list_display = ('id', 'dynamic_object', 'dynamic_variable', 'polymorphic_ctype', '__str__')
    list_filter = (PolymorphicChildModelFilter,)
    form = forms.ValueForm


'''




#class ValueInline(admin.TabularInline, PolymorphicInlineSupportMixin):
#    model = KeyValuePair
#    #max_num = 1
#    extra = 0


@admin.register(Record)
class RecordAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = (ValueInline,)
    extra = 0


@admin.register(Namespace)
class NamespaceAdmin(admin.ModelAdmin):
    pass 




'''

'''
# https://github.com/bfirsh/django-ordered-model (Inline auch verfügbar)
from ordered_model.admin import OrderedModelAdmin

@admin.register(DynamicVariable)
class ItemAdmin(OrderedModelAdmin):
    list_display = ('name', 'move_up_down_links')
'''
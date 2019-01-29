from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter, PolymorphicInlineSupportMixin, StackedPolymorphicInline
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin
#from .models import AbstractValue, NumberValue, StringValue, CustomField, Record, Namespace
from . import models
from . import forms


@admin.register(models.CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    pass 


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


class ValueInline(StackedPolymorphicInline):
    class NumberValueInline(StackedPolymorphicInline.Child):
        model = models.NumberValue
        form = forms.NumberValueForm

    class StringValueInline(StackedPolymorphicInline.Child):
        model = models.StringValue
        form = forms.StringValueForm

    model = models.AbstractValue
    child_inlines = (
        NumberValueInline,
        StringValueInline,
    )


@admin.register(models.Job)
class JobAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    list_display = ("id", "job_template")
    inlines = (ValueInline,)
    extra = 0
    form = forms.JobForm


@admin.register(models.NumberValue)
class NumberValueAdmin(PolymorphicChildModelAdmin):
    base_model = models.NumberValue
    show_in_index = False
    form = forms.NumberValueForm


@admin.register(models.StringValue)
class StringValueAdmin(PolymorphicChildModelAdmin):
    base_model = models.StringValue
    show_in_index = False
    form = forms.StringValueForm


@admin.register(models.AbstractValue)
class AbstractValueParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = models.AbstractValue
    child_models = (models.NumberValue, models.StringValue)
    list_display = ('id', 'field', 'polymorphic_ctype', '__str__')
    list_filter = (PolymorphicChildModelFilter,)




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

@admin.register(CustomField)
class ItemAdmin(OrderedModelAdmin):
    list_display = ('name', 'move_up_down_links')
'''
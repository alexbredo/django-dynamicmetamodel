from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter, PolymorphicInlineSupportMixin, StackedPolymorphicInline
from .models import AbstractValue, NumberValue, StringValue, CustomField, Record, Namespace
from . import forms


@admin.register(NumberValue)
class NumberValueAdmin(PolymorphicChildModelAdmin):
    base_model = NumberValue
    show_in_index = False
    form = forms.NumberValueForm


@admin.register(StringValue)
class StringValueAdmin(PolymorphicChildModelAdmin):
    base_model = StringValue
    show_in_index = False


@admin.register(AbstractValue)
class AbstractValueParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = AbstractValue
    child_models = (NumberValue, StringValue)
    list_display = ('id', 'get_name', 'polymorphic_ctype', '__str__')
    list_filter = (PolymorphicChildModelFilter,)

    def get_name(self, obj):
        return obj.field.name
    get_name.short_description = 'Field'
    get_name.admin_order_field = 'field__name'


class ValueInline(StackedPolymorphicInline):
    class NumberValueInline(StackedPolymorphicInline.Child):
        model = NumberValue

    class StringValueInline(StackedPolymorphicInline.Child):
        model = StringValue

    model = AbstractValue
    child_inlines = (
        NumberValueInline,
        StringValueInline,
    )

'''

class ValueInline(admin.TabularInline, PolymorphicInlineSupportMixin):
    model = KeyValuePair
    #max_num = 1
    extra = 0
'''

@admin.register(Record)
class RecordAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = (ValueInline,)
    extra = 0


@admin.register(Namespace)
class NamespaceAdmin(admin.ModelAdmin):
    pass 

@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    pass 
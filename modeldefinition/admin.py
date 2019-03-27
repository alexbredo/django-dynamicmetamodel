import adminactions.actions as actions
import nested_admin
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.contenttypes.admin import GenericTabularInline
from django.forms.models import BaseInlineFormSet
from ordered_model.admin import (OrderedInlineModelAdminMixin,
                                 OrderedTabularInline)
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicChildModelFilter,
                               PolymorphicInlineSupportMixin,
                               PolymorphicParentModelAdmin,
                               StackedPolymorphicInline)
from polymorphic.formsets import BasePolymorphicInlineFormSet
from treenode.admin import TreeNodeModelAdmin
from treenode.forms import TreeNodeForm

from . import forms, models

actions.add_to_site(site)  # register all adminactions


class ValueInlineFormset(BasePolymorphicInlineFormSet):  # BaseInlineFormSet
    def clean(self):
        # if any(self.errors):
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
        # print(too_many)
        # todo
        #raise forms.ValidationError("Missing fields: " + missing_str)


class ValueInline(StackedPolymorphicInline):
    class ValueNumberInline(StackedPolymorphicInline.Child):
        model = models.ValueNumber
        readonly = ('polymorphic_ctype', )
        #form = forms.ValueNumberForm

    class ValueStringInline(StackedPolymorphicInline.Child):
        model = models.ValueString
        #readonly = ('polymorphic_ctype', )
        #form = forms.ValueStringForm

    class ValueObjectInline(StackedPolymorphicInline.Child):
        model = models.ValueObject
        #form = forms.ValuePointerForm
        autocomplete_fields = ['value']
        
    class ValueObjectMultipleInline(StackedPolymorphicInline.Child):
        model = models.ValueObjectMultiple
        autocomplete_fields = ['value']

    model = models.Property
    child_inlines = (
        ValueNumberInline,
        ValueStringInline,
        ValueObjectInline,
        ValueObjectMultipleInline
    )
    #formset = ValueInlineFormset


@admin.register(models.ValueNumber)
class ValueNumberAdmin(PolymorphicChildModelAdmin):
    base_model = models.ValueNumber
    show_in_index = False
    readonly = ('polymorphic_ctype', )
    #form = forms.ValueNumberForm


@admin.register(models.ValueString)
class ValueStringAdmin(PolymorphicChildModelAdmin):
    base_model = models.ValueString
    show_in_index = False
    readonly = ('polymorphic_ctype', )
    #form = forms.ValueStringForm


@admin.register(models.ValueObject)
class ValueObjectAdmin(PolymorphicChildModelAdmin):
    base_model = models.ValueObject
    show_in_index = False
    #form = forms.ValuePointerForm
    #autocomplete_fields = ['value_reference']


@admin.register(models.ValueObjectMultiple)
class ValueObjectMultipleAdmin(PolymorphicChildModelAdmin):
    base_model = models.ValueObjectMultiple
    show_in_index = False

'''
@admin.register(models.AbstractValue)
class ValueParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.AbstractValue
    child_models = (models.ValueNumber, models.ValueString,
                    models.ValuePointer)
    list_display = ('id', 'element', 'field', 'polymorphic_ctype', '__str__')
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ['field__name']
'''



#class PropertyInlineAdmin(nested_admin.NestedTabularInline):
#    model = models.Property
#    extra = 0


class PropertyInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PropertyInlineFormSet, self).__init__(*args, **kwargs)
        self.queryset = models.Property.objects.filter(
            element__in=self.instance.ancestors)


class PropertyReadonlyInlineAdmin(admin.TabularInline):
    model = models.Property
    extra = 0
    formset = PropertyInlineFormSet
    verbose_name = "Inherited Property"
    verbose_name_plural = "Inherited Properties"
    readonly_fields = ['__str__']

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ElementInlineAdmin(admin.TabularInline):
    model = models.Element
    extra = 0
    show_change_link = True
    exclude = ('tn_priority', )


class PropertyInlineAdmin(admin.TabularInline):
    model = models.Property
    extra = 0
    show_change_link = True
    

@admin.register(models.Element)
class ElementAdmin(PolymorphicInlineSupportMixin, TreeNodeModelAdmin):  # admin.ModelAdmin
    #treenode_accordion = True 
    treenode_display_mode = TreeNodeModelAdmin.TREENODE_DISPLAY_MODE_ACCORDION
    autocomplete_fields = ['tn_parent']
    list_display = ('id', 'model_type', 'tn_parent', )
    search_fields = ['name', 'tn_parent__name']
    exclude = ('tn_priority', )
    form = TreeNodeForm
    inlines = [ElementInlineAdmin, PropertyReadonlyInlineAdmin, ValueInline] # PropertyInlineAdmin


@admin.register(models.Property)
class PropertyParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.Property
    child_models = (models.ValueNumber, models.ValueString, ) # models.ValuePointer
    list_display = ('id', 'name', 'polymorphic_ctype', '__str__')
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ['name']
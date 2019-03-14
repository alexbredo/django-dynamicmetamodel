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
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from . import forms, models

actions.add_to_site(site)  # register all adminactions


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
    child_models = (models.ValueNumber, models.ValueString,
                    models.ValuePointer)
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


# @admin.register(models.ValueObject)
# class ValueObjectAdmin(PolymorphicChildModelAdmin):
#    base_model = models.ValueObject
#    show_in_index = False
#    form = forms.ValueObjectForm


@admin.register(models.AbstractValue)
class ValueParentAdmin(PolymorphicParentModelAdmin):
    base_model = models.AbstractValue
    child_models = (models.ValueNumber, models.ValueString,
                    models.ValuePointer)
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


class PropertyInlineAdmin(nested_admin.NestedTabularInline):
    model = models.Property
    extra = 0


class ChildInline(nested_admin.NestedTabularInline):  # admin.TabularInline
    model = models.Element
    extra = 0
    show_change_link = True
    inlines = [PropertyInlineAdmin]

    # def get_formset(self, request, obj=None, **kwargs):
    #    self.parent_obj = obj
    #    return super(ChildInline, self).get_formset(request, obj, **kwargs)

    # def has_add_permission(self, request):
    #    # Return True only if the parent has status == 1
    #    return self.parent_obj.status == 1

    # def has_change_permission(self, request, obj=None):
    #    return False

    # def has_add_permission(self, request, obj=None):
    #    return False

    # def has_delete_permission(self, request, obj=None):
    #    return False


@admin.register(models.Element)
class ElementAdmin(nested_admin.NestedModelAdmin):  # admin.ModelAdmin
    autocomplete_fields = ['parent']
    list_display = ('id', 'model_type', 'name', 'parent', )
    search_fields = ['name', 'parent__name']
    list_filter = ('model_type',)
    inlines = [PropertyInlineAdmin, ChildInline]
    # filter_horizontal = ('related',)


class ChildInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(ChildInlineFormSet, self).__init__(*args, **kwargs)
        self.queryset = models.Eigenschaft.objects.filter(
            element__in=self.get_all_parents())

    def get_all_parents(self):
        parents = list()
        parent = self.instance
        while parent != None:
            parents.append(parent)
            parent = parent.get_parent()
        return parents


class EigenschaftInlineAdmin(admin.TabularInline):
    model = models.Eigenschaft
    extra = 0
    formset = ChildInlineFormSet

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Category)
class CategoryAdmin(TreeAdmin):
    # , 'body', 'is_edited', 'timestamp',
    fields = ('name', '_position', '_ref_node_id', )
    form = movenodeform_factory(models.Category)
    inlines = [EigenschaftInlineAdmin]

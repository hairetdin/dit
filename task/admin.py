from django.contrib import admin
from .models import Mission, Comment, Executor, ExecutorMission
from contact.models import Employee
from django import forms
from django.core.urlresolvers import reverse

class ExecutorInline(admin.StackedInline):
    model = ExecutorMission
    extra = 0


class CommentInline(admin.StackedInline):
    readonly_fields = ('creator',)
    model = Comment
    extra = 0


class TaskClosedFilter(admin.SimpleListFilter):
    #filter opened or closed task
    title = 'Задачи'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'closedtask'

    def lookups(self, request, model_admin):
        return (
            ('opened', 'Скрыть закрытые'),
            ('closed', 'Только закрытые'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'opened':
            return queryset.filter(date_closed__isnull=True)
        if self.value() == 'closed':
            return queryset.filter(date_closed__isnull=False)


class ExecutorFilter(admin.SimpleListFilter):
    #filter executor
    title = 'Исполнители'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'executors'

    def lookups(self, request, model_admin):
        executors = [(e.id, e.employee.person) for e in Executor.objects.all()]
        executors.append(('None','Без исполнителя'))
        return executors

    def queryset(self, request, queryset):
        if self.value() == 'None':
            return queryset.filter(executormission__executor__exact=None)
        elif self.value():
                return queryset.filter(executormission__executor__exact=self.value())
        else:
            return queryset


class MissionForm(forms.ModelForm):
# Эта форма была сделана для уменьшения каскадных запросов к базе данных. В Mission есть внешний ключ на Employee, в Employee есть внешние ключи на Person Organization Subdivision (это те поля которые участвуют в отображении __str__). Сделав select_related я уменьшил количество запросов к базе данных, т.е. обработка идет одним запросом. Производительность сильно увеличивает
    def __init__(self, *args, **kwargs):
        super(MissionForm, self).__init__(*args, **kwargs)
        self.fields['initiator'].queryset = Employee.objects.all().select_related('person').select_related('organization').select_related('subdivision')
        self.fields['customer'].queryset = Employee.objects.all().select_related('person', 'organization', 'subdivision')

    class Meta:
        model = Mission
        fields = '__all__'

class MissionAdmin(admin.ModelAdmin):
    inlines = [ExecutorInline, CommentInline]
    list_display = ('id','date_created', 'customer_link', 'subject','date_exec_max', 'executors', 'date_closed',)
    list_display_links = ('id',)
    search_fields = ['subject']
    readonly_fields = ('date_closed','date_created','creator','customer_link')
    list_filter = (TaskClosedFilter, ExecutorFilter)
    form = MissionForm
    
    # view in list_display executors
    def executors(self, obj):
        html = ""
        em = obj.executormission_set.all()
        for e in em:
            html+= '%s; ' %(e.executor.employee.person)
        return html
    executors.short_description = 'Исполнители'
    
    # view link to employee model as 'user' field(show employee detail in another window)
    def customer_link(self, obj):
        return '<a href="{}">{}</a>'.format(
            reverse("admin:contact_employee_change" , args=(obj.customer.id,)),
            obj.customer.person
        )
    customer_link.allow_tags = True
    customer_link.short_description = 'Заказчик (ссылка откроется в другом окне)'

    def save_model(self, request,obj,form,change):
        if getattr(obj, 'creator', None) is None:
            obj.creator = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        #if formset.model != CommentInline:
        #    return super(MissionAdmin, self).save_formset(request, form, formset, change)
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.creator = request.user
            instance.save()
        formset.save_m2m()

#task._meta.app_label = 'Заказчики'
#admin.site.register(Customer) #removed from model
admin.site.register(Mission, MissionAdmin)
admin.site.register(Executor)
#admin.site.register(ExecutorMission)

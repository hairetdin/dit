from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Organization, Subdivision, Person, Phone, Email, Employee, Building, LdapInfo, ADLogonFromComputer
from django.core.urlresolvers import reverse
from datetime import date
from django.db.models import Count
from django.utils.html import format_html

class PhoneInline(admin.StackedInline):
    fields = ('number',)
    model = Phone
    extra = 0

class EmailInline(admin.TabularInline):
    fields = ('address',)
    model = Email
    extra = 0
    readonly_fields = ('address',)

class LdapInfoInline(admin.TabularInline):
    readonly_fields = ('samaccountname','lastlogon')
    model = LdapInfo

class LastLogonFilter(admin.SimpleListFilter):
    title = 'Подключался к AD'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'lastlogoninad'

    def lookups(self, request, model_admin):
        return (
            ('1 month ago', 'более 1 месяца назад'),
            ('2 month ago', 'более 2 месяцев назад'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1 month ago':
            return queryset.filter(ldapinfo__lastlogon__lte=date(2015,9,1))
        if self.value() == '2 month ago':
            return queryset.filter(ldapinfo__lastlogon__lte=date(2015,8,1))

class ADLogonFromComputerAdmin(admin.ModelAdmin):
    list_display = ('person','login_name','computer_name','logon_date','logon_time')
    search_fields = ['person__name', 'login_name']
    list_filter = ('logon_date',)

class PersonAdmin(admin.ModelAdmin):
    inlines = [LdapInfoInline, PhoneInline, EmailInline]
    search_fields = ['name']
    exclude = ('organization','ad_objectguid')
    list_display = ('name','ldap_last_logon',)
    list_filter = (LastLogonFilter,)
    
    def ldap_last_logon(self,obj):
        return("%s" %(obj.ldapinfo.lastlogon))
    ldap_last_logon.short_description = 'Подключался к AD'


class EmployeeAdmin(admin.ModelAdmin):
    search_fields = ['person__name']
    readonly_fields = ('person_info','person_edit')
    raw_id_fields = ('parent_employee',)
    
    def person_info(self, obj):
        html = ''
        phones = obj.person.phone_set.all()
        emails = obj.person.email_set.all()
        last_logon = obj.person.ldapinfo.lastlogon
        ad_login = obj.person.ldapinfo.samaccountname
        logon_from_computer=obj.person.adlogonfromcomputer_set.all()
        
        if phones:
            html+='<p>Телефоны: '
            for phone in phones:
                html+= '%s; ' %(phone.number)
            html+='</p>'
        if emails:
            html+='<p>Email: '
            for email in emails:
                html+= '%s; ' %(email.address)
            html+='</p>'
        if last_logon:
            html+='<p>Подключался к AD: '
            html+= '%s; ' %(last_logon)
            html+='</p>'
        if ad_login:
            html+='<p>Логин пользователя в AD: '
            html+= '%s; ' %(ad_login)
            html+='</p>'
        if logon_from_computer:
            html+='<p>Входил в Active Directory с компьютера: '
            logon_group_by = logon_from_computer.values('computer_name').annotate(total=Count('computer_name')).order_by('-total')
            html+='<ul>'
            for logon in logon_group_by:
                html+='<li>'
                html+= '%s - %s раз; ' %(logon['computer_name'], logon['total'])
                html+='</li>'
            html+='</ul>'
            html+='Последние 10 входов в Active Directory: '
            html+='<ul>'
            logon_ordered = logon_from_computer.order_by('-logon_date','-logon_time')[:10]
            for logon in logon_ordered:
                html+='<li>'
                html+= '%s %s - с компьютера %s; ' %(logon.logon_date, logon.logon_time.strftime('%H:%M'), logon.computer_name)
                html+='</li>'
            html+='</ul>'

        return format_html(html) # вывод дополнительной информации о пользователе
    person_info.short_description = 'Контакты'
    
        # view link to employee model as 'user' field(show employee detail in another window)
    def person_edit(self, obj):
        return '<a href="{}">{}</a>'.format(
            reverse("admin:contact_person_change" , args=(obj.person.id,)),
            obj.person
        )
    person_edit.allow_tags = True
    person_edit.short_description = 'Редактировать человека'
    

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name_plural = 'Привязка к базе Люди'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (PersonInline, )

admin.site.register(Organization)
admin.site.register(ADLogonFromComputer, ADLogonFromComputerAdmin)
admin.site.register(Subdivision)
admin.site.register(Person, PersonAdmin)
admin.site.register(Building)
admin.site.register(Employee, EmployeeAdmin)
# Re-register UserAdmin
#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
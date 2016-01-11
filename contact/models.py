from django.db import models
from dit import settings
from django.contrib.auth.models import User

class Building(models.Model):
    address = models.CharField(max_length = 200, null=True, blank=True)

    class Meta:
        verbose_name = 'Строение'
        verbose_name_plural = 'Строения'

    def __str__(self):
        return self.address


class Organization(models.Model):
    name = models.CharField('Наименование',max_length = 50)
    full_name = models.CharField('Полное название',max_length = 200, blank=True, null=True)
    address = models.ForeignKey(Building, null=True, blank=True, verbose_name = "Адрес")

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.name


class Subdivision(models.Model):
    organization = models.ForeignKey(Organization, verbose_name = "Организация")
    parent_subdiv = models.ForeignKey('self', null=True, blank=True, verbose_name = "Вышестоящее подразделение")
    name = models.CharField('Наименование', max_length = 200)
    full_name = models.CharField('Полное название', max_length = 200, null=True, blank=True)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

    def __str__(self):
        return self.name


#Путь для сохранения аватарок людей
def image_file_name(instance, filename):
    import os
    fileName, fileExtension = os.path.splitext(filename)
    new_filename = filename
    fname= '/'.join(['uploads', 'avatar', new_filename])
    afolder= os.path.join(settings.MEDIA_ROOT, 'uploads/avatar')
    file_path = afolder+'/'+new_filename
    if os.path.isfile(file_path):
        os.remove(file_path)
    if not os.path.exists(afolder):
        os.makedirs(afolder)
    return fname


class Person(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, help_text='Привязка к логину для входа в Задачи через веб', verbose_name = "Учетная запись веб")
    name = models.CharField('Имя',max_length = 250)
    #first_name = models.CharField('Имя',max_length = 50)
    #second_name = models.CharField('Фамилия',max_length = 50)
    #patronymic = models.CharField('Отчество',max_length = 50)
    ad_objectguid = models.CharField('AD GUID',max_length=128, blank=True, null=True, unique = True)
    avatar = models.ImageField('Фото',upload_to=image_file_name, blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name = 'Человек'
        verbose_name_plural = 'Люди'
        
    def __str__(self):
        return '%s' % (self.name)


class LdapInfo(models.Model):
    person = models.OneToOneField(Person, blank=True, null=True, verbose_name = "Человек")
    samaccountname = models.CharField('AD логин',max_length=128, blank=True, null=True, unique = True)
    lastlogon = models.DateTimeField('Последнее подключение к AD', blank=True, null=True)

    class Meta:
        verbose_name = 'Информация из AD'
        verbose_name_plural = 'Информация из AD'

    def __str__(self):
        return 'Подключался к AD: %s' % (self.lastlogon)


class ADLogonFromComputer(models.Model):
    logon_date = models.DateField('Дата подключения')
    logon_time = models.TimeField('Время подключения')
    computer_name = models.CharField('Имя компьютера',max_length=128)
    login_name = models.CharField('AD логин',max_length=50)
    person = models.ForeignKey(Person, blank=True, null=True, verbose_name = "Человек")
    
    class Meta:
        verbose_name = 'Подключения к AD с компьютера'
        verbose_name_plural = 'Подключался к AD с компьютера'

    def __str__(self):
        return 'Подключался к AD с компьютера: %s' % (self.computer_name)


class Phone(models.Model):
    person = models.ForeignKey(Person, blank=True, null=True, verbose_name = "Человек")
    number = models.CharField('Номер', max_length = 20)

    class Meta:
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны'

    def __str__(self):
        return '%s, %s' % (self.number, self.person)


class Email(models.Model):
    person = models.ForeignKey(Person, blank=True, null=True, verbose_name = "Человек")
    address = models.EmailField('Email адрес')

    def __str__(self):
        return '%s, %s' % (self.address, self.person)


class Employee(models.Model):
    organization = models.ForeignKey(Organization, verbose_name = "Организация")
    subdivision = models.ForeignKey(Subdivision, verbose_name = "Подразделение")
    person = models.ForeignKey(Person, verbose_name = "Человек")
    position = models.CharField( 'Должность', max_length = 50, blank=True, null=True)
    parent_employee = models.ForeignKey('self', null=True, blank=True, verbose_name = "Руководитель")
    address = models.ForeignKey(Building, null=True, blank=True, verbose_name = "Место работы")
    addition = models.CharField('Дополнительная информация', max_length = 200, blank=True, null=True)
    
    class Meta:
        ordering = ["person"]
        verbose_name = 'Работник'
        verbose_name_plural = 'Работники'
    
    def __str__(self):
        return '%s, %s, %s, %s' % (self.person, self.organization, self.subdivision, self.position)
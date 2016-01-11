#set environment for django contact application
import os, sys
from sys import platform as _platform
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "dit.settings"
# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

#import contact.models
from contact.models import Person, Phone, Email, LdapInfo, Employee, Building, Subdivision, Organization
from ldap3 import Server, Connection, SIMPLE, SYNC, ASYNC, SUBTREE, ALL

#Active Directory/LDAP python timestamp converter (AD lastLogon attribute)
from datetime import datetime, timedelta
def convert_ad_timestamp(timestamp):
    epoch_start = datetime(year=1601, month=1,day=1)
    seconds_since_epoch = timestamp/10**7
    return epoch_start + timedelta(seconds=seconds_since_epoch)
#example to use: convert_ad_timestamp(129410017915727600).strftime("%y-%m-%d %H:%M")


def execute(srv, usr, pwd):

    #server = Server('srv1.test.ru')
    server = Server(srv)
    conn = Connection(server,auto_bind=True,user=usr,password=pwd)

    #'userAccountControl' can have these values: 512 	Enabled Account; 514 	Disabled Account;

    #conn.search('ou=АСУ,dc=test,dc=ru','(&(objectClass=person)(userAccountControl=66048))',SUBTREE, attributes =['cn','proxyAddresses','department','sAMAccountName', 'displayName', 'telephoneNumber', 'ipPhone', 'streetAddress','title','manager','objectGUID','company','lastLogon'])
    conn.search('dc=test,dc=ru','(&(objectCategory=Person)(!(UserAccountControl:1.2.840.113556.1.4.803:=2)))',SUBTREE, attributes =['cn','proxyAddresses','department','sAMAccountName', 'displayName', 'telephoneNumber', 'ipPhone', 'streetAddress','title','manager','objectGUID','company','lastLogon'])


    #get or create default organization
    try:
        org = Organization.objects.get(name="Не указано")
    except:
        org = Organization(name = 'Не указано')
        org.save()

    #get or create default organization
    try:
        dep = Subdivision.objects.get(name="Не указано")
    except:
        dep = Subdivision(organization = org, name="Не указано")
        dep.save()


    for entry in conn.entries:
        print('')
        print(' -------------------------- ')
        print('entry.cn', entry.cn)
        #print('entry.objectGUID', entry.objectGUID)
        
        #search person in contact app
        try:
            displayName = entry.displayName
        except:
            displayName = entry.cn
        print('displayName', displayName)
        try:
            person_obj = Person.objects.get(ad_objectguid = entry.objectGUID)
        except:
            person_obj = None
        print('person_obj', person_obj)
        if person_obj:
            person_obj.name = displayName
            #person_obj.ad_objectguid = entry.objectGUID
            person_obj.save()
        else:
            person_obj = Person(name = displayName, ad_objectguid = entry.objectGUID)
            person_obj.save()
        print('Человек: ',person_obj)
        try:
            ldapinfo_obj = LdapInfo.objects.get(person = person_obj)
        except:
            ldapinfo_obj = None
        #add AD sAMAccountName
        if ldapinfo_obj:
            try:
                ldapinfo_obj.samaccountname = entry.sAMAccountName
                ldapinfo_obj.save()
            except:
                pass
        else:
            try:
                sAMAccountName = LdapInfo(person = person_obj, samaccountname = entry.sAMAccountName)
                sAMAccountName.save()
            except:
                pass
        #add AD lastLogon
        if ldapinfo_obj:
            try:
                ldapinfo_obj.lastlogon = convert_ad_timestamp(int(entry.lastLogon.value))
                ldapinfo_obj.save()
            except:
                pass
        else:
            try:
                lastLogon = LdapInfo(person = person_obj, lastlogon = convert_ad_timestamp(int(entry.lastLogon.value)))
                lastLogon.save()
            except:
                pass
        #delete all person phones in contact app
        phones = Phone.objects.filter(person=person_obj)
        if phones:
            phones.delete()
        #add phones to contact  from Active Directory user entry
        try:
            newphone = Phone(person = person_obj, number = entry.telephoneNumber)
            newphone.save()
        except:
            pass
        try:
            newphone = Phone(person = person_obj, number = entry.ipPhone)
            newphone.save()
        except:
            pass
        #delete all emails in contact app
        emails  = Email.objects.filter(person=person_obj)
        if emails:
            emails.delete()
        #add emails to contact app from Active Directory user entry
        try:
            new_email = Email(person = person_obj, address= entry.proxyAddresses)
            new_email.save()
        except:
            pass
        #get organization
        try:
            entry_company = entry.company
        except:
            entry_company = None
        organization = None
        if entry_company:
            try:
                organization_obj = Organization.objects.get(name = entry.company)
            except:
                organization_obj = Organization(name = entry.company)
                organization_obj.save()
        else:
            organization_obj = org
        print('Организация: ',organization_obj.name)
        entry_company = None
        #get or create subdivision
        try:
            entry_subdiv = entry.department
        except:
            entry_subdiv = None
        subdiv = None
        if entry_subdiv:
            print("len entry.department %s: %s" % (entry.department, len(entry.department)))
            try:
                subdiv = Subdivision.objects.get(organization = organization_obj, name=entry.department)
            except:
                subdiv = Subdivision(organization = organization_obj, name=entry.department)
                subdiv.save()
        else:
            subdiv = dep
        print('Подразделение: ', subdiv.name)
        entry_subdiv = None
        #get person position
        try:
            position = entry.title
        except:
            position = None
        print('Должность', position)
        #create employee
        employee = None
        try:
            employee = Employee.objects.get(organization = organization_obj, subdivision = subdiv, person = person_obj, position = position)
            print('Найден работник')
        except:
            employee = Employee(organization = organization_obj, subdivision = subdiv, person = person_obj, position = position)
            employee.save()
            print('Создан работник')

if __name__ == '__main__':
    
    if len (sys.argv) > 1:
        server = sys.argv[1]
        user = sys.argv[2]
        password = sys.argv[3]
        execute(server, user, password)
    else:
        print ("Enter mandatory options: server user password")
        print ("server - ldap or active directory server, enter format: ip address or full domain name")
        print ("user - ldap or active directory user, enter format: ldapuser@domain.com or domain\ldapuser")
        print ("password - ldap or active directory user password")
        print ("Example usage:")
        print ("python import_cont_from_ad.py 192.168.1.1 ldapuser@domain.com ldappassword")

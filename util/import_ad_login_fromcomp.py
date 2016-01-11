import datetime
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
from contact.models import ADLogonFromComputer, LdapInfo

from django.db.models import Max
#import winmount for mount win_server share folder
from util import winmount

def import_person():
    adlogon = ADLogonFromComputer.objects.all()
    import_err = []
    for obj in adlogon:
        try:
            print(obj.login_name)
            ldap_obj=LdapInfo.objects.get(samaccountname__iexact=obj.login_name)
            obj.person=ldap_obj.person
            obj.save()
        except:
            import_err.append(obj.login_name)
    print(import_err)


def save_to_base(log_file, logons_err=None):
    """ parce log_file and save to contact ADLogonFromComputer table"""
    source_file = open(log_file)

    if logons_err:
        if os.path.isfile(logons_err):
            os.remove(logons_err)
            output_err = open(logons_err, "a", encoding='utf-8')
        else:
            output_err = open(logons_err, "a", encoding='utf-8')
        
    lines = source_file.readlines()
    
    #get max last logon date from ADLogonFromComputer
    last_logon_date = ADLogonFromComputer.objects.all().aggregate(Max('logon_date'))['logon_date__max']
    if last_logon_date:
        begin_date = last_logon_date-datetime.timedelta(2)
    else:
        begin_date = None
    import_err = []
    for line in lines:
        try:
            s_line = line.split(';  ')
            if len(s_line) == 7:
                l_date = datetime.datetime.strptime(s_line[0], "%d.%m.%Y").date()
                
                if begin_date == None:
                    #l_time = datetime.datetime.strptime(s_line[1], "%H:%M:%S,%f").time()
                    l_time = datetime.datetime.strptime(s_line[1], "%H:%M:%S").time()
                    comp = s_line[3]
                    login = s_line[4]
                    #l_time = datetime.datetime.strptime(s_line[1][-3], "%H:%M:%S").time()
                    
                    print('_____________________')
                    print(s_line)
                    #print('Дата: %s' %(s_line[0]))
                    print('Дата: %s' %(l_date))
                    #print('Время: %s' %(s_line[1]))
                    print('Время: %s' %(l_time))
                    print('Компьютер: %s' % (comp))
                    print('Логин: %s' % (login))
                    
                    try:
                        ad_logon = ADLogonFromComputer.objects.get(logon_date=l_date, logon_time=l_time, computer_name=comp, login_name=login)
                    except:
                        ad_logon = ADLogonFromComputer(logon_date=l_date, logon_time=l_time, computer_name=comp, login_name=login)
                        ad_logon.save()
                        
                        try:
                            ldap_obj=LdapInfo.objects.get(samaccountname__iexact=ad_logon.login_name)
                            ad_logon.person=ldap_obj.person
                            ad_logon.save()
                        except:
                            import_err.append(ad_logon.login_name)

                elif l_date > begin_date:
                    l_time = datetime.datetime.strptime(s_line[1], "%H:%M:%S").time()
                    comp = s_line[3]
                    login = s_line[4]
                    #l_time = datetime.datetime.strptime(s_line[1][-3], "%H:%M:%S").time()
                    
                    print('_____________________')
                    print(s_line)
                    #print('Дата: %s' %(s_line[0]))
                    print('Дата: %s' %(l_date))
                    #print('Время: %s' %(s_line[1]))
                    print('Время: %s' %(l_time))
                    print('Компьютер: %s' % (comp))
                    print('Логин: %s' % (login))
                    
                    try:
                        ad_logon = ADLogonFromComputer.objects.get(logon_date=l_date, logon_time=l_time, computer_name=comp, login_name=login)
                    except:
                        ad_logon = ADLogonFromComputer(logon_date=l_date, logon_time=l_time, computer_name=comp, login_name=login)
                        ad_logon.save()
                        
                        try:
                            ldap_obj=LdapInfo.objects.get(samaccountname__iexact=ad_logon.login_name)
                            ad_logon.person=ldap_obj.person
                            ad_logon.save()
                        except:
                            import_err.append(ad_logon.login_name)
            elif logons_err:
                output_err.write(line)
        except:
            if logons_err:
                output_err.write(line)
    if logons_err:
        output_err.close()
    source_file.close()
    print('Ошибка поиска ADLogonFromComputer.login_name в LdapInfo.samaccountname: ',import_err)


if __name__ == '__main__':
    
    if len (sys.argv) == 3:
        log_file = sys.argv[1]
        logons_err = sys.argv[2]
        save_to_base(log_file, logons_err)
        #import_person()
    elif len (sys.argv) == 2:
        log_file = sys.argv[1]
        save_to_base(log_file)
        #import_person()
    else:
        print ("Enter mandatory options: source_log_file output_error_file")
        print ("Example usage:")
        print ("python import_ad_login_fromcomp.py d:/temp/source_log_file d:/temp/output_error_file")
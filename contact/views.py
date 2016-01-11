import sys, os
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.context_processors import csrf
from util.import_cont_from_ad import execute
from util.import_ad_login_fromcomp import save_to_base
from util import winmount
from .forms import Import_user_from_adForm, Import_logon_to_adForm

def index(request):
    return HttpResponse("Contact index.")

def import_user_from_ad(request):
    c = {}
    c.update(csrf(request))
    
    if not request.user.is_staff:
        return HttpResponseNotFound('<h1>You have not permission to execute import</h1>')
        
    if request.method == 'POST':
        form = Import_user_from_adForm(request.POST)
        if form.is_valid():
            server_ad = form.cleaned_data['server_ad']
            user_ad = form.cleaned_data['user_ad']
            password_ad = form.cleaned_data['password_ad']
            execute(server_ad, user_ad, password_ad)
        
            success_message = "Импорт пользователей из Active Directory выполнен"
            return render_to_response('import_user_from_ad.html',{'success_message': success_message})
        else:
            c={'form':form}
            c.update(csrf(request))
            return render_to_response('import_user_from_ad.html',c)
    
    form = Import_user_from_adForm()
    c={'form':form}
    c.update(csrf(request))
    
    return render_to_response('import_user_from_ad.html',c)


def import_logon_to_ad(request):
    c = {}
    c.update(csrf(request))
    
    if not request.user.is_staff:
        return HttpResponseNotFound('<h1>У вас недостаточно прав для импорта</h1>')
        
    if request.method == 'POST':
        form = Import_logon_to_adForm(request.POST)
        if form.is_valid():
            win_server = form.cleaned_data['server']
            share_folder = form.cleaned_data['share']
            log_file = form.cleaned_data['log_file']
            user_name = form.cleaned_data['user_name']
            user_password = form.cleaned_data['user_pass']
            #connect to win_server share_folder and mount
            if sys.platform == "win32":
                mount_point = 'q:'
            else:
                mount_point = '/mnt/winlogshare'
            new_share = winmount.share(win_server, share_folder, mount_point, user_name, user_password)
            new_share.mount()
            if new_share.error:
                error_message = new_share.error[0]
                c={'form':form, 'error_message': error_message}
                c.update(csrf(request))
                return render_to_response('import_logon_to_ad.html',c)
            else:
                mount_point = new_share.options['mount_point']
                log_file_path = os.path.join(mount_point, log_file)
                save_to_base(log_file_path)
                success_message = "Импорт подключений к Active Directory выполнен"
                new_share.umount()
                return render_to_response('import_logon_to_ad.html',{'success_message': success_message})
        else:
            c={'form':form}
            c.update(csrf(request))
            return render_to_response('import_logon_to_ad.html',c)
    
    form = Import_logon_to_adForm()
    c={'form':form}
    c.update(csrf(request))
    
    return render_to_response('import_logon_to_ad.html',c)

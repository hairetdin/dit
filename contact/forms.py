from django import forms

class Import_user_from_adForm(forms.Form):
    server_ad = forms.CharField(label='Сервер AD', initial='192.168.1.1', max_length=100)
    user_ad = forms.CharField(label='Пользователь AD',initial='aduser@domain.ru', max_length=100)
    password_ad = forms.CharField(label='Пароль',widget=forms.PasswordInput(), max_length=100)


class Import_logon_to_adForm(forms.Form):
    server = forms.CharField(label='Сервер', initial=r'192.168.1.4', max_length=100)
    share = forms.CharField(label='Название расшаренной папки', initial=r'DomenLogons', max_length=100)
    log_file = forms.CharField(label='Имя лог файла', initial=r'LogonsUserAD 12.2015.log', max_length=100)
    user_name = forms.CharField(label='Пользователь',initial='aduser@domain.ru', max_length=100)
    user_pass = forms.CharField(label='Пароль',widget=forms.PasswordInput(), max_length=100)
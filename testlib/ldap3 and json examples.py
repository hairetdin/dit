### Example work with ldap3
# import objects and constants
from ldap3 import Server, Connection, SIMPLE, SYNC, ASYNC, SUBTREE, ALL

# set current server
server = Server('srv1.test.ru')

# open connection to server with user and password, 
conn = Connection(server,auto_bind=True,user='test\username',password='')

# search in Active Directory in 'ou=АСУ,dc=test,dc=ru'
conn.search('ou=АСУ,dc=test,dc=ru','(cn=К*)',SUBTREE, attributes =['cn','proxyAddresses'])

# search enabled user (atribut userAccountControl=66048), objectClass=person and copy to conn.entries attributes 'cn','proxyAddresses'
conn.search('ou=АСУ,dc=uis,dc=ru','(&(objectClass=person)(userAccountControl=66048))',SUBTREE, attributes =['cn','proxyAddresses'])

conn.search('ou=АСУ,dc=uis,dc=ru','(&(objectClass=person)(userAccountControl=66048))',SUBTREE, attributes =['cn','proxyAddresses','department','sAMAccountName', 'displayName', 'telephoneNumber', 'ipPhone', 'streetAddress','title','manager'])

#show searched entries
conn.entries

#show searched entries detail
for entry in conn.entries:
    print(entry.entry_get_dn())
    print(entry.cn)

#export connection response to file d:\ldap.json (data in file save json format and utf-8 encoding)
conn.response_to_file('d:\ldap.json')


### Example work with json
import json

#open saved file with utf-8 encoding
f = open('d:\ldap.json',encoding='utf-8')

#open data with json
j = json.load(f)

#view opened json file entries
print(j)

for entry in j['entries']:
    for attribut in entry['attributes']:
        print(attribut, entry['attributes'][attribut])
    print(entry['dn'])
    
#close opened file
f.close()
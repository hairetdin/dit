from ldap3 import Server, \
    Connection, \
    AUTO_BIND_NO_TLS, \
    SUBTREE, \
    ALL_ATTRIBUTES
 
def get_ldap_info(u):
    with Connection(Server('<Server IP Address>', port=636, use_ssl=True),
                    auto_bind=AUTO_BIND_NO_TLS,
                    read_only=True,
                    check_names=True,
                    user='Domain\\Username', password='password') as c:
 
        c.search(search_base='CN=Users,DC=domain,DC=local',
                 search_filter='(&(samAccountName=' + u + '))',
                 search_scope=SUBTREE,
                 attributes=ALL_ATTRIBUTES,
                 get_operational_attributes=True)
 
    print(c.response_to_json())
    print(c.result)
 
get_ldap_info('username')
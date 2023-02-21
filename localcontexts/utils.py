from django.contrib.sites.shortcuts import get_current_site

def dev_prod_or_local(hostname):
    if 'anth-ja77-lc-dev-42d5' in hostname:
        return 'DEV'
    elif 'localcontextshub' in hostname:
        return 'PROD'
    elif 'anth-ja77-local-contexts-8985' in hostname:
        return 'AE_PROD' 

def return_login_url_str(request):
    current_site=get_current_site(request)
    domain = current_site.domain
    if 'localhost' in domain:
        url = f'http://{domain}/login'
    else:
        url = f'https://{domain}/login'
    return url 

def return_register_url_str(request):
    current_site=get_current_site(request)
    domain = current_site.domain
    if 'localhost' in domain:
        url = f'http://{domain}/register'
    else:
        url = f'https://{domain}/register'
    return url 
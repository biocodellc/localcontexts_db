from django.contrib.sites.shortcuts import get_current_site
    
def dev_prod_or_local(hostname):
    # use: dev_prod_or_local(request.get_host())
    hostnames = {
        'anth-ja77-lc-dev-42d5.uc.r.appspot.com': 'DEV',
        'localcontextshub.org': 'PROD',
        'anth-ja77-local-contexts-8985.uc.r.appspot.com': 'AE_PROD'
    }
    return hostnames.get(hostname, 'LOCAL')

def get_site_url(request, path):
    # use: get_site_url(request, "/login") or get_site_url(request, "/register")
    current_site = get_current_site(request)
    domain = current_site.domain
    url = f'{request.scheme}://{domain}/{path}'
    return url
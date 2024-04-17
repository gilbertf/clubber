from django.conf import settings

def site(request):
    d = dict()

    d["EMAIL_SITE_URL"] = settings.EMAIL_SITE_URL

    try:
        d["LOGO_ENABLE"] = settings.LOGO_ENABLE
    except:
        d["LOGO_ENABLE"] = False
    
    try:
        d["LOGO_URL"] = settings.LOGO_URL
    except:
        d["LOGO_URL"] = "/"

    return d

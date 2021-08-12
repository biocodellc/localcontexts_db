def check_tklabel_type(label):
    if label == 'tka':
        return 'attribution'
    if label == 'tkcl':
        return 'clan'
    if label == 'tkf':
        return 'family'
    if label == 'tkcv':
        return 'community_voice'
    if label == 'tkmc':
        return 'tk_multiple_community'
    if label == 'tko':
        return 'outreach'
    if label == 'tknv':
        return 'non_verified'
    if label == 'tkv':
        return 'verified'
    if label == 'tknc':
        return 'non_commercial'
    if label == 'tkoc':
        return 'commercial'
    if label == 'tkcs':
        return 'culturally_sensitive'
    if label == 'tkco':
        return 'community_use_only'
    if label == 'tks':
        return 'seasonal'
    if label == 'tkwg':
        return 'women_general'
    if label == 'tkmg':
        return 'men_general'
    if label == 'tkmr':
        return 'men_restricted'
    if label == 'tkwr':
        return 'women_restricted'
    if label == 'tkss':
        return 'secret_sacred'
    if label == 'tkcb':
        return 'open_to_collaboration'
    if label == 'placeholder':
        return False

def assign_tklabel_img(label_type):
    baseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/tklabels/'

    if label_type == 'tka':
        return baseURL + 'tk-attribution.png'
    if label_type == 'tkcl':
        return baseURL + 'tk-clan.png'
    if label_type == 'tkf':
        return baseURL + 'tk-family.png'
    if label_type == 'tkcv':
        return baseURL + 'tk-community-voice.png'
    if label_type == 'tkmc':
        return baseURL + 'tk-multiple-communities.png'
    if label_type == 'tko':
        return baseURL + 'tk-outreach.png'
    if label_type == 'tknv':
        return baseURL + 'tk-non-verified.png'
    if label_type == 'tkv':
        return baseURL + 'tk-verified.png'
    if label_type == 'tknc':
        return baseURL + 'tk-non-commercial.png'
    if label_type == 'tkoc':
        return baseURL + 'tk-commercial.png'
    if label_type == 'tkcs':
        return baseURL + 'tk-culturally-sensitive.png'
    if label_type == 'tkco':
        return baseURL + 'tk-community-use-only.png'
    if label_type == 'tks':
        return baseURL + 'tk-seasonal.png'
    if label_type == 'tkwg':
        return baseURL + 'tk-women-general.png'
    if label_type == 'tkmg':
        return baseURL + 'tk-men-general.png'
    if label_type == 'tkmr':
        return baseURL + 'tk-men-restricted.png'
    if label_type == 'tkwr':
        return baseURL + 'tk-women-restricted.png'
    if label_type == 'tkss':
        return baseURL + 'tk-secret-sacred.png'
    if label_type == 'tkcb':
        return baseURL + 'tk-open-to-collaboration.png'
    if label_type == 'placeholder':
        return None

def set_tknotice_defaults(tknotice):
    tknotice.img_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/notices/tk-notice.png'
    tknotice.default_text = 'The TK Notice is a visible notification that there are accompanying cultural rights and responsibilities that need further attention for any future sharing and use of this material. The TK Notice may indicate that TK Labels are in development and their implementation is being negotiated.'
    tknotice.save()  
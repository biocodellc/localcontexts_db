def check_tklabel_type(label):
    if label == 'tka':
        return 'attribution'
    if label == 'tkcl':
        return 'clan'
    if label == 'tkf':
        return 'family'
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
    if label == 'tkc':
        return 'commercial'
    if label == 'tkcs':
        return 'culturally_sensitive'
    if label == 'tkco':
        return 'community_use_only'
    if label == 'tks':
        return 'season'
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
    if label == 'placeholder':
        return False
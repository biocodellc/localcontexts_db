def check_bclabel_type(label):
    if label == 'bccv':
        return 'consent_verified'
    if label == 'bcr':
        return 'research'
    if label == 'bcocomm':
        return 'commercialization'
    if label == 'bcocoll':
        return 'collaboration'
    if label == 'bcmc':
        return 'multiple_community'
    if label == 'bcp':
        return 'provenance'
    if label == 'placeholder':
        return False
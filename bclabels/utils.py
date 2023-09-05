from helpers.utils import get_labels_json

# fetch data from Labels.json
data = get_labels_json()

def check_bclabel_type(label):
    bc_labels = data.get('bcLabels', [])
    
    if label == 'placeholder':
        return False

    for value in bc_labels:
        if label == value['labelCode']:
            return value['labelType']

from helpers.utils import get_labels_json

# fetch data from Labels.json
data = get_labels_json()
                    
def check_tklabel_type(label):
    tk_labels = data.get('tkLabels', [])
    
    if label == 'placeholder':
        return False

    for value in tk_labels:
        if label == value['labelCode']:
            return value['labelType']

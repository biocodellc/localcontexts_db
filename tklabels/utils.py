from helpers.utils import get_labels_json

# fetch data from Labels.json
data = get_labels_json()

def check_tklabel_type(label):
    for key, values in data.items():
        if key == 'tkLabels':
            if(isinstance(values, list)):
                for value in values:
                    if label == value['labelCode']:
                        return value['labelType']
                    elif label == 'placeholder':
                        return False

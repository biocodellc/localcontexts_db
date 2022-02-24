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

storageBaseURL = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/labels/tklabels/'

def assign_tklabel_img(label_type):
    for key, values in data.items():
        if key == 'tkLabels':
            if(isinstance(values, list)):
                for value in values:
                    if label_type == value['labelCode']:
                        return storageBaseURL + value['imgFileName']
                    elif label_type == 'placeholder':
                        return None

def assign_tklabel_svg(label_type):
    for key, values in data.items():
        if key == 'tkLabels':
            if(isinstance(values, list)):
                for value in values:
                    if label_type == value['labelCode']:
                        return storageBaseURL + value['svgFileName']
                    elif label_type == 'placeholder':
                        return None

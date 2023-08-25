from .models import Community
from bclabels.utils import check_bclabel_type
from tklabels.utils import check_tklabel_type
from bclabels.forms import CustomizeBCLabelForm
from tklabels.forms import CustomizeTKLabelForm
from bclabels.models import BCLabel
from tklabels.models import TKLabel

def get_community(pk):
    return Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

def get_form_and_label_type(label_code):
    label_map = {
        'tk': (CustomizeTKLabelForm, "TK Label", check_tklabel_type(label_code)),
        'bc': (CustomizeBCLabelForm, "BC Label", check_bclabel_type(label_code))
    }
    return label_map.get(label_code[:2], (None, None, None))

def does_label_type_exist(community, label_code):
    tk_label_type = check_tklabel_type(label_code)
    bc_label_type = check_bclabel_type(label_code)
    
    if tk_label_type:
        return TKLabel.objects.filter(community=community, label_type=tk_label_type).exists()
    
    if bc_label_type:
        return BCLabel.objects.filter(community=community, label_type=bc_label_type).exists()

    return False


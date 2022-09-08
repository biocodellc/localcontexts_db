from api.base.views import *
from api.base import views as base_views
from . import serializers as v2_serializers

@api_view(['GET'])
def test_label_types(request):
    try:
        labeltypes = TKLabel.objects.all()

        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
from django.db import models
from communities.models import Community

class BCLabel(models.Model):
    TYPES = (
        ('provenance', 'Provenance BC Label (BC P)'),
        ('commercialization', 'Open to Commercialization BC Label (BC C)'),
        ('collaboration', 'Open to Collaboration BC Label (BC OC)'),
        ('consent_verified', 'Consent Verified BC Label (BC CV)'),
        ('multiple_community', 'Multiple Community BC Label (BC MC)'),
        ('research', 'Research Use BC Label (BC R)'),  
    )
    label_type = models.CharField(max_length=20, null=True, choices=TYPES)
    community = models.ForeignKey(Community, null=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='label name', max_length=90, null=True)
    default_text = models.TextField(null=True, blank=True)
    modified_text = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.label_type) + ' ' + str(self.name)
    
    class Meta:
        verbose_name = 'BC Label'
        verbose_name_plural = 'BC Labels'


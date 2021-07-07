from django.db import models
from bclabels.models import BCNotice, BCLabel
from tklabels.models import TKNotice, TKLabel

class LabelTranslation(models.Model):
    bclabel = models.ForeignKey(BCLabel, null=True, on_delete=models.CASCADE, related_name="bclabel_translation")
    tklabel = models.ForeignKey(TKLabel, null=True, on_delete=models.CASCADE, related_name="tklabel_translation")
    title = models.CharField(max_length=150, blank=True)
    language = models.CharField(max_length=150, blank=True)
    translation = models.TextField(blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Label Translation"
        verbose_name_plural = "Label Translations"
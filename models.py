# from django.db import models
from django.contrib.gis.db import models
import saintsophia.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from saintsophia.storages import OriginalFileStorage

class Place(abstract.AbstractBaseModel):
    
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("name"), help_text=_("this field refers to the placename"))
    geometry = models.GeometryField(verbose_name=_("geometry"), blank=True, null=True)
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Place")
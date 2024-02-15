# from django.db import models
from django.contrib.gis.db import models
import saintsophia.abstract.models as abstract
from django.utils.translation import gettext_lazy as _
from saintsophia.storages import OriginalFileStorage

# DEFINE TAG MODELS

class Tag(abstract.AbstractTagModel):
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class Language(abstract.AbstractTagModel):
    
    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class MeshTechnique(abstract.AbstractTagModel):
    
    class Meta:
        verbose_name = _("3D Mesh Technique")
        verbose_name_plural = _("3D Mesh Techniques")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class ImageType(abstract.AbstractTagModel):
    
    class Meta:
        verbose_name = _("Image Type")
        verbose_name_plural = _("Image Types")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class InscriptionType(abstract.AbstractTagModel):
    
    class Meta:
        verbose_name = _("Inscription Type")
        verbose_name_plural = _("Inscription Types")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)

# DEFINE OBJECTS MODELS

class Panel(abstract.AbstractBaseModel):
    
    title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("name"), help_text=_("this field refers to the panel designation"))
    geometry = models.GeometryField(verbose_name=_("geometry"), blank=True, null=True)
    room = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("room"), help_text=_("this field refers to the room in which the panel stands"))
    # documentation = 
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Place")
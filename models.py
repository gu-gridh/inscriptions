# from django.db import models
from django.contrib.gis.db import models
import saintsophia.abstract.models as abstract
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _
from saintsophia.storages import OriginalFileStorage
from django.contrib.postgres.fields import ArrayField

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

class Documentation(abstract.AbstractBaseModel):
    short_title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("short title"), help_text=_("documentation identifier"))
    observation = RichTextField(null=True, blank=True, help_text=("Write documentation here"))
    
    def __str__(self) -> str:
        return f"{self.short_title}"
    
    class Meta:
        verbose_name = _("Documentation")
    
    

class Panel(abstract.AbstractBaseModel):
    title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("title"), help_text=_("this field refers to the panel designation"))
    room = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("room"), help_text=_("this field refers to the room in which the panel stands"))
    documentation = models.ManyToManyField(Documentation, null=True, blank=True, verbose_name=_("documentation"), default=None)
    spatial_position = ArrayField(models.FloatField(), size=3, default=list, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))
    spatial_direction = ArrayField(models.FloatField(), size=3, default=list, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))
    tags = models.ManyToManyField(Tag, blank=True, help_text=_("Tags attached to the panel"))
    
    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Panel")
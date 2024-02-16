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
    documentation = models.ManyToManyField(Documentation, blank=True, verbose_name=_("documentation"), default=None)
    spatial_position = ArrayField(models.FloatField(), size=3, default=list, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))
    spatial_direction = ArrayField(models.FloatField(), size=3, default=list, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"))
    tags = models.ManyToManyField(Tag, blank=True, help_text=_("Tags attached to the panel"))
    
    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Panel")


class Inscription(abstract.AbstractBaseModel):
    title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("title"), help_text=_("this field refers to the designation of the inscription"))
    alt_title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("alt_title"), help_text=_("this field needs to be filled with an alternative designation"))
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, blank=True, null=True)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, blank=True, null=True)
    type_of_inscription = models.ManyToManyField(InscriptionType, blank=True)
    
    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Inscription")
    
        
class PanelOrInscription(models.IntegerChoices):
    PANEL = 1, "Panel"
    INSCRIPTION = 2, "Inscription"
    

class Image(abstract.AbstractImageModel):
    # title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    panel_or_inscription = models.IntegerField(choices=PanelOrInscription.choices)
    panel = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.CASCADE, related_name="panel")
    inscription = models.ForeignKey(Inscription, null=True, blank=True, on_delete=models.CASCADE, related_name="inscription")
    
    type_of_image = models.ForeignKey(ImageType, on_delete=models.SET_NULL, blank=True, null=True, related_name="image_type")
    
    def __str__(self) -> str:
        return f"Panel {self.panel}, {self.type_of_image}"

    class Meta:
        verbose_name = _("Image")
        
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_value_matches_type",
                check=(
                    models.Q(
                        panel_or_inscription=PanelOrInscription.PANEL,
                        panel__isnull=False,
                        inscription__isnull=True,
                    )
                    | models.Q(
                        panel_or_inscription=PanelOrInscription.INSCRIPTION,
                        panel__isnull=True,
                        inscription__isnull=False,
                    )
                ),
            )
        ]
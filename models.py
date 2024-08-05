# from django.db import models
from django.contrib.gis.db import models
import saintsophia.abstract.models as abstract
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _
from saintsophia.storages import OriginalFileStorage
from django.contrib.postgres.fields import ArrayField

# DEFINE TAG MODELS

class Tag(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("текст (укр)"))
    
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class Language(abstract.AbstractBaseModel):
    text = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("Language"))
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("мова (укр)"))
    
    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

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
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("Тип напису (укр)"))
    
    class Meta:
        verbose_name = _("Inscription Type")
        verbose_name_plural = _("Inscription Types")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class Genre(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("жанр (укр)"))
    
    class Meta:
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self) -> str:
        return self.text
    
    # def __repr__(self) -> str:
    #     return str(self)
    
    
class WritingSystem(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("система письма (укр)"))
    
    class Meta:
        verbose_name = _("Writing System")
        verbose_name_plural = _("Writing Systems")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)

# DEFINE OBJECTS MODELS

class Author(abstract.AbstractBaseModel):
    firstname = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("First name (eng)"))
    lastname = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Last name (eng)"))
    firstname_ukr = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("ім'я (укр)"))
    lastname_ukr = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("прізвище (укр)"))

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"


class Documentation(abstract.AbstractBaseModel):
    short_title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("short title"), help_text=_("documentation identifier"))
    observation = RichTextField(null=True, blank=True, verbose_name=("Observation (eng)"))
    text_ukr = RichTextField(null=True, blank=True, verbose_name=_("Спостереження (укр)"))
    
    def __str__(self) -> str:
        return f"{self.short_title}"
    
    class Meta:
        verbose_name = _("Documentation")
    

class Panel(abstract.AbstractBaseModel):
    title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("title"), help_text=_("this field refers to the surface designation"))
    room = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("room"), help_text=_("this field refers to the room in which the surface stands"))
    geometry = models.GeometryField(verbose_name=_("geometry"), blank=True, null=True)
   
    documentation = models.ManyToManyField(Documentation, blank=True, verbose_name=_("documentation"), default=None)
    spatial_position = ArrayField(models.FloatField(), size=3, default=list, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"), blank=True, null=True)
    spatial_direction = ArrayField(models.FloatField(), size=3, default=list, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"), blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, help_text=_("Tags attached to the panel"))
    
    class DataForPanel(models.IntegerChoices):
        POSITION = (1, "1")
        ORTHO_MESH = (2, "2")
        TOPOGRAPHY = (3, "3")
        RTI = (4, "4")
    
    data_available = models.IntegerField(choices=DataForPanel.choices, default=DataForPanel.POSITION)
    
    def __str__(self) -> str:
        return f"Surface {self.title}"

    class Meta:
        verbose_name = _("Surface")
        
    def list_all_pk(self):
        all_pk = []
        for obj in Panel.objects.all().order_by('pk'):
            all_pk.append(obj.pk)
        return all_pk
        
    def next(self):
        all_pk = self.list_all_pk()
        current_index = all_pk.index(self.pk)
        try: 
            return Panel.objects.get(pk=all_pk[current_index+1])
        except: 
            return None
        
    def previous(self):
        all_pk = self.list_all_pk()
        current_index = all_pk.index(self.pk)
        try:
            return Panel.objects.get(pk=all_pk[current_index-1])
        except:
            return None


class Inscription(abstract.AbstractBaseModel):
    title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("title"), help_text=_("fill if the inscription is known by an official name"))
    url_to_iiif_clip = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("Position on surface"), help_text=_("URL to clipped IIIF of the inscription"))
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, blank=True, null=True)
    writing_system = models.ForeignKey(WritingSystem, on_delete=models.SET_NULL, blank=True, null=True)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, blank=True, null=True, related_name="inscriptions", verbose_name=_("Surface"))
    type_of_inscription = models.ForeignKey(InscriptionType, on_delete=models.SET_NULL,  blank=True, null=True)
    genre = models.ManyToManyField(Genre, blank=True, help_text=_("Genre of the inscription"))
    tags = models.ManyToManyField(Tag, blank=True, help_text=_("Tags attached to the inscription"))
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self) -> str:
        if (self.title) is not None:
            return f"Inscription {self.panel.title}:{self.id} ({self.title})"
        else:
            return f"Inscription {self.panel.title}:{self.id}"

    class Meta:
        verbose_name = _("Inscription")
    
        
class PanelOrInscription(models.IntegerChoices):
    PANEL = 1, "Surface"
    INSCRIPTION = 2, "Inscription"
    

class Image(abstract.AbstractTIFFImageModel):
    # title = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("title"))
    panel_or_inscription = models.IntegerField(choices=PanelOrInscription.choices, verbose_name=_("Surface or inscription"))
    panel = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.CASCADE, related_name="images", verbose_name=_("Surface"))
    inscription = models.ForeignKey(Inscription, null=True, blank=True, on_delete=models.CASCADE, related_name="inscription")
    
    type_of_image = models.ForeignKey(ImageType, on_delete=models.SET_NULL, blank=True, null=True, related_name="image_type")
    
    def __str__(self) -> str:
        return f"Image for surface {self.panel}"

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
        
        
class ObjectRTI(abstract.AbstractBaseModel):
    title = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("name of the RTI object"))
    url = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL to location in storage"))
    panel = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.CASCADE, related_name="rti", verbose_name=_("Surface"))
    
    def __str__(self) -> str:
        return f"{self.panel}"
    
    class Meta:
        verbose_name = _("Object RTI")
        verbose_name_plural = _("Objects RTI")
        
        
class ObjectMesh3D(abstract.AbstractBaseModel):
    url = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("URL to location in storage"))
    panel = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.CASCADE, related_name="mesh", verbose_name=_("Surface"))
    number_of_triangles = models.IntegerField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.panel}"
    
    class Meta:
        verbose_name = _("Object 3D Mesh")
        verbose_name_plural = _("Objects 3D Mesh")
        
        
class Transcription(abstract.AbstractBaseModel):
    text = RichTextField(null=True, blank=True, verbose_name=_("Text of transcription"))
    inscription = models.ForeignKey(Inscription, null=True, blank=True, on_delete=models.CASCADE, related_name="transcription")
    author = models.ManyToManyField(Author, blank=True, verbose_name=_("Author"), default=None)
    
    def __str__(self) -> str:
        return f"Transcription for inscription {self.inscription}"
    
    class Meta:
        verbose_name = _("Transcription")
        verbose_name_plural = _("Transcriptions")
    

class Translation(abstract.AbstractBaseModel):
    text = RichTextField(null=True, blank=True, verbose_name=_("Translation text"))
    inscription = models.ForeignKey(Inscription, null=True, blank=True, on_delete=models.CASCADE, related_name="translation")
    author = models.ManyToManyField(Author, blank=True, verbose_name=_("Author"), default=None)
    language = models.ManyToManyField(Language, blank=True, related_name="language", default=None)
    
    def __str__(self) -> str:
        if self.language is not None:
            return f"{self.language} translation for {self.inscription}"
        else:
            return f"Translation for {self.inscription}"    
    
    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")
        
        
class Description(abstract.AbstractBaseModel):
    text = RichTextField(null=True, blank=True, verbose_name=_("Description text"))
    inscription = models.ForeignKey(Inscription, null=True, blank=True, on_delete=models.CASCADE, related_name="description")
    author = models.ManyToManyField(Author, blank=True, verbose_name=_("Author"), default=None)
    language = models.ForeignKey(Language, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    
    def __str__(self) -> str:
        if self.language is not None:
            return f"Description for {self.inscription} ({self.language})"
        else:
            return f"Description for {self.inscription}"
    
    class Meta:
        verbose_name = _("Description")
        verbose_name_plural = _("Descriptions")
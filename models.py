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
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
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
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class ImageType(abstract.AbstractTagModel):
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Image Type")
        verbose_name_plural = _("Image Types")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class InscriptionType(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("Тип напису (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Inscription Type")
        verbose_name_plural = _("Inscription Types")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class ExtraAlphabeticalSign(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("позаалфавітний знак (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Extra-alphabetical sign")
        verbose_name_plural = _("Extra-alphabetical signs")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    

class GraffitiCondition(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("стан графіті (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Graffiti condition")
        verbose_name_plural = _("Graffiti conditions")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class GraffitiAlignment(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("вирівнювання графіті (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Graffiti alignment")
        verbose_name_plural = _("Graffiti alignments")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)
    
    
class Genre(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("жанр (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self) -> str:
        return self.text
    
    # def __repr__(self) -> str:
    #     return str(self)


class DatingCriterium(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("критерій датування (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Dating criterium")
        verbose_name_plural = _("Dating criteria")

    def __str__(self) -> str:
        return self.text
    
    
class WritingSystem(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("система письма (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Writing System")
        verbose_name_plural = _("Writing Systems")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)

class Medium(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("? (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Medium")
        verbose_name_plural = _("Media")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)


class Material(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("матеріал (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")

    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return str(self)


class Section(abstract.AbstractTagModel):
    text_ukr = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("розділ (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

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


class HistoricalPerson(abstract.AbstractBaseModel):
    name = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Name (eng)"))
    name_ukr = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("назва (укр)"))
    uniform_resource_identifier = models.URLField(blank=True, null=True)
    
    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"
    

class BibliographyItem(abstract.AbstractBaseModel):
    title = models.CharField(max_length=1024, null=True, blank=True, help_text=_("Title of the publication"))
    authors = models.CharField(max_length=1024, null=True, blank=True, help_text=_("List of author in format F.N.LastName, F.N.LastName (use 'et al.' for more than two authors)"))
    year = models.IntegerField(null=True, blank=True, help_text=_("Year of the publication"))
    #title_ukr = models.CharField(max_length=1024, null=True, blank=True, help_text=_("Назва видання"))
    body_of_publication = models.CharField(max_length=1024, null=True, blank=True, help_text=_("Full bibliographic details, e.g. 'Journal of Advanced Studies, vol. 3, n. 3, pp. 33-333'"))
    
    
    class Meta:
        verbose_name = _("Bibliography item")
        verbose_name_plural = _("Bibliography items")
    
    def __str__(self) -> str:
        return f"{self.authors} ({self.year})"
        

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

    medium = models.ForeignKey(Medium, on_delete=models.SET_NULL, blank=True, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, blank=True, null=True)
   
    documentation = models.ManyToManyField(Documentation, blank=True, verbose_name=_("documentation"), default=None)
    spatial_position = ArrayField(models.FloatField(), size=3, default=list, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"), blank=True, null=True)
    spatial_direction = ArrayField(models.FloatField(), size=3, default=list, help_text=_("Format: 3 comma-separated float numbers, e.g.: 0.0, 1.1, 2.2"), blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, help_text=_("Tags attached to the panel"), related_name='surfaces')
    
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
    # metadata
    position_on_surface = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("Position on surface"), help_text=_("Position on the surface (PASTE HERE LINK COPIED IN CLIPBOARD)"))
    title = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("Alternative title"), help_text=_("Fill in if the inscription is known by an alternative name"))
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, blank=True, null=True, related_name="inscriptions", verbose_name=_("Surface"))
    
    # graffiti metadata
    type_of_inscription = models.ForeignKey(InscriptionType, on_delete=models.SET_NULL,  blank=True, null=True)
    genre = models.ManyToManyField(Genre, blank=True, help_text=_("Genre of the inscription"), verbose_name="Textual genre", related_name='inscriptions')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Pictorial descriptions"), help_text=_("Descriptions attached to the graffiti"), related_name='inscriptions')
    elevation = models.IntegerField(null=True, blank=True, help_text=_("Elevation of inscription from the floor, in mm"))
    height = models.IntegerField(null=True, blank=True, help_text=_("Height of inscription, in mm"))
    width = models.IntegerField(null=True, blank=True, help_text=_("Width of inscription, in mm"))
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, blank=True, null=True, related_name='inscriptions')
    writing_system = models.ForeignKey(WritingSystem, on_delete=models.SET_NULL, blank=True, null=True, related_name='inscriptions')
    min_year = models.IntegerField(null=True, blank=True, verbose_name=_("Lower dating boundary"), help_text=_("If no lower boundary is known (e.g. 'before XII century') leave blank."))
    max_year = models.IntegerField(null=True, blank=True, verbose_name=_("Higher dating boundary"), help_text=_("If no higher boundary is known (e.g. 'after XII century') leave blank."))
    dating_criteria = models.ManyToManyField(DatingCriterium, blank=True)
    
    # graffiti data
    transcription = RichTextField(null=True, blank=True, verbose_name=_("Textual graffiti"), help_text=_("Transcription of the graffiti"))
    interpretative_edition = RichTextField(null=True, blank=True, help_text=_("Interpretation of the graffiti"))
    romanisation = RichTextField(null=True, blank=True, help_text=_("Romanisation of the graffiti"))
    mentioned_person = models.ManyToManyField(HistoricalPerson, blank=True, related_name="people_mentioned")
    inscriber = models.ForeignKey(HistoricalPerson, on_delete=models.SET_NULL, blank=True, null=True, related_name="inscription_inscriber")
    translation_eng = RichTextField(null=True, blank=True, verbose_name=_("Translation (English)")) # models.ManyToManyField("Translation", blank=True)
    translation_ukr = RichTextField(null=True, blank=True, verbose_name=_("Переклад (укр)"))
    comments_eng = RichTextField(null=True, blank=True, verbose_name=_("Comments (English)")) # models.ManyToManyField("Description", blank=True, verbose_name=_("Comments"))
    comments_ukr = RichTextField(null=True, blank=True, verbose_name=_("Коментарі (укр)"))
    
    # material metadata
    condition = models.ManyToManyField(GraffitiCondition, blank=True, verbose_name=_("Graffiti condition"), help_text=_("In what condition is the graffiti?"))
    alignment = models.ManyToManyField(GraffitiAlignment, blank=True, verbose_name=_("Graffiti alignment"), help_text=_("Is the graffiti aligned in some way?"))
    extra_alphabetical_sign = models.ManyToManyField(ExtraAlphabeticalSign, blank=True, verbose_name=_("Extra-alphabetical signs"))
    
    # bibliography and contributions
    bibliography = models.ManyToManyField(BibliographyItem, blank=True, help_text=_("Add bibliography items"))
    author = models.ManyToManyField(Author, blank=True, verbose_name=_("Contributors"), help_text=_("List of authors for this inscription"))
    
    
    def __str__(self) -> str:
        if (self.title) is not None:
            return f"Inscription {self.panel.title}:{self.id} ({self.title})"
        else:
            return f"Inscription {self.panel.title}:{self.id}"
    

    class Meta:
        verbose_name = _("Inscription")


    def list_all_pk(self):
        all_pk = []
        for obj in Inscription.objects.all().order_by('pk'):
            all_pk.append(obj.pk)
        return all_pk
        
    def next(self):
        all_pk = self.list_all_pk()
        current_index = all_pk.index(self.pk)
        try: 
            return Inscription.objects.get(pk=all_pk[current_index+1])
        except: 
            return None
        
    def previous(self):
        all_pk = self.list_all_pk()
        current_index = all_pk.index(self.pk)
        try:
            return Inscription.objects.get(pk=all_pk[current_index-1])
        except:
            return None
    
        
class PanelOrInscription(models.IntegerChoices):
    PANEL = 1, "Surface"
    INSCRIPTION = 2, "Inscription"
    

class Image(abstract.AbstractTIFFImageModel):
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
    

# class Translation(abstract.AbstractBaseModel):
#     text = RichTextField(null=True, blank=True, verbose_name=_("Translation text"))
#     # inscription = models.ForeignKey(Inscription, null=True, blank=True, on_delete=models.CASCADE)#, related_name="translation")
#     author = models.ManyToManyField(Author, blank=True, verbose_name=_("Author"), default=None)
#     translation_language = models.ForeignKey(Language, blank=True, null=True, on_delete=models.SET_NULL, related_name="translation_language", default=None)
    
#     # def __str__(self) -> str:
#     #     if self.translation_language is not None:
#     #         return f"{self.translation_language} translation for {self.inscription}"
#     #     else:
#     #         return f"Translation for {self.inscription}"    
    
#     class Meta:
#         verbose_name = _("Translation")
#         verbose_name_plural = _("Translations")
        
        
# class Description(abstract.AbstractBaseModel):
#     text = RichTextField(null=True, blank=True, verbose_name=_("Description text"))
#     # inscription = models.ForeignKey(Inscription, null=True, blank=True, on_delete=models.CASCADE)#, related_name="description")
#     author = models.ManyToManyField(Author, blank=True, verbose_name=_("Author"), default=None)
#     language = models.ForeignKey(Language, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    
#     # def __str__(self) -> str:
#     #     if self.language is not None:
#     #         return f"Description for {self.inscription} ({self.language})"
#     #     else:
#     #         return f"Description for {self.inscription}"
    
#     class Meta:
#         verbose_name = _("Description")
#         verbose_name_plural = _("Descriptions")
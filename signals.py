from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .models import  Image, Inscription
import requests

@receiver(post_save, sender=Image)
def fetch_image_dimensions(sender, instance, created, **kwargs):
    """Fetch image dimensions from IIIF info.json after an Image is created."""
    if created and instance.iiif_file:
        # Construct IIIF URL from iiif_file path
        iiif_url = f"{settings.IIIF_URL}{instance.iiif_file.name}"
        info_json_url = f"{iiif_url}/info.json"
        
        try:
            response = requests.get(info_json_url, timeout=10)
            response.raise_for_status()
            info_data = response.json()
            width = info_data.get('width')
            height = info_data.get('height')
            print(f"Fetched dimensions for Image {instance.id}: width={width}, height={height}")
            
            if width and height:
                instance.width = width
                instance.height = height
                instance.save(update_fields=['width', 'height'])
                print(f"Updated Image {instance.id} with width {width} and height {height}")
            else:
                print(f"Width or height not found in info.json for Image {instance.id}")
        except requests.RequestException as e:
            print(f"Error fetching info.json for Image {instance.id} from {info_json_url}: {e}")
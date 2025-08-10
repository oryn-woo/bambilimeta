from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

def make_thumbnail(image_field, size=(400, 300)):
    img = Image.open(image_field)
    img.thumbnail(size, Image.ANTIALIAS)
    temp = BytesIO()
    img.save(temp, format='JPEG')
    return ContentFile(temp.getvalue())

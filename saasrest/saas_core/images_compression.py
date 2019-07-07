import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def compress_image(image):
    """Compress image"""
    if not image:
        return image
    image_tmp = Image.open(image)
    output_io_stream = BytesIO()
    fill_color = '#fff'  # your background

    if image_tmp.mode in ('RGBA', 'LA'):
        background = Image.new(image_tmp.mode[:-1], image_tmp.size, fill_color)
        background.paste(image_tmp, image_tmp.split()[-1])
        image_tmp = background

    image_tmp.thumbnail((1600, 1200), Image.ANTIALIAS)
    image_tmp.save(output_io_stream, format='JPEG', quality=70)
    output_io_stream.seek(0)

    uploaded_image = InMemoryUploadedFile(output_io_stream,
                                          'ImageField',
                                          "%s.jpg" % image.name.split('.')[0],
                                          'image/jpeg',
                                          sys.getsizeof(output_io_stream),
                                          None)
    return uploaded_image

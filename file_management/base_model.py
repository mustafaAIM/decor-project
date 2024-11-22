from django.db import models

class BaseFile(models.Model):
    FILE_TYPES = (
        ('image', 'Image'),
        ('pdf', 'PDF'),
        ('cad', 'AutoCAD'),
        ('3d', '3D Max'),
    )

    file = models.FileField(upload_to='files/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    is_primary = models.BooleanField(default=False)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_file_type_from_extension(self):
        ext = self.file.name.split('.')[-1].lower()
        extension_mapping = {
            'jpg': 'image', 'jpeg': 'image', 'png': 'image',
            'pdf': 'pdf',
            'dwg': 'cad', 'dxf': 'cad',
            '3ds': '3d', 'max': '3d'
        }
        return extension_mapping.get(ext, 'unknown')
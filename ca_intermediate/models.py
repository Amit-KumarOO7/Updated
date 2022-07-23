from django.db import models

# Create your models here.
class RootCAIM(models.Model):
    name = models.CharField(max_length=64)
    set_issuer = models.ForeignKey('self',on_delete=models.CASCADE,null=True, blank=True)
    certificate = models.TextField(unique=True)
    key = models.TextField(unique=True)

    def __str__(self) -> str:
        return self.name
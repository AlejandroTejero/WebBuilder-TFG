from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea un UserProfile vacío cada vez que se crea un User nuevo,
    independientemente de si viene del registro normal o de OAuth.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
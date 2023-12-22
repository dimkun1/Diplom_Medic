from django.apps import AppConfig


# from django.contrib.auth.models import Group


class HospitalAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospital_app'

    #
    # def ready(self):
    #     self.create_default_groups()
    #
    # def create_default_groups(self):
    #     # Создаем группы, если их еще нет
    #     Group.objects.get_or_create(name='Patient')
    #     Group.objects.get_or_create(name='Doctors')

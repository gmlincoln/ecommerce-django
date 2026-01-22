from django.apps import AppConfig
import django.template.context as context
from copy import copy

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'

    def ready(self):
        # Monkeypatch BaseContext.__copy__ for Python 3.14 compatibility
        # Django 4.2.10's BaseContext.__copy__ uses copy(super()) which fails in Python 3.14
        
        def fixed_copy(self):
            cls = self.__class__
            # Create a new instance without calling __init__
            duplicate = cls.__new__(cls)
            # Copy all attributes from the instance's __dict__
            duplicate.__dict__.update(self.__dict__)
            # Specifically ensure 'dicts' is a shallow copy of the list
            if hasattr(self, 'dicts'):
                duplicate.dicts = self.dicts[:]
            return duplicate
            
        context.BaseContext.__copy__ = fixed_copy

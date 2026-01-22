
from django.core.management.base import BaseCommand
from apps.store.models import Product

class Command(BaseCommand):
 def handle(self,*args,**kwargs):
  data=[('Laptop',65000,'https://picsum.photos/400?1'),
        ('Mouse',500,'https://picsum.photos/400?2'),
        ('Keyboard',1200,'https://picsum.photos/400?3')]
  for n,p,i in data:
   Product.objects.get_or_create(name=n,price=p,image=i)

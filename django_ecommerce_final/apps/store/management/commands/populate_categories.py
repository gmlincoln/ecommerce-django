from django.core.management.base import BaseCommand
from apps.store.models import Category
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Populate default categories'

    def handle(self, *args, **kwargs):
        categories = [
            ('Electronics', 'fas fa-laptop'),
            ('Groceries', 'fas fa-shopping-basket'),
            ('Fashion', 'fas fa-tshirt'),
            ('Home & Kitchen', 'fas fa-home'),
            ('Books', 'fas fa-book'),
            ('Sports & Fitness', 'fas fa-dumbbell'),
            ('Beauty & Personal Care', 'fas fa-spray-can'),
            ('Toys & Games', 'fas fa-gamepad'),
        ]

        created_count = 0
        for name, icon in categories:
            obj, created = Category.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name), 'icon': icon}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
            else:
                self.stdout.write(f'Category already exists: {name}')

        self.stdout.write(self.style.SUCCESS(f'\nTotal: {created_count} new categories created'))
        self.stdout.write(f'Total categories in database: {Category.objects.count()}')

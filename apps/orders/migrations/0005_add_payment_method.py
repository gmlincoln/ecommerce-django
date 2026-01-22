# Generated manually for payment_method field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_add_payment_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                choices=[('sslcommerz', 'SSLCommerz'), ('cod', 'Cash on Delivery')],
                default='sslcommerz',
                max_length=20
            ),
        ),
    ]
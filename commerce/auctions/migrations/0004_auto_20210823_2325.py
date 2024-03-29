# Generated by Django 3.2.4 on 2021-08-23 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20210815_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='category_listings', to='auctions.category'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='photo_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]

# Generated by Django 5.0.1 on 2024-01-21 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonApi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='featured',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
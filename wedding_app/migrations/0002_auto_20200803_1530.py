# Generated by Django 3.0.9 on 2020-08-03 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wedding_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ordered_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

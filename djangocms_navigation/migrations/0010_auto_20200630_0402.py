# Generated by Django 2.2.13 on 2020-06-30 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_navigation', '0009_language_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menucontent',
            name='language',
            field=models.CharField(db_index=True, max_length=15, verbose_name='language'),
        ),
    ]
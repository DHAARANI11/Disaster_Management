# Generated by Django 4.2.6 on 2024-02-08 04:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0019_alter_user_lattitude_alter_user_longitude'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='organization_type',
            new_name='profession',
        ),
    ]

# Generated by Django 5.0.3 on 2024-03-31 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_created_date_llmapikey_create_date'),
        ('genai_app', '0018_orgprovider'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orgprovider',
            options={'ordering': ['organization', 'provider', 'name']},
        ),
        migrations.RemoveIndex(
            model_name='orgprovider',
            name='genai_app_o_organiz_6cd576_idx',
        ),
        migrations.RenameField(
            model_name='orgprovider',
            old_name='api_key_name',
            new_name='name',
        ),
        migrations.AddIndex(
            model_name='orgprovider',
            index=models.Index(fields=['organization', 'provider', 'name'], name='genai_app_o_organiz_c25790_idx'),
        ),
    ]
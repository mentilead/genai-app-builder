# Generated by Django 5.0.2 on 2024-03-16 19:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("genai_app", "0015_alter_chatpage_table_alter_customform_table_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CustomForm",
        ),
    ]

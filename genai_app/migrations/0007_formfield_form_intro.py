# Generated by Django 5.0.2 on 2024-03-03 12:30

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("genai_app", "0006_promptpage_from_address_promptpage_subject_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="formfield",
            name="form_intro",
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]

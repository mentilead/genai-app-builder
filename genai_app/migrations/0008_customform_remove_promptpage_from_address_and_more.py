# Generated by Django 5.0.2 on 2024-03-03 16:08

import django.db.models.deletion
import wagtail.blocks
import wagtail.contrib.forms.models
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("genai_app", "0007_formfield_form_intro"),
        ("wagtailcore", "0091_remove_revision_submitted_for_moderation"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomForm",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("body", wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
            bases=(wagtail.contrib.forms.models.FormMixin, "wagtailcore.page"),
        ),
        migrations.RemoveField(
            model_name="promptpage",
            name="from_address",
        ),
        migrations.RemoveField(
            model_name="promptpage",
            name="subject",
        ),
        migrations.RemoveField(
            model_name="promptpage",
            name="to_address",
        ),
        migrations.AddField(
            model_name="promptpage",
            name="prompts",
            field=wagtail.fields.StreamField(
                [
                    (
                        "prompt_list",
                        wagtail.blocks.ListBlock(
                            wagtail.blocks.StructBlock(
                                [
                                    ("prompt_id", wagtail.blocks.CharBlock()),
                                    ("prompt_text", wagtail.blocks.TextBlock()),
                                ]
                            )
                        ),
                    )
                ],
                blank=True,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="promptpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", wagtail.blocks.CharBlock(form_classname="title")),
                    ("paragraph", wagtail.blocks.RichTextBlock()),
                    ("image", wagtail.images.blocks.ImageChooserBlock()),
                ]
            ),
        ),
    ]
# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Trigger",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("trigger_type", models.CharField(max_length=50, db_index=True)),
                ("source", models.CharField(max_length=250, null=True, blank=True)),
                ("date_received", models.DateTimeField()),
                (
                    "date_processed",
                    models.DateTimeField(db_index=True, null=True, blank=True),
                ),
                (
                    "process_after",
                    models.DateTimeField(db_index=True, null=True, blank=True),
                ),
            ],
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TriggerResult",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("result", models.TextField()),
                (
                    "trigger",
                    models.ForeignKey(
                        to="djtriggers.Trigger", on_delete=models.CASCADE
                    ),
                ),
            ],
            bases=(models.Model,),
        ),
    ]

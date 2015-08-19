# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0026_auto_20150819_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='founder',
            name='client_id',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]

# Generated by Django 4.2.4 on 2023-09-09 12:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_alter_question_end_date_alter_question_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 9, 12, 31, 54, 821032, tzinfo=datetime.timezone.utc), verbose_name='published date'),
        ),
    ]

# Generated by Django 4.2.4 on 2023-09-14 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_remove_choice_votes_alter_question_pub_date_vote'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='question',
            name='pub_date',
        ),
    ]

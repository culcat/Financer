# Generated by Django 5.0.2 on 2024-02-22 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FinancerApp', '0002_alter_user_options_remove_user_unique_username_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='balance',
            field=models.IntegerField(default=0),
        ),
    ]

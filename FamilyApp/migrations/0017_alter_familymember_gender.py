# Generated by Django 4.2.8 on 2025-01-26 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FamilyApp', '0016_alter_familymember_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familymember',
            name='gender',
            field=models.CharField(max_length=10),
        ),
    ]

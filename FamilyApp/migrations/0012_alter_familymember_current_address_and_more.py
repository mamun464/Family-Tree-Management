# Generated by Django 4.2.8 on 2024-02-24 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FamilyApp', '0011_familymember_date_of_death_familymember_facebook_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familymember',
            name='current_address',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='familymember',
            name='facebook',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='familymember',
            name='instagram',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='familymember',
            name='linkedin',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='familymember',
            name='permanent_address',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]

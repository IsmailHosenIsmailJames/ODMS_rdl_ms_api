# Generated by Django 4.2.4 on 2024-09-18 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_location_app', '0002_alter_customerlocationmodel_latitude_and_more'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='customerlocationmodel',
            new_name='rdl_custome_work_ar_b81882_idx',
            old_name='exf_custome_work_ar_3f32a1_idx',
        ),
        migrations.RenameIndex(
            model_name='customerlocationmodel',
            new_name='rdl_custome_custome_10cda4_idx',
            old_name='exf_custome_custome_4c1d97_idx',
        ),
        migrations.AlterField(
            model_name='customerlocationmodel',
            name='customer_id',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]
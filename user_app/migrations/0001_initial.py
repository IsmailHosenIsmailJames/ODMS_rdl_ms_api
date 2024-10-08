# Generated by Django 4.2 on 2023-04-09 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserList',
            fields=[
                ('sap_id', models.IntegerField(primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=255)),
                ('mobile_number', models.CharField(max_length=255)),
                ('user_type', models.CharField(blank=True, choices=[('Delivary Assistant', 'Delivary Assistant'), ('Driver', 'Driver')], max_length=20, null=True)),
                ('password', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'RDL User List',
                'verbose_name_plural': 'RDL User List',
                'db_table': 'rdl_user_list',
            },
        ),
    ]

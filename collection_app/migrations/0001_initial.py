# Generated by Django 4.2 on 2023-04-18 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CashCollectionInfoModel',
            fields=[
                ('id', models.TextField(blank=True, primary_key=True, serialize=False)),
                ('invoice_date', models.TextField(blank=True)),
                ('customer_name', models.TextField(blank=True)),
                ('customer_addreess', models.TextField(blank=True)),
                ('customer_mobile', models.TextField(blank=True)),
                ('delevery_type', models.TextField(blank=True)),
                ('route_name', models.TextField(blank=True)),
                ('latitude', models.TextField(blank=True)),
                ('longitude', models.TextField(blank=True)),
                ('status', models.TextField(blank=True)),
                ('product_code', models.TextField(blank=True)),
                ('product_name', models.TextField(blank=True)),
                ('qty', models.TextField(blank=True)),
                ('per_price', models.TextField(blank=True)),
                ('total_price', models.TextField(blank=True)),
            ],
            options={
                'managed': False,
            },
        ),
    ]
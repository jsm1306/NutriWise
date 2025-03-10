# Generated by Django 5.0.7 on 2025-02-28 16:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BMICalculation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField()),
                ('height', models.FloatField()),
                ('bmi_value', models.FloatField()),
                ('gender', models.CharField(max_length=10)),
                ('category', models.CharField(default=0, max_length=100)),
                ('calculated_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='NutritionInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100, unique=True)),
                ('calories', models.FloatField()),
                ('proteins', models.FloatField()),
                ('fats', models.FloatField()),
                ('sodium', models.FloatField(default=0)),
                ('fiber', models.FloatField(default=0)),
                ('carbs', models.FloatField()),
                ('sugar', models.FloatField(default=0)),
                ('price', models.FloatField(default=0)),
                ('image', models.ImageField(blank=True, null=True, upload_to='nutrition_images/')),
                ('unit_weight', models.FloatField(default=100)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='nutrition_items', to='nutrition.category')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ItemEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('quantity', models.FloatField()),
                ('calories', models.FloatField()),
                ('proteins', models.FloatField()),
                ('fats', models.FloatField()),
                ('sodium', models.FloatField(default=0)),
                ('fiber', models.FloatField(default=0)),
                ('carbs', models.FloatField()),
                ('sugar', models.FloatField(default=0)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='item_entries', to='nutrition.category')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='nutrition.usersubmission')),
            ],
        ),
    ]

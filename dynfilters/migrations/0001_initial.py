# Generated by Django 4.0.5 on 2022-06-02 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicFilterExpr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
                ('model', models.CharField(blank=True, default='Patent', max_length=16, null=True)),
                ('is_global', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Filter',
                'verbose_name_plural': 'Filters',
            },
        ),
        migrations.CreateModel(
            name='DynamicFilterTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('op', models.CharField(choices=[('-', '-'), ('!', 'NOT'), ('&', 'AND'), ('|', 'OR'), ('(', '('), (')', ')')], default='-', max_length=1)),
                ('field', models.CharField(blank=True, max_length=64, null=True)),
                ('lookup', models.CharField(choices=[('-', '---------'), ('=', 'Equals'), ('icontains', 'Contains'), ('istartswith', 'Starts with'), ('iendswith', 'Ends with'), ('in', 'One of'), ('-', '---------'), ('range', 'Date Range'), ('year', 'Date Year'), ('month', 'Date Month'), ('day', 'Date Day'), ('-', '---------'), ('isnull', 'Is NULL'), ('isnotnull', 'Is not NULL'), ('istrue', 'Is TRUE'), ('isfalse', 'Is FALSE'), ('-', '---------'), ('lt', 'Less Than'), ('gt', 'Greater Than'), ('lte', 'Less Than or Equal To'), ('gte', 'Greater Than or Equal To')], default='-', max_length=16)),
                ('value', models.CharField(blank=True, max_length=100, null=True)),
                ('bilateral', models.BooleanField(default=False)),
                ('order', models.PositiveSmallIntegerField(blank=True, db_index=True, default=0)),
                ('filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dynfilters.dynamicfilterexpr')),
            ],
            options={
                'verbose_name': 'Field',
                'verbose_name_plural': 'Fields',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='DynamicFilterColumnSortOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(blank=True, max_length=64, null=True)),
                ('order', models.PositiveSmallIntegerField()),
                ('filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dynfilters.dynamicfilterexpr')),
            ],
            options={
                'verbose_name': 'Column sort order',
                'verbose_name_plural': 'Column sort orders',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='DynamicFilterColumn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(blank=True, max_length=64, null=True)),
                ('order', models.PositiveSmallIntegerField()),
                ('filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dynfilters.dynamicfilterexpr')),
            ],
            options={
                'verbose_name': 'Column',
                'verbose_name_plural': 'Columns',
                'ordering': ('order',),
            },
        ),
    ]

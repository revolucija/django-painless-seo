# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


# this is a fake migration required to run tests
class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeoMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('path', models.CharField(help_text="This should be an absolute path, excluding the domain name. Example: '/foo/bar/'.", max_length=200, verbose_name='Path', db_index=True)),
                ('lang_code', models.CharField(default=b'en', max_length=2, verbose_name='Language', choices=[(b'en', 'English'), (b'pt', 'Portugu\xeas'), (b'es', 'Espa\xf1ol'), (b'de', 'Deutsch'), (b'fr', 'Fran\xe7ais')])),
                ('title', models.CharField(max_length=68, verbose_name='Title', blank=True)),
                ('description', models.CharField(max_length=155, verbose_name='Description', blank=True)),
                ('override_path', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('path', 'lang_code'),
                'db_table': 'seo_metadata',
                'verbose_name': 'SEO metadata',
                'verbose_name_plural': 'SEO metadata',
            },
        ),
        migrations.AlterUniqueTogether(
            name='seometadata',
            unique_together=set([('path', 'lang_code')]),
        ),
    ]

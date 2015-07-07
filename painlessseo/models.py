# Copyright (C) 2014 Glamping Hub (https://glampinghub.com)
# License: BSD 3-Clause

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate, get_language

from painlessseo import settings


class SeoMetadata(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    path = models.CharField(verbose_name=_('Path'), max_length=200, db_index=True,
                            help_text=_("This should be an absolute path, excluding the domain name. Example: '/foo/bar/'."))
    lang_code = models.CharField(verbose_name=_('Language'), max_length=2,
                                 choices=settings.SEO_LANGUAGES,
                                 default=settings.DEFAULT_LANG_CODE)
    title = models.CharField(verbose_name=_('Title'), max_length=68, blank=True)
    description = models.CharField(verbose_name=_('Description'), max_length=155, blank=True)
    override_path = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('SEO metadata')
        verbose_name_plural = _('SEO metadata')
        db_table = 'seo_metadata'
        unique_together = (('path', 'lang_code'), )
        ordering = ('path', 'lang_code')

    def __unicode__(self):
        return "Language: %s | URL: %s" % (self.lang_code, self.path)

    def save(self, *args, **kwargs):
        if kwargs.pop('override_path', None):
            self.override_path = True
        else:
            old_seo = SeoMetadata.objects.get(pk=self.pk)
            if old_seo.override_path:
                self.path = old_seo.path
            self.override_path = False
        super(SeoMetadata, self).save(*args, **kwargs)


def update_seo(sender, instance, **kwargs):
    active_lang = get_language()
    if hasattr(instance, 'get_current_language') and callable(instance.get_current_language):
        active_lang = instance.get_current_language()
    for lang_code, lang_name in settings.SEO_LANGUAGES:
        if active_lang == lang_code:
            activate(lang_code)
            try:
                sm = SeoMetadata.objects.get(content_type=ContentType.objects.get_for_model(instance),
                                             object_id=instance.id, lang_code=lang_code)
                if instance.get_absolute_url() != sm.path:
                    sm.path = instance.get_absolute_url()
            except SeoMetadata.DoesNotExist:
                sm = SeoMetadata(lang_code=lang_code, content_object=instance, path=instance.get_absolute_url())
            sm.save(override_path=True)
    activate(active_lang)


def delete_seo(sender, instance, **kwargs):
    ctype = ContentType.objects.get_for_model(instance)
    for sm in SeoMetadata.objects.filter(content_type=ctype, object_id=instance.id):
        sm.delete()


def register_seo_signals():
    for app, model in settings.SEO_MODELS:
        ctype = ContentType.objects.get(app_label=app, model=model)
        if not hasattr(ctype.model_class(), 'get_absolute_url'):
            raise ImproperlyConfigured("Needed get_absolute_url method not defined on %s.%s model." % (app, model))
        models.signals.post_save.connect(update_seo, sender=ctype.model_class(), weak=False)
        models.signals.pre_delete.connect(delete_seo, sender=ctype.model_class(), weak=False)

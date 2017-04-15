from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from practice.decorators import check_permission


class BaseModel(models.Model):
    """
    This is base class model for the application models. 
    Here we define default fields for all the UserWarning
    Like:  date_created, date_updated, created_by, updated_by
    """
    date_created = models.DateTimeField(
        verbose_name=_('Date Created'),
        help_text=_('Creation Date.'),
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        verbose_name=_('Date Updated'),
        help_text=_('Last Update.'),
        auto_now=True,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Updated By'),
        help_text=_('User Who Last Update This Record'),
        related_name='+',
        null=True, blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Created By'),
        help_text=_('User Who Create This Record'),
        related_name='+',
        null=True, blank=True
    )

    def update(self, *args, **kwargs):
        @check_permission(['change_{}'.format(self.__class__.__name__)], field='updated_by')
        def update(self, *args, **kwargs):
            print('update')
            if self.id is None:
                raise MissUseError(_("You need to create user first"))
            return super().save(*args, **kwargs)
        return update(self, *args, **kwargs)

    def create(self, *args, **kwargs):
        @check_permission(['add_{}'.format(self.__class__.__name__)], field='created_by')
        def create(self, *args, **kwargs):
            print('create')
            self.created_by = self.updated_by
            self.set_password(self.password)
            return super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        import inspect
        print(inspect.stack()[1][3])
        print('save', self.__dict__)
        if self.id is not None:
            return self.update(*args, **kwargs)
        else:
            return self.create(*args, **kwargs)

    class Meta:
        abstract = True

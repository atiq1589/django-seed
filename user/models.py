import uuid
from .base_model import BaseModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.signals import user_logged_in
from django.core import validators
from django.db import models, connection
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from practice.decorators import check_permission


class UserManager(BaseUserManager):
    """
    The Custom System User Manager for the Project. 
    Need to implement necessary methods for the system user throughout the application. 
    """

    # def filter(self, *args, **kwargs):
    #     if 'email' in kwargs:
    #         kwargs['email__iexact'] = kwargs['email']
    #         del kwargs['email']
    #     return super(UserManager, self).filter(*args, **kwargs)

    # def get(self, **kwargs):
    #     if 'email' in kwargs:
    #         kwargs['email__iexact'] = kwargs['email']
    #         del kwargs['email']
    #     return super(UserManager, self).get(**kwargs)

    def get_or_create_sys_admin(self, email):
        """		
        This Method will get or create a sys admin for application		
        :param email: email address		
        :return object, boolen: User object, True if created or False		
        """
        try:
            return self.get(email=email), False
        except Exception:
            return self.create_superuser(email=email, password=settings.SECRET_KEY), True
    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    The System User Model for the project.
    """

    uuid = models.UUIDField(
        verbose_name=_('Unique Identifier'),
        help_text=_('Unique Identifier For The System User.'),
        unique=True,
        default=uuid.uuid4,
        editable=False)

    username = models.CharField(
        verbose_name=_('Username'),
        unique=True,
        max_length=254,
        help_text=_(
            'Required. 254 Characters or Fewer. Letters, Digits And @/./+/-/_ Only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter A Valid Username. This Value May Contain Only Letters, Numbers And @/./+/-/_ Characters.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        }
    )

    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_(
            'Designates That User Should Be Treated as Active In All The Tenant.'),
    )

    is_staff = models.BooleanField(
        _('Staff Status'),
        default=False,
        help_text=_('Designates That User Able To Login Or Not.'),
    )

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        # return "{0} {1}".format(self.first_name, self.last_name).strip()
        pass

    def get_short_name(self):
        """
        Returns the short name (first name) for the user.
        """
        # return self.first_name
        pass

    def __str__(self):
        return str(self.username)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    
    
    def update_admin_last_login(sender, user, **kwargs):
        """
        A signal receiver which updates the last_login date for
        the user logging in.
        """
        user.updated_by = user
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

    from django.contrib.auth.models import update_last_login as django_update_last_login
    user_logged_in.disconnect(django_update_last_login)
    user_logged_in.connect(update_admin_last_login)

    class Meta:
        db_table = 'user_users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')

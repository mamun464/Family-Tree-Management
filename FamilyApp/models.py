from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from datetime import date

class FamilyMemberManager(BaseUserManager):
    def create_user(self, email, full_name, phone_no,password=None, password2=None,**extra_fields,):
    
       
        print(f"Input: {email}")
        
        if not phone_no:
            raise ValueError("Phone Number must be provided")
        if not password:
            raise ValueError('Password is not provided')

        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)

        user = self.model(
            email=email.lower(),
            full_name = full_name,
            phone_no = phone_no,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        # print(user)
        return user

    def create_superuser(self, email, password, full_name, phone_no, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_alive', True)
        return self.create_user(email, full_name, phone_no, password, **extra_fields)


class FamilyMember(AbstractBaseUser, PermissionsMixin):
    username = None
    full_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(db_index=True, unique=True, null=False, max_length=254)
    user_profile_img = models.URLField(blank=True, null=True)
    phone_no = models.CharField(db_index=True, max_length=20, null=False, unique=True)
    place_of_birth = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10)

    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True,blank=True)
    current_address = models.CharField(max_length=255, blank=True, default='')
    permanent_address = models.CharField(max_length=255, blank=True, default='')

    facebook = models.CharField(max_length=255, blank=True, default='')
    linkedin = models.CharField(max_length=255, blank=True, default='')
    instagram = models.CharField(max_length=255, blank=True, default='')

    is_staff = models.BooleanField(default=False) # must needed, otherwise you won't be able to loginto django-admin.
    is_active = models.BooleanField(default=True) # must needed, otherwise you won't be able to loginto django-admin.
    is_superuser = models.BooleanField(default=False)

    is_alive = models.BooleanField(default=True) # this field we inherit from PermissionsMixin.
    is_married = models.BooleanField(default=False) # this field we inherit from PermissionsMixin.

    objects = FamilyMemberManager()

    USERNAME_FIELD = 'phone_no'
    REQUIRED_FIELDS = ['email', 'full_name']

    class Meta:
        verbose_name = 'Family Member'
        verbose_name_plural = 'Family Members'

    def __str__(self):
        return f"{self.full_name} ({self.phone_no})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True
    

class Relationship(models.Model):
    PERSON_RELATIONSHIP_CHOICES = (
        ('Parent', 'Parent'),
        ('Child', 'Child'),
        ('Spouse', 'Spouse'),
        ('Sibling', 'Sibling'),
        ('Grandparent', 'Grandparent'),
        ('Grandchild', 'Grandchild'),
        ('Aunt', 'Aunt'),
        ('Uncle', 'Uncle'),
        ('Cousin', 'Cousin'),
        ('Niece', 'Niece'),
        ('Nephew', 'Nephew'),
        ('In-Law', 'In-Law'),
        ('Step-Parent', 'Step-Parent'),
        ('Step-Child', 'Step-Child'),
        ('Half-Sibling', 'Half-Sibling'),
        # Add other relationship types as needed
    )

    person = models.ForeignKey(
        'FamilyMember',  # Use string representation of the model name
        related_name='person_relationships',
        on_delete=models.PROTECT
    )
    related_person = models.ForeignKey(
        'FamilyMember',  # Use string representation of the model name
        related_name='related_person_relationships',
        on_delete=models.CASCADE
    )
    relationship_type = models.CharField(max_length=100, choices=PERSON_RELATIONSHIP_CHOICES)

    def __str__(self):
        return f"{self.person} - {self.related_person} ({self.relationship_type})"
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """Custom user manager untuk CustomUser"""
    
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username harus diisi')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', Role.objects.filter(nama='admin').first())
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser harus memiliki is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser harus memiliki is_superuser=True.')
        
        return self.create_user(username, password, **extra_fields)


class Role(models.Model):
    """Model untuk role/level pengguna"""
    
    NAMA_CHOICES = [
        ('admin', 'Admin'),
        ('pembimbing_sekolah', 'Pembimbing Sekolah'),
        ('pembimbing_industri', 'Pembimbing Industri'),
        ('peserta', 'Peserta Prakerin'),
        ('kepala_jurusan', 'Kepala Jurusan'),
    ]
    
    id = models.SmallIntegerField(primary_key=True)
    nama = models.CharField(max_length=50, unique=True, choices=NAMA_CHOICES)
    deskripsi = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['id']
    
    def __str__(self):
        return self.get_nama_display()


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom User Model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)  # Django uses password internally
    nama_lengkap = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True, db_index=True)
    no_hp = models.CharField(max_length=20, blank=True, null=True)
    foto_profil = models.ImageField(upload_to='profiles/', blank=True, null=True)
    role = models.ForeignKey(
        Role, 
        on_delete=models.RESTRICT, 
        related_name='users',
        verbose_name='Role'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False)  # Untuk akses admin panel
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nama_lengkap', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nama_lengkap} ({self.get_role_display()})"
    
    def get_role_display(self):
        return self.role.get_nama_display() if self.role else '-'
    
    @property
    def is_admin(self):
        return self.role and self.role.nama == 'admin'
    
    @property
    def is_pembimbing_sekolah(self):
        return self.role and self.role.nama == 'pembimbing_sekolah'
    
    @property
    def is_pembimbing_industri(self):
        return self.role and self.role.nama == 'pembimbing_industri'
    
    @property
    def is_peserta(self):
        return self.role and self.role.nama == 'peserta'
    
    @property
    def is_kepala_jurusan(self):
        return self.role and self.role.nama == 'kepala_jurusan'
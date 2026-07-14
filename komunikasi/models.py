from django.db import models
from prakerin.models import PesertaPrakerin
from jurnal.models import JurnalHarian
from accounts.models import CustomUser
import uuid


class Feedback(models.Model):
    """Model untuk feedback/catatan dari pembimbing"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jurnal = models.ForeignKey(
        JurnalHarian, 
        on_delete=models.CASCADE, 
        blank=True, null=True,
        related_name='feedback',
        db_index=True,
        help_text='Isi jika feedback terkait jurnal tertentu'
    )
    peserta = models.ForeignKey(
        PesertaPrakerin, 
        on_delete=models.CASCADE, 
        blank=True, null=True,
        related_name='feedback',
        db_index=True,
        help_text='Isi jika feedback umum (bukan per jurnal)'
    )
    dari_user = models.ForeignKey(
        CustomUser, 
        on_delete=models.RESTRICT, 
        related_name='feedback_dikirim',
        db_index=True
    )
    pesan = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedback'
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.jurnal:
            return f"Feedback dari {self.dari_user.nama_lengkap} - Hari {self.jurnal.hari_ke}"
        return f"Feedback dari {self.dari_user.nama_lengkap} - {self.peserta}"


class Notifikasi(models.Model):
    """Model untuk notifikasi sistem"""
    
    TIPE_CHOICES = [
        ('info', 'Info'),
        ('success', 'Sukses'),
        ('warning', 'Peringatan'),
        ('error', 'Error'),
    ]
    
    KATEGORI_CHOICES = [
        ('jurnal', 'Jurnal'),
        ('penilaian', 'Penilaian'),
        ('feedback', 'Feedback'),
        ('sistem', 'Sistem'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='notifikasi',
        db_index=True
    )
    judul = models.CharField(max_length=200)
    pesan = models.TextField()
    tipe = models.CharField(max_length=30, choices=TIPE_CHOICES, default='info')
    kategori = models.CharField(max_length=50, choices=KATEGORI_CHOICES, db_index=True)
    data_json = models.JSONField(blank=True, null=True, verbose_name='Data Tambahan')
    link = models.URLField(blank=True, null=True, help_text='Deep link ke halaman terkait')
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notifikasi'
        verbose_name = 'Notifikasi'
        verbose_name_plural = 'Notifikasi'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.judul} - {self.user.nama_lengkap}"
    
    def mark_as_read(self):
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
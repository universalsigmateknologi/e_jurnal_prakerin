from django.db import models
from prakerin.models import PesertaPrakerin
from accounts.models import CustomUser
import uuid


class KunjunganMonitoring(models.Model):
    """Model untuk catatan kunjungan monitoring pembimbing sekolah"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    peserta = models.ForeignKey(
        PesertaPrakerin, 
        on_delete=models.CASCADE, 
        related_name='kunjungan',
        db_index=True
    )
    pembimbing_sekolah = models.ForeignKey(
        CustomUser, 
        on_delete=models.RESTRICT, 
        related_name='kunjungan_monitoring',
        db_index=True,
        limit_choices_to={'role__nama': 'pembimbing_sekolah'}
    )
    tanggal_kunjungan = models.DateField(db_index=True)
    hasil_observasi = models.TextField(help_text='Hasil observasi selama kunjungan')
    catatan = models.TextField(blank=True, null=True)
    tindak_lanjut = models.TextField(blank=True, null=True, help_text='Tindak lanjut yang perlu dilakukan')
    lampiran = models.ImageField(
        upload_to='kunjungan/%Y/%m/', 
        blank=True, null=True,
        help_text='Foto bukti kunjungan (opsional)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kunjungan_monitoring'
        verbose_name = 'Kunjungan Monitoring'
        verbose_name_plural = 'Kunjungan Monitoring'
        ordering = ['-tanggal_kunjungan']
    
    def __str__(self):
        return f"Kunjungan {self.tanggal_kunjungan} - {self.peserta.user.nama_lengkap}"


class LogAktivitas(models.Model):
    """Model untuk log aktivitas pengguna"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        blank=True, null=True,
        related_name='log_aktivitas',
        db_index=True
    )
    aksi = models.CharField(max_length=100, db_index=True)  # create, update, delete, login, dll
    modul = models.CharField(max_length=50, db_index=True)  # jurnal, penilaian, user, dll
    record_id = models.UUIDField(blank=True, null=True, help_text='ID record yang terpengaruh')
    deskripsi = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'log_aktivitas'
        verbose_name = 'Log Aktivitas'
        verbose_name_plural = 'Log Aktivitas'
        ordering = ['-created_at']
    
    def __str__(self):
        user_str = self.user.nama_lengkap if self.user else 'Anonymous'
        return f"[{self.created_at}] {user_str} - {self.aksi} ({self.modul})"
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['modul', 'aksi']),
            models.Index(fields=['-created_at']),
        ]
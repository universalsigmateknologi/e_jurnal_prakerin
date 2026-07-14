from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import CustomUser
from master.models import TahunAjaran, Jurusan, Perusahaan, Departemen
import uuid


class Pembimbing(models.Model):
    """Model untuk data pembimbing (sekolah & industri)"""
    
    TIPE_CHOICES = [
        ('sekolah', 'Pembimbing Sekolah'),
        ('industri', 'Pembimbing Industri'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='pembimbing_profile',
        limit_choices_to={'role__nama__in': ['pembimbing_sekolah', 'pembimbing_industri']}
    )
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, db_index=True)
    perusahaan = models.ForeignKey(
        Perusahaan, 
        on_delete=models.SET_NULL, 
        blank=True, null=True,
        related_name='pembimbing_industri',
        help_text='Hanya diisi untuk pembimbing industri'
    )
    nip_nik = models.CharField(max_length=50, blank=True, null=True, verbose_name='NIP/NIK')
    jabatan = models.CharField(max_length=100, blank=True, null=True)
    no_hp_kantor = models.CharField(max_length=25, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pembimbing'
        verbose_name = 'Pembimbing'
        verbose_name_plural = 'Pembimbing'
        ordering = ['tipe', 'user__nama_lengkap']
    
    def __str__(self):
        return f"{self.user.nama_lengkap} ({self.get_tipe_display()})"


class PesertaPrakerin(models.Model):
    """Model untuk data peserta prakerin"""
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('selesai', 'Selesai'),
        ('dibatalkan', 'Dibatalkan'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='peserta_profile',
        limit_choices_to={'role__nama': 'peserta'}
    )
    tahun_ajaran = models.ForeignKey(
        TahunAjaran, 
        on_delete=models.RESTRICT, 
        related_name='peserta_prakerin',
        db_index=True
    )
    jurusan = models.ForeignKey(
        Jurusan, 
        on_delete=models.RESTRICT, 
        related_name='peserta_prakerin',
        db_index=True
    )
    perusahaan = models.ForeignKey(
        Perusahaan, 
        on_delete=models.RESTRICT, 
        related_name='peserta_prakerin',
        db_index=True
    )
    departemen = models.ForeignKey(
        Departemen, 
        on_delete=models.SET_NULL, 
        blank=True, null=True,
        related_name='peserta_prakerin'
    )
    nis = models.CharField(max_length=30, verbose_name='NIS')
    nisn = models.CharField(max_length=20, blank=True, null=True, verbose_name='NISN')
    kelas = models.CharField(max_length=20)  # XII TKJ 1
    no_absen = models.SmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    tanggal_mulai = models.DateField(db_index=True)
    tanggal_selesai = models.DateField()
    total_hari = models.SmallIntegerField(validators=[MinValueValidator(1)], help_text='Total hari prakerin')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif', db_index=True)
    catatan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'peserta_prakerin'
        verbose_name = 'Peserta Prakerin'
        verbose_name_plural = 'Peserta Prakerin'
        ordering = ['jurusan__kode', 'kelas', 'no_absen']
        unique_together = ['tahun_ajaran', 'nis']
    
    def __str__(self):
        return f"{self.user.nama_lengkap} - {self.kelas}"
    
    @property
    def jurnal_count(self):
        return self.jurnal_harian.filter(status__in=['submitted', 'verified_industri', 'verified_sekolah']).count()
    
    @property
    def progress_percent(self):
        if self.total_hari == 0:
            return 0
        return min(100, int((self.jurnal_count / self.total_hari) * 100))
    
    @property
    def hari_terakhir_jurnal(self):
        last = self.jurnal_harian.order_by('-hari_ke').first()
        return last.hari_ke if last else 0
    
    def save(self, *args, **kwargs):
        # Hitung total hari otomatis jika belum diisi
        if not self.total_hari and self.tanggal_mulai and self.tanggal_selesai:
            delta = self.tanggal_selesai - self.tanggal_mulai
            self.total_hari = delta.days + 1
        super().save(*args, **kwargs)


class PembimbingPeserta(models.Model):
    """Model relasi many-to-many antara pembimbing dan peserta"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pembimbing = models.ForeignKey(
        Pembimbing, 
        on_delete=models.CASCADE, 
        related_name='peserta_dibimbing',
        db_index=True
    )
    peserta = models.ForeignKey(
        PesertaPrakerin, 
        on_delete=models.CASCADE, 
        related_name='pembimbing',
        db_index=True
    )
    is_utama = models.BooleanField(default=False, help_text='Pembimbing utama')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'pembimbing_peserta'
        verbose_name = 'Pembimbing Peserta'
        verbose_name_plural = 'Pembimbing Peserta'
        unique_together = ['pembimbing', 'peserta']
        ordering = ['-is_utama', 'pembimbing__tipe']
    
    def __str__(self):
        return f"{self.pembimbing} -> {self.peserta}"
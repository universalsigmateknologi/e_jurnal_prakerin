from django.db import models
from django.core.validators import MinValueValidator
from prakerin.models import PesertaPrakerin
from master.models import ElemenKompetensi
from accounts.models import CustomUser
import uuid
import os


def get_upload_path(instance, filename):
    """Generate upload path untuk lampiran jurnal"""
    # Format: jurnal/{tahun}/{bulan}/{jurnal_id}_{timestamp}_{original_name}
    import time
    ext = filename.split('.')[-1].lower()
    timestamp = int(time.time())
    return f"jurnal/original/{instance.jurnal.tanggal.year}/{instance.jurnal.tanggal.month:02d}/{instance.jurnal.id}_{timestamp}_{instance.urutan:03d}.{ext}"


def get_thumbnail_path(instance, filename):
    """Generate upload path untuk thumbnail"""
    import time
    ext = filename.split('.')[-1].lower()
    timestamp = int(time.time())
    return f"jurnal/thumbnail/{instance.jurnal.tanggal.year}/{instance.jurnal.tanggal.month:02d}/{instance.jurnal.id}_{timestamp}_{instance.urutan:03d}.{ext}"


class JurnalHarian(models.Model):
    """Model untuk jurnal harian prakerin"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Terkirim'),
        ('verified_industri', 'Diverifikasi Industri'),
        ('verified_sekolah', 'Diverifikasi Sekolah'),
        ('rejected', 'Ditolak'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    peserta = models.ForeignKey(
        PesertaPrakerin, 
        on_delete=models.CASCADE, 
        related_name='jurnal_harian',
        db_index=True
    )
    hari_ke = models.SmallIntegerField(validators=[MinValueValidator(1)], db_index=True)
    tanggal = models.DateField(db_index=True)
    departemen = models.CharField(max_length=150, blank=True, null=True, help_text='Bisa berbeda dari dept utama')
    jam_masuk = models.TimeField(blank=True, null=True)
    jam_istirahat_mulai = models.TimeField(blank=True, null=True)
    jam_istirahat_selesai = models.TimeField(blank=True, null=True)
    jam_pulang = models.TimeField(blank=True, null=True)
    kegiatan = models.TextField()
    hasil_output = models.TextField(blank=True, null=True)
    kendala = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='draft', db_index=True)
    alasan_reject = models.TextField(blank=True, null=True)
    verified_by_industri = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        blank=True, null=True,
        related_name='jurnal_verified_industri',
        limit_choices_to={'role__nama': 'pembimbing_industri'}
    )
    verified_industri_at = models.DateTimeField(blank=True, null=True)
    verified_by_sekolah = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        blank=True, null=True,
        related_name='jurnal_verified_sekolah',
        limit_choices_to={'role__nama': 'pembimbing_sekolah'}
    )
    verified_sekolah_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jurnal_harian'
        verbose_name = 'Jurnal Harian'
        verbose_name_plural = 'Jurnal Harian'
        ordering = ['peserta', 'hari_ke']
        unique_together = ['peserta', 'hari_ke']
        constraints = [
            models.UniqueConstraint(
                fields=['peserta', 'tanggal'],
                name='unique_peserta_tanggal'
            )
        ]
    
    def __str__(self):
        return f"Hari ke-{self.hari_ke} - {self.peserta.user.nama_lengkap} ({self.tanggal})"
    
    @property
    def foto_count(self):
        return self.lampiran.count()
    
    @property
    def foto_utama(self):
        return self.lampiran.filter(is_primary=True).first() or self.lampiran.first()
    
    @property
    def kompetensi_list(self):
        return [jk.elemen_kompetensi for jk in self.kompetensi.select_related('elemen_kompetensi', 'elemen_kompetensi__kategori')]


class JurnalLampiran(models.Model):
    """Model untuk lampiran jurnal (bukti foto)"""
    
    KATEGORI_CHOICES = [
        ('bukti_kegiatan', 'Bukti Kegiatan'),
        ('hasil_output', 'Hasil Output'),
        ('dokumen_pendukung', 'Dokumen Pendukung'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jurnal = models.ForeignKey(
        JurnalHarian, 
        on_delete=models.CASCADE, 
        related_name='lampiran',
        db_index=True
    )
    nama_file = models.CharField(max_length=255)
    nama_asli = models.CharField(max_length=255, verbose_name='Nama File Asli')
    tipe_file = models.CharField(max_length=50, verbose_name='Tipe File')
    ukuran_file = models.PositiveBigIntegerField(verbose_name='Ukuran File (bytes)')
    url_file = models.ImageField(upload_to=get_upload_path, verbose_name='File')
    url_thumbnail = models.ImageField(
        upload_to=get_thumbnail_path, 
        blank=True, null=True,
        verbose_name='Thumbnail'
    )
    urutan = models.SmallIntegerField(default=0, db_index=True)
    kategori = models.CharField(max_length=30, choices=KATEGORI_CHOICES, default='bukti_kegiatan', db_index=True)
    keterangan = models.CharField(max_length=255, blank=True, null=True)
    lebar_pixel = models.PositiveIntegerField(blank=True, null=True)
    tinggi_pixel = models.PositiveIntegerField(blank=True, null=True)
    is_primary = models.BooleanField(default=False, db_index=True, help_text='Foto utama untuk thumbnail')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'jurnal_lampiran'
        verbose_name = 'Lampiran Jurnal'
        verbose_name_plural = 'Lampiran Jurnal'
        ordering = ['jurnal', 'urutan']
    
    def __str__(self):
        return f"{self.nama_asli} - {self.jurnal}"
    
    @property
    def ukuran_formatted(self):
        """Format ukuran file menjadi human readable"""
        bytes = self.ukuran_file
        if bytes < 1024:
            return f"{bytes} B"
        elif bytes < 1024 * 1024:
            return f"{bytes / 1024:.1f} KB"
        else:
            return f"{bytes / (1024 * 1024):.1f} MB"
    
    def save(self, *args, **kwargs):
        # Jika di-set sebagai primary, hapus primary dari lampiran lain di jurnal yang sama
        if self.is_primary:
            JurnalLampiran.objects.filter(
                jurnal=self.jurnal, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Hapus file fisik saat delete record
        if self.url_file:
            if os.path.isfile(self.url_file.path):
                os.remove(self.url_file.path)
        if self.url_thumbnail:
            if os.path.isfile(self.url_thumbnail.path):
                os.remove(self.url_thumbnail.path)
        super().delete(*args, **kwargs)


class JurnalKompetensi(models.Model):
    """Model relasi jurnal dengan elemen kompetensi yang dicapai"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jurnal = models.ForeignKey(
        JurnalHarian, 
        on_delete=models.CASCADE, 
        related_name='kompetensi',
        db_index=True
    )
    elemen_kompetensi = models.ForeignKey(
        ElemenKompetensi, 
        on_delete=models.RESTRICT, 
        related_name='jurnal_kompetensi',
        db_index=True
    )
    catatan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'jurnal_kompetensi'
        verbose_name = 'Kompetensi Jurnal'
        verbose_name_plural = 'Kompetensi Jurnal'
        unique_together = ['jurnal', 'elemen_kompetensi']
        ordering = ['jurnal', 'elemen_kompetensi__kode']
    
    def __str__(self):
        return f"{self.jurnal} - {self.elemen_kompetensi}"
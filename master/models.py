from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import CustomUser
import uuid


class TahunAjaran(models.Model):
    """Model untuk tahun ajaran/prakerin"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kode = models.CharField(max_length=20, unique=True, db_index=True)  # 2024-2025-GANJIL
    nama = models.CharField(max_length=100)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    is_active = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tahun_ajaran'
        verbose_name = 'Tahun Ajaran'
        verbose_name_plural = 'Tahun Ajaran'
        ordering = ['-tanggal_mulai']
    
    def __str__(self):
        return self.nama
    
    def save(self, *args, **kwargs):
        # Hanya satu tahun ajaran yang aktif
        if self.is_active:
            TahunAjaran.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Jurusan(models.Model):
    """Model untuk jurusan di SMK"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kode = models.CharField(max_length=20, unique=True, db_index=True)  # TKJ, RPL, MM
    nama = models.CharField(max_length=100)
    singkatan = models.CharField(max_length=10, blank=True, null=True)
    kepala_jurusan = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        blank=True, null=True,
        related_name='jurusan_dipimpin',
        limit_choices_to={'role__nama': 'kepala_jurusan'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jurusan'
        verbose_name = 'Jurusan'
        verbose_name_plural = 'Jurusan'
        ordering = ['kode']
    
    def __str__(self):
        return f"{self.nama} ({self.kode})"


class Perusahaan(models.Model):
    """Model untuk perusahaan/industri mitra"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=200, db_index=True)
    bidang_usaha = models.CharField(max_length=150, blank=True, null=True)
    alamat = models.TextField()
    kelurahan = models.CharField(max_length=100, blank=True, null=True)
    kecamatan = models.CharField(max_length=100, blank=True, null=True)
    kota = models.CharField(max_length=100, db_index=True)
    provinsi = models.CharField(max_length=100, blank=True, null=True)
    kode_pos = models.CharField(max_length=10, blank=True, null=True)
    no_telepon = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    nama_pic = models.CharField(max_length=150, blank=True, null=True, verbose_name='Nama PIC')
    jabatan_pic = models.CharField(max_length=100, blank=True, null=True, verbose_name='Jabatan PIC')
    no_hp_pic = models.CharField(max_length=25, blank=True, null=True, verbose_name='No. HP PIC')
    is_aktif = models.BooleanField(default=True, db_index=True)
    catatan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'perusahaan'
        verbose_name = 'Perusahaan'
        verbose_name_plural = 'Perusahaan'
        ordering = ['nama']
    
    def __str__(self):
        return self.nama
    
    @property
    def alamat_lengkap(self):
        parts = [self.alamat]
        if self.kelurahan:
            parts.append(f"Kel. {self.kelurahan}")
        if self.kecamatan:
            parts.append(f"Kec. {self.kecamatan}")
        if self.kota:
            parts.append(self.kota)
        if self.provinsi:
            parts.append(self.provinsi)
        if self.kode_pos:
            parts.append(self.kode_pos)
        return ', '.join(parts)


class Departemen(models.Model):
    """Model untuk departemen di perusahaan"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    perusahaan = models.ForeignKey(
        Perusahaan, 
        on_delete=models.CASCADE, 
        related_name='departemen',
        db_index=True
    )
    nama = models.CharField(max_length=150)
    deskripsi = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departemen'
        verbose_name = 'Departemen'
        verbose_name_plural = 'Departemen'
        ordering = ['perusahaan__nama', 'nama']
        unique_together = ['perusahaan', 'nama']
    
    def __str__(self):
        return f"{self.nama} - {self.perusahaan.nama}"


class KategoriKompetensi(models.Model):
    """Model untuk kategori kompetensi (Soft Skill, Hard Skill, dll)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100)  # Soft Skill, Hard Skill, Sikap, Pengetahuan
    deskripsi = models.TextField(blank=True, null=True)
    warna = models.CharField(max_length=20, default='#3B82F6', help_text='Hex color code untuk UI')
    urutan = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'kategori_kompetensi'
        verbose_name = 'Kategori Kompetensi'
        verbose_name_plural = 'Kategori Kompetensi'
        ordering = ['urutan', 'nama']
    
    def __str__(self):
        return self.nama


class ElemenKompetensi(models.Model):
    """Model untuk elemen kompetensi"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kategori = models.ForeignKey(
        KategoriKompetensi, 
        on_delete=models.CASCADE, 
        related_name='elemen',
        db_index=True
    )
    jurusan = models.ForeignKey(
        Jurusan, 
        on_delete=models.SET_NULL, 
        blank=True, null=True,
        related_name='kompetensi_khusus',
        help_text='Kosongkan jika berlaku untuk semua jurusan'
    )
    kode = models.CharField(max_length=50, unique=True, db_index=True)
    nama = models.CharField(max_length=250)
    deskripsi = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'elemen_kompetensi'
        verbose_name = 'Elemen Kompetensi'
        verbose_name_plural = 'Elemen Kompetensi'
        ordering = ['kategori__urutan', 'kode']
    
    def __str__(self):
        jurusan_text = f" [{self.jurusan.kode}]" if self.jurusan else ""
        return f"{self.kode} - {self.nama}{jurusan_text}"


class AspekPenilaian(models.Model):
    """Model untuk aspek-aspek penilaian"""
    
    TIPE_CHOICES = [
        ('industri', 'Penilaian Industri'),
        ('sekolah', 'Penilaian Sekolah'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kode = models.CharField(max_length=30, unique=True)
    nama = models.CharField(max_length=150)
    deskripsi = models.TextField(blank=True, null=True)
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, db_index=True)
    bobot = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Bobot dalam persen'
    )
    urutan = models.SmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'aspek_penilaian'
        verbose_name = 'Aspek Penilaian'
        verbose_name_plural = 'Aspek Penilaian'
        ordering = ['tipe', 'urutan']
    
    def __str__(self):
        return f"{self.kode} - {self.nama} ({self.get_tipe_display()})"


class Pengaturan(models.Model):
    """Model untuk pengaturan sistem"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kunci = models.CharField(max_length=100, unique=True, db_index=True)
    nilai = models.TextField()
    tipe = models.CharField(max_length=20, default='string')  # string, integer, boolean, json
    kategori = models.CharField(max_length=50, blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pengaturan'
        verbose_name = 'Pengaturan'
        verbose_name_plural = 'Pengaturan'
        ordering = ['kategori', 'kunci']
    
    def __str__(self):
        return self.kunci
    
    def get_value(self):
        """Parse nilai sesuai tipe"""
        if self.tipe == 'integer':
            return int(self.nilai) if self.nilai else 0
        elif self.tipe == 'boolean':
            return self.nilai.lower() in ('true', '1', 'yes')
        elif self.tipe == 'json':
            import json
            try:
                return json.loads(self.nilai)
            except:
                return None
        return self.nilai
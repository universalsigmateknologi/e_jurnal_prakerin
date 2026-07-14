from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from prakerin.models import PesertaPrakerin
from master.models import AspekPenilaian
from accounts.models import CustomUser
import uuid


class Penilaian(models.Model):
    """Model untuk penilaian peserta prakerin"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    peserta = models.ForeignKey(
        PesertaPrakerin, 
        on_delete=models.CASCADE, 
        related_name='penilaian',
        db_index=True
    )
    aspek = models.ForeignKey(
        AspekPenilaian, 
        on_delete=models.RESTRICT, 
        related_name='penilaian',
        db_index=True
    )
    penilai = models.ForeignKey(
        CustomUser, 
        on_delete=models.RESTRICT, 
        related_name='penilaian_diberikan',
        db_index=True
    )
    nilai = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Nilai 1-100'
    )
    catatan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'penilaian'
        verbose_name = 'Penilaian'
        verbose_name_plural = 'Penilaian'
        ordering = ['peserta', 'aspek__tipe', 'aspek__urutan']
        unique_together = ['peserta', 'aspek', 'penilai']
    
    def __str__(self):
        return f"{self.peserta.user.nama_lengkap} - {self.aspek.nama}: {self.nilai}"
    
    @property
    def nilai_huruf(self):
        """Konversi nilai ke huruf"""
        if self.nilai >= 90:
            return 'A'
        elif self.nilai >= 80:
            return 'B'
        elif self.nilai >= 70:
            return 'C'
        elif self.nilai >= 60:
            return 'D'
        else:
            return 'E'
    
    @property
    def predikat(self):
        """Konversi nilai ke predikat"""
        if self.nilai >= 90:
            return 'Sangat Baik'
        elif self.nilai >= 80:
            return 'Baik'
        elif self.nilai >= 70:
            return 'Cukup'
        elif self.nilai >= 60:
            return 'Kurang'
        else:
            return 'Sangat Kurang'
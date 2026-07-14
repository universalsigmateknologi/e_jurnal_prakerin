from django.contrib import admin
from django.utils.html import format_html
from .models import Penilaian


@admin.register(Penilaian)
class PenilaianAdmin(admin.ModelAdmin):
    list_display = [
        'peserta_display', 'aspek_display', 'tipe_display', 
        'nilai', 'nilai_badge', 'nilai_huruf_display', 'penilai', 'updated_at'
    ]
    list_display_links = ['peserta_display']
    list_filter = ['aspek__tipe', 'aspek', 'penilai', 'peserta__jurusan', 'peserta__perusahaan']
    search_fields = ['peserta__user__nama_lengkap', 'peserta__nis', 'aspek__nama', 'catatan']
    ordering = ['peserta__jurusan__kode', 'peserta__kelas', 'aspek__tipe', 'aspek__urutan']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Peserta & Aspek', {
            'fields': ('peserta', 'aspek', 'penilai')
        }),
        ('Penilaian', {
            'fields': ('nilai', 'catatan')
        }),
    )
    
    def peserta_display(self, obj):
        return f"{obj.peserta.user.nama_lengkap} ({obj.peserta.kelas})"
    peserta_display.short_description = 'Peserta'
    
    def aspek_display(self, obj):
        return obj.aspek.nama
    aspek_display.short_description = 'Aspek Penilaian'
    
    def tipe_display(self, obj):
        return obj.aspek.get_tipe_display()
    tipe_display.short_description = 'Tipe'
    
    def nilai_badge(self, obj):
        color = '#10B981' if obj.nilai >= 80 else '#F59E0B' if obj.nilai >= 60 else '#EF4444'
        return format_html(
            '<span style="background-color:{}; color:white; padding:4px 12px; border-radius:12px; font-weight:bold;">{}</span>',
            color, obj.nilai
        )
    nilai_badge.short_description = 'Nilai'
    nilai_badge.allow_tags = True
    
    def nilai_huruf_display(self, obj):
        color = '#10B981' if obj.nilai >= 80 else '#F59E0B' if obj.nilai >= 60 else '#EF4444'
        return format_html(
            '<span style="color:{}; font-weight:bold; font-size:16px;">{}</span>',
            color, obj.nilai_huruf
        )
    nilai_huruf_display.short_description = 'Huruf'
    nilai_huruf_display.allow_tags = True
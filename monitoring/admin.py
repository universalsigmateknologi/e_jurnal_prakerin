from django.contrib import admin
from .models import KunjunganMonitoring, LogAktivitas


@admin.register(KunjunganMonitoring)
class KunjunganMonitoringAdmin(admin.ModelAdmin):
    list_display = [
        'tanggal_kunjungan', 'peserta_display', 'pembimbing_display', 
        'hasil_truncated', 'lampiran_preview', 'created_at'
    ]
    list_display_links = ['tanggal_kunjungan', 'peserta_display']
    list_filter = ['tanggal_kunjungan', 'pembimbing_sekolah', 'peserta__jurusan', 'peserta__perusahaan']
    search_fields = [
        'peserta__user__nama_lengkap', 'pembimbing_sekolah__nama_lengkap',
        'hasil_observasi', 'catatan', 'tindak_lanjut'
    ]
    ordering = ['-tanggal_kunjungan']
    date_hierarchy = 'tanggal_kunjungan'
    
    fieldsets = (
        ('Informasi Kunjungan', {
            'fields': ('peserta', 'pembimbing_sekolah', 'tanggal_kunjungan')
        }),
        ('Hasil Monitoring', {
            'fields': ('hasil_observasi', 'catatan', 'tindak_lanjut')
        }),
        ('Lampiran', {
            'fields': ('lampiran',)
        }),
    )
    
    def peserta_display(self, obj):
        return f"{obj.peserta.user.nama_lengkap} ({obj.peserta.kelas})"
    peserta_display.short_description = 'Peserta'
    
    def pembimbing_display(self, obj):
        return obj.pembimbing_sekolah.nama_lengkap
    pembimbing_display.short_description = 'Pembimbing'
    
    def hasil_truncated(self, obj):
        if obj.hasil_observasi and len(obj.hasil_observasi) > 80:
            return obj.hasil_observasi[:80] + '...'
        return obj.hasil_observasi
    hasil_truncated.short_description = 'Hasil Observasi'
    
    def lampiran_preview(self, obj):
        if obj.lampiran:
            from django.utils.html import format_html
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="width:60px; height:60px; object-fit:cover; border-radius:4px;" /></a>',
                obj.lampiran.url, obj.lampiran.url
            )
        return '-'
    lampiran_preview.short_description = 'Lampiran'
    lampiran_preview.allow_tags = True


@admin.register(LogAktivitas)
class LogAktivitasAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'user_display', 'aksi', 'modul', 'deskripsi_truncated', 'ip_address'
    ]
    list_display_links = ['created_at']
    list_filter = ['aksi', 'modul', 'created_at', 'user__role']
    search_fields = [
        'user__nama_lengkap', 'user__username', 'deskripsi', 'ip_address'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'user_display', 'aksi', 'modul', 'record_id', 'deskripsi', 'ip_address', 'user_agent']
    
    fieldsets = (
        ('Detail Log', {
            'fields': ('created_at', 'user_display', 'aksi', 'modul', 'record_id')
        }),
        ('Informasi', {
            'fields': ('deskripsi', 'ip_address', 'user_agent')
        }),
    )
    
    def user_display(self, obj):
        if obj.user:
            role = obj.user.get_role_display()
            return f"{obj.user.nama_lengkap} ({role})"
        return 'Anonymous'
    user_display.short_description = 'User'
    
    def deskripsi_truncated(self, obj):
        if obj.deskripsi and len(obj.deskripsi) > 60:
            return obj.deskripsi[:60] + '...'
        return obj.deskripsi
    deskripsi_truncated.short_description = 'Deskripsi'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['delete_old_logs']
    
    def delete_old_logs(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        ninety_days_ago = timezone.now() - timedelta(days=90)
        old = queryset.filter(created_at__lt=ninety_days_ago)
        count = old.count()
        old.delete()
        self.message_user(request, f"{count} log lama (>90 hari) dihapus")
    delete_old_logs.short_description = 'Hapus log lama (>90 hari)'
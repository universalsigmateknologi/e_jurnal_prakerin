from django.contrib import admin
from .models import Pembimbing, PesertaPrakerin, PembimbingPeserta


class PembimbingPesertaInline(admin.TabularInline):
    model = PembimbingPeserta
    extra = 1
    fields = ['pembimbing', 'is_utama']
    verbose_name = 'Pembimbing'
    verbose_name_plural = 'Pembimbing'
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'pembimbing':
            kwargs['queryset'] = Pembimbing.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Pembimbing)
class PembimbingAdmin(admin.ModelAdmin):
    list_display = ['user', 'tipe', 'perusahaan', 'nip_nik', 'jabatan', 'is_active', 'peserta_count']
    list_display_links = ['user']
    list_filter = ['tipe', 'is_active', 'perusahaan']
    search_fields = ['user__nama_lengkap', 'user__username', 'nip_nik', 'jabatan']
    ordering = ['tipe', 'user__nama_lengkap']
    
    fieldsets = (
        ('Akun Pengguna', {
            'fields': ('user', 'tipe')
        }),
        ('Informasi Pembimbing', {
            'fields': ('nip_nik', 'jabatan', 'no_hp_kantor')
        }),
        ('Untuk Pembimbing Industri', {
            'fields': ('perusahaan',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def peserta_count(self, obj):
        return obj.peserta_dibimbing.count()
    peserta_count.short_description = 'Jumlah Peserta Dibimbing'


@admin.register(PesertaPrakerin)
class PesertaPrakerinAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'nis', 'kelas', 'jurusan', 'perusahaan', 
        'departemen', 'tanggal_mulai', 'tanggal_selesai', 
        'status', 'progress_display', 'jurnal_count_display'
    ]
    list_display_links = ['user', 'nis']
    list_filter = ['status', 'tahun_ajaran', 'jurusan', 'perusahaan', 'kelas']
    search_fields = [
        'user__nama_lengkap', 'user__username', 'nis', 'nisn', 'kelas'
    ]
    ordering = ['jurusan__kode', 'kelas', 'no_absen']
    date_hierarchy = 'tanggal_mulai'
    inlines = [PembimbingPesertaInline]
    
    fieldsets = (
        ('Akun & Identitas', {
            'fields': ('user', 'nis', 'nisn', 'kelas', 'no_absen')
        }),
        ('Penempatan', {
            'fields': ('tahun_ajaran', 'jurusan', 'perusahaan', 'departemen')
        }),
        ('Periode Prakerin', {
            'fields': ('tanggal_mulai', 'tanggal_selesai', 'total_hari')
        }),
        ('Status', {
            'fields': ('status', 'catatan')
        }),
    )
    
    def progress_display(self, obj):
        percent = obj.progress_percent
        color = 'green' if percent >= 80 else 'orange' if percent >= 50 else 'red'
        return f'<span style="color:{color}; font-weight:bold;">{percent}%</span>'
    progress_display.short_description = 'Progress'
    progress_display.allow_tags = True
    
    def jurnal_count_display(self, obj):
        count = obj.jurnal_count
        total = obj.total_hari
        return f"{count}/{total}"
    jurnal_count_display.short_description = 'Jurnal'
    
    actions = ['mark_selesai', 'mark_dibatalkan']
    
    def mark_selesai(self, request, queryset):
        queryset.update(status='selesai')
        self.message_user(request, f"{queryset.count()} peserta ditandai selesai")
    mark_selesai.short_description = 'Tandai sebagai Selesai'
    
    def mark_dibatalkan(self, request, queryset):
        queryset.update(status='dibatalkan')
        self.message_user(request, f"{queryset.count()} peserta dibatalkan")
    mark_dibatalkan.short_description = 'Tandai sebagai Dibatalkan'


@admin.register(PembimbingPeserta)
class PembimbingPesertaAdmin(admin.ModelAdmin):
    list_display = ['peserta', 'pembimbing', 'is_utama', 'created_at']
    list_display_links = ['peserta']
    list_filter = ['is_utama', 'pembimbing__tipe']
    search_fields = ['peserta__user__nama_lengkap', 'pembimbing__user__nama_lengkap']
    ordering = ['-is_utama', 'peserta__user__nama_lengkap']
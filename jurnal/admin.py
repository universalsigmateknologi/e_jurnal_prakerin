from django.contrib import admin
from django.utils.html import format_html
from .models import JurnalHarian, JurnalLampiran, JurnalKompetensi


class JurnalLampiranInline(admin.TabularInline):
    model = JurnalLampiran
    extra = 0
    fields = ['thumbnail_preview', 'nama_asli', 'kategori', 'ukuran_formatted', 'is_primary', 'urutan']
    readonly_fields = ['thumbnail_preview', 'nama_asli', 'ukuran_formatted']
    show_change_link = True
    can_delete = True
    
    def thumbnail_preview(self, obj):
        if obj.url_thumbnail:
            return format_html(
                '<img src="{}" style="width:80px; height:80px; object-fit:cover; border-radius:4px;" />',
                obj.url_thumbnail.url
            )
        elif obj.url_file and obj.tipe_file.startswith('image/'):
            return format_html(
                '<img src="{}" style="width:80px; height:80px; object-fit:cover; border-radius:4px;" />',
                obj.url_file.url
            )
        return '-'
    thumbnail_preview.short_description = 'Preview'
    thumbnail_preview.allow_tags = True


class JurnalKompetensiInline(admin.TabularInline):
    model = JurnalKompetensi
    extra = 1
    fields = ['elemen_kompetensi', 'catatan']
    raw_id_fields = ['elemen_kompetensi']
    verbose_name = 'Kompetensi'
    verbose_name_plural = 'Kompetensi yang Dicapai'


@admin.register(JurnalHarian)
class JurnalHarianAdmin(admin.ModelAdmin):
    list_display = [
        'hari_ke', 'peserta_display', 'tanggal', 'departemen',
        'jam_masuk', 'jam_pulang', 'foto_count_display', 
        'status', 'status_badge', 'created_at'
    ]
    list_display_links = ['hari_ke', 'peserta_display']
    list_filter = ['status', 'tanggal', 'peserta__jurusan', 'peserta__perusahaan']
    search_fields = [
        'peserta__user__nama_lengkap', 'peserta__nis', 'kegiatan', 'hasil_output'
    ]
    ordering = ['-tanggal', 'peserta__user__nama_lengkap']
    date_hierarchy = 'tanggal'
    inlines = [JurnalLampiranInline, JurnalKompetensiInline]
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('peserta', 'hari_ke', 'tanggal', 'departemen')
        }),
        ('Jam Kerja', {
            'fields': ('jam_masuk', 'jam_istirahat_mulai', 'jam_istirahat_selesai', 'jam_pulang'),
            'classes': ('collapse',)
        }),
        ('Isi Jurnal', {
            'fields': ('kegiatan', 'hasil_output', 'kendala')
        }),
        ('Status & Verifikasi', {
            'fields': ('status', 'alasan_reject', 'verified_by_industri', 'verified_industri_at', 
                      'verified_by_sekolah', 'verified_sekolah_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['verified_by_industri', 'verified_industri_at', 'verified_by_sekolah', 'verified_sekolah_at']
    
    def peserta_display(self, obj):
        return f"{obj.peserta.user.nama_lengkap} ({obj.peserta.kelas})"
    peserta_display.short_description = 'Peserta'
    
    def foto_count_display(self, obj):
        count = obj.foto_count
        return f"📷 {count}" if count > 0 else "-"
    foto_count_display.short_description = 'Foto'
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6B7280',
            'submitted': '#3B82F6',
            'verified_industri': '#10B981',
            'verified_sekolah': '#059669',
            'rejected': '#EF4444',
        }
        color = colors.get(obj.status, '#6B7280')
        label = obj.get_status_display()
        return format_html(
            '<span style="background-color:{}; color:white; padding:4px 8px; border-radius:4px; font-size:12px;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True
    
    actions = ['verify_industri', 'verify_sekolah', 'reject_jurnal']
    
    def verify_industri(self, request, queryset):
        from django.utils import timezone
        queryset.filter(status='submitted').update(
            status='verified_industri',
            verified_by_industri=request.user,
            verified_industri_at=timezone.now()
        )
        self.message_user(request, f"{queryset.count()} jurnal diverifikasi industri")
    verify_industri.short_description = 'Verifikasi oleh Industri'
    
    def verify_sekolah(self, request, queryset):
        from django.utils import timezone
        queryset.filter(status='verified_industri').update(
            status='verified_sekolah',
            verified_by_sekolah=request.user,
            verified_sekolah_at=timezone.now()
        )
        self.message_user(request, f"{queryset.count()} jurnal diverifikasi sekolah")
    verify_sekolah.short_description = 'Verifikasi oleh Sekolah'
    
    def reject_jurnal(self, request, queryset):
        queryset.exclude(status='rejected').update(status='rejected')
        self.message_user(request, f"{queryset.count()} jurnal ditolak")
    reject_jurnal.short_description = 'Tolak Jurnal'


@admin.register(JurnalLampiran)
class JurnalLampiranAdmin(admin.ModelAdmin):
    list_display = [
        'thumbnail_preview', 'jurnal_display', 'nama_asli', 'kategori', 
        'ukuran_formatted', 'dimensi', 'is_primary', 'urutan'
    ]
    list_display_links = ['thumbnail_preview', 'nama_asli']
    list_filter = ['kategori', 'is_primary', 'jurnal__peserta__perusahaan']
    search_fields = ['nama_asli', 'keterangan', 'jurnal__peserta__user__nama_lengkap']
    ordering = ['jurnal__peserta', 'jurnal__hari_ke', 'urutan']
    readonly_fields = ['thumbnail_preview', 'image_preview', 'ukuran_formatted', 'dimensi', 'created_at']
    
    fieldsets = (
        ('Preview', {
            'fields': ('thumbnail_preview', 'image_preview')
        }),
        ('Informasi File', {
            'fields': ('jurnal', 'nama_asli', 'nama_file', 'tipe_file', 'ukuran_file', 'ukuran_formatted', 'dimensi')
        }),
        ('File', {
            'fields': ('url_file', 'url_thumbnail')
        }),
        ('Pengaturan', {
            'fields': ('kategori', 'keterangan', 'urutan', 'is_primary')
        }),
    )
    
    def jurnal_display(self, obj):
        return f"Hari {obj.jurnal.hari_ke} - {obj.jurnal.peserta.user.nama_lengkap}"
    jurnal_display.short_description = 'Jurnal'
    
    def thumbnail_preview(self, obj):
        if obj.url_thumbnail:
            return format_html(
                '<img src="{}" style="width:60px; height:60px; object-fit:cover; border-radius:4px;" />',
                obj.url_thumbnail.url
            )
        return '-'
    thumbnail_preview.short_description = 'Thumb'
    thumbnail_preview.allow_tags = True
    
    def image_preview(self, obj):
        if obj.url_file and obj.tipe_file.startswith('image/'):
            return format_html(
                '<img src="{}" style="max-width:500px; max-height:400px; object-fit:contain;" />',
                obj.url_file.url
            )
        return '-'
    image_preview.short_description = 'Gambar Asli'
    image_preview.allow_tags = True
    
    def dimensi(self, obj):
        if obj.lebar_pixel and obj.tinggi_pixel:
            return f"{obj.lebar_pixel} x {obj.tinggi_pixel} px"
        return '-'
    dimensi.short_description = 'Dimensi'


@admin.register(JurnalKompetensi)
class JurnalKompetensiAdmin(admin.ModelAdmin):
    list_display = ['jurnal_display', 'elemen_kompetensi', 'kategori_display', 'catatan_truncated']
    list_display_links = ['jurnal_display']
    list_filter = ['elemen_kompetensi__kategori', 'elemen_kompetensi__jurusan']
    search_fields = ['jurnal__peserta__user__nama_lengkap', 'elemen_kompetensi__nama', 'catatan']
    raw_id_fields = ['jurnal', 'elemen_kompetensi']
    
    def jurnal_display(self, obj):
        return f"Hari {obj.jurnal.hari_ke} - {obj.jurnal.peserta.user.nama_lengkap}"
    jurnal_display.short_description = 'Jurnal'
    
    def kategori_display(self, obj):
        return obj.elemen_kompetensi.kategori.nama if obj.elemen_kompetensi.kategori else '-'
    kategori_display.short_description = 'Kategori'
    
    def catatan_truncated(self, obj):
        if obj.catatan and len(obj.catatan) > 50:
            return obj.catatan[:50] + '...'
        return obj.catatan
    catatan_truncated.short_description = 'Catatan'
from django.contrib import admin
from .models import (
    TahunAjaran, Jurusan, Perusahaan, Departemen,
    KategoriKompetensi, ElemenKompetensi, AspekPenilaian, Pengaturan
)


@admin.register(TahunAjaran)
class TahunAjaranAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'tanggal_mulai', 'tanggal_selesai', 'is_active', 'peserta_count']
    list_display_links = ['kode', 'nama']
    list_filter = ['is_active']
    search_fields = ['kode', 'nama']
    ordering = ['-tanggal_mulai']
    date_hierarchy = 'tanggal_mulai'
    
    fieldsets = (
        ('Informasi Tahun Ajaran', {
            'fields': ('kode', 'nama', 'is_active')
        }),
        ('Periode', {
            'fields': ('tanggal_mulai', 'tanggal_selesai')
        }),
    )
    
    def peserta_count(self, obj):
        return obj.peserta_prakerin.count()
    peserta_count.short_description = 'Jumlah Peserta'
    
    actions = ['activate_tahun_ajaran']
    
    def activate_tahun_ajaran(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} tahun ajaran diaktifkan")
    activate_tahun_ajaran.short_description = 'Aktifkan tahun ajaran terpilih'


class DepartemenInline(admin.TabularInline):
    model = Departemen
    extra = 1
    fields = ['nama', 'deskripsi', 'is_active']


@admin.register(Perusahaan)
class PerusahaanAdmin(admin.ModelAdmin):
    list_display = ['nama', 'bidang_usaha', 'kota', 'nama_pic', 'no_hp_pic', 'is_aktif', 'peserta_count']
    list_display_links = ['nama']
    list_filter = ['is_aktif', 'kota', 'provinsi']
    search_fields = ['nama', 'bidang_usaha', 'alamat', 'nama_pic']
    ordering = ['nama']
    inlines = [DepartemenInline]
    
    fieldsets = (
        ('Informasi Perusahaan', {
            'fields': ('nama', 'bidang_usaha', 'is_aktif')
        }),
        ('Alamat', {
            'fields': ('alamat', 'kelurahan', 'kecamatan', 'kota', 'provinsi', 'kode_pos')
        }),
        ('Kontak', {
            'fields': ('no_telepon', 'email', 'website')
        }),
        ('Person In Charge', {
            'fields': ('nama_pic', 'jabatan_pic', 'no_hp_pic'),
            'classes': ('collapse',)
        }),
        ('Catatan', {
            'fields': ('catatan',),
            'classes': ('collapse',)
        }),
    )
    
    def peserta_count(self, obj):
        return obj.peserta_prakerin.count()
    peserta_count.short_description = 'Jumlah Peserta'


@admin.register(Departemen)
class DepartemenAdmin(admin.ModelAdmin):
    list_display = ['nama', 'perusahaan', 'is_active', 'peserta_count']
    list_display_links = ['nama']
    list_filter = ['is_active', 'perusahaan']
    search_fields = ['nama', 'perusahaan__nama']
    ordering = ['perusahaan__nama', 'nama']
    
    def peserta_count(self, obj):
        return obj.peserta_prakerin.count()
    peserta_count.short_description = 'Jumlah Peserta'


@admin.register(Jurusan)
class JurusanAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'singkatan', 'kepala_jurusan', 'peserta_count']
    list_display_links = ['kode', 'nama']
    list_filter = ['kepala_jurusan']
    search_fields = ['kode', 'nama']
    ordering = ['kode']
    
    def peserta_count(self, obj):
        return obj.peserta_prakerin.count()
    peserta_count.short_description = 'Jumlah Peserta'


class ElemenKompetensiInline(admin.TabularInline):
    model = ElemenKompetensi
    extra = 1
    fields = ['kode', 'nama', 'is_active']
    show_change_link = True


@admin.register(KategoriKompetensi)
class KategoriKompetensiAdmin(admin.ModelAdmin):
    list_display = ['nama', 'warna_display', 'urutan', 'elemen_count']
    list_display_links = ['nama']
    search_fields = ['nama']
    ordering = ['urutan', 'nama']
    inlines = [ElemenKompetensiInline]
    
    fieldsets = (
        ('Informasi Kategori', {
            'fields': ('nama', 'deskripsi')
        }),
        ('Tampilan', {
            'fields': ('warna', 'urutan')
        }),
    )
    
    def warna_display(self, obj):
        return f'<span style="color:{obj.warna}; font-weight:bold;">■ {obj.warna}</span>'
    warna_display.short_description = 'Warna'
    warna_display.allow_tags = True
    
    def elemen_count(self, obj):
        return obj.elemen.filter(is_active=True).count()
    elemen_count.short_description = 'Jumlah Elemen Aktif'


@admin.register(ElemenKompetensi)
class ElemenKompetensiAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'kategori', 'jurusan', 'is_active']
    list_display_links = ['kode', 'nama']
    list_filter = ['kategori', 'jurusan', 'is_active']
    search_fields = ['kode', 'nama', 'deskripsi']
    ordering = ['kategori__urutan', 'kode']
    
    fieldsets = (
        ('Informasi Kompetensi', {
            'fields': ('kode', 'nama', 'deskripsi')
        }),
        ('Kategorisasi', {
            'fields': ('kategori', 'jurusan')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(AspekPenilaian)
class AspekPenilaianAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'tipe', 'bobot', 'urutan', 'is_active']
    list_display_links = ['kode', 'nama']
    list_filter = ['tipe', 'is_active']
    search_fields = ['kode', 'nama']
    ordering = ['tipe', 'urutan']
    
    fieldsets = (
        ('Informasi Aspek', {
            'fields': ('kode', 'nama', 'deskripsi')
        }),
        ('Pengaturan', {
            'fields': ('tipe', 'bobot', 'urutan', 'is_active')
        }),
    )


@admin.register(Pengaturan)
class PengaturanAdmin(admin.ModelAdmin):
    list_display = ['kunci', 'nilai_display', 'tipe', 'kategori', 'deskripsi_truncated']
    list_display_links = ['kunci']
    list_filter = ['tipe', 'kategori']
    search_fields = ['kunci', 'nilai', 'deskripsi']
    ordering = ['kategori', 'kunci']
    
    fieldsets = (
        ('Pengaturan', {
            'fields': ('kunci', 'nilai', 'tipe', 'kategori', 'deskripsi')
        }),
    )
    
    def nilai_display(self, obj):
        if len(obj.nilai) > 50:
            return obj.nilai[:50] + '...'
        return obj.nilai
    nilai_display.short_description = 'Nilai'
    
    def deskripsi_truncated(self, obj):
        if obj.deskripsi and len(obj.deskripsi) > 50:
            return obj.deskripsi[:50] + '...'
        return obj.deskripsi
    deskripsi_truncated.short_description = 'Deskripsi'
from django.contrib import admin
from django.utils.html import format_html
from .models import Feedback, Notifikasi


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'dari_display', 'tujuan_display', 'pesan_truncated', 
        'is_read', 'created_at'
    ]
    list_display_links = ['dari_display']
    list_filter = ['is_read', 'dari_user__role', 'created_at']
    search_fields = [
        'dari_user__nama_lengkap', 'pesan', 
        'jurnal__peserta__user__nama_lengkap',
        'peserta__user__nama_lengkap'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['dari_display', 'tujuan_display', 'is_read', 'read_at', 'created_at']
    
    fieldsets = (
        ('Informasi Feedback', {
            'fields': ('dari_display', 'tujuan_display', 'is_read', 'read_at')
        }),
        ('Konten', {
            'fields': ('pesan',)
        }),
    )
    
    def dari_display(self, obj):
        role = obj.dari_user.get_role_display()
        return f"{obj.dari_user.nama_lengkap} ({role})"
    dari_display.short_description = 'Dari'
    
    def tujuan_display(self, obj):
        if obj.jurnal:
            return f"Jurnal Hari {obj.jurnal.hari_ke} - {obj.jurnal.peserta.user.nama_lengkap}"
        elif obj.peserta:
            return f"Umum - {obj.peserta.user.nama_lengkap}"
        return '-'
    tujuan_display.short_description = 'Tujuan'
    
    def pesan_truncated(self, obj):
        if len(obj.pesan) > 80:
            return obj.pesan[:80] + '...'
        return obj.pesan
    pesan_truncated.short_description = 'Pesan'
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        queryset.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{queryset.count()} feedback ditandai sudah dibaca")
    mark_as_read.short_description = 'Tandai Sudah Dibaca'


@admin.register(Notifikasi)
class NotifikasiAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'judul', 'tipe_badge', 'kategori', 'is_read', 'created_at'
    ]
    list_display_links = ['user', 'judul']
    list_filter = ['tipe', 'kategori', 'is_read', 'created_at']
    search_fields = ['user__nama_lengkap', 'judul', 'pesan']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['user', 'judul', 'pesan', 'tipe', 'kategori', 'data_json', 'link', 'is_read', 'read_at', 'created_at']
    
    fieldsets = (
        ('Informasi Notifikasi', {
            'fields': ('user', 'judul', 'tipe', 'kategori', 'is_read', 'read_at', 'created_at')
        }),
        ('Konten', {
            'fields': ('pesan',)
        }),
        ('Lainnya', {
            'fields': ('link', 'data_json'),
            'classes': ('collapse',)
        }),
    )
    
    def tipe_badge(self, obj):
        colors = {
            'info': '#3B82F6',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444',
        }
        color = colors.get(obj.tipe, '#6B7280')
        return format_html(
            '<span style="background-color:{}; color:white; padding:2px 8px; border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_tipe_display()
        )
    tipe_badge.short_description = 'Tipe'
    tipe_badge.allow_tags = True
    
    actions = ['mark_as_read_action', 'delete_old_notifications']
    
    def mark_as_read_action(self, request, queryset):
        from django.utils import timezone
        queryset.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{queryset.count()} notifikasi ditandai sudah dibaca")
    mark_as_read_action.short_description = 'Tandai Sudah Dibaca'
    
    def delete_old_notifications(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        old = queryset.filter(is_read=True, created_at__lt=thirty_days_ago)
        count = old.count()
        old.delete()
        self.message_user(request, f"{count} notifikasi lama yang sudah dibaca dihapus")
    delete_old_notifications.short_description = 'Hapus notifikasi lama (>30 hari, sudah dibaca)'
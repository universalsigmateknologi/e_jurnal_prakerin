from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Role, CustomUser


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'nama', 'deskripsi_truncated', 'user_count']
    list_display_links = ['id', 'nama']
    list_filter = ['nama']
    search_fields = ['nama', 'deskripsi']
    ordering = ['id']
    
    def deskripsi_truncated(self, obj):
        return (obj.deskripsi[:50] + '...') if obj.deskripsi and len(obj.deskripsi) > 50 else obj.deskripsi
    deskripsi_truncated.short_description = 'Deskripsi'
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Jumlah User'
    
    def has_delete_permission(self, request, obj=None):
        # Jangan hapus role yang sedang digunakan
        if obj and obj.users.exists():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'nama_lengkap', 'email', 'role', 
        'is_active', 'is_staff', 'last_login', 'created_at'
    ]
    list_display_links = ['username', 'nama_lengkap']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'nama_lengkap', 'email', 'no_hp']
    ordering = ['-created_at']
    
    # Override total fieldsets untuk menghindari duplikasi 'is_active'
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Informasi Pribadi', {
            'fields': ('nama_lengkap', 'email', 'no_hp', 'foto_profil')
        }),
        ('Role & Akses', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Tanggal Penting', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'nama_lengkap', 'email', 'role')
        }),
    )
    
    readonly_fields = ['last_login', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    filter_horizontal = ['groups', 'user_permissions']
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Saat edit, password read only
            readonly.append('password')
        return readonly
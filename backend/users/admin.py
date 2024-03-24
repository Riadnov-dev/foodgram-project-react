from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserFollow


class UserFollowInline(admin.TabularInline):
    model = UserFollow
    fk_name = 'user_from'
    extra = 1

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "user_to":
            kwargs["queryset"] = self.model.user_to.field.related_model.objects.exclude(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active',)
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('email',)
    list_filter = ('email', 'username', 'is_staff', 'is_active',)
    inlines = [UserFollowInline]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'first_name', 'last_name', 'is_staff', 'is_active')}
        ),
    )

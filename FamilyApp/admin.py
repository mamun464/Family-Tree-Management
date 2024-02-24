from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FamilyMember,Relationship

class FamilyMemberAdmin(UserAdmin):
    model = FamilyMember
    list_display = ['id','full_name', 'email', 'phone_no','date_of_birth' ,'user_profile_img', 'is_alive','is_married','profession','current_address', 'permanent_address','date_of_death','facebook','instagram','linkedin']
    search_fields = ['email', 'phone_no', 'full_name']
    readonly_fields = ['date_of_birth']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_no', 'user_profile_img', 'place_of_birth', 'profession', 'date_of_birth', 'current_address', 'permanent_address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone_no', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

    ordering = ['email']
    filter_horizontal = ()

class RelationshipAdmin(admin.ModelAdmin):
    list_display = ['id','person', 'related_person', 'relationship_type']

admin.site.register(FamilyMember, FamilyMemberAdmin)
admin.site.register(Relationship,RelationshipAdmin)

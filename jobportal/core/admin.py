from django.contrib import admin
from .models import Job, Application
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EducationalQualification







@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Experience', {'fields': ('role', 'experience_years')}),
    )
    list_display = UserAdmin.list_display + ('role', 'experience_years')

admin.site.register(EducationalQualification)




# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
    # fieldsets = UserAdmin.fieldsets + (
        # ('Role & Profile', {'fields': ('role', 'experience_years')}),
    # )
    # list_display = UserAdmin.list_display + ('role', 'education_level', 'result', 'experience_years')

admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'posted_by', 'created_at')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'applied_at')
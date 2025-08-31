from django.contrib import admin
from .models import (
    CustomUser, Role, VerifiedEmail,
    Problem, TestCase,
    Submission, SubmissionTestCaseResult
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_verified', 'is_staff', 'is_superuser')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_verified', 'is_staff', 'is_superuser')}
        ),
    )


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'slug', 'time_limit', 'memory_limit')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TestCaseInline]



class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'status', 'language_name', 'submitted_at', 'time', 'memory')
    list_filter = ('status', 'language_name', 'submitted_at')
    search_fields = ('user__username', 'problem__title', 'language_name')
    readonly_fields = ('submitted_at',)


class SubmissionTestCaseResultAdmin(admin.ModelAdmin):
    list_display = ('submission', 'testcase', 'status', 'time', 'memory')
    search_fields = ('submission__user__username', 'testcase__problem__title')


class VerifiedEmailAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__username', 'user__email')


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('users',)



admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(VerifiedEmail, VerifiedEmailAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(TestCase)  
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionTestCaseResult, SubmissionTestCaseResultAdmin)

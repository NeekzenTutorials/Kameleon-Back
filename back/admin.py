from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    Member,
    Rank,
    Riddle,
    Clue,
    SoloRiddle,
    VersusRiddle,
    VersusRiddleImage,
    HasImage,
    Resolve,
    Clan,
    MemberRiddleStats
)

admin.site.site_header = "Administration de Kameleon"
admin.site.site_title = "Panneau Admin"
admin.site.index_title = "Bienvenue dans le panneau d'administration"

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'last_connection')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('profile_picture', 'bio', 'cv')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    filter_horizontal = ()
    
admin.site.register(User, UserAdmin)
    
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'member_score',
        'member_clan_score',
        'rank_name',
        'image_preview',
        'clan_name',
        'clan_image_preview',
        'is_clan_admin',
        'have_calculatrice'
    )
    search_fields = ('user__username', 'clan__clan_name')
    list_filter = ('member_score', 'clan')
    filter_horizontal = ('achieved_riddles', 'locked_riddles', 'achieved_coop_riddles', 'locked_coop_riddles', 'revealed_clues')
    
    def rank_name(self, obj):
        return obj.rank.rank_name if obj.rank else "No rank"

    def image_preview(self, obj):
        if obj.rank and obj.rank.rank_image:
            return format_html(f'<img src="{obj.rank.rank_image.url}" style="height: 50px;"/>')
        return "No image"
    
    def clan_name(self, obj):
        return obj.clan.clan_name if obj.clan else "No clan"

    def clan_image_preview(self, obj):
        if obj.clan and obj.clan.clan_pci:
            return format_html(f'<img src="{obj.clan.clan_pci.url}" style="height: 50px;"/>')
        return "No image"
    
    rank_name.short_description = 'Rank'
    image_preview.short_description = 'Rank Image'
    clan_name.short_description = 'Clan'
    clan_image_preview.short_description = 'Clan Image'

admin.site.register(Member, MemberAdmin)

@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('rank_name', 'image_preview')
    search_fields = ('rank_name',) 
    list_filter = ('rank_name',)

    def image_preview(self, obj):
        if obj.rank_image:
            return format_html(f'<img src="{obj.rank_image.url}" style="height: 50px;"/>')
        return "No image"
    
    image_preview.short_description = 'Preview'
    
class ClueInline(admin.TabularInline):
    model = Clue
    extra = 1
    fields = ('clue_text',)
    readonly_fields = ()
    show_change_link = True

class SoloRiddleInline(admin.StackedInline):
    model = SoloRiddle
    can_delete = False
    verbose_name_plural = 'Solo Riddle'
    fk_name = 'riddle'
    fields = ('riddle_image',)
    extra = 0

class VersusRiddleInline(admin.StackedInline):
    model = VersusRiddle
    can_delete = False
    verbose_name_plural = 'Versus Riddle'
    fk_name = 'riddle'
    fields = ('versus_nb_step',)
    extra = 0

class VersusRiddleImageInline(admin.TabularInline):
    model = VersusRiddleImage
    extra = 1
    fields = ('image_path', 'image_step',)
    readonly_fields = ()
    show_change_link = True

@admin.register(Riddle)
class RiddleAdmin(admin.ModelAdmin):
    list_display = (
        'riddle_id',
        'riddle_type',
        'riddle_theme',
        'riddle_difficulty',
        'riddle_points',
        'riddle_path',
        'display_dependencies',
        'riddle_mode'
    )
    search_fields = (
        'riddle_type',
        'riddle_variable',
        'riddle_response',
        'riddle_theme',
        'riddle_path'
    )
    list_filter = (
        'riddle_type',
        'riddle_difficulty',
        'riddle_theme'
    )
    inlines = [
        ClueInline,
        SoloRiddleInline,
        VersusRiddleInline,
    ]
    ordering = ('-riddle_points',)
    fields = (
        'riddle_type',
        'riddle_variable',
        'riddle_response',
        'riddle_difficulty',
        'riddle_theme',
        'riddle_points',
        'riddle_path',
        'riddle_dependance' ,
        'riddle_mode'
    )
    
    def display_dependencies(self, obj):
        dependencies = obj.riddle_dependance.all()
        if dependencies:
            return ", ".join([str(riddle) for riddle in dependencies])
        return "Aucune dépendance"
    display_dependencies.short_description = 'Dépendances de l\'énigme'

@admin.register(MemberRiddleStats)
class MemberRiddleStatsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'member',
        'riddle',
        'try_count',
        'errors_count',
        'solve_count',
        'is_solved',
        'first_solved_at',
    )
    search_fields = (
        'member__user__username',
        'riddle__riddle_type',
        'riddle__riddle_theme',
    )
    list_filter = (
        'is_solved',
        'riddle__riddle_theme',
        'riddle__riddle_difficulty',
    )
    ordering = ('-solve_count',)
    readonly_fields = ('first_solved_at',)
    fields = (
        'member',
        'riddle',
        'try_count',
        'errors_count',
        'solve_count',
        'is_solved',
        'first_solved_at',
    )

@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display = (
        'clan_id',
        'clan_name',
        'clan_bio',
        'clan_members_count',
        'clan_members_max_count',
        'clan_elo',
        'created_at',
    )
    search_fields = (
        'clan_name',
        'clan_bio',
    )
    list_filter = (
        'created_at',
        'clan_elo',
    )
    ordering = ('-clan_elo',)
    fields = (
        'clan_name',
        'clan_bio',
        'clan_pci',
        'clan_members_count',
        'clan_members_max_count',
        'clan_elo',
        'created_at',
    )
    readonly_fields = ('created_at', 'clan_members_count', 'clan_elo')

@admin.register(Clue)
class ClueAdmin(admin.ModelAdmin):
    list_display = ('clue_id', 'riddle', 'clue_text')
    search_fields = ('clue_text',)
    list_filter = ('riddle',)
    ordering = ('riddle',)
    
@admin.register(Resolve)
class ResolveAdmin(admin.ModelAdmin):
    list_display = ('resolve_id', 'get_member_username', 'get_riddle_theme', 'time_used', 'attempts', 'is_successful', 'completed_at')
    list_filter = ('is_successful', 'completed_at')

    def get_member_username(self, obj):
        return obj.member.user.username
    get_member_username.short_description = "Member Username"

    def get_riddle_theme(self, obj):
        return obj.riddle.riddle_theme
    get_riddle_theme.short_description = "Riddle Theme"

@admin.register(SoloRiddle)
class SoloRiddleAdmin(admin.ModelAdmin):
    list_display = ('riddle', 'riddle_image')
    search_fields = ('riddle__riddle_type', 'riddle__riddle_theme')
    list_filter = ('riddle__riddle_type', 'riddle__riddle_theme')
    ordering = ('riddle',)

@admin.register(VersusRiddle)
class VersusRiddleAdmin(admin.ModelAdmin):
    list_display = ('riddle', 'versus_nb_step')
    search_fields = ('riddle__riddle_type', 'riddle__riddle_theme')
    list_filter = ('riddle__riddle_type', 'riddle__riddle_theme')
    ordering = ('riddle',)
    inlines = [VersusRiddleImageInline]

@admin.register(VersusRiddleImage)
class VersusRiddleImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'get_riddle_type', 'image_step', 'image_path')
    search_fields = ('riddle__riddle__riddle_type', 'image_path')
    list_filter = ('riddle__riddle__riddle_type', 'image_step')
    ordering = ('riddle', 'image_step')

    def get_riddle_type(self, obj):
        return obj.riddle.riddle.riddle_type
    get_riddle_type.short_description = 'Riddle Type'

@admin.register(HasImage)
class HasImageAdmin(admin.ModelAdmin):
    list_display = ('riddle', 'image')
    search_fields = ('riddle__riddle_type', 'image__image_path')
    list_filter = ('riddle__riddle_type',)
    ordering = ('riddle',)

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Rank,
    Riddle,
    Clue,
    SoloRiddle,
    VersusRiddle,
    VersusRiddleImage,
    HasImage 
)

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
        'riddle_points'
    )
    search_fields = (
        'riddle_type',
        'riddle_variable',
        'riddle_response',
        'riddle_theme'
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

@admin.register(Clue)
class ClueAdmin(admin.ModelAdmin):
    list_display = ('clue_id', 'riddle', 'clue_text')
    search_fields = ('clue_text',)
    list_filter = ('riddle',)
    ordering = ('riddle',)

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

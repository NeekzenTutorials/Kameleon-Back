from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Rank,
    Riddle,
    Clue,
    SoloRiddle,
    VersusRiddle,
    VersusRiddleImage,
)

@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('rank_name', 'rank_image')
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

# Inline pour SoloRiddle associé à une énigme
class SoloRiddleInline(admin.StackedInline):
    model = SoloRiddle
    can_delete = False
    verbose_name_plural = 'Solo Riddle'
    fk_name = 'riddle'
    fields = ('riddle_image',)
    extra = 0

# Inline pour VersusRiddle associé à une énigme
class VersusRiddleInline(admin.StackedInline):
    model = VersusRiddle
    can_delete = False
    verbose_name_plural = 'Versus Riddle'
    fk_name = 'riddle'
    fields = ('versus_nb_step',)
    extra = 0

# Inline pour les images d'un VersusRiddle
class VersusRiddleImageInline(admin.TabularInline):
    model = VersusRiddleImage
    extra = 1
    fields = ('image_path', 'image_step',)
    readonly_fields = ()
    show_change_link = True

# Configuration de l'administration pour Riddle
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

# Configuration de l'administration pour Clue (optionnel si vous souhaitez les gérer séparément)
@admin.register(Clue)
class ClueAdmin(admin.ModelAdmin):
    list_display = ('clue_id', 'riddle', 'clue_text')
    search_fields = ('clue_text',)
    list_filter = ('riddle',)
    ordering = ('riddle',)

# Configuration de l'administration pour SoloRiddle
@admin.register(SoloRiddle)
class SoloRiddleAdmin(admin.ModelAdmin):
    list_display = ('riddle', 'riddle_image')
    search_fields = ('riddle__riddle_type', 'riddle__riddle_theme')
    list_filter = ('riddle__riddle_type', 'riddle__riddle_theme')
    ordering = ('riddle',)
    inlines = [HasImageInline]

# Configuration de l'administration pour VersusRiddle
@admin.register(VersusRiddle)
class VersusRiddleAdmin(admin.ModelAdmin):
    list_display = ('riddle', 'versus_nb_step')
    search_fields = ('riddle__riddle_type', 'riddle__riddle_theme')
    list_filter = ('riddle__riddle_type', 'riddle__riddle_theme')
    ordering = ('riddle',)
    inlines = [VersusRiddleImageInline]

# Configuration de l'administration pour VersusRiddleImage
@admin.register(VersusRiddleImage)
class VersusRiddleImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'riddle', 'image_step', 'image_path')
    search_fields = ('riddle__riddle_type', 'image_path')
    list_filter = ('riddle__riddle_type', 'image_step')
    ordering = ('riddle', 'image_step')
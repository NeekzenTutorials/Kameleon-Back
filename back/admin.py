from django.contrib import admin
from django.utils.html import format_html
from back.models import Rank

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
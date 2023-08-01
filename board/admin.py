from django.contrib import admin
from .models import Board, Comment, Reply
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import format_html

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'user_ip', 'created_at', 'author_id',)
    list_display_links = ('author_id', 'author', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'user_ip', 'created_at', 'author_id')
    list_display_links = ('author_id', 'author', 'content')

def change_category_to_female_idol(modeladmin, request, queryset):
    # This is the custom action function that will be called when the action is selected
    queryset.update(board_name='여자 아이돌')

change_category_to_female_idol.short_description = "Change category to '여자 아이돌'"

@admin.register(Board)
class BoardAdmin(SummernoteModelAdmin):
    summernote_fields = ('contents',)
    list_display = (
        'title',
        'short_contents',
        'has_image',
        'has_video',
        'writer', 
        'board_name',
        'hits',
        'likes_count',
        'write_dttm',
        'update_dttm'
    )
    list_display_links = list_display
    actions = [change_category_to_female_idol]  # Add the custom action to the admin

    def short_contents(self, obj):
        return obj.contents[:30] + '...' if len(obj.contents) > 30 else obj.contents
    short_contents.short_description = 'Contents'

    def has_image(self, obj):
        if obj.contents.find('<img') != -1:
            return format_html('<span style="color: green;">Yes</span>')
        else:
            return 'No'
    has_image.short_description = 'Image'

    def has_video(self, obj):
        if obj.contents.find('<video') != -1 or obj.contents.find('<iframe') != -1:
            return format_html('<span style="color: green;">Yes</span>')
        else:
            return 'No'
    has_video.short_description = 'Video'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'    

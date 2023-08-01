from django.db import models
from django.utils import timezone

# Create your models here.    
class Board(models.Model):
    title = models.CharField(max_length=48, verbose_name='글 제목')
    contents = models.TextField(verbose_name='')
    writer = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='작성자')
    write_dttm = models.DateTimeField(auto_now_add=True, verbose_name='글 작성일')
    board_name = models.CharField(max_length=32, default='여자 아이돌', verbose_name='카타고리')
    update_dttm = models.DateTimeField(auto_now=True, verbose_name='마지막 수정일')
    hits = models.PositiveIntegerField(default=0, verbose_name='조회수')
    likes = models.ManyToManyField('user.User', related_name='liked_boards', blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'board'
        verbose_name = '게시판'
        verbose_name_plural = '게시판'

class Comment(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='board_comments')
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user_comments', default=None)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f'{self.author} - {self.content[:50]}'

    class Meta:
        ordering = ['created_at']

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies_level_1')
    author = models.ForeignKey('user.User', on_delete=models.CASCADE)
    content = models.TextField()
    user_ip = models.GenericIPAddressField(null=True, blank=True)    
    created_at = models.DateTimeField(default=timezone.now)

    # 추가: 답글에 대한 답글 허용
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies_level_2')

    def __str__(self):
        return f'{self.author} - {self.content[:50]}'

    class Meta:
        ordering = ['created_at']    

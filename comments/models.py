# comments/models.py
from django.db import models

class Comment(models.Model):
    user_id = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey('board.Board', on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"{self.user_id}: {self.content[:20]}"
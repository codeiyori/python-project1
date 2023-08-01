from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.CharField(max_length=32, unique=True, verbose_name='아이디')
    user_pw = models.CharField(max_length=128, verbose_name='비밀번호')
    user_name = models.CharField(max_length=16, unique=True, verbose_name='이름')
    user_email = models.EmailField(max_length=128, unique=True, verbose_name='이메일')
    register_date = models.DateTimeField(auto_now_add=True, verbose_name='계정 생성시간')

    def __str__(self):
        return self.user_id
    
    class Meta:
        db_table = 'user'
        verbose_name = '멤버'
        verbose_name_plural = '멤버'
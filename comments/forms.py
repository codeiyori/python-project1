# comments/forms.py
from django import forms

class NewCommentForm(forms.Form):
    user_id = forms.CharField(label='아이디', max_length=100)
    password = forms.CharField(label='비밀번호', max_length=100, widget=forms.PasswordInput)
    content = forms.CharField(label='댓글', widget=forms.TextInput)

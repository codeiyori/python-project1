from django import forms
from django.db import models
from .models import Board, Comment, Reply
from user.models import User
from django.shortcuts import get_object_or_404, redirect
from django_summernote.fields import SummernoteTextField
from django_summernote.widgets import SummernoteWidget

class BoardWriteForm(forms.ModelForm):
    title = forms.CharField(
        label='글 제목',
        widget=forms.TextInput(
            attrs={
                'placeholder': '게시글 제목'
            }),
            required=True,
    )

    contents = SummernoteTextField()

    options = (
        ('움짤', '움짤'),
        ('갤러리', '갤러리'),
    )

    board_name = forms.ChoiceField(
        label='게시판 선택',
        widget=forms.Select(),
        choices=options
    )

    field_order = [
        'title',
        'board_name',
        'contents'
    ]

    class Meta:
        model = Board
        fields = [
            'title',
            'contents',
            'board_name'
        ]
        widgets = {
            'contents' : SummernoteWidget()
        }

    def clean(self):
        cleaned_data = super().clean()

        title = cleaned_data.get('title', '')
        contents = cleaned_data.get('contents', '')
        board_name = cleaned_data.get('board_name', '')

        if title == '':
            self.add_error('title', '글 제목을 입력하세요.')
        elif contents == '':
            self.add_error('contents', '글 내용을 입력하세요.')
        else:
            self.title = title
            self.contents = contents
            self.board_name = board_name

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control form-control-xs'})
        }
        parent = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['autocomplete'] = 'off'  # 자동완성 비활성화

    def reset_content(self):
            self.data = self.data.copy()  # 입력 데이터를 복사하여 수정
            self.data['content'] = ''  # content 필드의 값을 비움
            self.is_bound = False  # 폼이 바인딩되지 않은 상태로 설정하여 리셋된 상태로 처리
            self._errors = {}  # 에러 메시지를 비움

# Reply form for adding replies to comments
class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']

class LikeForm(forms.Form):
    pass
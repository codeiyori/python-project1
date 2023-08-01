# comments/views.py
from django.shortcuts import redirect, render, get_object_or_404
from board.models import Board  # Board 모델 import
from .forms import NewCommentForm
from .models import Comment

def comment_create(request, pk):
    board = Board.objects.get(pk=pk)  # 해당 게시물(Board) 가져오기

    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            content = form.cleaned_data['content']

            # Comment 모델에 댓글 저장하기
            comment = Comment.objects.create(user_id=user_id, password=password, content=content, board=board)

            # 댓글 저장 후 리다이렉트
            return redirect('board:board_detail', pk=pk)

    else:
        form = NewCommentForm()
    context = {'form': form}
    return render(request, 'comments/comment_create.html', context)


def test_comment_form(request):
    form = NewCommentForm()
    return render(request, 'comments/comment_create.html', {'form': form})

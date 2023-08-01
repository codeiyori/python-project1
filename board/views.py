from django.shortcuts import render, redirect, get_object_or_404
from .forms import BoardWriteForm, CommentForm, ReplyForm, LikeForm
from user.models import User
from django.urls import reverse
from user.decorators import login_required
from datetime import date, datetime, timedelta
from .models import Board, Comment, Reply
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count

def get_boards(search_query):
    if search_query:
        return Board.objects.filter(Q(title__icontains=search_query))
    return Board.objects.all()

def get_page_range(current_page, total_pages):
    if current_page <= 8:
        return range(1, min(total_pages + 1, 9))
    return range((current_page - 1) // 8 * 8 + 1, min((current_page - 1) // 8 * 8 + 9, total_pages + 1))

def get_total_comments(board):
    return Comment.objects.filter(board=board).count()

def increment_board_hits(board):
    board.hits += 1
    board.save()

def prepare_comment_data(comments):
    for comment in comments:
        comment.display_time = comment.created_at.time() if comment.created_at.date() == timezone.now().date() else comment.created_at

def calculate_total_comments_for_boards(page_obj):
    board_ids = [board.pk for board in page_obj]
    total_comments_for_boards = (
        Comment.objects.filter(board__in=board_ids)
        .values('board')
        .annotate(total_comments=Count('board'))
    )
    total_comments_dict = {item['board']: item['total_comments'] for item in total_comments_for_boards}
    for board in page_obj:
        board.total_comments = total_comments_dict.get(board.pk, 0)

@login_required
def comment_delete(request, pk):
    # Get the login session
    login_session = request.session.get('login_session', '')
    # Find the comment by primary key (pk)
    comment = get_object_or_404(Comment, pk=pk)
    # Check if the logged-in user is the author of the comment
    if login_session == comment.author.user_id:
        # Delete the comment
        comment.delete()
    # Redirect back to the board detail page
    return redirect('board:board_detail', pk=comment.board.pk)

@login_required
def reply_delete(request, pk):
    # Get the login session
    login_session = request.session.get('login_session', '')
    # Find the reply by primary key (pk)
    reply = get_object_or_404(Reply, pk=pk)
    # Check if the logged-in user is the author of the reply
    if login_session == reply.author.user_id:
        # Delete the reply
        reply.delete()
    # Redirect back to the board detail page
    return redirect('board:board_detail', pk=reply.comment.board.pk)

@login_required
def add_reply(request, comment_id):
    login_session = request.session.get('login_session', '')
    context = {'login_session': login_session}
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            author = User.objects.get(user_id=login_session)
            content = form.cleaned_data['content']
            # IP 주소 가져오기
            user_ip = request.META.get('REMOTE_ADDR')
            reply = Reply(
                comment=comment,  # Assign the comment to the reply here
                author=author,
                content=content,
                user_ip=user_ip
            )
            reply.save()
            # Instead of resetting the form, create a new instance of the form
            form = ReplyForm()
            return redirect('board:board_detail', pk=comment.board.id)
    else:
        form = ReplyForm()

    return render(request, 'add_reply.html', {'form': form, 'comment': comment}, context)

@login_required
def comment_delete(request, pk):
    # Get the login session
    login_session = request.session.get('login_session', '')
    # Find the comment by primary key (pk)
    comment = get_object_or_404(Comment, pk=pk)
    # Check if the logged-in user is the author of the comment
    if login_session == comment.author.user_id:
        # Delete the comment
        comment.delete()
    # Redirect back to the board detail page
    return redirect('board:board_detail', pk=comment.board.pk)

@login_required
def like_board(request, pk):
    login_session = request.session.get('login_session', '')
    context = {'login_session': login_session}
    
    board = get_object_or_404(Board, id=pk)
    context['board'] = board

    # 기존 페이지 번호와 검색 쿼리 파라미터 가져오기
    page_number = request.GET.get('page', '')
    search_query = request.GET.get('q', '')

    # Handle the like functionality when the form is submitted
    if request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            author = User.objects.get(user_id=login_session)
            
            # 이미 좋아요를 눌렀을 경우 좋아요 취소
            if author in board.likes.all():
                board.likes.remove(author)
            # 아니면 좋아요 추가
            else:
                board.likes.add(author)

            # 리다이렉트할 URL 생성
            redirect_url = reverse('board:board_detail', kwargs={'pk': pk})

            # 기존 페이지 번호가 있으면 해당 페이지 번호도 추가
            if page_number:
                redirect_url += f"?page={page_number}"

            # 검색 쿼리 파라미터가 있으면 해당 파라미터도 추가
            if search_query:
                redirect_url += f"&q={search_query}"

            # 좋아요 처리 후 해당 URL로 리다이렉트
            return redirect(redirect_url)

    # Render the board detail template with likes
    return render(request, 'board_detail_likes.html', context)



def board_detail(request, pk):
    # Create a context dictionary to store data to be passed to the template
    login_session = request.session.get('login_session', '')
    context = {'login_session': login_session}

    # Check if the user is logged in
    if not login_session:
        # If the user is not logged in, set search_query to an empty string
        search_query = ''
    else:
        # If the user is logged in, get the search query from the request's GET parameters
        search_query = request.GET.get('q', '')
        # If logged in, add the current_user information to the context
        try:
            current_user = User.objects.get(user_id=login_session)
            context['current_user'] = current_user
        except User.DoesNotExist:
            pass
        
        user_ip = request.META.get('REMOTE_ADDR')
        context['user_ip'] = user_ip
               
    boards = get_boards(search_query)

    # Paginate the boards with 10 boards per page
    paginator = Paginator(boards.order_by('-id'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_pages = paginator.num_pages

    context['boards'] = boards
    context['page_obj'] = page_obj
    context['page_range'] = get_page_range(page_obj.number, total_pages)
    context['total_boards'] = paginator.count
    context['search_query'] = search_query

    board = get_object_or_404(Board, id=pk)
    context['board'] = board

    # 조회수 기능
    board.hits += 1
    board.save()

    context['selected_board_pk'] = board.pk

    # 글쓴이인지 확인
    if board.writer.user_id == login_session:
        context['writer'] = True
    else:
        context['writer'] = False

    # 댓글 기능 추가
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            author = User.objects.get(user_id=login_session)
            content = form.cleaned_data['content']
            # IP 주소 가져오기
            user_ip = request.META.get('REMOTE_ADDR')
            comment = Comment(
                board=board,
                author=author,
                content=content,
                user_ip=user_ip
            )
            comment.save()
            form.reset_content()  # 입력 필드 리셋
            # POST 요청 처리 후 리다이렉트
            redirect_url = reverse('board:board_detail', kwargs={'pk': pk})
            query_params = request.GET.urlencode()
            if query_params:
                redirect_url += f"?{query_params}"
            return redirect(redirect_url)
    else:
        form = CommentForm()

    comments = Comment.objects.filter(board=board)
    for comment in comments:
        if comment.created_at.date() == timezone.now().date():
            comment.display_time = comment.created_at.time()
        else:
            comment.display_time = comment.created_at

    total_comments = comments.count()  # 전체 댓글 수 계산
    context['comments'] = comments
    context['form'] = form
    context['total_comments'] = total_comments  # 전체 댓글 수 전달

    # Calculate the total comments for each board and update the context
    board_ids = [board.pk for board in page_obj]  # Get a list of board IDs on the current page
    total_comments_for_boards = (
        Comment.objects.filter(board__in=board_ids)
        .values('board')
        .annotate(total_comments=Count('board'))
    )

    # Create a dictionary mapping board IDs to their total comments count
    total_comments_dict = {item['board']: item['total_comments'] for item in total_comments_for_boards}

    # Update the context with the total comments count for each board
    for board in page_obj:
        board.total_comments = total_comments_dict.get(board.pk, 0)

    return render(request, 'board/board_detail.html', context)


def board_list(request):
    # Get the login session from the request
    login_session = request.session.get('login_session', '')
    context = {'login_session': login_session}

    # Check if the user is logged in
    if not login_session:
        # If the user is not logged in, set search_query to an empty string
        search_query = ''
    else:
        # If the user is logged in, get the search query from the request's GET parameters
        search_query = request.GET.get('q', '')

    boards = get_boards(search_query)

    # Paginate the boards with 10 boards per page
    paginator = Paginator(boards.order_by('-id'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_pages = paginator.num_pages

    context['boards'] = boards
    context['page_obj'] = page_obj
    context['page_range'] = get_page_range(page_obj.number, total_pages)
    context['total_boards'] = paginator.count
    context['search_query'] = search_query

    # Calculate the total comments for each board and update the context
    board_ids = [board.pk for board in page_obj]  # Get a list of board IDs on the current page
    total_comments_for_boards = (
        Comment.objects.filter(board__in=board_ids)
        .values('board')
        .annotate(total_comments=Count('board'))
    )

    # Create a dictionary mapping board IDs to their total comments count
    total_comments_dict = {item['board']: item['total_comments'] for item in total_comments_for_boards}

    # Update the context with the total comments count for each board
    for board in page_obj:
        board.total_comments = total_comments_dict.get(board.pk, 0)

    # Render the template with the context data
    return render(request, 'board/board_list.html', context)

    # #조회수 기능(쿠키이용)
    # expire_date, now = datetime.now(), datetime.now()
    # expire_date += timedelta(days=1)
    # expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
    # expire_date -= now
    # max_age = expire_date.total_seconds()
    # cookie_value = request.COOKIES.get('hitboard', '_')
    # if f'_{pk}_' not in cookie_value:
    #     cookie_value += f'{pk}_'
    #     response.set_cookie('hitboard', value=cookie_value, max_age=max_age, httponly=True)
    #     board.hits += 1
    #     board.save()
    # return response

@login_required
def board_write(request):
    login_session = request.session.get('login_session', '')
    context = { 'login_session': login_session}

    if request.method == 'GET':
        write_form = BoardWriteForm()
        context['forms'] = write_form
        return render(request, 'board/board_write.html', context)
    
    elif request.method == 'POST':
        write_form = BoardWriteForm(request.POST)

        if write_form.is_valid():
            write = User.objects.get(user_id=login_session)
            board = Board(
                title=write_form.cleaned_data['title'],  # Use cleaned_data to access form fields
                contents=write_form.contents,
                writer=write,
                board_name=write_form.board_name
            )
            board.save()
            # Redirect to the detail page of the newly created board
            return redirect('board:board_detail', pk=board.pk)

        else:
            context['forms'] = write_form
            if write_form.errors:
                for value in write_form.errors.values():
                    context['error'] = value
            return render(request, 'board/board_write.html', context)
     
@login_required
def board_modify(request, pk):
    login_session = request.session.get('login_session', '')
    context = { 'login_session': login_session}

    board = get_object_or_404(Board, id=pk)
    context['board'] = board

    if board.writer.user_id != login_session:
        return redirect(f'/board/detail/{pk}/')

    if request.method == 'GET':
        write_form = BoardWriteForm(instance=board)
        context['forms'] = write_form
        return render(request, 'board/board_write.html', context)
    
    elif request.method == 'POST':
        write_form = BoardWriteForm(request.POST)

        if write_form.is_valid():
            board.title = write_form.cleaned_data['title']
            board.contents = write_form.cleaned_data['contents']
            board.board_name = write_form.cleaned_data['board_name']
            board.save()
            
            # Preserve the existing query parameters in the redirect URL
            redirect_url = reverse('board:board_detail', kwargs={'pk': pk})
            query_params = request.GET.urlencode()
            if query_params:
                redirect_url += f"?{query_params}"

            return redirect(redirect_url)
        else:
            context['forms'] = write_form
            if write_form.errors:
                for value in write_form.errors.values():
                    context['error'] = value
            return render(request, 'board/board_modify.html', context)
        
@login_required
def board_delete(request, pk):
    login_session = request.session.get('login_session', '')
    board = get_object_or_404(Board, id=pk)

    if board.writer.user_id == login_session:
        board.delete()
        return redirect('/board/')
    else:
        return redirect(f'/board/detail/{pk}/')


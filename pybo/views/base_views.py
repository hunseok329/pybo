from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count

from ..models import Question, Category, QuestionCount

def index(request, category_name='qna'):
    """
    pybo 목록 출력
    """
    # 입력 인자
    page = request.GET.get('page', '1')     # 페이지
    kw = request.GET.get('kw', '')          # 검색어
    so = request.GET.get('so', 'recent')    # 정렬기준

    # 사이드바
    category_list = Category.objects.all()
    category = get_object_or_404(Category, name=category_name)

    # 정렬
    if so == 'recommend':
        question_list = Question.objects.filter(category=category).annotate(
            num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = Question.objects.filter(category=category).annotate(
            num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    else:
        question_list = Question.objects.filter(category=category).order_by('-create_date')

    # 조회
    # question_list = Question.objects.order_by('-create_date')
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(answer__author__username__icontains=kw)
        ).distinct()


    # 페이징 처리
    paginator = Paginator(question_list, 10)
    page_obj = paginator.get_page(page)

    context = { 'question_list': page_obj, 'page': page, 'kw': kw, 'so': so, 'category_list': category_list, 'category': category}
    return render(request, 'pybo/question_list.html', context)

def detail(request, question_id):
    """
    pybo 내용 출력
    """
    # 입력 인자
    page = request.GET.get('page', '1')     # 페이지
    so = request.GET.get('so', 'recent')    # 정렬기준

    # 조회
    question = get_object_or_404(Question, pk=question_id)

    #조회수
    ip = get_client_ip(request)
    cnt = QuestionCount.objects.filter(ip=ip, question=question).count()
    if cnt == 0:
        qc = QuestionCount(ip=ip, question=question)
        qc.save()
        if question.view_count:
            question.view_count += 1
        else:
            question.view_count = 1
        question.save()


    # 정렬
    if so == 'popular':
        answer_list = question.answer_set.all().annotate(
            num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    else:
        answer_list = question.answer_set.all().order_by('-create_date')

    paginator = Paginator(answer_list, 10)
    answer_obj = paginator.get_page(page)

    context = {'question': question, 'answer_list': answer_obj, 'page': page, 'so': so,}
    return render(request, 'pybo/question_detail.html', context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
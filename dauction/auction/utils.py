from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def pagination(request, list, num):
    paginator = Paginator(list, num)
    page = request.GET.get('page')
    try:
        list = paginator.page(page)
    except PageNotAnInteger:
        list = paginator.page(1)
    except EmptyPage:
        list = paginator.page(1)
    return list
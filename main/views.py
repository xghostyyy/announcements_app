from django.shortcuts import render, get_list_or_404, redirect
from .models import Announcement, User, Image, Status
from django.http import JsonResponse

def trade_list(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Неправильный метод'}, status=405)
    try:
        open_status = Status.objects.get(pk=1)
    except Status.DoesNotExist:
        return JsonResponse({'error': 'Статус "Открыто" не найден'}, status=500)
    announcement = Announcement.objects.filter(status=open_status).order_by('-created_at')

    data = []
    for ann in announcement:
        data.append({
            'id': ann.id,
            'title': ann.title,
            'created_at': ann.created_at.isoformat(),
        })
    return JsonResponse(data, safe=False, status=200)
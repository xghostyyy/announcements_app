from .models import Announcement, User, Image, Status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def announcement_list(request):
    if request.method == 'GET':
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
        
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Пользователь не авторизован'}, status=401)
        
        try:
            body = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный JSON'}, status=400)
        
        title = body.get('title', '').strip()
        text = body.get('text', '').strip()
        status_id = body.get('status')
        
        if not title or not text:
            return JsonResponse({'error': 'Заголовок и описание обязательные поля!'}, status=400)
        elif len(title) > 50:
            return JsonResponse({'error': f'Максимальная длина заголовка 50 символов! (У вас {len(title)} символов)'}, status=400)
        
        try:
            status_obj = Status.objects.get(pk=status_id)
        except (Status.DoesNotExist, TypeError, ValueError):
            return JsonResponse({'error': 'Статус не найден'}, status=400)
        
        announcement = Announcement(
            title=title,
            text=text,
            status=status_obj,
        )
        announcement.author_id = request.user.pk 
        announcement.save()
        
        serialized = {
            'id': announcement.id,
            'status': announcement.status_id, 
            'title': announcement.title,
            'text': announcement.text,
            'author': announcement.author.email,
            'created_at': announcement.created_at.isoformat(),
            'update_at': announcement.update_at.isoformat(),
            'images_urls': [],
        }
        return JsonResponse(serialized, status=201)
    else:
        return JsonResponse({'error': 'Метод запрещен'}, status=405)
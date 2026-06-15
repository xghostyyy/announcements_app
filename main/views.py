from .models import Announcement, User, Image, Status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from functools import wraps
import json

def auth_message(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "Авторизация успешна!")
            
            token, created = Token.objects.get_or_create(user=request.user)
            
            request.user_token = token.key
        else:
            messages.error(request, "Ошибка авторизации")
            request.user_token = None
            
        return func(request, *args, **kwargs)
    return wrapper

@auth_message
def index(request):  
    context = {
        'user_token': getattr(request, 'user_token', None)
    } 
    return render(request, 'main/index.html', context )

@auth_message
@csrf_exempt
def announcement_list(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Пользователь не авторизован'}, status=401)

        try:
            open_status = Status.objects.get(pk=1)
        except Status.DoesNotExist:
            return JsonResponse({'error': 'Статус "Открыто" не найден'}, status=500)
        
        author_id = request.GET.get('author_id')
        order_by = request.GET.get('order_by')

        allowed_sort = ('created_at', 'update_at', 'title', 'id')

        if order_by:
            sort = order_by.lstrip('-')
            if sort not in allowed_sort:
                return JsonResponse(
                    {'error': f'Недопустимое поле для сортировки (Допустимы: {', '.join(allowed_sort)})'},
                    status=400
                )

        if author_id:
            announcement = Announcement.objects.filter(status=open_status, author_id=author_id).prefetch_related('images').order_by('-created_at')
        if order_by:
            announcement = Announcement.objects.filter(status=open_status).prefetch_related('images').order_by(order_by)
        if not author_id and not order_by:
            announcement = Announcement.objects.filter(status=open_status).prefetch_related('images').order_by('-created_at')

        data = []
        for ann in announcement:
            image_urls = []
            for image in ann.images.all():
                image_url = request.build_absolute_uri(image.image.url)
                image_urls.append(image_url)
            
            data.append({
                'id': ann.id,
                'title': ann.title,
                'created_at': ann.created_at.isoformat(),
                'images_urls': image_urls,
                'author_id': ann.author_id,
        })
        return JsonResponse(data, safe=False, status=200)
        
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Пользователь не авторизован'}, status=401)
        
        try:
            body = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный JSON'}, status=400)
        
        if isinstance(body, list):
            if len(body) > 0:
                body = body[0]
            else:
                return JsonResponse({'error': 'Пустой массив'}, status=400)
        elif not isinstance(body, dict):
            return JsonResponse({'error': 'Некорректный формат данных'}, status=400)

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
        
        return JsonResponse({
            'id': announcement.id,
            'status': announcement.status_id, 
            'title': announcement.title,
            'text': announcement.text,
            'author': announcement.author.email,
            'created_at': announcement.created_at.isoformat(),
            'update_at': announcement.update_at.isoformat(),
            'images_urls': [],
        }, status=201)
    else:
        return JsonResponse({'error': 'Метод запрещен'}, status=405)

@auth_message
@csrf_exempt 
def announcement_data(request, id):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Пользователь не авторизован'}, status=401)

        announcement = get_object_or_404(Announcement, pk=id)

        image_urls = []
        for image in announcement.images.all():
            image_url = request.build_absolute_uri(image.image.url)
            image_urls.append(image_url)

        return JsonResponse({
            'id': announcement.id,
            'author': f'Эл.Почта: {announcement.author.email} Телефон: {announcement.author.phone}',
            'title': announcement.title,
            'text': announcement.text,
            'status': announcement.status.name,
            'created_at': announcement.created_at,
            'update_at': announcement.update_at,
            'images_urls': image_urls,
        }, safe=False, status=200)
    
    elif request.method == 'PUT':
        try:
            body = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный JSON'}, status=400)
        
        if isinstance(body, list):
            if len(body) > 0:
                body = body[0]
            else:
                return JsonResponse({'error': 'Пустой массив'}, status=400)
        elif not isinstance(body, dict):
            return JsonResponse({'error': 'Некорректный формат данных'}, status=400)

        title = body.get('title', '').strip()
        text = body.get('text', '').strip()
        status_id = body.get('status')

        announcement = get_object_or_404(Announcement, pk=id)

    
        if request.user != announcement.author or not request.user.is_admin:
            return JsonResponse({'error': 'Нет прав для редактирования'}, status=403)

        try:
            status_obj = Status.objects.get(pk=status_id)
        except (Status.DoesNotExist, TypeError, ValueError):
            return JsonResponse({'error': 'Статус не найден'}, status=400)
        
        if title:
            if len(title) > 50:
                return JsonResponse({'error': f'Максимальная длина заголовка 50 символов! (У вас {len(title)} символов)'}, status=400)
            announcement.title = title
        if text:
            announcement.text = text
        if status_id:
            announcement.status = status_obj

        announcement.save()

        return JsonResponse({
            'id': announcement.id,
            'status': announcement.status_id, 
            'title': announcement.title,
            'text': announcement.text,
            'author': announcement.author.email,
            'created_at': announcement.created_at.isoformat(),
            'update_at': announcement.update_at.isoformat(),
        }, status=201)
    else:
        return JsonResponse({'error': 'Метод запрещен!'}, status=405)

@auth_message
@csrf_exempt 
def add_image(request, id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
                return JsonResponse({'error': 'Пользователь не авторизован'}, status=401)
        
        image_file = request.FILES.get('image')
        if not image_file:
                return JsonResponse({'error': 'Изображение не передано'}, status=400)
        user = User.objects.get(pk=request.user.pk)
        announcement = get_object_or_404(Announcement, pk=id)
        announcement_image = Image.objects.create(announcement=announcement, author=user,
                                                image=image_file)
        announcement_image.save()
        
        return JsonResponse({
            'id': announcement_image.pk,
            'announcement_title':  announcement_image.announcement.title,
            'announcement': announcement_image.announcement.pk,
            'image': announcement_image.image.url,
        }, status=200)

@auth_message
@csrf_exempt 
def delete_image(request, id, image_id):
    if request.method == 'DELETE':
        if not request.user.is_authenticated:
                return JsonResponse({'error': 'Пользователь не авторизован'}, status=401)
        announcement = get_object_or_404(Announcement, pk=id)
        image = get_object_or_404(Image, pk=image_id, announcement=announcement)
        
        image.image.delete(save=False)
        image.delete()

        return JsonResponse({
            'Изображение удалено':'',
            'id': announcement.pk,
            'announcement_title': announcement.title,
        }, status=200)
    
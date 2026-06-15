from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from main.models import Announcement, Status, Image
from .serializers import AnnouncementSerializer, AnnouncementCreateSerializer, ImageCreateSerializer

class AnnouncementList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            open_status = Status.objects.get(pk=1)
        except Status.DoesNotExist:
            return Response(
                {'error': 'Статус "Открыто" не найден'}
            )
        author_id = request.query_params.get('author_id')
        order_by = request.query_params.get('order_by')

        if author_id:
            queryset = Announcement.objects.filter(
                status=open_status,
                author_id=author_id,
            ).prefetch_related('images').order_by('-created_at')
        elif order_by:
            queryset = Announcement.objects.filter(
                status=open_status,
            ).prefetch_related('images').order_by(order_by)
        else:
            queryset = Announcement.objects.filter(
                status=open_status,
            ).prefetch_related('images').order_by('-created_at')
        
        data = []
        for ann in queryset:
            image_urls = []
            for image in ann.images.all():
                image_url = request.build_absolute_uri(image.image.url)
                image_urls.append(image_url)

            serializer = AnnouncementSerializer(ann)

            item_data = serializer.data
            item_data['images_urls'] = image_urls
            item_data['author_id'] = ann.author_id
            data.append(item_data)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        
        body = request.data

        if isinstance(body, list):
            if len(body) > 0:
                body = body[0]
            else:
                return Response(
                    {'error': 'Пустой массив'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif not isinstance(body, dict):
            return Response(
                {'error': 'Некорректный формат данных'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AnnouncementCreateSerializer(data=body, context={'request': request})

        if not serializer.is_valid():
            errors = serializer.errors
            if 'title' in errors:
                error_msg = errors['title'][0]
            elif 'text' in errors:
                error_msg = errors['text'][0]
            elif 'status_id' in errors:
                error_msg = errors['status_id'][0]
            elif 'non_field_errors' in errors:
                error_msg = errors['non_field_errors'][0]
            else:
                error_msg = 'Ошибка валидации'
            
            return Response(
                {'error': error_msg}, status=status.HTTP_400_BAD_REQUEST
            )
        
        announcement = serializer.save()

        return Response(
            {
                'id': announcement.id,
                'status': announcement.status_id,
                'title': announcement.title,
                'text': announcement.text,
                'author': announcement.author.email,
                'created_at': announcement.created_at.isoformat(),
                'update_at': announcement.update_at.isoformat(),
                'images_urls': [],
            },
            status=status.HTTP_201_CREATED
        )

class AnnouncementData(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        announcement = get_object_or_404(Announcement, pk=id)

        images_urls = []
        for image in announcement.images.all():
            image_url = request.build_absolute_uri(image.image.url)
            images_urls.append(image_url)

        serializer = AnnouncementSerializer(announcement)

        item_data = serializer.data
        item_data['images_urls'] = images_urls
        item_data['author_id'] = announcement.author_id

        return Response(item_data, status=status.HTTP_200_OK)

    def put(self, request, id):
        announcement = get_object_or_404(Announcement, pk=id)

        if request.user != announcement.author and not request.user.is_superuser:
            return Response(
                {'error': 'У вас нет прав для редактирования'},
                status=status.HTTP_403_FORBIDDEN
            )

        body = request.data

        if isinstance(body, list):
            if len(body) > 0:
                body = body[0]
            else:
                return Response(
                    {'error': 'Пустой массив'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif not isinstance(body, dict):
            return Response(
                {'error': 'Некорректный формат данных'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AnnouncementCreateSerializer(
            announcement,
            data=body,
            context={'request': request},
            partial=True
        )

        if not serializer.is_valid():
            errors = serializer.errors
            if 'title' in errors:
                error_msg = errors['title'][0]
            elif 'text' in errors:
                error_msg = errors['text'][0]
            elif 'status_id' in errors:
                error_msg = errors['status_id'][0]
            elif 'non_field_errors' in errors:
                error_msg = errors['non_field_errors'][0]
            else:
                error_msg = 'Ошибка валидации'

            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        announcement = serializer.save()

        return Response(
            {
                'id': announcement.id,
                'status': announcement.status_id,
                'title': announcement.title,
                'text': announcement.text,
                'author': announcement.author.email,
                'created_at': announcement.created_at.isoformat(),
                'update_at': announcement.update_at.isoformat(),
            },
            status=status.HTTP_200_OK
        )
    
class AddImage(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        announcement = get_object_or_404(Announcement, pk=id)

        if request.user != announcement.author and not request.user.is_superuser:
            return Response(
                {'error': 'У вас нет прав для редактирования'},
                status=status.HTTP_403_FORBIDDEN
            )

        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {'error': 'Изображение не прикреплено'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {'image': image_file, 'announcement_id': announcement.pk}
        
        serializer = ImageCreateSerializer(data=data, 
                                           context={'request': request})
        
        if not serializer.is_valid():
            error = serializer.errors
            return Response({'error': error}, 
                            status=status.HTTP_400_BAD_REQUEST)
        image = serializer.save()

        return Response({
            'id': image.pk,
            'announcement_id': announcement.pk,
            'announcement_title': announcement.title,
            'image': image.image.url,
        }, status=status.HTTP_201_CREATED)

        

class DeleteImage(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, id, image_id):

        announcement = get_object_or_404(Announcement, pk=id)
        select_image = get_object_or_404(Image, pk=image_id)

        if request.user != announcement.author and not request.user.is_superuser:
            return Response(
                {'error': 'У вас нет прав для редактирования'},
                status=status.HTTP_403_FORBIDDEN
            )

        select_image.image.delete(save=False)
        select_image.delete()

        return Response({
            'Изображение удалено': '',
            'announcement_id': announcement.pk,
            'announcement_title': announcement.title
        }, status=status.HTTP_200_OK)

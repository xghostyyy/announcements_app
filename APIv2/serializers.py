from rest_framework import serializers
from main.models import User, Status, Announcement, Image

class UserSerielizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'phone', 'is_active',)
        read_only_fields = ('id', 'is_active', 'is_admin',)

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('name',)

class AnnouncementSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.name', read_only=True)
    class Meta:
        model = Announcement
        fields = ('title', 'text', 'status', 
                  'author', 'created_at',)
        
class AnnouncementCreateSerializer(serializers.ModelSerializer):
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), 
        write_only=True
    )
    
    class Meta:
        model = Announcement
        fields = ('title', 'text', 'status_id')
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Заголовок обязателен!")
        if len(value) > 50:
            raise serializers.ValidationError(
                f"Максимальная длина заголовка 50 символов (У вас {len(value)} символов)"
            )      
        return value.strip()

    def validate_text(self, value):
        if not value:
            raise serializers.ValidationError("Описание обязательное поле!")
        return value.strip()
    
    def validate(self, data):
        if not data.get('title') and not data.get('text'):
            raise serializers.ValidationError(
                "Заголовок и описание обязательные поля!"
            )
        return data
    
    def create(self, validated_data):
        status_obj = validated_data.pop('status_id')  
        request = self.context.get('request')
        
        announcement = Announcement.objects.create(
            title=validated_data['title'],
            text=validated_data['text'],
            status=status_obj,
            author_id=request.user.pk
        )
        
        return announcement

class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    author = serializers.CharField(source='author.email', read_only=True)
    class Meta:
        model = Image
        fields = ('image_url', 'announcement', 'author', 
                  'created_at', 'update_at',)
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    
class ImageCreateSerializer(serializers.ModelSerializer):
    announcement_id = serializers.PrimaryKeyRelatedField(
        queryset=Announcement.objects.all(),
        write_only=True,
        source='announcement'
    )
    
    class Meta:
        model = Image
        fields = ('announcement_id', 'image')
    
    def create(self, validated_data):
        request = self.context.get('request')
        return Image.objects.create(
            announcement=validated_data['announcement'],
            image=validated_data['image'],
            author=request.user
        )
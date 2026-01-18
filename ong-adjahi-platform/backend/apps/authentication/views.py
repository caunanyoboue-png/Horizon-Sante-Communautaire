"""
Views for Authentication API
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import LoginHistory
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    LoginHistorySerializer
)
from .permissions import IsAdminOrReadOnly

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with user data"""
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema_view(
    list=extend_schema(description="Liste de tous les utilisateurs"),
    retrieve=extend_schema(description="Détails d'un utilisateur"),
    create=extend_schema(description="Créer un nouvel utilisateur"),
    update=extend_schema(description="Modifier un utilisateur"),
    destroy=extend_schema(description="Supprimer un utilisateur"),
)
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User CRUD operations"""
    
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['role', 'location', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['created_at', 'last_name', 'role']
    
    def get_permissions(self):
        """Allow registration without authentication"""
        if self.action == 'register':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    @extend_schema(
        description="Enregistrer un nouvel utilisateur",
        request=RegisterSerializer,
        responses={201: UserSerializer}
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        """User registration endpoint"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        description="Obtenir le profil de l'utilisateur connecté",
        responses={200: UserProfileSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        description="Modifier le profil de l'utilisateur connecté",
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(
        description="Changer le mot de passe",
        request=ChangePasswordSerializer,
        responses={200: {'description': 'Mot de passe changé avec succès'}}
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change password for current user"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Update password
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Mot de passe changé avec succès.'
        })
    
    @extend_schema(
        description="Historique des connexions de l'utilisateur",
        responses={200: LoginHistorySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def login_history(self, request):
        """Get login history for current user"""
        history = LoginHistory.objects.filter(user=request.user).order_by('-created_at')[:20]
        serializer = LoginHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Statistiques des utilisateurs par rôle",
        responses={200: {
            'type': 'object',
            'properties': {
                'total': {'type': 'integer'},
                'by_role': {'type': 'object'},
                'by_location': {'type': 'object'},
                'active': {'type': 'integer'}
            }
        }}
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request):
        """Get user statistics (admin only)"""
        from django.db.models import Count
        
        stats = {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'by_role': dict(User.objects.values('role').annotate(count=Count('role')).values_list('role', 'count')),
            'by_location': dict(User.objects.values('location').annotate(count=Count('location')).values_list('location', 'count')),
        }
        
        return Response(stats)

from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from .serializers import UserSerializer, MovieSerializer, RatingSerializer
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from movierater.api.models import Movie, Rating
from rest_framework.decorators import list_route

class UserViewSet(viewsets.ModelViewSet):
   
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class MovieViewSet(viewsets.ModelViewSet):
   
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
class RatingViewSet(viewsets.ModelViewSet):
   
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['POST'])
    def rate_movie(self, request):
        if 'movie' in request.data and 'user' in request.data and 'stars' in request.data:
            movie = Movie.objects.get(id=request.data['movie'])
            user = User.objects.get(id=request.data['user'])
            stars = request.data['stars']

            try:
                my_rating=Rating.objects.get(movie=movie.id, user=user.id)
                my_rating.stars=stars
                my_rating.save()
                serializer=MovieSerializer(movie, many=False)
                response={'message':'Rating updated','result': serializer.data }
                return Response(response, status=status.HTTP_200_OK)
            except:
                Rating.objects.create(movie=movie, user=user, stars=stars)
                serializer=MovieSerializer(movie, many=False)
                response={'message':'Rating created','result': serializer.data }
                return Response(response, status=status.HTTP_200_OK)


        else:
            response = {'message':'You need to pass all params'}
            return Response(response,status=status.HTTP_400_BAD_REQUEST)



class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token':token.key, 'user': serializer.data})
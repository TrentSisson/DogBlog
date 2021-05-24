"""View module for handling requests about posts"""
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth.models import User
from DogBlogapi.models import Post, PostUser
from datetime import date


class Posts(ViewSet):
    """Posts"""

    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized Task instance
        """
        # Uses the token passed in the `Authorization` header
        user = PostUser.objects.get(user=request.auth.user)
        # Create a new Python instance of the Post class
        # and set its properties from what was sent in the
        # body of the request from the client.
        post = Post()
        post.user = user
        post.title = request.data["title"]
        post.date = date.today()
        post.text = request.data["text"]
        # Try to save the new Post to the database, then
        # serialize the Post instance as JSON, and send the
        # JSON as a response to the client request
        try:
            post.save()
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)
        # If anything went wrong, catch the exception and
        # send a response with a 400 status code to tell the
        # client that something was wrong with its request data
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single Post
        Returns:
            Response -- JSON serialized Post instance
        """
        try:
            # `pk` is a parameter to this function, and
            # Django parses it from the URL route parameter
            #   http://localhost:8000/Posts/2
            #
            # The `2` at the end of the route becomes `pk`
            post = Post.objects.get(pk=pk)

            user = PostUser.objects.get(user=request.auth.user)

            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a Post
        Returns:
            Response -- Empty body with 204 status code
        """
        user = PostUser.objects.get(user=request.auth.user)
        # Do mostly the same thing as POST, but instead of
        # creating a new instance of Post, get the Post record
        # from the database whose primary key is `pk`
        post = Post.objects.get(pk=pk)
        post.user = user
        post.title = request.data["title"]
        post.date = request.data["date"]
        post.text = request.data["text"]
        post.save()
        # 204 status code means everything worked but the
        # server is not sending back any data in the response
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single Post
        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            post = Post.objects.get(pk=pk)
            post.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to Posts resource
        Returns:
            Response -- JSON serialized list of Posts
        """
        # Get all Post records from the database
        posts = Post.objects.all()
        serializer = PostSerializer(
            posts, many=True, context={'request': request})
        return Response(serializer.data)


class UserSerializer(serializers.ModelSerializer):
    """JSON serializer for Users
    Arguments:
        serializer type
    """
    class Meta:
        model = User
        fields = ('id', 'username')


class PostUserSerializer(serializers.ModelSerializer):
    """JSON serializer for RareUsers
    Arguments:
        serializer type
    """
    user = UserSerializer(many=False)

    class Meta:
        model = PostUser
        fields = ('id', 'user')
        depth = 1


class PostSerializer(serializers.ModelSerializer):
    user = PostUserSerializer(many=False)

    class Meta:
        model = Post
        fields = ('id', 'user', 'title', 'date', 'text')
        depth = 1

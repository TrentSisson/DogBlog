import json
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def login_user(request):
    '''Handles the authentication of a gamer
    Method arguments:
        request -- The full HTTP request object
    '''
    req_body = json.loads(request.body.decode())
    # If the request is a HTTP POST, try to pull out the relevant info.
    if request.method == 'POST':
        # Use the built-in authenticate method to verify
        username = req_body['username']
        password = req_body['password']
        authenticated_user = authenticate(username=username, password=password)
        # If authentication was successful, respond with their token
        if authenticated_user is not None:
            token = Token.objects.get(user=authenticated_user)
            if authenticated_user.is_staff:
                data = json.dumps(
                    {"valid": True, "token": token.key, "is_staff": True})
            else:
                data = json.dumps(
                    {"valid": True, "token": token.key, "is_staff": False})
            return HttpResponse(data, content_type='application/json')

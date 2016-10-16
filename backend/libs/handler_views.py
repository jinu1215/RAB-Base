import json

from django.http import HttpResponse

from rest_framework import status as http_status
from rest_framework.response import Response


def handler400(request):
    detail = {'message': 'Bad Request.'}
    return HttpResponse(json.dumps(detail), content_type='application/json', status=http_status.HTTP_400_BAD_REQUEST)


def handler404(request):
    detail = {'message': 'Invalid URL.'}
    return HttpResponse(json.dumps(detail), content_type='application/json', status=http_status.HTTP_404_NOT_FOUND)


def handler500(request):
    detail = {'message': 'Internal server error.'}
    return HttpResponse(json.dumps(detail), content_type='application/json',
                        status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

# -*- coding: utf-8 -*-
import functools
import types
import json
import logging
import sys
import time
import traceback
import pytz

from datetime import datetime

from django.core import urlresolvers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AnonymousUser

from rest_framework import status as http_status
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.response import Response

from backend import urls
from backend.libs import exceptions


log = logging.getLogger(__name__)
api_logger = logging.getLogger('api')


class ServerInfo():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ServerInfo, cls).__new__(cls, *args, **kwargs)
            return cls._instance

    def __init__(self):
        self._hostname = ''

    #@property
    #def hostname(self):
    #    if not self._hostname:
    #        result = commands.getstatusoutput('/bin/hostname')
    #        self._hostname = result[1] if result[0] == 0 else None
    #    return self._hostname


def request_handler(func):
    def decorator(request, *args, **kwargs):
        log.debug('[REQUEST] {0}, method={1}, headers={2}, body={3}'.format(request.get_full_path(),
                                                                            request.method,
                                                                            [(k, request.META[k]) for k in request.META.keys()],
                                                                            request.body))
        start_time = time.time()
        response = func(request, *args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        log.debug('[RESPONSE] {0}, status_code={1}, elapsed_time={2}'.format(request.get_full_path(),
                                                                             response.status_code,
                                                                             elapsed_time))

        server = ServerInfo()
        application = getattr(request, 'application', None)
        user = getattr(request, 'user', AnonymousUser())

        if user.is_authenticated():
            user.last_visited = datetime.now(pytz.utc)
            user.save(update_fields=['last_visited'])

        params_get = request.GET.dict()
        params_post = request.POST.dict()
        for param in params_get:
            if param == 'password': params_get['password'] = '*'
        for param in params_post:
            if param == 'password': params_post['password'] = '*'
        headers = {'Authoziation': request.META.get('HTTP_AUTHORIZATION')}

        api_log = {
                'datetime': datetime.now(pytz.utc).isoformat(),
                #'source_ip': request.META['REMOTE_ADDR'],
                'application': application.key if application else None,
                'auth_type': getattr(request, 'auth_type', None),
                'user': {
                    'member_id': getattr(user, 'member_id', None),
                    'account_type': getattr(user, 'account_type', None),
                    'country_code': getattr(user, 'country_code', None),
                    'user_number': getattr(user, 'user_number', None),
                },
                'request': {
                    'method': request.method,
                    'path': request.path,
                    'params_get': params_get,
                    'params_post': params_post,
                    'headers': headers,
                },
                'response': {
                    'status_code': response.status_code,
                    'error_message': getattr(response, 'error_message', None)
                },
                'extras': getattr(request, 'extras', None),
                #'server_hostname': server.hostname,
                'elapsed_time': elapsed_time,
                'log_version': '1.0',
            }

        try: api_logger.info(json.dumps(api_log))
        except Exception as e: log.exception(e.__class__)

        return response

    return decorator


def exception_handler(exc):
    log.exception(exc.__class__)
    api_exc = exceptions.BackendException()

    headers = {}
    if isinstance(exc, exceptions.APIException):
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header

    if isinstance(exc, Http404):
        message = 'Not found.'
        status_code = http_status.HTTP_404_NOT_FOUND
    elif isinstance(exc, exceptions.BackendException):
        message = getattr(exc, 'detail', api_exc.detail)
        status_code = api_exc.status_code
    else:
        message = api_exc.detail
        status_code = api_exc.status_code

    data = {'message': message}
    if settings.DEBUG: data = exceptions.update_exc_data_for_debug(data)

    res = Response(data,
                   status=status_code,
                   headers=headers)
    res.error_message = message

    return res


def api_call(methods, auth_required=True):
    """API endpoint에 붙이는 decorators

    .. note::
        rest_framework의 decorator가 function에 attribute를 설정하는 방식으로 동작하기 때문에
        이 decorator는 rest_ramework decorators가 사용한 이후에 사용되어야한다. 중간에 끼어들어가면 안된다.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        @request_handler
        @api_view(methods)
        def inner(request, *args, **kwargs):
            request._request.user = request.user or AnonymousUser()
            request._request.auth = request.auth or None

            if auth_required and isinstance(request.user, AnonymousUser):
                raise exceptions.NotAuthenticated()

            ret = view_func(request, *args, **kwargs)

            if type(ret) == dict:
                res = Response(ret)
            elif isinstance(ret, HttpResponseRedirect):
                res = ret
            elif isinstance(ret, HttpResponse):
                res = ret
            elif ret is None:
                ret = {}
                res = Response(ret)
            else:
                raise Exception('Invalid return from view function.')

            return res

        return inner

    return decorator

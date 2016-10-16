# -*- coding: utf-8 -*-
import sys
import traceback

from rest_framework import status as http_status
from rest_framework.exceptions import *


def update_exc_data_for_debug(data):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    _data = data
    _data.update({'type': str(exc_type),
                  'value': str(exc_value),
                  'traceback': traceback.format_tb(exc_traceback)})

    return _data


class BackendException(APIException):
    default_detail = 'Internal server error'

    def __init__(self, error_code, status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=None):
        self.error_code = error_code
        self.status_code = status_code
        self.detail = detail or self.default_detail

    @property
    def value(self):
        return self.detail

    def __unicode__(self):
        return repr(self.detail)

    def __str__(self):
        return self.__unicode__()

from rest_framework.exceptions import APIException


class WrongQueryParams(APIException):
    status_code = 405
    default_detail = 'Wrong filter parameters or not specified manual_id. ' \
                     'You need to use only next parameters: category_id or category, search.'
    default_code = 'WrongQueryParams'

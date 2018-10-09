import json
import traceback
from bson.json_util import dumps
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from goRun.handlers import Marathon
from django.http.response import JsonResponse

# Create your views here.


class getmarathonDataViewSet(APIView):
    '''MeasureColumnsViewSet'''

    def __init__(self):
        self.marathon_data_handler = Marathon()

    def get(self, request):
        '''
        '''
        date_range = request.query_params.get('DateRange', 'all')
        type1 = request.query_params.get('type1')
        cities = request.query_params.get('Cities')
        month = request.query_params.get('month')

        err, res = self.marathon_data_handler.get_marathon_data(
            date_range=date_range, type1=type1, cities=cities, month=month)
        if err:
            return JsonResponse({'message': "some error occured !!", 'statusCode': 400})
        return JsonResponse({'data': res, 'statusCode': 200})

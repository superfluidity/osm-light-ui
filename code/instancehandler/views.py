from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, JsonResponse
import json
import logging
from lib.osm.osmclient.client import Client


def list(request, type=None):

    client = Client()
    if type == 'ns':
        result = client.ns_list()

    return __response_handler(request, {'instances': result, 'type': 'ns'}, 'instance_list.html')


def create(request):

    result = {}
    ns_data={
      "nsName": request.POST.get('nsName', 'WithoutName'),
      "nsDescription": request.POST.get('nsDescription', ''),
      "nsdId": request.POST.get('nsdId', ''),
      "vimAccountId": request.POST.get('vimAccountId', ''),
      "ssh-authorized-key": [
        {
          request.POST.get('key-pair-ref', ''): request.POST.get('keyValue', '')
        }
      ]
    }
    print ns_data
    client = Client()
    result =  client.ns_create(ns_data)
    return  __response_handler(request, result, 'instances:list', to_redirect=True, type='ns')


def delete(request, instance_id=None, type=None):
    result = {}
    return __response_handler(request, result, 'instances:list', to_redirect=True)


def show(request, instance_id=None, type=None):
    result = {}
    return __response_handler(request, result)


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types:
        return JsonResponse(data_res)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)

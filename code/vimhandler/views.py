from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, JsonResponse
from lib.osm.osmclient.client import Client
import json
import logging


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('helper.py')


datacenters = [
    {
        "uuid": "739cde4e-220c-11e8-a805-0242ac120006",
        "vim_tenants": [
            {
                "vim_tenant_id": "asdasdas-220c-11e8-a805-0242ac120006",
                "passwd": "******",
                "config": "string",
                "vim_tenant_name": "string",
                "user": "string"
            }
        ],
        "type": "openstack",
        "description": "no description",
        "name": "MyOpenStack",
        "vim_url": "http://devstack.westeurope.cloudapp.azure.com/identity/v3",
        "config": {},
        "created_at": "2018-03-07T13:35:50",
        "vim_url_admin": "http://devstack.westeurope.cloudapp.azure.com/identity/v3"
    },
    {
        "uuid": "c000ec6c-220c-11e8-a805-0242ac120006",
        "vim_tenants": [
            {
                "vim_tenant_id": "asdasdas-220c-11e8-a805-0242ac120006",
                "passwd": "******",
                "config": "string",
                "vim_tenant_name": "string",
                "user": "string"
            }
        ],
        "type": "openstack",
        "description": "vim-emu openstack",
        "name": "emu-ba",
        "vim_url": "http://localhost:6001/v2.0",
        "config": {},
        "created_at": "2018-03-07T13:37:59",
        "vim_url_admin": "http://localhost:6001/v2.0"
    }
]


def list(request):
    client = Client()
    result = client.vim_list()
    print result
    result = {
        "datacenters": result
    }
    return __response_handler(request, result, 'vim_list.html')


def create(request):
    result = {}
    if request.method == 'GET':
        return __response_handler(request, result, 'vim_create.html')
    else:
        new_vim_dict= request.POST.dict()
        print new_vim_dict
        client = Client()
        del new_vim_dict['csrfmiddlewaretoken']
        result = client.vim_create(new_vim_dict)
        print result
        return __response_handler(request, result, 'vim:list', to_redirect=True)


def delete(request, vim_id=None):
    try:
        client = Client()
        del_res = client.vim_delete(vim_id)
    except Exception as e:
        log.exception(e)
    return __response_handler(request, {}, 'vim:list', to_redirect=True)


def show(request, vim_id=None):
    client = Client()
    result = client.vim_list()
    datacenter = next((x for x in datacenters if x['uuid'] == vim_id), None)
    print datacenter
    return __response_handler(request, {
        "datacenter": datacenter
    })


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types:
        return JsonResponse(data_res)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)

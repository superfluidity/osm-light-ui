from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, JsonResponse
import json
import logging

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
    result = {
        "datacenters": datacenters
    }
    return __response_handler(request, result, 'vim_list.html')


def create(request):
    result = {}
    return __response_handler(request, result, 'vim:list', to_redirect=True)


def delete(request, vim_id=None):
    result = {}
    return __response_handler(request, result, 'vim:list', to_redirect=True)


def show(request, vim_id=None):
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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, JsonResponse
from lib.osm.osmclient.client import Client
import json
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('helper.py')


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
        new_vim_dict = request.POST.dict()
        print new_vim_dict
        client = Client()
        keys = ["schema_version",
                "schema_type",
                "name",
                "vim_url",
                "vim_type",
                "vim_user",
                "vim_password",
                "vim_tenant_name",
                "description"]
        config_keys = {
            "aws": ["region_name", "vpc_cidr_block", "security_groups", "key_pair", "flavor_info"],
            "openstack": ["sdn_controller", "sdn_port_mapping", "security_groups", "availability_zone", "region_name",
                          "insecure", "use_existing_flavors", "vim_type", "use_internal_endpoint", "APIversion",
                          "project_domain_id", "project_domain_name", "user_domain_id", "user_domain_name", "keypair",
                          "dataplane_physical_net", "use_floating_ip", "dataplane_net_vlan_range", "microversion"],
            "vmware": ["sdn_controller", "sdn_port_mapping", "orgname", "admin_username", "admin_password",
                       "nsx_manager", "nsx_user", "nsx_password", "vcenter_ip", "vcenter_port", "vcenter_user",
                       "vcenter_password", "vrops_site", "vrops_user", "vrops_password"],
            "openvim": ["sdn_controller", "sdn_port_mapping"]
        }
        vim_data = dict(filter(lambda i: i[0] in keys and len(i[1]) > 0, new_vim_dict.items()))
        vim_data['config'] = dict(
            filter(lambda i: i[0] in config_keys[vim_data['vim_type']] and len(i[1]) > 0, new_vim_dict.items()))

        result = client.vim_create(vim_data)
        # TODO  'vim:show', to_redirect=True, vim_id=vim_id
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
    datacenter = client.vim_get(vim_id)
    print datacenter
    return __response_handler(request, {
        "datacenter": datacenter
    }, 'vim_show.html')


def __response_handler(request, data_res, url=None, to_redirect=None, *args, **kwargs):
    raw_content_types = request.META.get('HTTP_ACCEPT', '*/*').split(',')
    if 'application/json' in raw_content_types:
        return JsonResponse(data_res)
    elif to_redirect:
        return redirect(url, *args, **kwargs)
    else:
        return render(request, url, data_res)

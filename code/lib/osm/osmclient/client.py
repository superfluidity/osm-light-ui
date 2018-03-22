import requests
import logging
import json
from lib.util import Util
import hashlib


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('helper.py')


class Client(object):
    def __init__(self, host="192.168.100.212", so_port=9999, so_project='admin', ro_host=None, ro_port=9090, **kwargs):

        self._user = 'admin'
        self._password = 'admin'
        # self._project = so_project
        self._project = so_project
        self._token_endpoint = 'admin/v1/tokens'
        self._user_endpoint = 'admin/v1/users'

        self._headers = {}
        self._host = host

        self._base_path = "https://{0}:{1}/osm".format(self._host, so_port)

    def get_token(self):
        postfields_dict = {'username': self._user,
                           'password': self._password,
                           'project-id': self._project}
        token_url = "{0}/{1}".format(self._base_path, self._token_endpoint)
        token = self._send_post(token_url, None, postfields_dict, headers={"Content-Type": "application/yaml", "accept": "application/json"})
        if token is not None:
            return token['id']
        return None

    def nsd_list(self):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/json'
            _url = "{0}/nsd/v1/ns_descriptors_content".format(self._base_path)
            return self._send_get(_url, headers=self._headers)
        return None

    def nsd_get(self, id):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/json'
            _url = "{0}/nsd/v1/ns_descriptors_content/{1}".format(self._base_path,id)
            return self._send_get(_url, headers=self._headers)
        return None

    def nsd_delete(self, id):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/json'
            _url = "{0}/nsd/v1/ns_descriptors_content/{1}".format(self._base_path, id)
            return self._send_delete(_url, headers=self._headers)
        return None

    def nsd_onboard(self, package):
        token = self.get_token()
        headers = {}
        if token:

            headers['Authorization'] = 'Bearer {}'.format(token)
            headers['Content-Type'] = 'application/gzip'
            headers['accept'] = 'application/json'
            with open('/tmp/'+package.name, 'wb+') as destination:
                for chunk in package.chunks():
                    destination.write(chunk)
            headers['Content-File-MD5'] = self.md5(open('/tmp/'+package.name, 'rb'))
            #print type(open('cirros_2vnf_ns.tar.gz', 'rb').read())
            #r = requests.post(url='http://upload.example.com', data={'title': 'test_file},  files =  {'file':package})
            _url = "{0}/nsd/v1/ns_descriptors_content/".format(self._base_path)
            return self._send_post(_url, headers=headers,
                                  data=open('/tmp/'+package.name, 'rb'))
        return None

    def vnfd_list(self):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/json'
            _url = "{0}/vnfpkgm/v1/vnf_packages_content".format(self._base_path)
            return self._send_get(_url, headers=self._headers)
        return None

    def vnfd_get(self, id):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/json'
            _url = "{0}/vnfpkgm/v1/vnf_packages_content/{1}".format(self._base_path, id)
            return self._send_get(_url, headers=self._headers)
        return None

    def vnfd_delete(self, id):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/json'
            _url = "{0}/vnfpkgm/v1/vnf_packages_content/{1}".format(self._base_path, id)
            return self._send_delete(_url, headers=self._headers)
        return None

    def vnfd_onboard(self, package):
        token = self.get_token()
        headers = {}
        if token:
            headers['Authorization'] = 'Bearer {}'.format(token)
            headers['Content-Type'] = 'application/gzip'
            headers['accept'] = 'application/json'
            with open('/tmp/'+package.name, 'wb+') as destination:
                for chunk in package.chunks():
                    destination.write(chunk)
            headers['Content-File-MD5'] = self.md5(open('/tmp/'+package.name, 'rb'))
            _url = "{0}/vnfpkgm/v1/vnf_packages_content".format(self._base_path)
            return self._send_post(_url, headers=headers,
                                   data=open('/tmp/' + package.name, 'rb'))
        return None

    def _upload_package(self, filename, package):
        token = self.get_token()
        headers = {}
        if token:
            headers['Authorization'] = 'Bearer {}'.format(token)
            headers['Content-Type'] = 'application/gzip'
            headers['Content-File-MD5'] = self.md5(package)
            headers['accept'] = 'application/json'
        return None

    def _send_post(self, url, data=None, json=None, **kwargs):
        try:
            r = requests.post(url, data=data, json=json, verify=False, **kwargs)
            print r.text
        except Exception as e:
            log.exception(e)
            print "Exception during send POST"
            return {'error': 'error during connection to agent'}
        return Util.json_loads_byteified(r.text)

    def _send_get(self, url, params=None, **kwargs):
        try:
            r = requests.get(url, params=None, verify=False, **kwargs)
        except Exception as e:
            log.exception(e)
            print "Exception during send GET"
            return {'error': 'error during connection to agent'}
        return Util.json_loads_byteified(r.text)

    def _send_delete(self, url, params=None, **kwargs):
        try:
            r = requests.delete(url, params=None, verify=False, **kwargs)
        except Exception as e:
            log.exception(e)
            print "Exception during send DELETE"
            return {'error': 'error during connection to agent'}
        return Util.json_loads_byteified(r.text)

    def md5(self, f):
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: f.read(1024), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()


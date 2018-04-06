import requests
import logging
import json
import tarfile
import yaml
import StringIO
from lib.util import Util
import hashlib
import os

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('helper.py')


class Client(object):
    def __init__(self, host=os.getenv('OSM_SERVER',"localhost"), so_port=9999, so_project='admin', ro_host=None, ro_port=9090, **kwargs):
#os.getenv('OSM_SERVER', "localhost")
        ##print os.getenv('OSM_SERVER',"40.86.191.138")
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
            #self._headers['accept'] = 'application/json'
            _url = "{0}/nsd/v1/ns_descriptors/{1}/nsd".format(self._base_path,id)
            return yaml.load(self._send_get(_url, headers=self._headers))
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
    def nsd_update(self, id, data):
        token = self.get_token()
        if token:
            tar_pkg = self.get_nsd_pkg(id)

            for tarinfo in tar_pkg:
                print(tarinfo.name, "is", tarinfo.size, "bytes in size and is")
                if tarinfo.isreg():
                    print("a regular file.")
                elif tarinfo.isdir():
                    print("a directory.")
                else:
                    print("something else.")
        return True

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
            ##print type(open('cirros_2vnf_ns.tar.gz', 'rb').read())
            #r = requests.post(url='http://upload.example.com', data={'title': 'test_file},  files =  {'file':package})
            _url = "{0}/nsd/v1/ns_descriptors_content/".format(self._base_path)
            return self._send_post(_url, headers=headers,
                                  data=open('/tmp/'+package.name, 'rb'))
        return None

    def nsd_artifacts(self, id):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'text/plain'
            _url = "{0}/nsd/v1/ns_descriptors/{1}/artifacts".format(self._base_path, id)
            return self._send_get(_url, headers=self._headers)
        return None

    def ns_list(self):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/json'
            _url = "{0}/nslcm/v1/ns_instances_content".format(self._base_path)
            return self._send_get(_url, headers=self._headers)
        return None

    def ns_create(self, ns_data):
        token = self.get_token()
        headers = {}
        if token:
            headers['Authorization'] = 'Bearer {}'.format(token)
            headers['Content-Type'] = 'application/yaml'
            headers['accept'] = 'application/json'

            _url = "{0}/nslcm/v1/ns_instances_content".format(self._base_path)
            return self._send_post(_url, headers=headers,
                                  json=ns_data)
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
            #self._headers['accept'] = 'application/yaml'
            _url = "{0}/vnfpkgm/v1/vnf_packages/{1}/vnfd".format(self._base_path, id)
            return yaml.load(self._send_get(_url, headers=self._headers))
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
    def vnf_packages_artifacts(self, id):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            self._headers['Content-Type'] = 'application/yaml'
            _url = "{0}/vnfpkgm/v1/vnf_packages/{1}/artifacts".format(self._base_path, id)
            return self._send_get(_url, headers=self._headers)
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
            #print r.text
        except Exception as e:
            log.exception(e)
            #print "Exception during send POST"
            return {'error': 'error during connection to agent'}
        return Util.json_loads_byteified(r.text)

    def _send_get(self, url, params=None, **kwargs):
        try:
            r = requests.get(url, params=None, verify=False, stream=True, **kwargs)
            ##print r.header
        except Exception as e:
            log.exception(e)
            #print "Exception during send GET"
            return {'error': 'error during connection to agent'}
        if 'accept' in kwargs['headers']:
            accept = kwargs['headers']['accept']
            if accept == 'application/json':
                #print "json"
                return Util.json_loads_byteified(r.text)
            elif accept == 'application/zip':
                tarf =StringIO.StringIO(r.content)
                #tarf = tarfile.open(fileobj=StringIO.StringIO(r.content))
                # for tarinfo in tarf:
                #     #print(tarinfo.name, "is", tarinfo.size, "bytes in size and is")
                #     if tarinfo.isreg():
                #         #print("a regular file.")
                #     elif tarinfo.isdir():
                #         #print("a directory.")
                #     else:
                #         #print("something else.")
                return tarf
            else:
                return r.text
        else:
            return r.text

    def _send_delete(self, url, params=None, **kwargs):
        try:
            r = requests.delete(url, params=None, verify=False, **kwargs)
        except Exception as e:
            log.exception(e)
            #print "Exception during send DELETE"
            return {'error': 'error during connection to agent'}
        return Util.json_loads_byteified(r.text)

    def md5(self, f):
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: f.read(1024), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_nsd_pkg(self, id):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            #self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/zip'
            _url = "{0}/nsd/v1/ns_descriptors/{1}/nsd_content".format(self._base_path, id)
            return self._send_get(_url, headers=self._headers)
        return None

    def get_vnfd_pkg(self, id):
        token = self.get_token()
        if token:
            self._headers['Authorization'] = 'Bearer {}'.format(token)
            #self._headers['Content-Type'] = 'application/yaml'
            self._headers['accept'] = 'application/zip'
            _url = "{0}/vnfpkgm/v1/vnf_packages/{1}/package_content".format(self._base_path, id)
            return self._send_get(_url, headers=self._headers)
        return None
if __name__ == '__main__':
    client = Client()
    package = client.get_nsd_pkg()

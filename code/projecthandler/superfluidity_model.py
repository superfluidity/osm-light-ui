#
#   Copyright 2017 CNIT - Consorzio Nazionale Interuniversitario per le Telecomunicazioni
#
#   Licensed under the Apache License, Version 2.0 (the );
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an  BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from __future__ import unicode_literals

import copy
import json
import os.path
import yaml
from lib.util import Util
import logging
from django.db import models
from projecthandler.click_model import ClickProject
from projecthandler.etsi_model import EtsiProject
from projecthandler.models import Project

from lib.superfluidity.superfluidity_parser import SuperfluidityParser
from lib.superfluidity.superfluidity_rdcl_graph import SuperfluidityRdclGraph


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('SuperfluidityModel.py')


PATH_TO_SCHEMAS = 'lib/superfluidity/schemas/'
PATH_TO_DESCRIPTORS_TEMPLATES = 'lib/superfluidity/descriptor_template'
DESCRIPTOR_TEMPLATE_SUFFIX = '.json'
GRAPH_MODEL_FULL_NAME = 'lib/TopologyModels/superfluidity/superfluidity.yaml'
EXAMPLES_FOLDER = 'usecases/SUPERFLUIDITY/'


class SuperfluidityProject(EtsiProject, ClickProject):
    """Superfluidity Project class
    The data model has the following descriptors:
        # descrtiptor list in comment #

    """

    @classmethod
    def data_project_from_files(cls, request):

        file_dict = {}
        for my_key in request.FILES.keys():
            file_dict[my_key] = request.FILES.getlist(my_key)

        log.debug(file_dict)

        data_project = SuperfluidityParser.importprojectfiles(file_dict)

        return data_project

    @classmethod
    def data_project_from_example(cls, request):
        superfluidity_id = request.POST.get('example-superfluidity-id', '')
        data_project = SuperfluidityParser.importprojectdir(EXAMPLES_FOLDER + superfluidity_id, 'json')
        return data_project

    @classmethod
    def get_example_list(cls):
        """Returns a list of directories, in each directory there is a project superfluidity"""

        path = EXAMPLES_FOLDER
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        return {'superfluidity': dirs}

    @classmethod
    def get_new_descriptor(cls, descriptor_type, request_id):

        json_template = cls.get_descriptor_template(descriptor_type)

        return json_template

    @classmethod
    def get_descriptor_template(cls, type_descriptor):
        """Returns a descriptor template for a given descriptor type"""

        try:
            schema = Util.loadjsonfile(os.path.join(PATH_TO_DESCRIPTORS_TEMPLATES, type_descriptor + DESCRIPTOR_TEMPLATE_SUFFIX))
            return schema
        except Exception as e:
            log.exception(e)
            return False

    @classmethod
    def get_clone_descriptor(cls, descriptor, type_descriptor, new_descriptor_id):
        new_descriptor = copy.deepcopy(descriptor)

        return new_descriptor

    def get_type(self):
        return "superfluidity"

    def __str__(self):
        return self.name

    def get_overview_data(self):
        current_data = json.loads(self.data_project)
        result = {
            'owner': self.owner.__str__(),
            'name': self.name,
            'updated_date': self.updated_date.__str__(),
            'info': self.info,
            'type': 'superfluidity',
            'nsd': len(current_data['nsd'].keys()) if 'nsd' in current_data else 0,

            'vnfd': len(current_data['vnfd'].keys()) if 'vnfd' in current_data else 0,

            'click': len(current_data['click'].keys()) if 'click' in current_data else 0,

            'validated': self.validated
        }

        return result

    def get_graph_data_json_topology(self, descriptor_id):
        rdcl_graph = SuperfluidityRdclGraph()
        project = self.get_dataproject()
        topology = rdcl_graph.build_graph_from_project(project,
                                                     model=self.get_graph_model(GRAPH_MODEL_FULL_NAME))
        return json.dumps(topology)

    def create_descriptor(self, descriptor_name, type_descriptor, new_data, data_type):
        """Creates a descriptor of a given type from a json or yaml representation

        Returns the descriptor id or False
        """
        try:
            current_data = json.loads(self.data_project)
            if data_type == 'json':
                new_descriptor = json.loads(new_data)
            elif data_type == 'yaml':
                yaml_object = yaml.load(new_data)
                new_descriptor = json.loads(Util.yaml2json(yaml_object))
            else:
                log.debug('Create descriptor: Unknown data type')
                return False

            # schema = cls.loadjsonfile("lib/superfluidity/schemas/"+type_descriptor+".json")
            #reference_schema = self.get_json_schema_by_type(type_descriptor)
            # validate = Util.validate_json_schema(reference_schema, new_descriptor)
            validate = False
            new_descriptor_id = descriptor_name
            if not type_descriptor in current_data:
                current_data[type_descriptor] = {}
            current_data[type_descriptor][new_descriptor_id] = new_descriptor
            self.data_project = current_data
            self.validated = validate  
            self.update()
            result = new_descriptor_id
        except Exception as e:
            log.exception(e)
            result = False
        return result

    def set_validated(self, value):
        self.validated = True if value is not None and value == True else False

    def get_add_element(self, request):
        result = False
        group_id = request.POST.get('group_id')
        element_id = request.POST.get('element_id')
        element_type = request.POST.get('element_type')
        existing_vnf = request.POST.get('existing_vnf')
        if element_type == 'ns_cp':
            result = self.add_ns_sap(group_id, element_id)
        elif element_type == 'ns_vl':
            result = self.add_ns_vl(group_id, element_id)
        elif element_type == 'vnf':
            if existing_vnf == 'true':
                result = self.add_ns_existing_vnf(group_id, element_id)
            else:
                result = self.add_ns_vnf(group_id, element_id)
        elif element_type == 'vnf_vl':
            result = self.add_vnf_intvl(group_id, element_id)
        elif element_type == 'vnf_ext_cp':
            result = self.add_vnf_vnfextcpd(group_id, element_id)
        elif element_type == 'vnf_vdu':
            result = self.add_vnf_vdu(group_id, element_id)
        elif element_type == 'vnf_vdu_cp':
            vdu_id = request.POST.get('choice')
            result = self.add_vnf_vducp(group_id, vdu_id, element_id)
        elif element_type == 'vnffg':
            # log.debug("Add ") group_id, element_id
            result = self.add_vnffg(group_id, element_id)
        return result

    def get_remove_element(self, request):

        result = False
        group_id = request.POST.get('group_id')
        element_id = request.POST.get('element_id')
        element_type = request.POST.get('element_type')
        log.debug('in get_remove_element : ' + str(element_id))  # TODO log
        if element_type == 'ns_cp':
            result = self.remove_ns_sap(group_id, element_id)
        elif element_type == 'ns_vl':
            result = self.remove_ns_vl(group_id, element_id)
        elif element_type == 'vnf':
            result = self.remove_ns_vnf(group_id, element_id)
        elif element_type == 'vnf_vl':
            result = self.remove_vnf_intvl(group_id, element_id)
        elif element_type == 'vnf_ext_cp':
            result = self.remove_vnf_vnfextcpd(group_id, element_id)
        elif element_type == 'vnf_vdu':
            result = self.remove_vnf_vdu(group_id, element_id)
        elif element_type == 'vnf_vdu_cp':
            vdu_id = request.POST.get('choice')
            result = self.remove_vnf_vducp(group_id, vdu_id, element_id)
        elif element_type == 'vnf_click_vdu':
            result = self.remove_vnf_vdu(group_id, request.POST.get('vduId'))

        return result

    def get_add_link(self, request):

        result = False
        parameters = request.POST.dict()
        link = json.loads(parameters['link'])
        source = link['source']
        destination = link['target']
        # source = json.loads(request.POST.get('source'))
        # destination = json.loads(request.POST.get('destination'))
        source_type = source['info']['type']
        destination_type = destination['info']['type']
        if (source_type, destination_type) in [('ns_vl', 'ns_cp'), ('ns_cp', 'ns_vl')]:
            vl_id = source['id'] if source_type == 'ns_vl' else destination['id']
            sap_id = source['id'] if source_type == 'ns_cp' else destination['id']
            result = self.link_vl_sap(source['info']['group'][0], vl_id, sap_id)
        elif (source_type, destination_type) in [('ns_vl', 'vnf'), ('vnf', 'ns_vl')]:
            vl_id = source['id'] if source_type == 'ns_vl' else destination['id']
            vnf_id = source['id'] if source_type == 'vnf' else destination['id']
            ns_id = source['info']['group'][0]
            vnf_ext_cp = request.POST.get('choice')
            result = self.link_vl_vnf(ns_id, vl_id, vnf_id, vnf_ext_cp)
        if (source_type, destination_type) in [('vnf', 'ns_cp'), ('ns_cp', 'vnf')]:
            vnf_id = source['id'] if source_type == 'vnf' else destination['id']
            sap_id = source['id'] if source_type == 'ns_cp' else destination['id']
            ns_id = source['info']['group'][0]
            vnf_ext_cp = request.POST.get('choice')
            result = self.link_vnf_sap(ns_id, vnf_id, sap_id, vnf_ext_cp)
        elif (source_type, destination_type) in [('vnf_vl', 'vnf_vdu_cp'), ('vnf_vdu_cp', 'vnf_vl')]:
            vdu_id = request.POST.get('choice')
            vnf_id = source['info']['group'][0]
            intvl_id = source['id'] if source_type == 'vnf_vl' else destination['id']
            vducp_id = source['id'] if source_type == 'vnf_vdu_cp' else destination['id']
            result = self.link_vducp_intvl(vnf_id, vdu_id, vducp_id, intvl_id)
        elif (source_type, destination_type) in [('vnf_ext_cp', 'vnf_vl'), ('vnf_vl', 'vnf_ext_cp')]:
            vnfExtCpd_id = source['id'] if source_type == 'vnf_ext_cp' else destination['id']
            intvl_id = source['id'] if source_type == 'vnf_vl' else destination['id']
            result = self.link_vnfextcpd_intvl(source['info']['group'][0], vnfExtCpd_id, intvl_id)
        return result

    def get_remove_link(self, request):

        result = False
        parameters = request.POST.dict()
        # print "param remove_link", parameters
        link = json.loads(parameters['link'])
        source = link['source']
        destination = link['target']

        source_type = source['info']['type']
        destination_type = destination['info']['type']
        if (source_type, destination_type) in [('ns_vl', 'ns_cp'), ('ns_cp', 'ns_vl')]:
            vl_id = source['id'] if source_type == 'ns_vl' else destination['id']
            sap_id = source['id'] if source_type == 'ns_cp' else destination['id']
            result = self.unlink_vl_sap(source['info']['group'][0], vl_id, sap_id)
        elif (source_type, destination_type) in [('ns_vl', 'vnf'), ('vnf', 'ns_vl')]:
            vl_id = source['id'] if source_type == 'ns_vl' else destination['id']
            vnf_id = source['id'] if source_type == 'vnf' else destination['id']
            ns_id = source['info']['group'][0]
            result = self.unlink_vl_vnf(ns_id, vl_id, vnf_id)
        if (source_type, destination_type) in [('vnf', 'ns_cp'), ('ns_cp', 'vnf')]:
            vnf_id = source['id'] if source_type == 'vnf' else destination['id']
            sap_id = source['id'] if source_type == 'ns_cp' else destination['id']
            ns_id = source['info']['group'][0]
            result = self.unlink_vl_sap(ns_id, vnf_id, sap_id)
        elif (source_type, destination_type) in [('vnf_vl', 'vnf_vdu_cp'), ('vnf_vdu_cp', 'vnf_vl')]:
            intvl_id = source['id'] if source_type == 'vnf_vl' else destination['id']
            vducp_id = source['id'] if source_type == 'vnf_vdu_cp' else destination['id']
            vnf_id = source['info']['group'][0]
            result = self.unlink_vducp_intvl(vnf_id, vducp_id, intvl_id)
        elif (source_type, destination_type) in [('vnf_ext_cp', 'vnf_vl'), ('vnf_vl', 'vnf_ext_cp')]:
            vnfExtCpd_id = source['id'] if source_type == 'vnf_ext_cp' else destination['id']
            intvl_id = source['id'] if source_type == 'vnf_vl' else destination['id']
            result = self.unlink_vnfextcpd_intvl(source['info']['group'][0], vnfExtCpd_id, intvl_id)
        return result

    def get_unused_vnf(self, nsd_id):
        try:
            current_data = json.loads(self.data_project)
            result = []
            if 'vnfd' in current_data:
                for vnf in current_data['vnfd']:
                    if vnf not in current_data['nsd'][nsd_id]['vnfdId']:
                        result.append(vnf)
        except Exception as e:
            log.exception(e)
            result = None  # TODO maybe we should use False ?
        return result

    def get_available_nodes(self, args):
        """Returns all available node """
        log.debug('get_available_nodes')
        try:
            result = []
            # current_data = json.loads(self.data_project)
            model_graph = self.get_graph_model(GRAPH_MODEL_FULL_NAME)
            for node in model_graph['layer'][args['layer']]['nodes']:
                current_data = {
                    "id": node,
                    "category_name": model_graph['nodes'][node]['label'],
                    "types": [
                        {
                            "name": "generic",
                            "id": node
                        }
                    ]
                }
                result.append(current_data)

                # result = current_data[type_descriptor][descriptor_id]
        except Exception as e:
            log.debug(e)
            result = []
        return result
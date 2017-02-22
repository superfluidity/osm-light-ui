from __future__ import unicode_literals

import copy
import json
import os.path
import yaml
from lib.util import Util
import logging
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


class SuperfluidityProject(Project):
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

        return result

    def get_remove_element(self, request):
        result = False
        
        return result

    def get_add_link(self, request):

        result = False

        return result

    def get_remove_link(self, request):
        result = False

        return result


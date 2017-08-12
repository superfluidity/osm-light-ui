#
#   Copyright 2017 CNIT - Consorzio Nazionale Interuniversitario per le Telecomunicazioni
#
#   Licensed under the Apache License, Version 2.0 (the "License");
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

import logging
from lib.clickparser import click_parser
from lib.etsi.etsi_rdcl_graph import EtsiRdclGraph
from lib.rdcl_graph import RdclGraph
from lib.superfluidity.superfluidity_parser import SuperfluidityParser

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('SuperfluidityRdclGraph')


class SuperfluidityRdclGraph(RdclGraph):
    """Operates on the graph representation used for the GUI graph views"""

    def __init__(self):
        pass

    def build_graph_from_project(self, json_project, model={}):
        """Creates a single graph for a whole project"""

        graph_object = {
            'vertices': [],
            'edges': [],
            'graph_parameters': {},
            'model': model
        }


        try:
            positions = json_project['positions'] if 'positions' in json_project else {}
            etsi_topology = EtsiRdclGraph().build_graph_from_project(json_project)
            click_vertices = []
            click_edges = []
            click_topology = click_parser.importprojectjson(json_project, positions=positions)
            click_vertices = click_vertices + click_topology['vertices']
            click_edges = click_edges + click_topology['edges']
            if 'vnfd' in json_project:
                for vnf_id in json_project['vnfd']:
                    vnfd = json_project['vnfd'][vnf_id]
                    k8s_service_map = {}
                    for vdu in vnfd['vdu']:
                        if 'vduNestedDesc' in vdu:
                            vdu_type = None
                            for vdu_nested_dec_id in vdu['vduNestedDesc']:
                                vdu_nested = SuperfluidityParser().get_nested_vdu_from_id(vdu_nested_dec_id, vnfd)
                                if vdu_nested:
                                    if vdu_nested['vduNestedDescriptorType'] == 'kubernetes':
                                        vdu_type = 'vnf_k8s_vdu'
                                        nest_desc_id = vdu_nested['vduNestedDescriptor']
                                        if nest_desc_id in k8s_service_map:
                                            k8s_service_map[nest_desc_id].append(vdu['vduId'])
                                        else:
                                            k8s_service_map[nest_desc_id] = [vdu['vduId']]
                                    elif vdu_nested['vduNestedDescriptorType'] == 'click':
                                        vdu_type = 'vnf_click_vdu'
                                    elif vdu_nested['vduNestedDescriptorType'] == 'docker':
                                        vdu_type = 'vnf_docker_vdu'

                            vertice = next((x for x in etsi_topology['vertices'] if x['id'] == vdu['vduId']), None)
                            if vertice is not None:
                                if vdu_type:
                                    vertice['info']['type'] = vdu_type
                                vertice['group'] = [vdu['vduNestedDesc']]
                                vertice['vduId'] = vdu['vduId']
                    # create vertices and edges related to k8SServiceCpd
                    if 'k8SServiceCpd' in vnfd:
                        for k8SServiceCpd in vnfd['k8SServiceCpd']:
                            if 'serviceDescriptor' in k8SServiceCpd:
                                self.add_node(k8SServiceCpd['cpdId'], 'k8s_service_cp', vnf_id, positions, graph_object)
                            if k8SServiceCpd['serviceDescriptor'] in k8s_service_map:
                                for ref in k8s_service_map[k8SServiceCpd['serviceDescriptor']]:
                                    self.add_link(k8SServiceCpd['cpdId'], ref, 'vnf', vnf_id, graph_object)

            graph_object['vertices'] += etsi_topology['vertices'] + click_vertices
            graph_object['edges'] += etsi_topology['edges'] + click_edges
            log.debug('build graph from project json')

        except Exception as e:
            log.exception('Exception in build_graph_from_project')
            raise

        return graph_object

    def build_deployment_descriptor(self, json_project, nsd_id):
        descriptor = {
            'nsd': {},
            'vnfd': {},
            'click': {},
            'k8s': {}
        }
        nsd_to_deploy = json_project['nsd'][nsd_id]
        descriptor['nsd'][nsd_id] = json_project['nsd'][nsd_id]
        for vnfdId in nsd_to_deploy['vnfdId']:
            descriptor['vnfd'][vnfdId] = json_project['vnfd'][vnfdId]
            for vdu in descriptor['vnfd'][vnfdId]['vdu']:
                if 'vduNestedDescType' in vdu:
                    if vdu['vduNestedDescType'] == 'click' and vdu['vduNestedDesc'] and vdu['vduNestedDesc'] in json_project['click']:
                        descriptor['click'][vdu['vduNestedDesc']] = json_project['click'][vdu['vduNestedDesc']]

        return descriptor

import json
import logging
import copy
import six
from lib.rdcl_graph import RdclGraph

from toscaparser.tosca_template import ToscaTemplate
from translator.hot.tosca_translator import TOSCATranslator

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('ToscaRdclGraph')

class ToscaRdclGraph(RdclGraph):
    """Operates on the graph representation used for the GUI graph views"""

    def __init__(self):
        pass


    def build_graph_from_project(self, json_project, model={}):
        """Creates a single graph for a whole project"""

        #print "json_project ",json_project
        graph_object = {
            'vertices': [],
            'edges': [],
            'graph_parameters': {},
            'model': model
        }
        try:
            positions = json_project['positions'] if 'positions' in json_project else False
            log.debug('build graph from project json')

            # print json.dumps(json_project, sort_keys=True, indent=4, separators=(',', ': '))

            path = '/home/user/RDCL/heat-translator/translator/tests/data/network/tosca_two_servers_one_network.yaml'
            # tosca = ToscaTemplate(path, parsed_params, a_file)
            tosca = ToscaTemplate(path, {}, True)
            version = tosca.version
            if tosca.version:
                print("\nversion: " + version)

            if hasattr(tosca, 'description'):
                description = tosca.description
                if description:
                    print("\ndescription: " + description)

            if hasattr(tosca, 'inputs'):
                inputs = tosca.inputs
                if inputs:
                    print("\ninputs:")
                    for input in inputs:
                        print("\t" + input.name)

            if hasattr(tosca, 'nodetemplates'):
                nodetemplates = tosca.nodetemplates
                if nodetemplates:
                    print("\nnodetemplates:")
                    for node in nodetemplates:
                        print("\t" + node.name)

            if hasattr(tosca, 'outputs'):
                outputs = tosca.outputs
                if outputs:
                    print("\noutputs:")
                    for output in outputs:
                        print("\t" + output.name)

            for node in tosca.graph.nodetemplates:
                if node.name in tosca.graph.vertices:
                    print 'node '+node.name+' is related to:'
                    self.add_node(node.name, node.type, 'vnf', positions, graph_object)
                    related = tosca.graph.vertex(node.name).related_nodes
                    for related_node in related:
                        print related_node.name + '->' + tosca.graph.vertex(node.name).related[related_node].type

            # #THIS IS FOR THE TRANSLATION INTO HOT TEMPLATES
            # translator = TOSCATranslator(tosca, {}, False,
            #                              csar_dir=None)
            # yaml_files = translator.output_to_yaml_files_dict('output.yaml')
            # for name, content in six.iteritems(yaml_files):
            #     if name != "output.yaml":
            #         with open(name, 'w+') as f:
            #             f.write(content)
            # print(yaml_files['output.yaml'])

        except Exception as e:
            log.error('Exception in build_graph_from_project')
            raise

        return graph_object

if (typeof dreamer === 'undefined') {
    var dreamer = {};
}
var level = {}

dreamer.SuperfluidityController = (function(global) {
    'use strict';

    var DEBUG = true;

    SuperfluidityController.prototype.constructor = SuperfluidityController;


    /**
     * Constructor
     */
    function SuperfluidityController() {
         SuperfluidityController.clickController = new dreamer.ClickController();
         SuperfluidityController.etsiController = new dreamer.EtsiController();

    }

    SuperfluidityController.prototype.addVnf = function(graph_editor, node, success, error) {
        SuperfluidityController.etsiController.addVnf(graph_editor, node, success, error);
    };

    SuperfluidityController.prototype.addVnfVdu = function(graph_editor, node, success, error) {
        SuperfluidityController.etsiController.addVnfVdu(graph_editor, node, success, error);
    }

    SuperfluidityController.prototype.addVnfVduCp = function(graph_editor, node, success, error) {
         var vnf_id = node.info.group[0];
        var vnf_vdus = $.grep(graph_editor.d3_graph.nodes, function(e) {
            return (e.info.group.indexOf(vnf_id) >= 0 && (e.info.type == 'vnf_vdu' || e.info.type == 'vnf_click_vdu'));
        });

        if (typeof vnf_vdus == 'undefined' || vnf_vdus.length <= 0) {
            alert('You should add a VDU')
        } else {
            console.log(vnf_vdus)
            showChooserModal('Select the VDU to link', vnf_vdus, function(choice) {
                var target = choice;
                choice = $.grep(vnf_vdus, function(e){ return e.id == choice; });
                console.log(choice)
                var choiceId = choice[0].info.type == 'vnf_vdu' ? choice[0].id : choice[0].vduId;
                var data_to_send = {
                'group_id': node.info.group[0],
                'element_id': node.id,
                'element_type': node.info.type,
                'element_desc_id': node.info.desc_id,
                'x': node.x,
                'y': node.y,
                'choice': choiceId,
                 };
                 console.log(typeof choiceId,data_to_send);
                new dreamer.GraphRequests().addNode(data_to_send, choice, function() {
                    var link = {
                        source: node.id,
                        target: target,
                        view: graph_editor.filter_parameters.link.view[0],
                        group: [node.info.group[0]],
                    };

                    graph_editor.parent.addLink.call(graph_editor, link);
                    if (success)
                        success();
                    $('#modal_create_link_chooser').modal('hide');
                });
            });
        }
    }

    SuperfluidityController.prototype.nsCpExclusiveConnection = function(graph_editor, link, success, error) {
        SuperfluidityController.etsiController.nsCpExclusiveConnection(graph_editor, link, success, error);
    }

    SuperfluidityController.prototype.linkVnftoNsVl = function(graph_editor, link, success, error) {
        SuperfluidityController.etsiController.linkVnftoNsVl(graph_editor, link, success, error);
    }

    SuperfluidityController.prototype.linkVnftoNsCp = function(graph_editor, link, success, error) {
        SuperfluidityController.etsiController.linkVnftoNsCp(graph_editor, link, success, error);
    }

    SuperfluidityController.prototype.linkVltoVduCp = function(graph_editor, link, success, error) {
        var s = link.source;
        var d = link.target;
        var source_id = s.id;
        var target_id = d.id;
        var source_type = s.info.type;
        var destination_type = d.info.type;
        var vnf_vdu_cp_id = source_type == 'vnf_vdu_cp' ? source_id : target_id;
        var vdu_links = $.grep(graph_editor.d3_graph.links, function(e) {
            return (e.source.id == vnf_vdu_cp_id || e.target.id == vnf_vdu_cp_id) && (e.source.info.type == 'vnf_vdu' || e.target.info.type == 'vnf_vdu'
            || e.source.info.type == 'vnf_click_vdu' || e.target.info.type == 'vnf_click_vdu')
        });
        var vdu_id = vdu_links[0].source.info.type == 'vnf_vdu' ? vdu_links[0].source.id : vdu_links[0].target.id;
        if(vdu_links[0].source.info.type == 'vnf_vdu'){
            vdu_id = vdu_links[0].source.id;
        }else if (vdu_links[0].target.info.type == 'vnf_vdu'){
            vdu_id = vdu_links[0].target.id;
        } else if(vdu_links[0].source.info.type == 'vnf_click_vdu'){
          var vnf_vdus = $.grep(graph_editor.d3_graph.nodes, function(e) {
            return (e.id == vdu_links[0].source.id) && (e.info.type == 'vnf_click_vdu')
          });
          vdu_id = vnf_vdus[0].vduId;
        }else{
            var vnf_vdus = $.grep(graph_editor.d3_graph.nodes, function(e) {
            return (e.id == vdu_links[0].target.id) && (e.info.type == 'vnf_click_vdu')
          });
          vdu_id = vnf_vdus[0].vduId;
        }
        var old_link = $.grep(graph_editor.d3_graph.links, function(e) {
            return (e.source.id == vnf_vdu_cp_id || e.target.id == vnf_vdu_cp_id) && (e.source.info.type == 'vnf_vl' || e.target.info.type == 'vnf_vl')
        });
        new dreamer.GraphRequests().addLink(link,  vdu_id, function() {
            graph_editor._deselectAllNodes();
            if (typeof old_link !== 'undefined' && old_link.length > 0 && old_link[0].index !== 'undefined') {
                graph_editor.parent.removeLink.call(graph_editor, old_link[0].index);
            }
            if (success) {
                success();
            }
        });
    }

   SuperfluidityController.prototype.linkVnfVltoExpCp = function(graph_editor, link, success, error) {
        SuperfluidityController.etsiController.linkVnfVltoExpCp(graph_editor, link, success, error);
   }

   SuperfluidityController.prototype.removeVnfVdu = function(graph_editor, node, success, error) {
        SuperfluidityController.etsiController.removeVnfVdu(graph_editor, node, success, error);
   }

    SuperfluidityController.prototype.removeVnfVduCp = function(graph_editor, node, success, error) {
        var vdu_links = $.grep(graph_editor.d3_graph.links, function(e) {
            return (e.source.id == node.id || e.target.id == node.id) && (e.source.info.type == 'vnf_vdu' || e.target.info.type == 'vnf_vdu'
            || e.source.info.type == 'vnf_click_vdu' || e.target.info.type == 'vnf_click_vdu')
        });
        var vdu_id;
        if(vdu_links[0].source.info.type == 'vnf_vdu'){
            vdu_id = vdu_links[0].source.id;
        }else if(vdu_links[0].target.info.type == 'vnf_vdu' ){
            vdu_id = vdu_links[0].target.id;
        }else if(vdu_links[0].source.info.type == 'vnf_click_vdu' ){
            vdu_id = vdu_links[0].source.vduId;
        }else{
            vdu_id = vdu_links[0].target.vduId;
        }
        console.log(vdu_id)
        var data_to_send = {
            'group_id': node.info.group[0],
            'element_id': node.id,
            'element_type': node.info.type,
            'element_desc_id': node.info.desc_id,
            };
        new dreamer.GraphRequests().removeNode(data_to_send, vdu_id, function() {
            if (success) {
                success();
            }
        });
    }

    SuperfluidityController.prototype.addNode = function(graph_editor, node, success, error) {
        console.log("add node in view", JSON.stringify(graph_editor.getCurrentView()))
        var current_view = graph_editor.getCurrentView();
        if(current_view != 'compact' && current_view != 'expandable' ){
            SuperfluidityController.etsiController.addNode(graph_editor, node, success, error);
        }
        else{
            SuperfluidityController.clickController.addNode(graph_editor, node, success, error);
        }
    };

    SuperfluidityController.prototype.addToCurrentVNFFG = function(graph_editor, args, error) {
        if(current_view != 'compact' && current_view != 'expandable' ){
            SuperfluidityController.etsiController.addToCurrentVNFFG(graph_editor, args, error);
        }
    }

    SuperfluidityController.prototype.removeNode = function(graph_editor, node, success, error) {
        var current_view = graph_editor.getCurrentView();
        if(current_view != 'compact' && current_view != 'expandable' ){
            SuperfluidityController.etsiController.removeNode(graph_editor, node, success, error)
        }
        else{
            SuperfluidityController.clickController.removeNode(graph_editor, node, success, error)
        }
    };

    SuperfluidityController.prototype.removeLink = function(graph_editor, link, success, error) {
        var current_view = graph_editor.getCurrentView();
        if(current_view != 'compact' && current_view != 'expandable' ){
            SuperfluidityController.etsiController.removeLink(graph_editor, link, success, error)
        }
        else{
            SuperfluidityController.clickController.removeLink(graph_editor, link, success, error)
        }
    };


    return SuperfluidityController;


}(this));

if (typeof module === 'object') {
    module.exports = dreamer.SuperfluidityController;
}
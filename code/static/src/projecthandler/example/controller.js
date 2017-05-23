if (typeof dreamer === 'undefined') {
    var dreamer = {};
}
var level = {}

dreamer.ExampletokenController = (function(global) {
    'use strict';

    var DEBUG = true;

    ExampletokenController.prototype.constructor = ExampletokenController;

    /**
     * Constructor
     */
    function ExampletokenController() {


    }


    ExampletokenController.prototype.addNode = function(graph_editor, node, success, error) {
        log('addNode');
        var data_to_send = {
                'group_id': node.info.group[0],
                'element_id': node.id,
                'element_type': node.info.type,
                'element_desc_id': node.info.desc_id,
                'x': node.x,
                'y': node.y
         };
        new dreamer.GraphRequests().addNode(data_to_send, null, function() {
            if (success)
                success();
        },error);
    };

    ExampletokenController.prototype.addLink = function(graph_editor, link, success, error) {
        log('addLink');

        new dreamer.GraphRequests().addLink(link, null, function() {
            graph_editor._deselectAllNodes();
            if (typeof old_link !== 'undefined' && old_link.length > 0 && old_link[0].index !== 'undefined') {
                graph_editor.parent.removeLink.call(graph_editor, old_link[0].index);
            }
            if (success) {
                success();
            }
        },error);
    };

    ExampletokenController.prototype.removeNode = function(graph_editor, node, success, error) {
        log('removeNode');
        var data_to_send = {
            'group_id': node.info.group[0],
            'element_id': node.id,
            'element_type': node.info.type,
            'element_desc_id': node.info.desc_id,
            };
        new dreamer.GraphRequests().removeNode(data_to_send, null, function() {
            if (success) {
                success();
            }
        },error);
    };

    ExampletokenController.prototype.removeLink = function(graph_editor, link, success, error) {
        log('removeLink');
        var s = link.source;
        var d = link.target;
        new dreamer.GraphRequests().removeLink(link, function() {
            if (success) {
                success();
            }
        },error);
    };

    /**
     * Log utility
     */
    function log(text) {
        if (DEBUG)
            console.log("::ExampletokenController::", text);
    }

    return ExampletokenController;
}(this));

if (typeof module === 'object') {
    module.exports = dreamer.ExampletokenController;
}
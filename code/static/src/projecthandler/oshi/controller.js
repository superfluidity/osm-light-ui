if (typeof dreamer === 'undefined') {
    var dreamer = {};
}
var level = {}

dreamer.OshiController = (function(global) {
    'use strict';

    var DEBUG = true;

    OshiController.prototype.constructor = OshiController;

    /**
     * Constructor
     */
    function OshiController() {


    }


    OshiController.prototype.addNode = function(self, node, success, error) {
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

    OshiController.prototype.addLink = function(self, link, success, error) {
        log('addLink');

        new dreamer.GraphRequests().addLink(link, null, function() {
            self._deselectAllNodes();
            if (typeof old_link !== 'undefined' && old_link.length > 0 && old_link[0].index !== 'undefined') {
                self.parent.removeLink.call(self, old_link[0].index);
            }
            if (success) {
                success();
            }
        },error);
    };

    OshiController.prototype.removeNode = function(self, node, success, error) {
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

    OshiController.prototype.removeLink = function(self, link, success, error) {
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
            console.log("::OshiController::", text);
    }

    return OshiController;
}(this));

if (typeof module === 'object') {
    module.exports = dreamer.OshiController;
}
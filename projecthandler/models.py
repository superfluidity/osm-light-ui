from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import jsonfield
from StringIO import StringIO
import zipfile
import json
import yaml
from lib.util import Util
from model_utils.managers import InheritanceManager
#import projecthandler.etsi_model

project_types = {}

class Project(models.Model):
    owner = models.ForeignKey('sf_user.CustomUser', db_column='owner')
    name = models.CharField(max_length=20)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    info = models.TextField(default='No info')
    data_project = jsonfield.JSONField(default={})
    '''Stores a validated JSON representation of the project'''

    validated = models.BooleanField(default=False)

    #InheritanceManager
    objects = InheritanceManager()
   

    @classmethod
    def get_project_types(cls):
        global project_types
        return project_types        

    @classmethod
    def add_project_type(cls, type, my_class):
        global project_types
        project_types [type]= my_class


    @classmethod
    def create_project(cls, name, user, validated, info, data_project):
        # project = EtsiProject.objects.create(name=name, owner=user, validated=False, info=info,
        #                                                  data_project=data_project)
        project = cls.objects.create(name=name, owner=user, validated=False, info=info,
                                                       data_project=data_project)
        return project


    def get_type(self):
        return "Base"

    def get_dataproject(self):
        current_data = json.loads(self.data_project)
        return current_data

    def get_overview_data(self):
        result = {
            'owner': self.owner,
            'name': self.name,
            'updated_date': self.updated_date,
            'info': self.info,
            'validated': self.validated
        }

        return result

    def set_data_project(self, new_data, validated):
        self.data_project = new_data
        self.set_validated(validated)
        self.update()

    def update(self):
        self.updated_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    def get_descriptors(self, type_descriptor):
        '''Returns all descriptors of a given type'''

        try:
            current_data = json.loads(self.data_project)
            result = current_data[type_descriptor]
        except Exception:
            result = {}
        return result

    def get_descriptor(self, descriptor_id, type_descriptor):
        '''Returns a specific descriptor'''

        try:
            current_data = json.loads(self.data_project)
            result = current_data[type_descriptor][descriptor_id]
        except Exception:
            print "Exception in get_descriptor"
            result = {}

        return result

    def delete_descriptor(self, type_descriptor, descriptor_id):
        try:
            print descriptor_id, type_descriptor
            current_data = json.loads(self.data_project)
            del (current_data[type_descriptor][descriptor_id])
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'Exception in delete_descriptor', e
            result = False
        return result

    def clone_descriptor(self, type_descriptor, descriptor_id, new_id):
        try:
            current_data = json.loads(self.data_project)
            descriptor = current_data[type_descriptor][descriptor_id]
            new_descriptor = self.get_clone_descriptor(descriptor, type_descriptor, new_id)
            current_data[type_descriptor][new_id] = new_descriptor
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'Exception in clone_descriptor', e
            result = False
        return result

    def edit_descriptor(self, type_descriptor, descriptor_id, new_data, data_type):
        try:
            #utility = Util()
            print descriptor_id, type_descriptor #TODO(stefano) mettere logger
            current_data = json.loads(self.data_project)
            if data_type == 'json':
                new_descriptor = json.loads(new_data)
            else:
                yaml_object = yaml.load(new_data)
                new_descriptor = json.loads(Util.yaml2json(yaml_object))

            reference_schema = self.get_json_schema_by_type(type_descriptor)
            Util.validate_json_schema(reference_schema, new_descriptor)
            current_data[type_descriptor][descriptor_id] = new_descriptor
            self.data_project = current_data
            self.update()
            result = True
        except Exception as e:
            print 'Exception in edit_descriptor', e
            result = False
        return result


    def get_zip_archive(self):
        in_memory = StringIO()
        try:
            current_data = json.loads(self.data_project)
            zip = zipfile.ZipFile(in_memory, "w", zipfile.ZIP_DEFLATED)
            for desc_type in current_data:
                for current_desc in current_data[desc_type]:
                    zip.writestr(current_desc + '.json', json.dumps(current_data[desc_type][current_desc]))

            zip.close()
        except Exception as e:
            print e

        in_memory.flush()
        return in_memory



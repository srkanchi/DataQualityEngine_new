## create schema format through avro for eachtest
## get schema existing from schema registry 
## create schema based on test-format-schema 

import uuid
import avro.schema
import json
import avro
from avro.datafile import DataFileWriter, DataFileReader
from avro.io import DatumWriter, DatumReader
import boto3


class SchemaHandler(object):
    """
    class of Schema Handler 
    Use this class to create schemas and get existing schemas
    """
    

    def __init__(self):
        self.client = boto3.client('glue')
        self.schema_name = None
        
        
    def list_schemas(self, registry_name='DataQualityEngine'):
        """
        Returns schema
        """
        
        response = self.client.list_schemas(
            RegistryId={
                'RegistryName': registry_name
            },
            MaxResults=10
        ) 
            
        return response
    
        
    def get_schema(self,schema_name,registry_name='DataQualityEngine'):
              
        response = self.client.get_schema(
                        SchemaId={
                            'SchemaName': schema_name,
                            'RegistryName': registry_name
                        }
                    )
        return response
        

    

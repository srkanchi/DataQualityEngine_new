## create schema format through avro for eachtest
## get schema existing from schema registry 
## create schema based on test-format-schema 

import uuid
import avro.schema
import json
import avro
from avro.datafile import DataFileWriter, DataFileReader
from avro.io import DatumWriter, DatumReader
import Schema.schema_registry as sr


### schema_format for performing test on range 
demo = {'data': {json},
                     "test": [

                    {'test_schema_format': 'range_test'},

                    {'range': {'upper_bound': int, 'lower_bound': int}}

                    ]}


class SchemaHandler(object):
    """
    class of Schema Handler 
    Use this class to create schemas and get existing schemas
    """

    def __init__(self,schema_name):
        print("Schema name")
        self.schema_name = schema_name
        
        
    
    def get_schema(self, schema_name):
        """
        Returns schema
        """
        sr.get_schema_by_subject_from_client(schema_name)
        return self.schema
        
    
    def get_schema_format(self,schema):
        
        schema = avro.schema.Parse(open("demo.avsc", "rb").read())
        
        return self.schema
            
        
    ## creates schema for a test and writes to registry
    def create_schema_for_test(self,schema_name):
       print("Enter details to create schema") 
       schema_name = input()
       print(schema_name)
       dataFile    = open(schema_name + ".avro", "wb")
       schema = get_schema_format()
       ## writer for creating schema from schema format 
       writer = DataFileWriter(dataFile, DatumWriter(), schema)
       # Write data using DatumWriter
       writer.append( {'data': 'sample_data.json',
                    
                     'test': [

                    {'test_schema_format': 'range_test'},

                    {'range': {'upper_bound': 50, 'lower_bound': 25}}

                    ]})
       writer.close()
            

    

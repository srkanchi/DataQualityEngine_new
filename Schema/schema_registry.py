## this consists of schema registry 

from schema_registry.client import SchemaRegistryClient, schema

client = SchemaRegistryClient(url="")

#### sample for testing our code

## actual schema for range to be deployed on client
deployment_schema_2 = {
'type':'schema_format',
"namespace": "",
"name":"SchemaDeployment",    
'test': 'Range test',                     
'range': [{"name" :"upper_bound", "type":"int"} ,
          {"name" : "lower_bound", "type" :"int"} ]

}



avro_schema = schema.AvroSchema(deployment_schema_2)

schema_id = client.register("test-deployment", avro_schema)

## get schema from registry by subject
def get_schema_by_subject_from_client(schema_subject_name):
    sr = SchemaRegistryClient('localhost:8081')
    my_schema = sr.get_schema(subject=schema_subject_name, version='latest')
    

## get schema from registry by id 
def get_schema_by_id_from_client():
    sr = SchemaRegistryClient('localhost:8081')
    my_schema = sr.get_by_id(schema_id=1)
        
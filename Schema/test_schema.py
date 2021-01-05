import avro.schema

from avro.datafile import DataFileReader, DataFileWriter

from avro.io import DatumReader, DatumWriter

 

# Parse the schema file

schema = avro.schema.Parse(open("demo.avsc", "rb").read())

 

# Create a data file using DataFileWriter

dataFile    = open("participants.avro", "wb")

writer      = DataFileWriter(dataFile, DatumWriter(), schema)

 

# Write data using DatumWriter

writer.append({"name": "Virutal conference",

               "date": 25612345,

               "location":"New York",

               "speakers":["Speaker1","Speaker2"],

               "participants":["Participant1","Participant2","Participant3","Participant4","Participant5"],

               "seatingArrangement":{"Participant1":1,

                                     "Participant2":2,

                                     "Participant3":3,

                                     "Participant4":4,

                                     "Participant5":5}

               })

writer.close()



########################################################################################################################################3

read_schema = avro.schema.parse(json.dumps({
    "namespace": "example.avro",
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "first_name", "type": "string", "default": "", "aliases": ["name"]},
        {"name": "favorite_number", "type": ["int", "null"]},
        {"name": "favorite_color", "type": ["string", "null"]}
    ]
}))

# 1. open avro and extract passport + data
reader = DataFileReader(open("users.avro", "rb"), DatumReader(write_schema, read_schema))
new_schema = reader.get_meta("avro.schema")
users = []
for user in reader:
    users.append(user)
reader.close()

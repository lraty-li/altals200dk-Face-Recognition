import random
import numpy as np
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

# +-+------------+------------+------------------+------------------------------+
# | | field name | field type | other attributes |       field description      |
# +-+------------+------------+------------------+------------------------------+
# |1|    "pk"    |    Int64   |  is_primary=True |      "primary field"         |
# | |            |            |   auto_id=True   |                              |
# +-+------------+------------+------------------+------------------------------+
# |2|  "user_pk" |    STRING  |                  |      "a string field"        |
# +-+------------+------------+------------------+------------------------------+
# |3|"embeddings"| FloatVector|     dim=512      |  "float vector with dim 512" |
# +-+------------+------------+------------------+------------------------------+

fmt = "\n=== {:30} ===\n"


class MilvusDB:
    def __init__(self):
        self.serverUrl = "IP"
        self.serverPort = "19530"
        self.dbName = "faceDB"
        self.serachParams={"metric_type": "L2", "params": {"nprobe": 10}}
        self.threshold=1.1
        print(fmt.format("start connecting to Milvus"))
        connections.connect("default", host=self.serverUrl,
                            port=self.serverPort)
        has = utility.has_collection("faceDB")
        print(f"Does collection {self.dbName} exist in Milvus: {has}")
        if has:
            self.coll = Collection(self.dbName)
        else:
            self._initDB()

    def _initDB(self):
        fields = [
            FieldSchema(name="pk", dtype=DataType.INT64,
                        is_primary=True, auto_id=True),
            FieldSchema(name="user_pk", dtype=DataType.INT64),
            FieldSchema(name="embeddings",
                        dtype=DataType.FLOAT_VECTOR, dim=512)
        ]
        schema = CollectionSchema(
            fields, "faces vertor database")

        print(fmt.format("Create collection `{self.dbName}`"))
        self.coll = Collection(self.dbName, schema, consistency_level="Strong")
    def queryVetc(self,vetc):
        #vetc is a list
        if vetc is None:
            return []
        searchRslt = self.coll.search(data=[vetc],
                     anns_field="embeddings", param=self.serachParams, limit=10,output_fields=["pk","user_pk"]
                    )
        results=[]
        for hits in searchRslt:
            for hit in hits:
                if hit.distance <self.threshold:
                    results.append(hit.entity.get('user_pk'))
        return results
    def queryUserpk(self,userPk):
        expr = f"user_pk in [{userPk}]"
        result = self.coll.query(expr=expr, output_fields=["pk"])
        return result

    def delByUserPk(self,userPk):
        res=self.queryUserpk(userPk)
        for hit in res:
            self.coll.delete(f"user_pk in [{hit['pk']}]")
        # result = self.coll.search(expr=expr)
        # self.coll.delete(expr)
        
        pass
    def inserData(self,userPk,faceVetc):
        #faceVetc should be list
        entity=[
            [userPk],
            [faceVetc]
        ]
        insert_result = self.coll.insert(entity)

ybyb = MilvusDB()
# faceVetc = np.load("./data/LiData.npy")
# obama=np.load("./data/obameData.npy")

# ybyb.inserData(9,obama.tolist())
# ybyb.inserData(10,faceVetc.tolist())
# ybyb.delByUserPk(7)

# ybyb.inserData(7,[0.02 for _ in range(512)])

# ybyb.queryVetc(obama.tolist())


# ybyb.inserData(1234567,[0 for _ in range(512)])


# res2=ybyb.queryVetc([0 for _ in range(512)])
# print(res2)
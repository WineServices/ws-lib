import copy
from datetime import datetime
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel


class DB(BaseModel):

    __TABLE_NAME__ = "table"
    __NON_DB_FIELDS__ = set()

    id: Optional[int]  # null when not registered in db

    @property
    def non_db_fields(self):
        fields_to_exclude = copy.deepcopy(self.__NON_DB_FIELDS__)
        fields_to_exclude.add("id")
        return fields_to_exclude

    def dict(self, *args, **kwargs):
        object_as_dict = super().dict(*args, **kwargs)
        if "id" in object_as_dict:
            object_as_dict.pop("id")

        return object_as_dict

    def insert_into_db(self,  conn) -> int:
        # if id object is known that means that it is already inserted in data
        if self.id is not None:
            return self.id

        obj_as_dict = self.dict(exclude=self.non_db_fields)

        columns = ", ".join(obj_as_dict.keys())
        values = obj_as_dict.values()
        values_str = ", ".join(len(obj_as_dict) * ["%s"])

        query = f"""
                insert into {self.__TABLE_NAME__} 
                    ({columns})
                    VALUES ({values_str})
                    RETURNING id;
                """

        res = conn.execute(query, tuple(values)).fetchone()
        return res[0]

    def delete_row(self, conn, row_id):

        query = f"""
        DELETE FROM {self.__TABLE_NAME__}
        WHERE id = %s
        """

        conn.execute(query, (row_id, ))

    @classmethod
    def insert_bulk(cls, conn, rows: List['DB']) -> Optional[List[int]]:
        return_ids = False
        if 'creation_date' in cls.__fields__:
            creation_date = datetime.utcnow()
            return_ids = True
            for row in rows:
                row.creation_date = creation_date

        objs_as_dicts = [row.dict(exclude=row.non_db_fields) for row in rows]

        schema_name = cls.__TABLE_NAME__.split(".")[0]
        table_name = cls.__TABLE_NAME__.split(".")[1]

        df = pd.DataFrame(objs_as_dicts)
        df.to_sql(con=conn, name=table_name, schema=schema_name, index=False, if_exists="append")

        if return_ids:
            # get inserted_ids
            query = f"""
                    SELECT id FROM {cls.__TABLE_NAME__} where creation_date = %s
                """
            res = conn.execute(query, (creation_date,)).fetchall()

            return [r[0] for r in res]

        return None
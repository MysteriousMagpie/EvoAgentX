try:
    import psycopg2
except ImportError:
    raise ImportError("psycopg2 is required. Install with 'pip install psycopg2'.")

import threading
import json
from typing import Dict, Literal, Optional
from .base import DBStoreBase
from ..schema import TableType, MemoryStore, AgentStore, WorkflowStore, HistoryStore

class PostgreSQL(DBStoreBase):
    def __init__(self, db_name, ip="", port="5432", user=None, password=None, **kwargs):
        self.connection = psycopg2.connect(
            dbname=db_name, user=user, password=password, host=ip, port=port
        )
        self._lock = threading.Lock()

    def _create_table(self, table: str, columns: list):
        col_defs = [f'"{columns[0]}" TEXT PRIMARY KEY'] + [f'"{col}" TEXT' for col in columns[1:]]
        sql = f'CREATE TABLE IF NOT EXISTS {table} ({", ".join(col_defs)})'
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute(sql)
            self.connection.commit()

    def _insert_meta(self, table: str, columns: list):
        col_names = ', '.join([f'"{c}"' for c in columns])
        values = ', '.join(['%s'] * len(columns))
        return f'INSERT INTO {table} ({col_names}) VALUES ({values})'

    def insert_memory(self, metadata, store_type=None, table=None, *args, **kwargs):
        if table is None:
            table = TableType.store_memory
        columns = list(MemoryStore.model_fields.keys())
        metadata = MemoryStore.model_validate(metadata)
        self._create_table(table, columns)
        insert_sql = self._insert_meta(table, columns)
        values = [json.dumps(v) if not isinstance(v, str) else v for v in metadata.model_dump().values()]
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute(insert_sql, values)
            self.connection.commit()

    def insert_agent(self, metadata, store_type=None, table=None, *args, **kwargs):
        if table is None:
            table = TableType.store_agent
        columns = list(AgentStore.model_fields.keys())
        metadata = AgentStore.model_validate(metadata)
        self._create_table(table, columns)
        insert_sql = self._insert_meta(table, columns)
        values = [json.dumps(v) if not isinstance(v, str) else v for v in metadata.model_dump().values()]
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute(insert_sql, values)
            self.connection.commit()

    def insert_workflow(self, metadata, store_type=None, table=None, *args, **kwargs):
        if table is None:
            table = TableType.store_workflow
        columns = list(WorkflowStore.model_fields.keys())
        metadata = WorkflowStore.model_validate(metadata)
        self._create_table(table, columns)
        insert_sql = self._insert_meta(table, columns)
        values = [json.dumps(v) if not isinstance(v, str) else v for v in metadata.model_dump().values()]
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute(insert_sql, values)
            self.connection.commit()

    def insert_history(self, metadata, store_type=None, table=None, *args, **kwargs):
        if table is None:
            table = TableType.store_history
        columns = list(HistoryStore.model_fields.keys())
        metadata = HistoryStore.model_validate(metadata)
        self._create_table(table, columns)
        insert_sql = self._insert_meta(table, columns)
        values = [json.dumps(v) if not isinstance(v, str) else v for v in metadata.model_dump().values()]
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute(insert_sql, values)
            self.connection.commit()

    def insert(self, metadata, store_type=None, table=None, *args, **kwargs):
        if store_type == TableType.store_memory:
            self.insert_memory(metadata, store_type=store_type, table=table, *args, **kwargs)
        elif store_type == TableType.store_agent:
            self.insert_agent(metadata, store_type=store_type, table=table, *args, **kwargs)
        elif store_type == TableType.store_workflow:
            self.insert_workflow(metadata, store_type=store_type, table=table, *args, **kwargs)
        elif store_type == TableType.store_history:
            self.insert_history(metadata, store_type=store_type, table=table, *args, **kwargs)
        else:
            raise ValueError("Invalid store_type provided.")

    def delete(self, metadata_id, store_type=None, table=None, *args, **kwargs):
        if table is None:
            if store_type is None:
                raise ValueError("store_type must not be None")
            table = getattr(TableType, store_type)
        columns = self._get_columns(store_type)
        id_col = columns[0]
        sql = f'DELETE FROM {table} WHERE "{id_col}" = %s'
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute(sql, (metadata_id,))
            self.connection.commit()
            return cur.rowcount > 0

    def update(self, metadata_id, new_metadata=None, store_type=None, table=None, *args, **kwargs):
        if table is None:
            if store_type is None:
                raise ValueError("store_type must not be None")
            table = getattr(TableType, store_type)
        columns = self._get_columns(store_type)
        new_metadata = self._validate_metadata(store_type, new_metadata)
        set_clause = ', '.join([f'"{col}" = %s' for col in columns[1:]])
        sql = f'UPDATE {table} SET {set_clause} WHERE "{columns[0]}" = %s'
        values = [json.dumps(v) if not isinstance(v, str) else v for v in new_metadata.model_dump().values()][1:] + [metadata_id]
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute(sql, values)
            self.connection.commit()
            return cur.rowcount > 0

    def get_by_id(self, metadata_id, store_type=None, table=None, *args, **kwargs):
        if table is None:
            if store_type is None:
                raise ValueError("store_type must not be None")
            table = getattr(TableType, store_type)
        columns = self._get_columns(store_type)
        id_col = columns[0]
        sql = f'SELECT * FROM {table} WHERE "{id_col}" = %s'
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute(sql, (metadata_id,))
                result = cur.fetchone()
                if result:
                    return dict(zip(columns, result))
                return None

    def col_info(self):
        with self._lock:
            with self.connection.cursor() as cur:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = cur.fetchall()
                table_info = []
                for (table_name,) in tables:
                    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s", (table_name,))
                    columns = cur.fetchall()
                    table_info.append({
                        "table_name": table_name,
                        "columns": {col: dtype for col, dtype in columns}
                    })
                return table_info

    def _get_columns(self, store_type):
        if store_type == TableType.store_memory:
            return list(MemoryStore.model_fields.keys())
        elif store_type == TableType.store_agent:
            return list(AgentStore.model_fields.keys())
        elif store_type == TableType.store_workflow:
            return list(WorkflowStore.model_fields.keys())
        elif store_type == TableType.store_history:
            return list(HistoryStore.model_fields.keys())
        else:
            raise ValueError("Invalid store_type provided.")

    def _validate_metadata(self, store_type, metadata):
        if store_type == TableType.store_memory:
            return MemoryStore.model_validate(metadata)
        elif store_type == TableType.store_agent:
            return AgentStore.model_validate(metadata)
        elif store_type == TableType.store_workflow:
            return WorkflowStore.model_validate(metadata)
        elif store_type == TableType.store_history:
            return HistoryStore.model_validate(metadata)
        else:
            raise ValueError("Invalid store_type provided.")

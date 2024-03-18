"""
This file has just been created automatically.
This is the file where you can write you own service.
Currently, the is code provides a basic producer and an basic consumer.
In order for your code to work, you must delete the code that you are not using and add your own application logic.
"""

import asyncio
import logging
import pprint
import random
import uuid

from sqlalchemy import create_engine, Table, Column, Integer, MetaData, String
from sqlalchemy.orm import declarative_base, sessionmaker

from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_broker_facade import ok_response_thing, error_response_thing
from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_subjects_name import _SAVE_MANY_RAW_DATA_SUBJECT_NAME, \
    DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT, DB_GET_ALL_RAW_DATA_SUBJECT, DB_UPSERT_MANY_PROCESSED_DATAPOINTS_SUBJECT, \
    DB_GET_PROCESSED_DATA_COUNT_SUBJECT, DB_GET_PROCESSED_DATA_PAGE_SUBJECT
from src.blueprint_dev_v2.logger.logger import log
from datetime import datetime

from fastiot.core import FastIoTService, Subject, subscribe, loop, reply, ReplySubject
from fastiot.core.core_uuid import get_uuid
from fastiot.core.time import get_time_now
from fastiot.db.mariadb_helper_fn import get_mariadb_client_from_env
from fastiot.msg.thing import Thing

Base = declarative_base()


class DatabaseMariaService(FastIoTService):

    _DB_NAME = "MariaDB"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # NOTE: create the database/schema and table in the mariadb database before running this service
        #       you can use the following SQL statement to create the database and table:
        #
        #       CREATE DATABASE <database_name>;
        #
        #       replace <database_name> with the name of the database you want to create.
        self._mariadb_connection = get_mariadb_client_from_env(schema="TestDB")

    async def _stop(self):
        log.info(f"{self._DB_NAME}-Service stopped")
        self._mariadb_connection.close()

    def setup_schemas_if_not_exists(self):
        # create table if not exists. table-name: KIOptiPackRaw
        cursor = self._mariadb_connection.cursor()
        try:
            # create table if not exists. table-name: KIOptiPackRaw
            # NOTE: replace the table name with your own table name
            res = cursor.execute("CREATE TABLE IF NOT EXISTS KIOptiPackRaw("
                                              "id UUID PRIMARY KEY,"
                                              "material_id VARCHAR(36),"
                                              "datum VARCHAR(36),"
                                              "laborant VARCHAR(16),"
                                              "rohwert_1_labormessung FLOAT(12),"
                                              "rohwert_2_labormessung FLOAT(12),"
                                              "rohwert_3_labormessung FLOAT(12),"
                                              "aufbereiteter_wert FLOAT(12));"
                                              )
            log.info(f"{self._DB_NAME}-Table 'KIOptiPackRaw' created successfully")


            res = cursor.execute("CREATE TABLE IF NOT EXISTS KIOptiPackProcessed("
                                    "id UUID PRIMARY KEY,"
                                    "aufbereiteter_wert FLOAT(12),"
                                    "laborant_AN FLOAT(12),"
                                    "laborant_HANS FLOAT(12),"
                                    "laborant_SO FLOAT(12),"
                                    "laborant_TK FLOAT(12),"
                                    "material_id_00000000 FLOAT(12),"
                                    "material_id_11111111 FLOAT(12),"
                                    "material_id_22222222 FLOAT(12),"
                                    "material_id_33333333 FLOAT(12),"
                                    "rohwert_1_high FLOAT(12),"
                                    "rohwert_1_low FLOAT(12),"
                                    "rohwert_1_medium FLOAT(12),"
                                    "rohwert_1_very_high FLOAT(12),"
                                    "rohwert_1_very_low FLOAT(12),"
                                    "rohwert_2_labormessung FLOAT(12),"
                                    "rohwert_3_labormessung FLOAT(12));"
                                 )

            # material_id_00000000
            # material_id_00000000-0000-0000-0000-000000000000
            log.info(f"{self._DB_NAME}-Table 'KIOptiPackProcessed' created successfully")
        except Exception as e:
            log.error(f"Error while creating {self._DB_NAME}-Table: {e}")
            raise e
        finally:
            cursor.close()

    async def _start(self):
        log.info("{self._DB_NAME}-Service started")
        self.setup_schemas_if_not_exists()

    @reply(DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT)
    async def db_save_many_raw_datapoints(self, topic: str, msg: Thing) -> Thing:
        if not isinstance(msg.value, list):
            log.error(f"Payload (the 'value' field of the msg Thing) must be of type list, "
                      f"but received: {type(msg.value)}")
            raise ValueError("Payload must be a list of raw data points")

        data_points: list[dict] = msg.value
        log.info(f"Received {len(data_points)} raw data points to be inserted into {self._DB_NAME}")

        # create uuids for each data point
        for data_point in data_points:
            data_point["id"] = str(uuid.uuid4())

        log.info(f"Insering data points into {self._DB_NAME}")

        cursor = self._mariadb_connection.cursor()
        res = None

        try:
            no_rows = cursor.executemany(
                "INSERT INTO KIOptiPackRaw (id, material_id, datum, laborant, rohwert_1_labormessung, "
                "rohwert_2_labormessung, rohwert_3_labormessung, aufbereiteter_wert) "
                "VALUES (%(id)s,%(material_id)s, %(datum)s, %(laborant)s, %(rohwert_1_labormessung)s, "
                "%(rohwert_2_labormessung)s, %(rohwert_3_labormessung)s, %(aufbereiteter_wert)s)",
                data_points
            )
            self._mariadb_connection.commit()
            log.info(f"DB transaction result: {no_rows}")
            log.info(f"Inserted {no_rows} data points into {self._DB_NAME}")

            # feel free to include whatever information you want to return here.
            res = {
                "acknowledged": True,
                "db": self._DB_NAME,
                "no_rows": no_rows,
            }

            # in principle one does not need to return information here.
            # However, some infos are return here, so that the requesting service can log the information.
            return ok_response_thing(payload=res, fiot_service=self)
        except Exception as e:
            log.error(f"Error while inserting data points into {self._DB_NAME}: {e}")
            return error_response_thing(exception=e, fiot_service=self)
        finally:
            cursor.close()

    @reply(DB_GET_ALL_RAW_DATA_SUBJECT)
    async def get_all_raw_data(self, topic: str, msg: Thing) -> Thing:
        log.info(f"Received request to get all raw data from {self._DB_NAME}")

        # query all entries from the table KIOptiPackRaw
        cursor = self._mariadb_connection.cursor()
        try:
            cursor.execute("SELECT * FROM KIOptiPackRaw")
            raw_data_entries = cursor.fetchall()
        except Exception as e:
            log.error(f"Error while querying data from {self._DB_NAME}: {e}")
            return error_response_thing(exception=e, fiot_service=self)
        finally:
            cursor.close()

        return ok_response_thing(payload=raw_data_entries, fiot_service=self)

    @reply(DB_UPSERT_MANY_PROCESSED_DATAPOINTS_SUBJECT)
    async def db_save_upsert_processed_datapoints(self, topic: str, msg: Thing) -> Thing:

        if not isinstance(msg.value, list):
            log.error(f"Payload (the 'value' field of the msg Thing) must be of type list, "
                      f"but received: {type(msg.value)}")
            raise ValueError("Payload must be a list of processed data points")

        data_points: list[dict] = msg.value
        log.info(f"Received {len(data_points)} processed data points to be inserted into {self._DB_NAME}")

        cursor = self._mariadb_connection.cursor()
        try:
            res = cursor.executemany(
                "INSERT INTO KIOptiPackProcessed ("
                "id, aufbereiteter_wert, laborant_AN, laborant_HANS, laborant_SO, laborant_TK, "
                "material_id_00000000, material_id_11111111, "
                "material_id_22222222, material_id_33333333, "
                "rohwert_1_high, rohwert_1_low, rohwert_1_medium, rohwert_1_very_high, rohwert_1_very_low, "
                "rohwert_2_labormessung, rohwert_3_labormessung"
                ") VALUES ("
                "%(id)s, %(aufbereiteter_wert)s, %(laborant_AN)s, %(laborant_HANS)s, %(laborant_SO)s, %(laborant_TK)s, "
                "%(material_id_00000000)s, %(material_id_11111111)s, "
                "%(material_id_22222222)s, %(material_id_33333333)s, "
                "%(rohwert_1_high)s, %(rohwert_1_low)s, %(rohwert_1_medium)s, %(rohwert_1_very_high)s, %(rohwert_1_very_low)s, "
                "%(rohwert_2_labormessung)s, %(rohwert_3_labormessung)s"
                ") ON DUPLICATE KEY UPDATE "
                "aufbereiteter_wert = VALUES(aufbereiteter_wert),"
                "laborant_AN = VALUES(laborant_AN),"
                "laborant_HANS = VALUES(laborant_HANS),"
                "laborant_SO = VALUES(laborant_SO),"
                "laborant_TK = VALUES(laborant_TK),"
                "material_id_00000000 = VALUES(material_id_00000000),"
                "material_id_11111111 = VALUES(material_id_11111111),"
                "material_id_22222222 = VALUES(material_id_22222222),"
                "material_id_33333333 = VALUES(material_id_33333333),"
                "rohwert_1_high = VALUES(rohwert_1_high),"
                "rohwert_1_low = VALUES(rohwert_1_low),"
                "rohwert_1_medium = VALUES(rohwert_1_medium),"
                "rohwert_1_very_high = VALUES(rohwert_1_very_high),"
                "rohwert_1_very_low = VALUES(rohwert_1_very_low),"
                "rohwert_2_labormessung = VALUES(rohwert_2_labormessung),"
                "rohwert_3_labormessung = VALUES(rohwert_3_labormessung)",
                data_points
            )
            self._mariadb_connection.commit()
            log.info(f"DB transaction result: {res}")
            log.info(f"Inserted {res} data points into {self._DB_NAME}")
        except Exception as e:
            log.error(f"Error while inserting data points into {self._DB_NAME}: {e}")
            return error_response_thing(exception=e, fiot_service=self)

        # feel free to include whatever information you want to return here.
        db_specific_info = {
                "acknowledged": True,
                "db": "MariaDB"
        }

        # in principle one does not need to return information here.
        # However, some infos are return here, so that the requesting service can log the information.
        return ok_response_thing(payload=db_specific_info, fiot_service=self)

    @reply(DB_GET_PROCESSED_DATA_COUNT_SUBJECT)
    async def get_processed_data_count(self, topic: str, msg: Thing) -> Thing:
        log.info(f"Received request to get the number of processed data points from {self._DB_NAME}")

        try:
            cursor = self._mariadb_connection.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM KIOptiPackProcessed")
            result = cursor.fetchone()
            count = result['count']
            cursor.close()
        except Exception as e:
            log.error(f"Error while counting processed data points in mariadb: {e}")
            return error_response_thing(exception=e, fiot_service=self)

        return ok_response_thing(payload=count, fiot_service=self)

    @reply(DB_GET_PROCESSED_DATA_PAGE_SUBJECT)
    async def get_processed_data_page(self, topic: str, msg: Thing) -> Thing:
        log.info(f"Received request to get a page of processed data points from {self._DB_NAME}")
        default_params = {
            "page": 0,
            "page_size": 10,
        }

        params: dict = msg.value

        # warning if unexpected parameters are present
        for k in params.keys():
            if k not in default_params.keys():
                log.warning(f"Unexpected parameter '{k}' in request. Ignoring it.")

        # merge default and user parameters
        params = {**default_params, **params}

        # check 'page' and 'page_size' are in the params dict
        try:
            if "page" not in params or "page_size" not in params:
                raise ValueError("params must contain 'page' and 'page_size'")
            if params["page"] < 0:
                raise ValueError("page must be >= 0")
            if params["page_size"] < 0:
                raise ValueError("page_size must be >= 0")

            page = params["page"]
            page_size = params["page_size"]
            offset = page * page_size

            cursor = self._mariadb_connection.cursor()
            cursor.execute("SELECT * FROM KIOptiPackProcessed LIMIT %s OFFSET %s", (page_size, offset))
            page_documents = cursor.fetchall()
            cursor.close()

            # drop id column
            page_documents = [dict(row) for row in page_documents]
            for row in page_documents:
                del row["id"]

        except Exception as e:
            log.error(f"Error while counting processed data points in {self._DB_NAME}: {e}")
            return error_response_thing(exception=e, fiot_service=self)

        return ok_response_thing(payload=page_documents, fiot_service=self)


if __name__ == '__main__':
    # Change this to reduce verbosity or remove completely to use `FASTIOT_LOG_LEVEL` environment variable to configure
    # logging.
    logging.basicConfig(level=logging.DEBUG)
    DatabaseMariaService.main()

"""
This file has just been created automatically.
This is the file where you can write you own service.
Currently, the is code provides a basic producer and an basic consumer.
In order for your code to work, you must delete the code that you are not using and add your own application logic.
"""

import asyncio
import logging
import random

from sqlalchemy import create_engine, Table, Column, Integer, MetaData, String
from sqlalchemy.orm import declarative_base, sessionmaker

from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_broker_facade import db_ok_response_thing, db_error_response_thing
from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_subjects_name import SAVE_MANY_RAW_DATA_SUBJECT_NAME, \
    DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT
from src.blueprint_dev_v2.logger.logger import log
from datetime import datetime

from fastiot.core import FastIoTService, Subject, subscribe, loop, reply, ReplySubject
from fastiot.core.core_uuid import get_uuid
from fastiot.core.time import get_time_now
from fastiot.db.mariadb_helper_fn import get_mariadb_client_from_env
from fastiot.msg.thing import Thing

Base = declarative_base()


class DatabaseMariaService(FastIoTService):

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
        log.info("MariaDB-Service stopped")
        self._mariadb_connection.close()

    async def _start(self):
        log.info("MariaDB-Service started")

        cursor = self._mariadb_connection.cursor()
        try:
            # create table if not exists. table-name: KIOptiPackRaw
            # NOTE: replace the table name with your own table name
            no_affected_rows = cursor.execute("CREATE TABLE IF NOT EXISTS KIOptiPackRaw("
                                              "id INT(11) PRIMARY KEY AUTO_INCREMENT,"
                                              "material_id VARCHAR(36),"
                                              "datum VARCHAR(36),"
                                              "laborant VARCHAR(16),"
                                              "rohwert_1_labormessung FLOAT(12),"
                                              "rohwert_2_labormessung FLOAT(12),"
                                              "rohwert_3_labormessung FLOAT(12),"
                                              "aufbereiteter_wert FLOAT(12));"
                                              )
            log.info("MariaDB-Table created successfully")
        except Exception as e:
            log.error(f"Error while creating MariaDB-Table: {e}")
            raise e
        finally:
            cursor.close()

    @reply(DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT)
    async def db_save_many_raw_datapoints(self, topic: str, msg: Thing) -> Thing:
        if not isinstance(msg.value, list):
            log.error(f"Payload (the 'value' field of the msg Thing) must be of type list, "
                      f"but received: {type(msg.value)}")
            raise ValueError("Payload must be a list of raw data points")

        data_points: list[dict] = msg.value
        log.info(f"Received {len(data_points)} raw data points to be inserted into MariaDB")

        # self._mariadb_client.

        log.info(f"Insering data points into mariaDB")

        cursor = self._mariadb_connection.cursor()
        res = None
        try:
            no_rows = cursor.executemany(
                "INSERT INTO KIOptiPackRaw (material_id, datum, laborant, rohwert_1_labormessung, "
                "rohwert_2_labormessung, rohwert_3_labormessung, aufbereiteter_wert) "
                "VALUES (%(material_id)s, %(datum)s, %(laborant)s, %(rohwert_1_labormessung)s, "
                "%(rohwert_2_labormessung)s, %(rohwert_3_labormessung)s, %(aufbereiteter_wert)s)",
                data_points
            )
            self._mariadb_connection.commit()
            log.info(f"DB transaction result: {no_rows}")
            log.info(f"Inserted {no_rows} data points into MariaDB")

            # feel free to include whatever information you want to return here.
            res = {
                "acknowledged": True,
                "db": "MariaDB",
                "no_rows": no_rows,
            }

            # in principle one does not need to return information here.
            # However, some infos are return here, so that the requesting service can log the information.
            return db_ok_response_thing(payload=res, fiot_service=self)
        except Exception as e:
            log.error(f"Error while inserting data points into MariaDB: {e}")
            return db_error_response_thing(exception=e, fiot_service=self)
        finally:
            cursor.close()


if __name__ == '__main__':
    # Change this to reduce verbosity or remove completely to use `FASTIOT_LOG_LEVEL` environment variable to configure
    # logging.
    logging.basicConfig(level=logging.DEBUG)
    DatabaseMariaService.main()

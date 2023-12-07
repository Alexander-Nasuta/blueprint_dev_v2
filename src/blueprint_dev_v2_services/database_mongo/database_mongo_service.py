"""
This file has just been created automatically.
This is the file where you can write you own service.
Currently, the is code provides a basic producer and an basic consumer.
In order for your code to work, you must delete the code that you are not using and add your own application logic.
"""

import asyncio
import logging
import random

from datetime import datetime

from fastiot.core import FastIoTService, Subject, subscribe, loop, reply, ReplySubject
from fastiot.core.core_uuid import get_uuid
from fastiot.core.time import get_time_now
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.msg.thing import Thing
from pymongo.results import InsertManyResult

from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_broker_facade import db_ok_response_thing
from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_error_handling import propagate_errors_via_broker
from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_subjects_name import SAVE_MANY_RAW_DATA_SUBJECT_NAME, \
    DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT

from src.blueprint_dev_v2.logger.logger import log


class DatabaseMongoService(FastIoTService):
    """
    This service is responsible for storing and retrieving data from the database.
    It implements the CRUD operations (create, read, update, delete) and provides these functionalities to other
    services via the broker.
    """
    _MONGO_DB = "KIOptiPackDb"
    _MONGO_RAW_DATA_COLLECTION = "KIOptiPackRaw"
    _MONGO_PROCESSED_DATA_COLLECTION = "KIOptiPackProcessed"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mongodb_client = get_mongodb_client_from_env()
        self._db = self._mongodb_client[self._MONGO_DB]

        self._raw_data_collection = self._db[self._MONGO_RAW_DATA_COLLECTION]
        # self._processed_data_collection = self._db[self._MONGO_PROCESSED_DATA_COLLECTION]
        # self._trained_model_collection = self._db[self._MONGO_TRAINED_MODEL_COLLECTION]

    @reply(DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT)
    async def db_save_many_raw_datapoints(self, topic: str, msg: Thing) -> Thing:
        if not isinstance(msg.value, list):
            log.error(f"Payload (the 'value' field of the msg Thing) must be of type list, "
                      f"but received: {type(msg.value)}")
            raise ValueError("Payload must be a list of raw data points")

        data_points: list[dict] = msg.value
        log.info(f"Received {len(data_points)} raw data points to be inserted into mongodb")

        log.info(f"Insering data points into mongodb")
        res: InsertManyResult = self._raw_data_collection.insert_many(data_points)
        log.info(f"DB transaction result: {res.acknowledged}")

        log.info(f"Inserted {len(res.inserted_ids)} raw data points into mongodb")

        # feel free to include whatever information you want to return here.
        db_specific_info = {
            "acknowledged": True,
            "db": "MongoDB",
        }

        # in principle one does not need to return information here.
        # However, some infos are return here, so that the requesting service can log the information.
        return db_ok_response_thing(payload=db_specific_info, fiot_service=self)


if __name__ == '__main__':
    # Change this to reduce verbosity or remove completely to use `FASTIOT_LOG_LEVEL` environment variable to configure
    # logging.
    logging.basicConfig(level=logging.DEBUG)
    DatabaseMongoService.main()

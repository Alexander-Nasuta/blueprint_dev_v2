"""
This file has just been created automatically.
This is the file where you can write you own service.
Currently, the is code provides a basic producer and an basic consumer.
In order for your code to work, you must delete the code that you are not using and add your own application logic.
"""

import asyncio
import logging
import random
import uuid

from datetime import datetime

from fastiot.core import FastIoTService, Subject, subscribe, loop, reply, ReplySubject
from fastiot.core.core_uuid import get_uuid
from fastiot.core.time import get_time_now
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.msg.thing import Thing
from pymongo import UpdateOne
from pymongo.results import InsertManyResult, BulkWriteResult

from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_broker_facade import ok_response_thing, error_response_thing
from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_error_handling import propagate_errors_via_broker
from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_subjects_name import _SAVE_MANY_RAW_DATA_SUBJECT_NAME, \
    DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT, _GET_ALL_RAW_DATA_SUBJECT_NAME, DB_GET_ALL_RAW_DATA_SUBJECT, \
    DB_UPSERT_MANY_PROCESSED_DATAPOINTS_SUBJECT, DB_GET_PROCESSED_DATA_COUNT_SUBJECT, DB_GET_PROCESSED_DATA_PAGE_SUBJECT

from src.blueprint_dev_v2.logger.logger import log


class DatabaseMongoService(FastIoTService):
    _DB_NAME = "mongodb"

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
        self._processed_data_collection = self._db[self._MONGO_PROCESSED_DATA_COLLECTION]
        # self._trained_model_collection = self._db[self._MONGO_TRAINED_MODEL_COLLECTION]

    @reply(DB_SAVE_MANY_RAW_DATAPOINTS_SUBJECT)
    async def db_save_many_raw_datapoints(self, topic: str, msg: Thing) -> Thing:
        if not isinstance(msg.value, list):
            log.error(f"Payload (the 'value' field of the msg Thing) must be of type list, "
                      f"but received: {type(msg.value)}")
            raise ValueError("Payload must be a list of raw data points")

        data_points: list[dict] = msg.value
        log.info(f"Received {len(data_points)} raw data points to be inserted into mongodb")

        # add uuids to data points
        for data_point in data_points:
            data_point["_id"] = str(uuid.uuid4())

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
        return ok_response_thing(payload=db_specific_info, fiot_service=self)

    @reply(DB_UPSERT_MANY_PROCESSED_DATAPOINTS_SUBJECT)
    async def db_save_upsert_processed_datapoints(self, topic: str, msg: Thing) -> Thing:

        if not isinstance(msg.value, list):
            log.error(f"Payload (the 'value' field of the msg Thing) must be of type list, "
                      f"but received: {type(msg.value)}")
            raise ValueError("Payload must be a list of processed data points")

        data_points: list[dict] = msg.value
        log.info(f"Received {len(data_points)} processed data points to be inserted into mongodb")

        log.info(f"Upserting data points into mongodb using bulk wirte")
        # Prepare a list of UpdateOne operations
        operations = [
            UpdateOne(
                {"_id": data_point["_id"]},  # filter
                {"$set": data_point},  # update
                upsert=True  # upsert
            )
            for data_point in data_points
        ]
        try:
            res: BulkWriteResult = self._processed_data_collection.bulk_write(operations)
        except Exception as e:
            log.error(f"Error while upserting processed data points into mongodb: {e}")
            return error_response_thing(exception=e, fiot_service=self)
        log.info(f"DB transaction result: {res.acknowledged}")

        # feel free to include whatever information you want to return here.
        db_specific_info = {
            "acknowledged": True,
            "db": "MongoDB",
        }

        # in principle one does not need to return information here.
        # However, some infos are return here, so that the requesting service can log the information.
        return ok_response_thing(payload=db_specific_info, fiot_service=self)

    @reply(DB_GET_ALL_RAW_DATA_SUBJECT)
    async def get_all_raw_data(self, topic: str, msg: Thing) -> Thing:
        log.info("Received request to get all raw data from mongodb")

        filter_kwargs = {}  # empty dict means no filter
        raw_data_entries = self._raw_data_collection.find()
        raw_data_entries = [dict(data) for data in raw_data_entries]

        # the native mongo ID is not serializable to json
        # so we convert it to a string
        for data in raw_data_entries:
            data["_id"] = str(data["_id"])


        return ok_response_thing(payload=raw_data_entries, fiot_service=self)

    @reply(DB_GET_PROCESSED_DATA_COUNT_SUBJECT)
    async def get_processed_data_count(self, topic: str, msg: Thing) -> Thing:
        log.info("Received request to get the number of processed data points from mongodb")

        try:
            count = self._processed_data_collection.count_documents({})
        except Exception as e:
            log.error(f"Error while counting processed data points in mongodb: {e}")
            return error_response_thing(exception=e, fiot_service=self)

        return ok_response_thing(payload=count, fiot_service=self)

    @reply(DB_GET_PROCESSED_DATA_PAGE_SUBJECT)
    async def get_processed_data_page(self, topic: str, msg: Thing) -> Thing:
        log.debug(f"Received request to get a page of processed data points from {self._DB_NAME}")
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

            page_documents = self._processed_data_collection.find() \
                .skip(params["page"] * params["page_size"]) \
                .limit(params["page_size"])
            res = [dict(doc) for doc in page_documents]
            # drop the native mongo ID
            for doc in res:
                doc.pop("_id", None)

        except Exception as e:
            log.error(f"Error while counting processed data points in mongodb: {e}")
            return error_response_thing(exception=e, fiot_service=self)

        return ok_response_thing(payload=res, fiot_service=self)




if __name__ == '__main__':
    # Change this to reduce verbosity or remove completely to use `FASTIOT_LOG_LEVEL` environment variable to configure
    # logging.
    logging.basicConfig(level=logging.DEBUG)
    DatabaseMongoService.main()

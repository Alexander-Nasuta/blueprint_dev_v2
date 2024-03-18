import asyncio
from asyncio import Future

from fastiot.core import FastIoTService, ReplySubject
from fastiot.msg import Thing

from datetime import datetime

from blueprint_dev_v2.logger.logger import log
from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_subjects_name import _SAVE_MANY_RAW_DATA_SUBJECT_NAME, \
    _GET_ALL_RAW_DATA_SUBJECT_NAME, _UPSERT_MANY_PROCESSED_DATA_SUBJECT_NAME, DB_GET_PROCESSED_DATA_COUNT_SUBJECT, \
    _GET_PROCESSED_DATA_COUNT_SUBJECT_NAME, DB_GET_PROCESSED_DATA_PAGE_SUBJECT, _GET_PROCESSED_DATA_PAGE_SUBJECT_NAME, \
    _PROCESS_RAW_DATA_SUBJECT_NAME, _PREDICT_SUBJECT_NAME


def ok_response_thing(payload: dict | list, fiot_service: FastIoTService) -> Thing:
    return Thing(
        machine=f'{fiot_service.__class__.__name__}',
        name="",
        value=payload,
        timestamp=datetime.now()
    )


def error_response_thing(exception: Exception, fiot_service: FastIoTService) -> Thing:
    error_info_dict = {
        "__error_occured__": True,
        "error_type": type(exception).__name__,
        "error_msg": str(exception),
        "error_args": exception.args,
    }
    return Thing(
        machine=f'{fiot_service.__class__.__name__}',
        name="",
        value=error_info_dict,
        timestamp=datetime.now()
    )


async def request_replysubject_thing_wrapper(fiot_service: FastIoTService, data: dict | list[dict],
                                             subject: str, timeout: float) -> Future[
    dict | list[dict] | int | float | str | None]:
    if not isinstance(data, dict) and not isinstance(data, list):
        raise TypeError("The data parameter has to be a dict or a list of dicts.")

    payload = Thing(
        machine=f'{fiot_service.__class__.__name__}',
        name="",
        value=data,
        timestamp=datetime.now()
    )
    # subject = ReplySubject(name="reply", msg_cls=Thing, reply_cls=Thing)
    subject = ReplySubject(name=subject, msg_cls=Thing, reply_cls=Thing)

    log.debug(f"Sending reply-subject request to broker (subject={subject.name}, requesting service={payload.machine})")
    # asyncio.ensure_future does not work here. It has to be awaited.
    response_thing = await fiot_service.broker_connection.request(subject=subject, msg=payload, timeout=timeout)

    if isinstance(response_thing.value, dict) and "__error_occured__" in response_thing.value.keys():
        log.error(f"Error occured while requesting service: {response_thing.value}")
        error_type = response_thing.value["error_type"]
        error_args = response_thing.value["error_args"]
        raise globals()[error_type](*error_args) from None
    return response_thing.value


async def request_save_many_raw_data_points(fiot_service: FastIoTService, data: list[dict],
                                            timeout: float = 10) -> Future[dict | list[dict]]:
    if not isinstance(data, list):
        raise TypeError("The data parameter has to be a list of dicts.")
    # asyncio.ensure_future does not work here. It has to be awaited.
    return await request_replysubject_thing_wrapper(
        fiot_service=fiot_service,
        data=data,
        subject=_SAVE_MANY_RAW_DATA_SUBJECT_NAME,  # same as the string "save-many-raw-datapoints"
        timeout=timeout,  # default is 10
    )


async def request_upsert_many_processed_data_points(fiot_service: FastIoTService, data: list[dict],
                                                    timeout: float = 10) -> Future[dict | list[dict]]:
    if not isinstance(data, list):
        raise TypeError("The data parameter has to be a list of dicts.")
    # asyncio.ensure_future does not work here. It has to be awaited.
    return await request_replysubject_thing_wrapper(
        fiot_service=fiot_service,
        data=data,
        subject=_UPSERT_MANY_PROCESSED_DATA_SUBJECT_NAME,  # same as the string "save-many-raw-datapoints"
        timeout=timeout,  # default is 10
    )


async def request_get_all_raw_data_points(fiot_service: FastIoTService,
                                          timeout: float = 10) -> Future[dict | list[dict]]:
    return await request_replysubject_thing_wrapper(
        fiot_service=fiot_service,
        data={},
        subject=_GET_ALL_RAW_DATA_SUBJECT_NAME,  # same as the string "get-all-raw-datapoints"
        timeout=timeout,  # default is 10
    )


async def request_get_all_processed_data_points(fiot_service: FastIoTService,
                                                timeout: float = 10) -> Future[dict | list[dict]]:
    return await request_replysubject_thing_wrapper(
        fiot_service=fiot_service,
        data={},
        subject=_GET_ALL_RAW_DATA_SUBJECT_NAME,  # same as the string "get-all-raw-datapoints"
        timeout=timeout,  # default is 10
    )


# pagination requests
async def request_get_processed_data_points_count(fiot_service: FastIoTService,
                                                  timeout: float = 10) -> Future[int]:
    return await request_replysubject_thing_wrapper(
        fiot_service=fiot_service,
        data={},
        subject=_GET_PROCESSED_DATA_COUNT_SUBJECT_NAME,  # same as the string "get-all-raw-datapoints"
        timeout=timeout,  # default is 10
    )


async def request_get_processed_data_points_page(fiot_service: FastIoTService, page: int = 0, page_size: int = 10,
                                                 timeout: float = 10) -> Future[list[dict]]:
    return await request_replysubject_thing_wrapper(
        fiot_service=fiot_service,
        data={
            "page": page,
            "page_size": page_size,
        },
        subject=_GET_PROCESSED_DATA_PAGE_SUBJECT_NAME,  # same as the string "get-all-raw-datapoints"
        timeout=timeout,  # default is 10
    )


async def request_get_processed_data_points_from_raw_data(fiot_service: FastIoTService, data: dict,
                                                          timeout: float = 10) -> Future[list[dict]]:
    return await request_replysubject_thing_wrapper(
        fiot_service=fiot_service,
        data=data,
        subject=_PROCESS_RAW_DATA_SUBJECT_NAME,  # same as the string "get-all-raw-datapoints"
        timeout=timeout,  # default is 10
    )


async def request_get_prediction(fiot_service: FastIoTService, data: dict,
                                                          timeout: float = 10) -> Future[list[dict]]:
    return await request_replysubject_thing_wrapper(
        fiot_service=fiot_service,
        data=data,
        subject=_PREDICT_SUBJECT_NAME,  # same as the string "get-all-raw-datapoints"
        timeout=timeout,  # default is 10
    )

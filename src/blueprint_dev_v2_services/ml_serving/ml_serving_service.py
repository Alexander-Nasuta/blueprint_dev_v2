"""
This file has just been created automatically.
This is the file where you can write you own service.
Currently, the is code provides a basic producer and an basic consumer.
In order for your code to work, you must delete the code that you are not using and add your own application logic.
"""

import asyncio
import logging
import random
from asyncio import Future
from typing import Coroutine, List

from fastiot.core import FastIoTService, Subject, subscribe, loop, reply
from fastiot.core.core_uuid import get_uuid
from fastiot.core.time import get_time_now
from fastiot.msg.thing import Thing

import torch
import torch.nn as nn
import numpy as np
import pandas as pd

from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_broker_facade import \
    request_get_processed_data_points_from_raw_data, ok_response_thing, error_response_thing
from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_subjects_name import ML_SERVING_SUBJECT
from blueprint_dev_v2_services.ml_pytorch_regression.ml_pytorch_regression_service import DemonstratorNeuralNet
from src.blueprint_dev_v2.logger.logger import log


class MlServingService(FastIoTService):
    _regression_model = None

    _example_raw_payload = {
        'laborant': "TK",
        'material_id': "11111111",
        'datum': "15.03.2024, 16:14:48",
        'rohwert_1_labormessung': 22.64237723051251,
        'rohwert_2_labormessung': 0.55194,
        'rohwert_3_labormessung': -0.472279,
        'aufbereiteter_wert''': 0.287696
    }

    async def _start(self):
        log.info("MlPytorchRegressionService started")
        await self._setup_model()

    async def _setup_model(self):
        log.info("Setting up Demonstrator Regression model")

        self._regression_model = DemonstratorNeuralNet(
            input_dim=15,
            hidden_dim=10,
            output_dim=1
        )

        # Load model weights
        await self._load_model_weights_wandb()

        # test model with example payload
        _ = await self._get_prediction(
            raw_datapoints=[
                self._example_raw_payload,
                self._example_raw_payload,
                self._example_raw_payload,
            ]
        )

    async def _load_model_weights_wandb(self):
        log.info("Loading model weights from wandb")

        import wandb

        # Create a new API object
        api = wandb.Api()

        # Get all the artifacts of a specific project
        wandb_config = {
            "entity": "querry",  # Replace with your username
            "project": "KIOptipack-dev",  # Replace with your project name
            "name": "model_4c7eb0ae-2dc6-49f5-a179-605a89",  # Replace with your artifact name
            "version": "v6",
            "group": "MVDP-pytorch-regression",
            "model_type": "pytorch-regression-model",
        }
        artifact = api.artifact("querry/KIOptipack-dev/DemonstratorNeuralNet:latest")
        log.info(f"Downloading model weights for model '{artifact.metadata['model_name']}'")
        artifact.download()

        model_name = artifact.metadata["model_name"]
        model_version = artifact.version
        path = f"./artifacts/DemonstratorNeuralNet:{model_version}/{model_name}"
        if self._regression_model is None:
            raise ValueError("Regression model not initialized. Please call _setup_model() first.")
        self._regression_model.load_state_dict(
            torch.load(f"./artifacts/DemonstratorNeuralNet:{model_version}/{model_name}"))

    async def _process_raw_data_points(self, data: list[dict]) -> Future[list[dict]]:
        log.info(f"Processing raw data points, received")
        return await request_get_processed_data_points_from_raw_data(
            fiot_service=self,
            data=data,
        )

    async def _get_prediction(self, raw_datapoints: list[dict]) -> Future[list[list[float]]]:
        if self._regression_model is None:
            raise ValueError("Regression model not initialized. Please call _setup_model() first.")

        processed_data = await self._process_raw_data_points(data=raw_datapoints)
        temp = pd.DataFrame(processed_data)
        _ = np.array([temp.pop("aufbereiteter_wert")])
        x_data = temp.to_numpy()

        prediction = self._regression_model(torch.tensor(x_data, dtype=torch.float32))
        return prediction.tolist()

    @reply(ML_SERVING_SUBJECT)
    async def prediction(self, topic: str, msg: Thing) -> Thing:
        if not isinstance(msg.value, list):
            log.error(f"Payload (the 'value' field of the msg Thing) must be of type list, "
                      f"but received: {type(msg.value)}")
            raise ValueError("Payload must be a list of raw data points")

        raw_data_points: list[dict] = msg.value

        try:
            res:list[list[float]] = await self._get_prediction(raw_datapoints=raw_data_points)

            return ok_response_thing(payload=res, fiot_service=self)

        except Exception as e:
            log.error(f"Error while processing raw data points: {e}")
            return error_response_thing(exception=e, fiot_service=self)


if __name__ == '__main__':
    # Change this to reduce verbosity or remove completely to use `FASTIOT_LOG_LEVEL` environment variable to configure
    # logging.
    logging.basicConfig(level=logging.DEBUG)
    MlServingService.main()

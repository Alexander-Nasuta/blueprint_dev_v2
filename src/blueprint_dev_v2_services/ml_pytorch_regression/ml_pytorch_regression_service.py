"""
This file has just been created automatically.
This is the file where you can write you own service.
Currently, the is code provides a basic producer and an basic consumer.
In order for your code to work, you must delete the code that you are not using and add your own application logic.
"""

import asyncio
import logging
import uuid

import wandb
import random

import torch

import numpy as np
import pandas as pd

from fastiot.core import FastIoTService, Subject, subscribe, loop
from fastiot.core.core_uuid import get_uuid
from fastiot.core.time import get_time_now
from fastiot.msg.thing import Thing
from rich.progress import Progress
from torch.utils.data import Dataset

from blueprint_dev_v2.ml_lifecycle_utils.ml_lifecycle_broker_facade import request_get_processed_data_points_count, \
    request_get_all_raw_data_points, request_get_processed_data_points_page
from src.blueprint_dev_v2.logger.logger import log

from torch import nn, optim


class DemonstratorNeuralNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer_1 = nn.Linear(input_dim, hidden_dim)
        self.layer_2 = nn.Linear(hidden_dim, hidden_dim)
        self.layer_3 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = torch.relu(self.layer_1(x))
        x = torch.relu(self.layer_2(x))
        x = self.layer_3(x)
        return x


class PageDataset(Dataset):
    _page_size: int
    _total_pages: int
    _num_entries_in_db: int
    _current_page: int

    _fast_iot_service: FastIoTService
    _broker_timeout: float

    _page_df: pd.DataFrame

    def __init__(self, fast_iot_service: FastIoTService, page_size: int, broker_timeout=10):
        self._fast_iot_service = fast_iot_service
        self._broker_timeout = broker_timeout

        self._page_size = page_size

    def __len__(self):
        return len(self._page_df)

    async def _init_total_pages(self):
        # count
        count: int = await request_get_processed_data_points_count(fiot_service=self._fast_iot_service)
        self._num_entries_in_db = count
        self._total_pages = int(np.ceil(self._num_entries_in_db / self._page_size))

    async def _get_page_df(self, page: int) -> pd.DataFrame:
        # query the db_service for the number of raw data points
        page: list[dict] = await request_get_processed_data_points_page(fiot_service=self._fast_iot_service, page=page,
                                                                        page_size=self._page_size)
        return pd.DataFrame(page)

    async def init_dataset(self):
        # init total number of pages
        await self._init_total_pages()
        df = await self._get_page_df(page=0)
        self._page_df = df
        self._current_page = 0

    def has_next_page(self):
        return self._current_page < self._total_pages

    @property
    def num_pages(self):
        if self._total_pages is None:
            log.warn("total pages not initialized. init_page() needs to called and awaited first.")
        return self._total_pages

    async def load_next_page(self):
        if self._current_page is None:
            log.error("page not initialized. init_page() needs to called and awaited first.")
            raise ValueError("page not initialized. init_page() needs to called and awaited first.")

        if self._current_page >= self._total_pages:
            log.error("no more pages available")
            raise ValueError("no more pages available")

        self._current_page += 1
        df = await self._get_page_df(page=self._current_page)
        self._page_df = df

    def __getitem__(self, idx):  # idx means index of the chunk.
        # drop index column
        temp = self._page_df
        temp = temp.iloc[idx]

        y_data = np.array([temp.pop("aufbereiteter_wert")])
        x_data = temp.to_numpy()

        # The following condition is actually needed in Pytorch. Otherwise, for our particular example,
        # the iterator will be an infinite loop.
        # Readers can verify this by removing this condition.
        if idx == self.__len__():
            raise IndexError

        return x_data, y_data


class MlPytorchRegressionService(FastIoTService):

    async def _start(self):
        log.info("MlPytorchRegressionService started")

        # the following requests are needed for the custom dataset
        # you can comment the m in to see if they are working
        # count: int = await request_get_processed_data_points_count(fiot_service=self)
        # page = await request_get_processed_data_points_page(fiot_service=self, page=0, page_size=10)
        # pageDataset = PageDataset(fast_iot_service=self, page_size=10)
        # await pageDataset.init_dataset()
        # await pageDataset.load_next_page()

    async def _stop(self):
        log.info("MlPytorchRegressionService stopped")

    def get_model(self) -> DemonstratorNeuralNet:
        return DemonstratorNeuralNet(
            input_dim=15,
            hidden_dim=10,
            output_dim=1
        )

    @loop
    async def training_loop(self):
        model = self.get_model()
        loss_fn = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        dataset = PageDataset(fast_iot_service=self, page_size=10)

        # await self.train_model_without_experiment_tracking(dataset, model, loss_fn, optimizer)
        await self.train_model_with_wandb_tracking(dataset, model, loss_fn, optimizer)

        return asyncio.sleep(24 * 60 * 60)

    async def train_model_without_experiment_tracking(self, dataset: PageDataset, model: DemonstratorNeuralNet,
                                                      loss_fn: nn.MSELoss,
                                                      optimizer: optim.Adam, epochs: int = 5, batch_size: int = 5,
                                                      shuffle: bool = True):
        log.info("Starting training loop without experiment tracking.")
        await dataset.init_dataset()
        progress = Progress()
        total_steps = dataset.num_pages * epochs
        task_id = progress.add_task("[cyan]Training...", total=total_steps)

        with progress:
            for page in range(dataset.num_pages):
                # define pytorch data loader
                data_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

                # define pytorch training loop
                for epoch in range(epochs):
                    for batch_idx, (x, y) in enumerate(data_loader):
                        optimizer.zero_grad()
                        y_pred = model(x.to(torch.float32)).to(torch.float32)
                        # loss = loss_fn(y_pred, y.to(torch.float32))
                        # loss.backward()
                        # optimizer.step()
                        # log.info(f"page: {page}, epoch: {epoch}, batch_idx: {batch_idx}, loss: {loss.item()}")
                    progress.update(task_id, advance=1)

                await dataset.load_next_page()

        log.info("Training loop without experiment tracking completed.")
        # save model
        # here you can implement a saving mechanism for the model

    async def train_model_with_wandb_tracking(self, dataset: PageDataset, model: DemonstratorNeuralNet,
                                              loss_fn: nn.MSELoss, optimizer: optim.Adam, epochs: int = 5,
                                              batch_size: int = 5, shuffle: bool = True):
        log.info("Starting training loop with wandb tracking.")
        await dataset.init_dataset()
        progress = Progress()
        total_steps = dataset.num_pages * epochs
        task_id = progress.add_task("[cyan]Training", total=total_steps)

        # Initialize a new wandb run
        config_dict = {
            "epochs": epochs,
            "batch_size": batch_size,
            "shuffle": shuffle,
            "optimizer": str(optimizer),
            "loss_function": str(loss_fn)
        }
        run_id = uuid.uuid4()
        wandb_run = wandb.init(
            project="KIOptipack-dev",
            config=config_dict,
            group="MVDP-pytorch-regression",
            name=f"run_{run_id}",
        )

        # Log gradients and model parameters
        wandb.watch(model)

        with progress:
            optimizer_step = 0
            for page in range(dataset.num_pages):
                # define pytorch data loader
                data_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

                # define pytorch training loop
                for epoch in range(epochs):
                    for batch_idx, (x, y) in enumerate(data_loader):
                        optimizer.zero_grad()
                        y_pred = model(x.to(torch.float32)).to(torch.float32)
                        loss = loss_fn(y_pred, y.to(torch.float32))
                        loss.backward()
                        optimizer.step()
                        # Log metrics with wandb
                        wandb.log({
                            "loss": loss.item(),
                            "epoch": epoch,
                            "page": page,
                            "optimizer_step": optimizer_step
                        })
                        log.debug(f"page: {page}, epoch: {epoch}, batch_idx: {batch_idx}, loss: {loss.item()}")

                        optimizer_step += 1
                    progress.update(task_id, advance=1, )

                await dataset.load_next_page()

        log.info("Training loop with wandb tracking completed.")
        # save model
        model_name = f"model_{run_id}.pth"
        torch.save(model.state_dict(), model_name)
        artifact = wandb.Artifact(
            f'DemonstratorNeuralNet',
            incremental=True,
            type='pytorch-regression-model',
            description="Pytorch regression model, saved using the state_dict method.",
            metadata={
                "run_id": run_id,
                "model_name": model_name,
                "class": model.__class__.__name__,
                "input_dim": model.layer_1.in_features,
                "output_dim": model.layer_3.out_features,
            }
        )
        artifact.add_file(model_name)
        wandb_run.log_artifact(artifact)
        # Finish the wandb run
        wandb_run.finish()

        # delete to local model file
        try:
            import os
            os.remove(model_name)
        except Exception as e:
            log.warning(f"Error while deleting local model file: {e}")


if __name__ == '__main__':
    # Change this to reduce verbosity or remove completely to use `FASTIOT_LOG_LEVEL` environment variable to configure
    # logging.
    logging.basicConfig(level=logging.DEBUG)
    MlPytorchRegressionService.main()

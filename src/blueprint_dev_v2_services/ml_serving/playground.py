import wandb
import pandas as pd
import numpy as np
import torch
import torch.nn as nn

from blueprint_dev_v2_services.ml_pytorch_regression.ml_pytorch_regression_service import DemonstratorNeuralNet

if __name__ == '__main__':
    api = wandb.Api()
    # Get the artifact
    wandb_config = {
        "entity": "querry",  # Replace with your username
        "project": "KIOptipack-dev",  # Replace with your project name
        "name": "model_4c7eb0ae-2dc6-49f5-a179-605a89",  # Replace with your artifact name
        "version": "v6",
        "group": "MVDP-pytorch-regression",
        "model_type": "pytorch-regression-model",
    }
    # artifact = api.artifact("querry/KIOptipack-dev/model_5ab8b873-0ea5-463a-b75d-33004cbaf4ba:v0")
    # Download the artifact to a directory
    # artifact.download()

    import wandb

    # Create a new API object
    api = wandb.Api()

    # Get all the artifacts of a specific project
    artifact = api.artifact("querry/KIOptipack-dev/DemonstratorNeuralNet:latest")
    print(artifact.metadata["model_name"])
    artifact.download()

    # load model
    import torch

    model_name = artifact.metadata["model_name"]
    model_version = artifact.version
    path = f"./artifacts/DemonstratorNeuralNet:{model_version}/{model_name}"
    print(path)
    model = torch.load(f"./artifacts/DemonstratorNeuralNet:{model_version}/{model_name}")
    # print(model)
    # model_74db7d6e-4e2c-4282-b8d6-24fd790ba514.pth
    # model_74db7d6e-4e2c-4282-b8d6-24fd790ba514.pth
    model = DemonstratorNeuralNet(
        input_dim=15,
        hidden_dim=10,
        output_dim=1
    )
    model.load_state_dict(torch.load(f"./artifacts/DemonstratorNeuralNet:{model_version}/{model_name}"))

    data = [{
        'aufbereiteter_wert': 0.287696,
        'laborant_AN': 0.0,
        'laborant_HANS': 0.0,
        'laborant_SO': 0.0,
        'laborant_TK': 1.0,
        'material_id_00000000': 0.0,
        'material_id_11111111': 1.0,
        'material_id_22222222': 0.0,
        'material_id_33333333': 0.0,
        'rohwert_1_high': 0.0,
        'rohwert_1_low': 0.0,
        'rohwert_1_medium': 0.0,
        'rohwert_1_very_high': 1.0,
        'rohwert_1_very_low': 0.0,
        'rohwert_2_labormessung': 0.55194,
        'rohwert_3_labormessung': -0.472279
    }] * 3

    temp = pd.DataFrame(data)

    y_data = np.array([temp.pop("aufbereiteter_wert")])
    x_data = temp.to_numpy()

    # do a prediction with the model and the data
    prediction = model(torch.tensor(x_data, dtype=torch.float32))
    # prediction to list
    prediction = prediction.tolist()
    print(prediction)





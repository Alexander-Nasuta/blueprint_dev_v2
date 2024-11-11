import pandas as pd
import numpy as np
import torch
import torch.nn as nn


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


def get_model() -> DemonstratorNeuralNet:
    return DemonstratorNeuralNet(
        input_dim=15,
        hidden_dim=10,
        output_dim=1
    )


if __name__ == '__main__':
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
    }] * 13

    temp = pd.DataFrame(data)

    y_data = np.array([temp.pop("aufbereiteter_wert")])
    x_data = temp.to_numpy()

    model = get_model()

    # do a prediction with the model and the data
    prediction = model(torch.tensor(x_data, dtype=torch.float32))
    # prediction to list
    prediction = prediction.tolist()
    print(prediction)

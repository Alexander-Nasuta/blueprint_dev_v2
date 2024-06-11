# ML Training Blueprints

## What are ML Training Blueprints?

ML Training Blueprints are templates for training a ML model in a microservice architecture via the FastIoT framework.
Each blueprint is designed to be an example how to train a specific model type and framework (like for example a regression model in pytorch or a classifier in LightGBM).
Most frameworks have some peculiarities when it comes loading data.
ML Training Blueprints are designed to showcase how one can implement data loading, preprocessing in a microservice architecture.
It also showcases how to train a model and store it in a model repository.

## Pytorch Regression Blueprint (WandB)

```{note}
WandB support might be removed in the future in favor of MLflow.
```

```{index} triple: Pytorch; Regression; WandB;
```

```{raw} html
<span class="index-entry">Pytorch</span>
<span class="index-entry">Regression</span>
<span class="index-entry">WandB</span>
```

```{literalinclude} ../../src/blueprint_dev_v2_services/ml_pytorch_regression/ml_pytorch_regression_service.py
:language: python
:linenos: true
```

## Pytorch Regression Blueprint (MLflow)

```{note}
Make sure to have the MLflow server running before starting the service.
```

```{index} triple: Pytorch; Regression; MLflow;
```

```{raw} html
<span class="index-entry">Pytorch</span>
<span class="index-entry">Regression</span>
<span class="index-entry">MLflow</span>
```

```{literalinclude} ../../src/blueprint_dev_v2_services/ml_pytorch_regression_mlflow/ml_pytorch_regression_mlflow_service.py
:language: python
:linenos: true
```

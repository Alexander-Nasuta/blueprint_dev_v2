# ML Serving Blueprints

## What are ML Serving Blueprints?

Serving Blueprints are templates for a serving a trained model.
Each blueprint is designed to serve a specific model type and framework.
Each blueprint corresponds to a microservice that trains a model.


## Pytorch Regression Serving Blueprint (MLflow)

```{index} triple: Pytorch; Regression; MLflow;
```

```{raw} html
<span class="index-entry">Pytorch</span>
<span class="index-entry">Regression</span>
<span class="index-entry">MLflow</span>
 <span class="index-entry">Serving</span>
```

```{literalinclude} ../../src/blueprint_dev_v2_services/ml_serving_mlflow/ml_serving_mlflow_service.py
:language: python
:linenos: true
```



## Pytorch Regression Serving Blueprint (WandB)

```{note}
WandB support might be removed in the future in favor of MLflow.
```

```{index} single: Pytorch; Regression; WandB; Serving
```

```{raw} html
<span class="index-entry">Pytorch</span>
<span class="index-entry">Regression</span>
<span class="index-entry">WandB</span>
 <span class="index-entry">Serving</span>
```

```{literalinclude} ../../src/blueprint_dev_v2_services/ml_serving/ml_serving_service.py
:language: python
:linenos: true
```

```{index} single: MLflow; Serving
```


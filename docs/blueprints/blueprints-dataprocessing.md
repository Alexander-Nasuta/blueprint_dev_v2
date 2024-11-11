# Data Processing Blueprints

This service is responsible for processing the data.
The Data-Processing-Service defines a data processing pipeline that can be used to preprocess the data before it is used for training the model.
It pulls the raw data from the database regularly, processes it and stores the processed data back in the database.
The service is also used when performing a prediction with the model.
In that case the Model-Serving-Service requests the data from the Data-Processing-Service, processes raw data points, that the Model-Serving-Service provides, and returns the processed data to the Model-Serving-Service.

```{note}
Currently, the data processing service pulls the hole database and processes it.
The broker has currently a limit for the maximum message size.
FastIoT has a feature in development that allows to split the data processing into multiple messages and merge the results.
So in future the maximum message size will not be a problem.
However a sufficiently large database could still cause problems.
The data will eventually not fit into the memory of the data processing service.
Therefore the data processing service will be changed to process the data in chunks in the future.
```

## What are Data Processing Blueprints?

Data Processing Blueprints are templates for a Data-Processing-Service.
As all services in the FastIoT framework, the Data-Processing-Service is a microservice.
It is responsible for processing the data.
The Processing pipeline is just example and should be adapted to the specific use case.
The Pipeline is a scikit-learn [Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html).
The scikit-learn provides tools to process data as numpy arrays.
In the scope of this project, we provide processing steps that work on pandas dataframes.
We believe that pandas is a more verbose and convenient way to work with data.


## Data Processing Blueprint

```{index} triple: Data-Processing; Pandas; scikit-learn pipeline
```

```{raw} html
<span class="index-entry">Data-Processing</span>
```


```{literalinclude} ../../src/blueprint_dev_v2_services/data_processing/data_processing_service.py
:language: python
:linenos: true
```

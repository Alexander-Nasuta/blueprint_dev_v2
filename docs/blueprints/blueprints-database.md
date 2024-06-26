# Database Blueprints

## What are Database Blueprints?

This service is responsible for storing the data and providing it to the other services. It is an abstraction layer between the data and the services that need it. This service is responsible for storing the data and providing it to the other services. It is an abstraction layer between the data and the services that need it. Putting all the DB interactions in one service enables to implement drop in replacements for different databases. 
So the end user can choose between different databases without changing the other services.

## MongoDB Database Blueprint

```{index} single: Database; MongoDB;
```

```{raw} html
<span class="index-entry">Database</span>
<span class="index-entry">MongoDB</span>
```


```{important}
You to setup a username and a password for your MongoDB Instance. 
The service will not work without it even when your MongoDB database does not require authentication.
```

```{note}
Provide the following enviorment variables when starting the service:
 - `FASTIOT_MONGO_DB_USER` 
 - `FASTIOT_MONGO_DB_PASSWORD`
 - `FASTIOT_MONGO_DB_HOST`
 - `FASTIOT_MONGO_DB_PORT`


When using PyCharm, you can set the environment variables in the run configuration (accessible via the dropdown menu of the green play button).
Here is a screenshot of an example configuration:

![Mongo example env config](../_static/mongo_env.png)
```



```{literalinclude} ../../src/blueprint_dev_v2_services/database_mongo/database_mongo_service.py
:language: python
:linenos: true
```

## MariaDB Database Blueprint

```{note}
Provide the following enviorment variables when starting the service:
 - `FASTIOT_MARIA_DB_USER` 
 - `FASTIOT_MARIA_DB_PASSWORD`
 - `FASTIOT_MARIA_DB_HOST`
 - `FASTIOT_MARIA_DB_PORT`

When using PyCharm, you can set the environment variables in the run configuration (accessible via the dropdown menu of the green play button).
Here is a screenshot of an example configuration:

![Mongo example env config](../_static/maria_env.png)
```

```{index} pair: Database; MariaDB;
```

```{raw} html
<span class="index-entry">Database</span>
<span class="index-entry">MariaDB</span>
```

```{literalinclude} ../../src/blueprint_dev_v2_services/database_maria/database_maria_service.py
:language: python
:linenos: true
```

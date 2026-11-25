# spark-deploy-006: Use Jupyter as a client-mode driver

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-004`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## A notebook owns a long-lived driver

Jupyter's web server, kernel and Spark driver are different roles. The browser talks to Jupyter over HTTP/WebSocket. The Python kernel builds a SparkSession and communicates with executors. A working browser session does not establish that executor callbacks can reach that kernel's driver. A browser disconnect does not necessarily stop the kernel or release executor resources.

The notebook profile uses its own prepared image, a writable notebook directory and a private token file. It advertises the service name `notebook`, not the host laptop's loopback address. Its Spark UI is a different published port from the notebook UI. Keep authentication enabled and enter the private token through the login form; do not copy token-bearing URLs into reports.

## Key terms

- **Jupyter server:** The web process the browser reaches over HTTP and WebSocket; it is separate from the kernel and the driver.
- **Kernel:** The Python process that builds the SparkSession and therefore hosts a long-lived client-mode driver.
- **Advertised driver name:** The service name notebook that executors use to reach the kernel's driver instead of the host's loopback address.
- **Login token:** A private credential entered through the login form and never copied into reports as part of a URL.
- **Session release:** Stopping the SparkSession to free executor resources, which a browser disconnect does not do.

## Worked case A: start a prepared session and run one action

Initialize the notebook state as shown in the image-preparation chapter, then:

The prepared session is created by this file, which runs inside the notebook
container:

From [`projects/cluster-lab/app/notebook_session.py`](../projects/cluster-lab/app/notebook_session.py):

```python external
spark = (
    SparkSession.builder.appName("ds60-notebook-session")
    .master("spark://master:7077")
    .config("spark.driver.host", "notebook")
    .config("spark.driver.bindAddress", "0.0.0.0")
    .config("spark.driver.port", "39000")
    .config("spark.driver.blockManager.port", "39001")
    .config("spark.driver.maxResultSize", "1m")
    .getOrCreate()
)
try:
    result = spark.range(100_000, numPartitions=8).selectExpr("sum(id) AS sum_id").first()
    assert result.sum_id == 4_999_950_000
    print({"application_id": spark.sparkContext.applicationId, "sum_id": result.sum_id})
finally:
    spark.stop()
```

`.master("spark://master:7077")` connects to the Standalone master, which makes the
notebook process the client-mode driver. `spark.driver.host` is the name executors
use to call back, `bindAddress` is the local interface it listens on, and the two
fixed ports let the Compose network route those callbacks.

```sh
python3 lab.py --state .notebook-lab up
python3 lab.py --state .notebook-lab notebook
python3 lab.py --state .notebook-lab urls
```

Open the printed notebook URL on loopback. Read the private token from `.notebook-lab/private/notebook-token` locally, without displaying it in shared logs. Create a notebook and copy the complete `app/notebook_session.py` example into a cell. It uses the actual remote master, fixed callback ports and a 1 MiB driver result bound. The expected aggregate is 4999950000 from 100000 rows. The application ID is an observed runtime value, not a fixed teaching constant.

The complete example stops Spark in `finally`. For interactive exploration, separate creation, actions and final cleanup into clearly labeled cells and run the cleanup even when an intermediate cell raises. Save the code and observed application ID beside the result, not an invented success Boolean.

## Worked case B: reproduce a stale-session configuration

```python fragment
# In a kernel that already has a session, this may return that existing session.
same = SparkSession.builder.config("spark.driver.host", "new-name").getOrCreate()
print(same.sparkContext.applicationId)
```

Some deployment settings belong to SparkContext creation. Changing builder text after a session exists does not establish that the live driver moved. Inspect the effective Spark configuration and application ID. Stop the old session, release its resources and create the intended new context. If state remains confusing, restart only the owned kernel and record that lifecycle event.

## Worked example: separate notebook cells for create, act and clean up

```python external
# Cell 1: create
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.master("spark://master:7077")
    .appName("notebook-session")
    .config("spark.driver.host", "notebook")
    .config("spark.driver.bindAddress", "0.0.0.0")
    .config("spark.driver.port", "39000")
    .config("spark.driver.blockManager.port", "39001")
    .config("spark.driver.maxResultSize", "1m")
    .getOrCreate()
)
print(spark.sparkContext.applicationId, spark.sparkContext.uiWebUrl)

# Cell 2: act
total = spark.range(100_000).selectExpr("sum(id) AS s").first()["s"]
assert total == 4_999_950_000

# Cell 3: clean up, run even after an error in cell 2
spark.stop()
```

These cells are shown without output because they require the notebook container and the Standalone master. Cell 1 sets the same creation time settings as app/notebook_session.py: the master URL, the advertised name notebook, the two fixed callback ports and the 1m result bound. Printing the application ID and UI URL immediately ties later evidence to this exact session. Cell 2 runs one action and checks the sum against 4999950000 without collecting rows. Cell 3 exists because a notebook has no finally block across cells; if cell 2 raises, the kernel keeps the driver alive and its executors stay registered until spark.stop runs or the kernel is restarted. Running the cleanup cell after a failure releases the two worker cores so the next session or the bounded job can obtain executors.

## Worked example: which builder settings a running session ignores

```python
CREATION_ONLY = {
    "spark.master",
    "spark.driver.host",
    "spark.driver.port",
    "spark.driver.blockManager.port",
    "spark.driver.memory",
    "spark.executor.memory",
}
live = {"spark.driver.host": "notebook", "spark.app.id": "app-20260115093000-0003"}
requested = {"spark.driver.host": "new-name", "spark.sql.shuffle.partitions": "16"}
for key, value in requested.items():
    if key in CREATION_ONLY and live.get(key) != value:
        print(f"{key}: live value {live[key]!r} kept; stop the session to apply {value!r}")
    else:
        print(f"{key}: runtime SQL setting, spark.conf.set can apply {value!r}")
print("application id unchanged:", live["spark.app.id"])
```

Output from running the block above:

```text
spark.driver.host: live value 'notebook' kept; stop the session to apply 'new-name'
spark.sql.shuffle.partitions: runtime SQL setting, spark.conf.set can apply '16'
application id unchanged: app-20260115093000-0003
```

The sets here are a teaching summary written for this example, not a list read from Spark. The script compares builder settings requested after a session exists with the live values. spark.driver.host was fixed when the SparkContext was created, so getOrCreate returns the old session and the requested new-name has no effect; the message says the session must stop for the value to apply. spark.sql.shuffle.partitions is a runtime SQL setting that spark.conf.set can change on the live session. The unchanged application ID is the quickest evidence that no new driver was created. In a real kernel, read spark.sparkContext.getConf().get('spark.driver.host') and compare it with what you asked for instead of trusting the builder text in the cell.

## Diagnose and transfer

A `jupyter` executable missing at container startup means the notebook image was not actually prepared. Installing a package in a notebook kernel does not install it in executor images. A token login failure is unrelated to Spark RPC authentication. A UI port conflict can make Spark choose another port unless the configuration refuses retries; discover the actual UI rather than assuming 4040 always won.

In Kubernetes the notebook needs a driver Service and an explicit Pod identity for executor ownership. The later client-mode chapter adds those mechanisms. A publicly exposed notebook requires a reviewed authentication/TLS deployment; this loopback lab is not that deployment.

## Primary references

- [Jupyter Server authentication](https://jupyter-server.readthedocs.io/en/latest/operators/security.html)
- [Spark configuration lifecycle](https://spark.apache.org/docs/4.0.1/configuration.html)

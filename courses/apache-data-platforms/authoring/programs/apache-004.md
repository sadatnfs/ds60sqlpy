# Actual namespace and Flight observations

From the repository root, copy the complete project into a fresh owned location.
Prepare the native `data-platforms-python` image as documented in its README.

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/arrow-flight work/arrow-flight
cd work/arrow-flight
bash run.sh start
bash run.sh network-check
```

The result must report actual service DNS addresses, `service_dns_read_passed:true`
and `client_loopback_rejected:true`. Addresses are observations, not stable config.

```bash
bash run.sh status
bash run.sh logs
bash run.sh stop
bash run.sh resume
bash run.sh network-check
```

Use the project README for down, retained-state replacement and explicitly
confirmed deletion. Do not run service commands in a classroom pad.

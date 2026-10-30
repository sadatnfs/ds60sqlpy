package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.node.ObjectNode
import java.nio.file.{Files, Path}
import java.nio.file.attribute.PosixFilePermissions
import java.util.UUID
import java.util.concurrent.{CompletableFuture, TimeUnit}
import org.apache.spark.sql.SparkSession

/** Deliberate protocol faults. The Python emitter is test-only, never numerical model evidence. */
object LifecycleChecks {
  def main(args: Array[String]): Unit = {
    require(args.length == 2, "Usage: artifact.json report.json")
    val base = Json.read(Files.readString(Path.of(args(0))))
    val spark =
      SparkSession.builder().appName("Prepared worker lifecycle fault contracts").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    val root = Files.createTempDirectory("tmbad-lifecycle-").toRealPath()
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwx------"))
    val report = Json.obj();
    report
      .put("kind", "spark-tmbad-lifecycle-faults")
      .put(
        "scope",
        "test-only Python protocol emitter; not native numerical or Python-free executor evidence"
      )
    val cases = report.putArray("cases")
    def fixture(mode: String): (PreparedArtifact, Path, Path) = {
      val pid = root.resolve(mode + ".pid")
      val file = root.resolve(mode + ".py")
      val declaration = base.deepCopy[ObjectNode]()
      val payload = Json.obj();
      payload.set[com.fasterxml.jackson.databind.JsonNode]("engine", base.get("engine"))
      payload.set[com.fasterxml.jackson.databind.JsonNode]("models", base.get("models"))
      payload.put("build_id", Json.text(base, "build_id"))
      val script = """#!/usr/local/bin/python3
import hashlib,json,os,struct,sys,time
from pathlib import Path
MODE=__MODE__
PID=__PID__
METADATA=json.loads(__METADATA__)
Path(PID).write_text(str(os.getpid())+' '+Path('/proc/self/stat').read_text().split()[21])
def read_exact(size):
    result=b''
    while len(result)<size:
        part=sys.stdin.buffer.read(size-len(result))
        if not part: raise EOFError()
        result+=part
    return result
header=read_exact(4)
raw=read_exact(struct.unpack('>I',header)[0])
if MODE in ('timeout','cancel'):
    time.sleep(60)
    raise SystemExit(0)
request=json.loads(raw)
reply=dict(METADATA,protocol=1,request_id=request['request_id'],status='ok',request_sha256=hashlib.sha256(raw).hexdigest())
encoded=json.dumps(reply,separators=(',',':')).encode()
sys.stdout.buffer.write(struct.pack('>I',len(encoded))+encoded)
sys.stdout.buffer.flush()
if MODE.startswith('error_'):
    header=read_exact(4)
    raw=read_exact(struct.unpack('>I',header)[0])
    request=json.loads(raw)
    reply=dict(protocol=1,request_id=request['request_id'],status='error',request_sha256=hashlib.sha256(raw).hexdigest(),build_id=METADATA['build_id'],model_id=request['model_id'],model_digest=request['model_digest'],error=dict(code='RESOURCE_LIMIT' if MODE=='error_resource' else 'INNER_MODE_FAILURE',message='Controlled diagnostic error'))
    if MODE=='error_build': reply['build_id']='0'*64
    if MODE=='error_model': reply['model_digest']='0'*64
    if MODE=='error_request': reply['request_sha256']='0'*64
    encoded=json.dumps(reply,separators=(',',':')).encode()
    sys.stdout.buffer.write(struct.pack('>I',len(encoded))+encoded)
    if MODE=='error_trailing': sys.stdout.buffer.write(b'!')
    sys.stdout.buffer.flush()
    raise SystemExit(7 if MODE=='error_exit7' else 2)
sys.stdin.buffer.read()
raise SystemExit(7 if MODE=='exit7' else 0)
""".replace(
        "__MODE__",
        (new com.fasterxml.jackson.databind.ObjectMapper()).writeValueAsString(mode)
      ).replace(
        "__PID__",
        (new com.fasterxml.jackson.databind.ObjectMapper()).writeValueAsString(pid.toString)
      ).replace(
        "__METADATA__",
        (new com.fasterxml.jackson.databind.ObjectMapper()).writeValueAsString(Json.write(payload))
      )
      Files.writeString(file, script)
      Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("r-x------"))
      val binary = declaration.get("binary").asInstanceOf[ObjectNode]
      binary.put("path", file.toString).put("sha256", Json.fileHash(file))
      (PreparedArtifact.parse(Json.write(declaration)), file, pid)
    }
    def alive(pidFile: Path): Boolean = {
      if (!Files.exists(pidFile)) false
      else {
        val identity = Files.readString(pidFile).split(" ")
        val process = Path.of("/proc", identity(0), "stat")
        try {
          val fields = Files.readString(process).split(" ")
          // A matching zombie is still present and has not been reaped.
          fields(21) == identity(1)
        } catch { case _: java.nio.file.NoSuchFileException => false }
      }
    }
    def awaitGone(pidFile: Path): Unit = {
      val end = System.nanoTime() + TimeUnit.SECONDS.toNanos(5)
      while (alive(pidFile) && System.nanoTime() < end) Thread.sleep(20)
      require(!alive(pidFile), "Fault worker survived cleanup")
    }
    try {
      for (mode <- Vector("exit0", "exit7", "timeout")) {
        val (artifact, executable, pid) = fixture(mode)
        val executableName = executable.toString
        var completed = false
        var failure = ""
        val acknowledgement = root.resolve(mode + ".ack").toString
        try {
          val results = spark.sparkContext
            .parallelize(Vector(1), 1)
            .mapPartitions { _ =>
              val worker = new NativeWorker(
                artifact,
                Path.of(executableName),
                if (mode == "timeout") 1 else 10
              )
              try {
                worker.handshake(); Files.writeString(Path.of(acknowledgement), "validated frame");
                worker.finish(); Iterator("accepted")
              } finally worker.close()
            }
            .collect()
          completed = results.toVector == Vector("accepted")
        } catch { case error: Exception => failure = error.toString }
        if (mode == "exit7")
          require(
            Files.exists(Path.of(acknowledgement)) && failure.contains(
              "exited 7 after valid output"
            ),
            "Exit7 did not fail at the intended finalization boundary"
          )
        if (mode == "timeout")
          require(failure.contains("deadline"), "Timeout failed for an unrelated reason")
        require(completed == (mode == "exit0"), "Fault output acceptance differs")
        require(Files.exists(pid), "Fault worker did not actually start")
        awaitGone(pid)
        val observation = Json.obj();
        observation.put("mode", mode).put("accepted", completed).put("child_reaped", true)
        cases.add(observation)
      }
      for (
        mode <- Vector(
          "error_exit2",
          "error_exit7",
          "error_build",
          "error_model",
          "error_request",
          "error_trailing",
          "error_resource"
        )
      ) {
        val (artifact, executable, pid) = fixture(mode)
        val executableName = executable.toString
        val observations = spark.sparkContext
          .parallelize(Vector(1), 1)
          .mapPartitions { _ =>
            val worker = new NativeWorker(artifact, Path.of(executableName), 10)
            try {
              worker.handshake()
              worker.exchange(
                NativeWorker.modelRequest("evaluate", artifact.model("normal"), Vector(0, 0))
              )
              throw new IllegalStateException("Fault response was accepted")
            } catch {
              case failure: NativeFailure =>
                val value = Json.obj();
                value
                  .put("reviewed", NumericalRejection.reviewed(failure))
                  .put("reason", failure.code)
                Iterator(Json.write(value))
              case failure: IllegalArgumentException =>
                val value = Json.obj();
                value.put("reviewed", false).put("reason", failure.getMessage)
                Iterator(Json.write(value))
            } finally worker.close()
          }
          .collect()
        require(observations.length == 1)
        val observed = Json.read(observations.head)
        require(
          Json.boolean(observed, "reviewed") == (mode == "error_exit2"),
          "Unverified or infrastructure fault became numerical rejection"
        )
        val expected = Map(
          "error_exit2" -> "INNER_MODE_FAILURE",
          "error_exit7" -> "nonzero_exit",
          "error_build" -> "build identity",
          "error_model" -> "model identity",
          "error_request" -> "request binding",
          "error_trailing" -> "trailing output",
          "error_resource" -> "RESOURCE_LIMIT"
        )
        require(
          Json.text(observed, "reason").contains(expected(mode)),
          "Fault rejected at an unrelated boundary"
        )
        require(Files.exists(pid)); awaitGone(pid)
        val record = Json.obj();
        record
          .put("mode", mode)
          .put("numerical_rejection", Json.boolean(observed, "reviewed"))
          .put("child_reaped", true)
        cases.add(record)
      }
      val (artifact, executable, pid) = fixture("cancel")
      val executableName = executable.toString
      val job = "tmbad-cancel-" + UUID.randomUUID()
      val completion = new CompletableFuture[Boolean]()
      val thread = new Thread(() => {
        spark.sparkContext.setJobGroup(job, "Owned lifecycle cancellation fixture", true)
        try {
          spark.sparkContext
            .parallelize(Vector(1), 1)
            .mapPartitions { _ =>
              val worker = new NativeWorker(
                artifact,
                Path.of(executableName),
                30,
                registerCompletionHook = false
              )
              try { worker.handshake(); worker.finish(); Iterator(1) }
              finally worker.close()
            }
            .count()
          completion.complete(false)
        } catch { case _: Exception => completion.complete(true) }
      })
      thread.start()
      val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(15)
      while (!Files.exists(pid) && !completion.isDone && System.nanoTime() < deadline)
        Thread.sleep(20)
      require(Files.exists(pid), "Cancellation worker did not start")
      spark.sparkContext.cancelJobGroup(job)
      require(completion.get(10, TimeUnit.SECONDS), "Cancelled Spark job was accepted")
      thread.join(1000); awaitGone(pid)
      val cancellation = Json.obj();
      cancellation
        .put("mode", "cancel")
        .put("accepted", false)
        .put("child_reaped", true)
        .put("completion_hook", false)
      cases.add(cancellation)
      report.put("passed", true)
      Files.writeString(Path.of(args(1)), Json.write(report) + "\n")
      println("DS60_TMBAD_LIFECYCLE_RESULT " + Json.write(report))
    } finally {
      spark.stop()
      val paths = Files.list(root)
      try paths.forEach(path => Files.deleteIfExists(path))
      finally paths.close()
      Files.deleteIfExists(root)
    }
  }
}

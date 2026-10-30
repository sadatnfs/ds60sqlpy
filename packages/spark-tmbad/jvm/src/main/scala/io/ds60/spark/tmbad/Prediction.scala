package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{DataFrame, Row}
import org.apache.spark.sql.functions.{encode, length}
import org.apache.spark.sql.types._

private[tmbad] final case class PredictionOptions(
    targetName: String,
    columns: Map[String, String],
    historyColumns: Map[String, String],
    ids: Vector[String],
    groups: Vector[String],
    order: Vector[String],
    historyGroups: Vector[String],
    historyOrder: Vector[String],
    prefix: String,
    allowUnconverged: Boolean,
    batchRows: Int,
    taskTimeoutSeconds: Int
) extends Serializable
private[tmbad] object PredictionOptions {
  def parse(
      text: String,
      loaded: ModelDocument.Loaded,
      forecast: Boolean,
      conditional: Boolean,
      grouped: Boolean = false
  ): PredictionOptions = {
    val value = Json.read(text)
    val base =
      Set("target", "output_prefix", "allow_unconverged", "batch_rows", "task_timeout_seconds")
    val roles =
      if (forecast)
        Set(
          "future_id_columns",
          "future_group_columns",
          "future_order_columns",
          "future_columns",
          "history_columns",
          "history_group_columns",
          "history_order_columns"
        )
      else
        Set("id_columns", "group_columns", "order_columns", "columns") ++
          (if (conditional) Set("history_columns", "history_group_columns", "history_order_columns")
           else Set.empty[String])
    val required = Set("target", if (forecast) "future_columns" else "columns") ++
      (if (conditional) Set("history_columns") else Set.empty[String])
    Json.fields(value, required, base ++ roles -- required)
    val name = Json.text(value, "target", 64)
    val target = (if (forecast) loaded.model.forecasting else loaded.model.prediction)
      .getOrElse(
        name,
        throw new IllegalArgumentException("Model does not declare this prediction/forecast target")
      )
    require(
      forecast || conditional || !target.needsHistory,
      "Use predictConditional with explicit history for this target"
    )
    def names(key: String, default: Vector[String]): Vector[String] =
      if (value.has(key)) Json.strings(value.get(key), 64, key) else default
    val ids = names(if (forecast) "future_id_columns" else "id_columns", loaded.spec.idColumns)
    val groups =
      names(if (forecast) "future_group_columns" else "group_columns", loaded.spec.groupColumns)
    val order = names(
      if (forecast) "future_order_columns" else "order_columns",
      if (forecast) loaded.spec.orderColumns else Vector.empty
    )
    val historyGroups = names("history_group_columns", loaded.spec.groupColumns)
    val historyOrder = names("history_order_columns", loaded.spec.orderColumns)
    require(ids.nonEmpty, "Prediction requires explicit future/target identity columns")
    require(
      !forecast || !loaded.model.ordered || order.nonEmpty,
      "Ordered forecasting requires future order columns"
    )
    require(
      !target.needsHistory || (groups.nonEmpty && historyGroups.nonEmpty),
      "Conditional prediction/forecast requires explicit matching group keys"
    )
    require(
      !target.needsHistory || !loaded.model.ordered || historyOrder.nonEmpty,
      "Ordered conditional targets require history order columns"
    )
    val fieldName = if (forecast) "future_columns" else "columns"
    val columns = FitSpecification.mapping(value.get(fieldName), target.fields, fieldName)
    val historyColumns = if (value.has("history_columns")) {
      val mapping = value.get("history_columns")
      if (!target.needsHistory && mapping.isObject && mapping.size() == 0) Map.empty[String, String]
      else FitSpecification.mapping(mapping, loaded.model.fitFields, "history columns")
    } else {
      require(!target.needsHistory, "Conditional target requires history_columns")
      Map.empty[String, String]
    }
    val prefix = if (value.has("output_prefix")) {
      require(value.get("output_prefix").isTextual, "output_prefix must be a string")
      val selected = value.get("output_prefix").textValue()
      require(selected.codePointCount(0, selected.length) <= 128, "Output prefix exceeds its bound")
      selected
    } else "tmbad_"
    val allow = value.has("allow_unconverged") && Json.boolean(value, "allow_unconverged")
    require(
      loaded.converged || allow || grouped,
      "Unconverged fit cannot predict/forecast without explicit allow_unconverged=true"
    )
    PredictionOptions(
      name,
      columns,
      historyColumns,
      ids,
      groups,
      order,
      historyGroups,
      historyOrder,
      prefix,
      allow,
      if (value.has("batch_rows")) Json.integer(value, "batch_rows", 1, 8192).toInt else 1024,
      if (value.has("task_timeout_seconds"))
        Json.integer(value, "task_timeout_seconds", 1, 3600).toInt
      else 120
    )
  }
}

private[tmbad] final case class JointKey(
    group: String,
    role: Int,
    order: Vector[KeyAtom],
    ids: Vector[KeyAtom]
) extends GroupSortKey
private[tmbad] object JointKey {
  implicit val ordering: Ordering[JointKey] = new Ordering[JointKey] with Serializable {
    override def compare(a: JointKey, b: JointKey): Int = {
      val group = a.group.compareTo(b.group)
      if (group != 0) group
      else if (a.role != b.role) java.lang.Integer.compare(a.role, b.role)
      else {
        val order = KeyAtom.compare(a.order, b.order)
        if (order != 0) order else KeyAtom.compare(a.ids, b.ids)
      }
    }
  }
}
private[tmbad] final case class JointRecord(
    role: Int,
    row: Option[NativeRow],
    model: Option[String]
) extends Serializable

private[tmbad] object Prediction {
  private def target(
      loaded: ModelDocument.Loaded,
      options: PredictionOptions,
      forecast: Boolean
  ): NativeTarget =
    (if (forecast) loaded.model.forecasting else loaded.model.prediction) (options.targetName)
  private def schema(
      frame: DataFrame,
      projected: Projected,
      target: NativeTarget,
      prefix: String
  ): StructType = {
    val outputs = target.columns.map(prefix + _)
    require(
      ColumnNames.unique(outputs) && !outputs.exists(output =>
        frame.schema.fieldNames.exists(input => ColumnNames.equivalent(input, output))
      ),
      "Prediction output column collides with an existing input column"
    )
    StructType(
      projected.layout.keySchema ++ outputs.map(name =>
        StructField(name, DoubleType, nullable = false)
      )
    )
  }
  private def sameKeyTypes(
      left: DataFrame,
      leftNames: Vector[String],
      right: DataFrame,
      rightNames: Vector[String]
  ): Unit = {
    require(leftNames.size == rightNames.size, "History/future/model group-key dimensions differ")
    require(
      leftNames.zip(rightNames).forall { case (a, b) =>
        left.schema(a).dataType == right.schema(b).dataType
      },
      "History/future/model group-key Spark types differ"
    )
  }
  private def hasRows(rows: RDD[NativeRow]): Boolean = rows.map(_ => 1).take(1).nonEmpty

  def rows(
      frame: DataFrame,
      loaded: ModelDocument.Loaded,
      artifact: DistributedArtifact,
      options: PredictionOptions
  ): DataFrame = {
    val declared = target(loaded, options, forecast = false)
    require(
      !declared.needsHistory && loaded.model.fitKind == "rows",
      "Row prediction requires an independent response-free target"
    )
    val projected = Data.project(
      frame,
      declared.fields,
      options.columns,
      options.ids,
      options.groups,
      options.order,
      None
    )
    Data.checkUniqueIds(projected.rdd)
    val outputSchema = schema(frame, projected, declared, options.prefix)
    val keyCount = projected.layout.keySchema.size
    val batch = math.min(
      options.batchRows,
      if (loaded.model.fitKind == "unit") loaded.model.maxUnitRows else 8192
    )
    val rows = projected.rdd.mapPartitions { input =>
      val spool = new TaskSpool
      var worker: NativeWorker = null
      try {
        val batches = Data.batches(input, batch)
        if (batches.hasNext) {
          artifact.artifact.requireLoadedJvm(classOf[NativeWorker])
          worker =
            new NativeWorker(artifact.artifact, artifact.executable, options.taskTimeoutSeconds)
          worker.handshake()
          batches.foreach { source =>
            val data = source.toVector
            val values = NativeCalls.predict(
              worker,
              loaded.model,
              loaded.parameters,
              options.targetName,
              declared,
              data,
              Vector.empty,
              forecast = false
            )
            data.zip(values).foreach { case (row, value) =>
              spool.append(OutputRows.prediction(row.keys, value))
            }
          }
          worker.finish()
        }
        spool.result(node => OutputRows.predictionRow(node, keyCount, declared.columns.size))
      } catch { case error: Throwable => spool.close(); throw error }
      finally if (worker != null) worker.close()
    }
    frame.sparkSession.createDataFrame(rows, outputSchema)
  }

  /** Exactly one bounded model document is driver metadata, never raw observations/all models. */
  def groupModelTemplate(models: DataFrame, artifact: PreparedArtifact): ModelDocument.Loaded = {
    require(
      !models.isStreaming && models.schema.fieldNames.contains("tmbad_model_json") &&
        models.schema("tmbad_model_json").dataType == StringType,
      "Expected fitted group-model DataFrame"
    )
    val field = Data.literal("tmbad_model_json")
    require(
      models
        .filter(field.isNull || length(encode(field, "UTF-8")) > Json.MaxBytes)
        .limit(1)
        .count() == 0,
      "Group model document is null or exceeds its byte bound"
    )
    val one = models.select(field).limit(1).collect()
    require(one.length == 1, "Group-model DataFrame is empty")
    val loaded = ModelDocument.parse(one.head.getString(0), artifact)
    require(loaded.spec.groupColumns.nonEmpty, "Independent models require group keys")
    loaded
  }

  private def modelRecords(
      models: DataFrame,
      template: ModelDocument.Loaded,
      artifact: PreparedArtifact
  ): RDD[(JointKey, JointRecord)] = {
    val names = template.spec.groupColumns
    require(
      names.forall(models.schema.fieldNames.contains),
      "Fitted-model group columns are missing"
    )
    val types = names.map(name => models.schema(name).dataType)
    types.foreach(KeyAtom.kind)
    models.select((names.map(Data.literal) :+ Data.literal("tmbad_model_json")): _*).rdd.map {
      row =>
        val keys = names.indices.map(i => KeyAtom.from(row.get(i), types(i))).toVector
        val encoded = row.getString(names.size)
        val loaded = ModelDocument.parse(encoded, artifact)
        require(
          loaded.model.id == template.model.id && loaded.spec.copy(json = "") == template.spec
            .copy(json = ""),
          "Independent fitted models do not share one declared model/specification"
        )
        JointKey(KeyAtom.encode(keys), 0, Vector.empty, Vector.empty) -> JointRecord(
          0,
          None,
          Some(encoded)
        )
    }
  }

  def joined(
      history: Option[DataFrame],
      future: DataFrame,
      template: ModelDocument.Loaded,
      models: Option[DataFrame],
      artifact: DistributedArtifact,
      options: PredictionOptions,
      forecast: Boolean
  ): DataFrame = {
    val declared = target(template, options, forecast)
    require(
      !declared.needsHistory || history.nonEmpty,
      "Conditional target requires an explicit history DataFrame"
    )
    if (models.nonEmpty)
      require(options.groups.nonEmpty, "Independent prediction needs target/future group columns")
    val projected = Data.project(
      future,
      declared.fields,
      options.columns,
      options.ids,
      options.groups,
      options.order,
      None
    )
    require(
      projected.rdd.getNumPartitions > 0 && projected.rdd.getNumPartitions <= 4096,
      "Forecast/prediction partition count exceeds its bound"
    )
    if (forecast) require(hasRows(projected.rdd), "Forecast future DataFrame must be nonempty")
    Data.checkUniqueIds(projected.rdd)
    val outputSchema = schema(future, projected, declared, options.prefix)
    val keyCount = projected.layout.keySchema.size
    var tagged = projected.rdd.map(row =>
      JointKey(row.groupKey, 2, row.order, row.ids) -> JointRecord(2, Some(row), None)
    )
    history.foreach { frame =>
      require(!frame.isStreaming, "Use a bounded history snapshot")
      if (!declared.needsHistory) {
        require(
          frame.limit(1).count() == 0,
          "Unconditional target requires absent or empty history"
        )
      } else {
        require(
          options.historyColumns.nonEmpty,
          "Supplied history requires its explicit native-field mapping"
        )
        sameKeyTypes(frame, options.historyGroups, future, options.groups)
        // History identity is used only for bounded within-unit ordering, never emitted as a future ID.
        val keys = (options.historyGroups ++ options.historyOrder).distinct
        require(keys.nonEmpty, "History requires explicit grouping/order keys")
        val prepared = Data.project(
          frame,
          template.model.fitFields,
          options.historyColumns,
          keys,
          options.historyGroups,
          options.historyOrder,
          None
        )
        tagged = tagged.union(
          prepared.rdd.map(row =>
            JointKey(row.groupKey, 1, row.order, row.ids) -> JointRecord(1, Some(row), None)
          )
        )
      }
    }
    models.foreach { frame =>
      sameKeyTypes(frame, template.spec.groupColumns, future, options.groups)
      tagged = tagged.union(modelRecords(frame, template, artifact.artifact))
    }
    import JointKey.ordering
    val sorted = tagged.repartitionAndSortWithinPartitions(
      new GroupPartitioner(projected.rdd.getNumPartitions)
    )
    val separateModels = models.nonEmpty
    val rows = sorted.mapPartitions { source =>
      val input = source.buffered
      val spool = new TaskSpool
      var worker: NativeWorker = null
      try {
        while (input.hasNext) {
          val group = input.head._1.group
          var fitted: Option[ModelDocument.Loaded] = None
          val past = scala.collection.mutable.ArrayBuffer.empty[NativeRow]
          val targets = scala.collection.mutable.ArrayBuffer.empty[NativeRow]
          val pastBudget = new RowBudget
          val targetBudget = new RowBudget
          val rowIndependent =
            !forecast && !declared.needsHistory && template.model.fitKind == "rows"
          def emitTargets(): Unit = if (targets.nonEmpty) {
            // Future-only groups are preserved. A missing model/history fails rather than disappearing.
            val loaded =
              if (separateModels)
                fitted.getOrElse(
                  throw new IllegalArgumentException("Future group has no fitted independent model")
                )
              else template
            require(
              loaded.converged || options.allowUnconverged,
              "Unconverged independent model cannot predict/forecast without explicit override"
            )
            require(
              !declared.needsHistory || past.nonEmpty,
              "Future group is missing required conditional history"
            )
            if (worker == null) {
              artifact.artifact.requireLoadedJvm(classOf[NativeWorker])
              worker =
                new NativeWorker(artifact.artifact, artifact.executable, options.taskTimeoutSeconds)
              worker.handshake()
            }
            val targetRows = targets.toVector
            val values = NativeCalls.predict(
              worker,
              loaded.model,
              loaded.parameters,
              options.targetName,
              declared,
              targetRows,
              past.toVector,
              forecast
            )
            targetRows.zip(values).foreach { case (row, value) =>
              spool.append(OutputRows.prediction(row.keys, value))
            }
            targets.clear(); targetBudget.clear()
          }
          while (input.hasNext && input.head._1.group == group) {
            val (_, item) = input.next()
            item.role match {
              case 0 =>
                require(fitted.isEmpty, "Duplicate independent model for a group")
                fitted = Some(ModelDocument.parse(item.model.get, artifact.artifact))
              case 1 =>
                require(
                  past.size < template.model.maxUnitRows,
                  "Complete history exceeds the model bound"
                )
                val row = item.row.get
                if (template.model.ordered && past.nonEmpty)
                  require(
                    KeyAtom.compare(past.last.order, row.order) < 0,
                    "Duplicate/nonincreasing history order"
                  )
                pastBudget.add(row); past += row
              case 2 =>
                if (rowIndependent && targets.size >= options.batchRows) emitTargets()
                require(
                  targets.size < (if (rowIndependent) options.batchRows
                                  else template.model.maxUnitRows),
                  "Complete future/conditional target unit exceeds the model bound"
                )
                val row = item.row.get
                if (forecast && template.model.ordered && targets.nonEmpty)
                  require(
                    KeyAtom.compare(targets.last.order, row.order) < 0,
                    "Duplicate/nonincreasing future order"
                  )
                targetBudget.add(row); targets += row
              case _ => throw new IllegalArgumentException("Unknown grouped request role")
            }
          }
          emitTargets()
        }
        if (worker != null) worker.finish()
        spool.result(node => OutputRows.predictionRow(node, keyCount, declared.columns.size))
      } catch { case error: Throwable => spool.close(); throw error }
      finally if (worker != null) worker.close()
    }
    future.sparkSession.createDataFrame(rows, outputSchema)
  }
}

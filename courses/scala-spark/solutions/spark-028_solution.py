from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType


def observe(frame):
    summary = frame.agg(F.count(F.lit(1)),F.countDistinct("fact_id"),F.count("amount"),F.sum("amount"),F.sum(F.col("amount")*F.col("factor")))
    values = dict(zip(["rows","unique_facts","known_amounts","amount_total","weighted_total"],tuple(summary.collect()[0]),strict=True))
    exchanges = []
    pending = [summary._jdf.queryExecution().executedPlan()]
    while pending:
        node = pending.pop()
        if "Exchange" in node.nodeName():
            metrics = {}; iterator = node.metrics().iterator()
            while iterator.hasNext():
                entry = iterator.next(); metrics[str(entry._1())] = int(entry._2().value())
            exchanges.append((node.nodeName(),metrics))
        children = node.children().iterator()
        while children.hasNext():
            pending.append(children.next())
    return values,exchanges
def same_bag(left, right):
    return left.exceptAll(right).count() == 0 and right.exceptAll(left).count() == 0

def classify_facts(raw):
    return raw.withColumn("reason",F.when(F.col("fact_id").isNull(),"missing_identity").when(F.col("amount")<0,"negative_amount").otherwise("accepted"))

def review_dimension(raw):
    reviewed = raw.filter(F.col("approved")).select("key","factor")
    rows = reviewed.limit(101).count()
    if rows > 100 or reviewed.agg(F.countDistinct("key")).first()[0] != rows:
        raise ValueError("Approved keys must be known,unique and bounded")
    return reviewed

def baseline_product(facts, dimension):
    return facts.join(dimension,on="key",how="inner").select("source_id","fact_id","key","amount","factor")

def broadcast_product(facts, dimension):
    return facts.join(F.broadcast(dimension),on="key",how="inner").select("source_id","fact_id","key","amount","factor")

def configuration_receipt(spark):
    return {"version":spark.version,"master":spark.sparkContext.master,"aqe":spark.conf.get("spark.sql.adaptive.enabled"),"automatic_broadcast":spark.conf.get("spark.sql.autoBroadcastJoinThreshold")}

def choose_product(facts, dimension, use_broadcast):
    if not isinstance(use_broadcast,bool):
        raise ValueError("Explicit Boolean strategy switch required")
    return broadcast_product(facts,dimension) if use_broadcast else baseline_product(facts,dimension)

def main():

    spark = (SparkSession.builder.appName("ds60-spark-028").master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC").getOrCreate())
    try:
        assert spark.sparkContext.master == "local[2]"
        spark.sparkContext.setLogLevel("ERROR")
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold","-1")
        fact_schema = StructType([StructField("source_id",LongType(),False),StructField("fact_id",LongType(),True),StructField("key",LongType(),False),StructField("amount",LongType(),True)])
        generated = [(i,i,0 if i<=1600 else (i-1601)%4+1,None if i%10==0 else i%7+1) for i in range(1,2001)]
        raw_facts = spark.createDataFrame(generated+[(2001,None,0,10),(2002,2001,99,-3)],schema=fact_schema)
        dim_schema = StructType([StructField("key",LongType(),False),StructField("factor",LongType(),False),StructField("approved",BooleanType(),False)])
        raw_dimension = spark.createDataFrame([(0,1,False),(0,2,True)]+[(k,k+2,True) for k in range(1,6)],schema=dim_schema)
        expected_metrics = {"rows":2000,"unique_facts":2000,"known_amounts":1800,"amount_total":7196,"weighted_total":17913}
        # Exercise 1: Classify facts and reconcile the whole source population
        classified = classify_facts(raw_facts)
        accepted = classified.filter(F.col("reason")=="accepted").drop("reason")
        rejected = classified.filter(F.col("reason")!="accepted")
        assert [tuple(r) for r in rejected.select("source_id","reason").orderBy("source_id").collect()] == [(2001,"missing_identity"),(2002,"negative_amount")]
        assert accepted.count() == 2000 and rejected.count() == 2 and classified.count() == 2002
        assert tuple(accepted.agg(F.countDistinct("fact_id"),F.count("amount")).first()) == (2000,1800)
        # Exercise 2: Select an approved unique dimension before tuning
        reviewed = review_dimension(raw_dimension)
        assert [tuple(r) for r in reviewed.orderBy("key").collect()] == [(k,k+2) for k in range(6)]
        try:
            review_dimension(raw_dimension.unionByName(raw_dimension.filter((F.col("key")==0)&F.col("approved"))))
        except ValueError:
            pass
        else:
            raise AssertionError("Conflicting approved dimension accepted")
        # Exercise 3: Produce the correct baseline and independent key summary
        baseline = baseline_product(accepted,reviewed)
        baseline_values,baseline_exchanges = observe(baseline)
        assert baseline_values == expected_metrics
        key_summary = [tuple(r) for r in baseline.groupBy("key").agg(F.count(F.lit(1)),F.count("amount"),F.sum("amount"),F.sum(F.col("amount")*F.col("factor"))).orderBy("key").collect()]
        assert key_summary == [(0,1600,1440,5755,11510),(1,100,100,401,1203),(2,100,80,321,1284),(3,100,100,398,1990),(4,100,80,321,1926)]
        # Exercise 4: Compare a bounded broadcast strategy with the same business contract
        candidate = broadcast_product(accepted,reviewed)
        candidate_values,candidate_exchanges = observe(candidate)
        assert candidate_values == expected_metrics and same_bag(candidate,baseline)
        assert "BroadcastHashJoin" in candidate._jdf.queryExecution().executedPlan().toString()
        # Exercise 5: Assemble an honest bounded comparison receipt
        configuration = configuration_receipt(spark)
        assert configuration == {"version":"4.0.1","master":"local[2]","aqe":"false","automatic_broadcast":"-1"}
        frequencies = [tuple(r) for r in accepted.groupBy("key").count().orderBy("key").collect()]
        assert frequencies == [(0,1600),(1,100),(2,100),(3,100),(4,100)]
        assert baseline_exchanges and candidate_exchanges
        print("configuration=",configuration,"key_frequencies=",frequencies,"baseline_metrics=",baseline_exchanges,"candidate_metrics=",candidate_exchanges)
        print("baseline_plan=",baseline._jdf.queryExecution().executedPlan().toString(),"candidate_plan=",candidate._jdf.queryExecution().executedPlan().toString())
        # Exercise 6: Roll back execution policy without rolling back data quality
        rolled_back = choose_product(accepted,reviewed,False)
        assert observe(rolled_back)[0] == expected_metrics and same_bag(rolled_back,candidate)
        assert "BroadcastHashJoin" not in rolled_back._jdf.queryExecution().executedPlan().toString()
        assert same_bag(choose_product(accepted,reviewed,True),baseline)
        print("spark-028: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        try:
            pass
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Classify facts and reconcile the whole source population. Inputs/task: Add reason using missing fact identity, negative known amount, then accepted precedence. Retain all source records;acceptedNULL amounts remain unknown. Expected: Accepted 2000, rejected 2 with source 2001 missing_identity and 2002 negative_amount. Accepted unique fact IDs 2000 and known amounts 1800. Verify: Assert every rejection identity/reason, source reconciliation and accepted uniqueness/completeness counts.
# Exercise 2: Select an approved unique dimension before tuning. Inputs/task: Keep approved dimension rows, require at most 100 rows and known unique keys, then return key, factor. Reject a candidate with a second approved key 0 row. Expected: Reviewed keys 0..5, factors 2..7, six rows. The conflicting approved candidate fails before joining. Verify: Assert all six key/factor rows and the explicit duplicate-approved rejection.
# Exercise 3: Produce the correct baseline and independent key summary. Inputs/task: Build the ordinary equality join over accepted facts and reviewed dimension, projecting source_id, fact_id, key, amount, factor. Summarize per key with rows, known amounts, total amount and weighted total. Expected: Key 0:(1600,1440,5755,11510);1:(100,100,401,1203);2:(100,80,321,1284);3:(100,100,398,1990);4:(100,80,321,1926). Verify: Assert all five summary tuples and aggregate metrics 2000,2000,1800,7196,17913.
# Exercise 4: Compare a bounded broadcast strategy with the same business contract. Inputs/task: Broadcast the reviewed dimension for the same equality join and projection. Preserve all output occurrences using exceptAll in both directions against baseline. Expected: Identical metrics and empty directional bag differences. The candidate plan containsBroadcastHashJoin. Verify: Assert the full metric map, both distributed bag differences and the observed strategy marker.
# Exercise 5: Assemble an honest bounded comparison receipt. Inputs/task: Return version, master, AQE and automatic broadcast threshold as named fields. Attach key frequencies, the baseline/candidate plans and each observed summary-query exchange metric map. Expected: Spark 4.0.1, local[2], AQEfalse, threshold-1;key 0 frequency 1600 and others 100. Both runs expose actual nonempty exchange observations. No peak-memory or throughput value is invented. Verify: Assert controlled settings and frequency ledger, then print plans and separately labeled actual metric maps.
# Exercise 6: Roll back execution policy without rolling back data quality. Inputs/task: Choose baseline or broadcast using an explicit Boolean switch over the same accepted facts and reviewed dimension. Switch back to baseline and revalidate the complete product. Expected: Both switch positions satisfy the same metric map and bag contract. The disabled position has noBroadcastHashJoin under the controlled configuration. Verify: Assert golden metrics and bag equality after rollback, and inspect the restored baseline plan.

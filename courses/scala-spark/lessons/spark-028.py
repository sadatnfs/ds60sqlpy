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
    raise NotImplementedError("Complete classify_facts")

def review_dimension(raw):
    raise NotImplementedError("Complete review_dimension")

def baseline_product(facts, dimension):
    raise NotImplementedError("Complete baseline_product")

def broadcast_product(facts, dimension):
    raise NotImplementedError("Complete broadcast_product")

def configuration_receipt(spark):
    raise NotImplementedError("Complete configuration_receipt")

def choose_product(facts, dimension, use_broadcast):
    raise NotImplementedError("Complete choose_product")

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
        predicted_raw_join_rows = 1600*2+400
        assert predicted_raw_join_rows == 3600
        print("Raw dimension multiplicity predicts3600 pairs for2000 accepted facts")
        known = [i for i in range(1,2001) if i%10 != 0]
        amount_total = sum(i%7+1 for i in known)
        weighted = sum((i%7+1)*((0 if i<=1600 else (i-1601)%4+1)+2) for i in known)
        assert len(known) == 1800 and amount_total == 7196 and weighted == 17913
        print("Independent formula totals=",amount_total,weighted)
        print("spark-028: worked examples passed; six task implementations remain")
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

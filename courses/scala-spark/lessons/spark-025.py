from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
from pathlib import Path
import tempfile
import shutil
from pyspark.errors import AnalysisException

def same_bag(left, right):
    columns = ["id","day","amount","payload"]
    a = left.select(*columns); b = right.select(*columns)
    return a.exceptAll(b).count() == 0 and b.exceptAll(a).count() == 0

def write_compact(source, path):
    raise NotImplementedError("Complete write_compact")

def filtered_product(frame):
    raise NotImplementedError("Complete filtered_product")

def scan_evidence(frame):
    raise NotImplementedError("Complete scan_evidence")

def file_inventory(path):
    raise NotImplementedError("Complete file_inventory")

def layout_receipt(frame, path):
    raise NotImplementedError("Complete layout_receipt")

def reject_existing(source, path):
    raise NotImplementedError("Complete reject_existing")

def main():
    owned_root = None
    spark = (SparkSession.builder.appName("ds60-spark-025").master("local[2]")
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
        owned_root = Path(tempfile.mkdtemp(prefix=".ds60-spark-025-",dir=".")).resolve()
        schema = StructType([StructField("id",LongType(),False),StructField("day",StringType(),False),StructField("amount",LongType(),False),StructField("payload",StringType(),False)])
        source = spark.createDataFrame([(i,"even" if i%2==0 else "odd",i*7,"x"*32) for i in range(2000)],schema=schema)
        compact_path = str(owned_root/"compact")
        many_path = str(owned_root/"many")
        assert isinstance(source.schema["id"].dataType,LongType) and source.count() == 2000
        assert source.agg(F.sum("amount")).first()[0] == 13993000
        print("Explicit-schema source:2000 rows,total13993000")
        ids = [i for i in range(1990,2000) if i%2==0]
        assert ids == [1990,1992,1994,1996,1998]
        print("Independent filtered identity oracle=",ids)
        print("spark-025: worked examples passed; six task implementations remain")
    finally:
        try:
            if owned_root is not None:
                shutil.rmtree(owned_root)
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Write and validate a compact partitioned round trip. Inputs/task: Repartition source by day into 2 execution partitions, write Parquet with error-if-exists and partitionBy(day), then read it back. Compare field types and the complete duplicate-sensitive bag. Expected: 2000 rows and total 13993000 survive. Types remain id/amount bigints and day/payload strings;read nullability may differ. Verify: Assert type mapping and exceptAll emptiness in both directions, plus row count and amount total.
# Exercise 2: Read a narrow filtered projection with an independent oracle. Inputs/task: Select only id and amount for day=even and id>=1990. Return the five ordered tuples. Expected: (1990,13930),(1992,13944),(1994,13958),(1996,13972),(1998,13986). No payload column is requested. Verify: Assert every projected identity and amount and exact two-column output schema.
# Exercise 3: Locate partition, column and predicate evidence in the scan. Inputs/task: Capture a FORMATTED plan for the selected query on the owned Parquet view. Extract ReadSchema, PartitionFilters and PushedFilters lines and interpret each scope. Expected: ReadSchema has id and amount but not payload;PartitionFilters mentions day/even;PushedFilters includes the id lower bound. Verify: Assert the relevant field/predicate markers and retain the exact five-row output oracle;do not claim bytes skipped from the plan alone.
# Exercise 4: Compare a deliberately larger file count without changing data. Inputs/task: Write the same source after repartition 12 using the same day directory partitioning. Inventory only.parquet data files and their actual byte sizes for both layouts. Expected: Both round trips match the source bag. The many layout has more data files than compact;both byte totals are positive and below 32 MiB. Verify: Assert bag parity, file-count inequality and measured data-byte bounds. Ignore checksum and success-marker files in data counts.
# Exercise 5: Report storage partitions, files and scan partitions separately. Inputs/task: Return a receipt with the number of day= directories, the data-file count and the read DataFrame execution-partition count for each layout. Expected: Both layouts have 2 day directories. Data-file counts are the measured inventory values. Scan partitions are positive observed values and need not equal either other count. Verify: Assert two directory partitions and independent file-count consistency;print actual scan partition counts without imposing equality.
# Exercise 6: Reject an existing target and preserve its product. Inputs/task: Attempt a second error-if-exists write to the already owned compact path. Require the expected analysis error, then read the original product and reconcile its bag. Expected: The second write fails with an existing-path analysis exception;the original 2000-row product remains unchanged. Verify: Assert the exception and full original bag after the failed write. Do not delete or overwrite the target to make the retry succeed.

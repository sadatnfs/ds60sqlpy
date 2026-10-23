from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType, BooleanType, ArrayType, MapType, TimestampType, DecimalType
import re

def collected(frame):
    return [tuple(r) for r in frame.select("id","normalized").orderBy("id").collect()]

def normalize_label(value):
    if value is None:
        return None
    collapsed = re.sub(r"[ \t\r\n]+"," ",value).strip(" ")
    return collapsed.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"))

def builtin_labels(raw):
    return raw.select("id",F.trim(F.regexp_replace(F.translate("label","ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),r"[ \t\r\n]+"," ")).alias("normalized"))

def udf_labels(raw):
    normalize = F.udf(normalize_label,StringType(),useArrow=False)
    return raw.select("id",normalize("label").alias("normalized"))

def plan_evidence(frame):
    return frame._jdf.queryExecution().executedPlan().toString()

def label_categories(frame):
    return sorted(tuple(r) for r in frame.withColumn("category",F.when(F.col("normalized").isNull(),"missing").when(F.col("normalized")=="","empty").otherwise("text")).groupBy("category").count().collect())

def validate_golden(actual, expected):
    if actual != expected:
        raise ValueError("Golden label contract mismatch")

def main():

    spark = (SparkSession.builder.appName("ds60-spark-026").master("local[2]")
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
        schema = StructType([StructField("id",LongType(),False),StructField("label",StringType(),True)])
        raw = spark.createDataFrame([(1,None),(2,""),(3,"   "),(4,"  ALPHA  Beta "),(5,"\tA\nB\r "),(6,"CAFÉ"),(7,"Straße"),(8,"\u00a0A\u00a0"),(9,"İI"),(10,"🙂 OK"),(11,"e\u0301"),(12,"NULL")],schema=schema)
        expected = [(1,None),(2,""),(3,""),(4,"alpha beta"),(5,"a b"),(6,"cafÉ"),(7,"straße"),(8,"\u00a0a\u00a0"),(9,"İi"),(10,"🙂 ok"),(11,"e\u0301"),(12,"null")]
        # Exercise 1: Implement the pure scalar rule precisely
        scalar = [(r[0],normalize_label(r[1])) for r in raw.orderBy("id").collect()]
        assert scalar == expected
        # Exercise 2: Express the same rule with native Spark functions
        builtin = builtin_labels(raw)
        assert collected(builtin) == expected and isinstance(builtin.schema["normalized"].dataType,StringType)
        # Exercise 3: Wrap the scalar rule with a declared UDF return type
        custom = udf_labels(raw)
        assert collected(custom) == expected and isinstance(custom.schema["normalized"].dataType,StringType)
        # Exercise 4: Locate the execution boundary in physical evidence
        builtin_plan = plan_evidence(builtin);custom_plan = plan_evidence(custom)
        assert "BatchEvalPython" not in builtin_plan and "ArrowEvalPython" not in builtin_plan
        assert "BatchEvalPython" in custom_plan and "ArrowEvalPython" not in custom_plan
        print("builtin_plan=",builtin_plan,"python_udf_plan=",custom_plan)
        # Exercise 5: Preserve missing, empty and ordinary-text populations
        for frame in [builtin,custom]:
            assert label_categories(frame) == [("empty",2),("missing",1),("text",9)]
            assert [r[0] for r in frame.filter(F.col("normalized")=="null").select("id").collect()] == [12]
            assert [r[0] for r in frame.filter(F.col("normalized").isNull()).select("id").collect()] == [1]
        # Exercise 6: Reject a plausible but semantically broader implementation
        validate_golden(collected(builtin),expected)
        wrong = [(r[0],None if r[1] is None else r[1].strip().lower()) for r in raw.orderBy("id").collect()]
        mismatches = {a[0] for a,b in zip(wrong,expected,strict=True) if a != b}
        assert {4,5,6,8,9} <= mismatches
        try:
            validate_golden(wrong,expected)
        except ValueError:
            pass
        else:
            raise AssertionError("Wrong normalization policy accepted")
        print("wrong_rule_mismatch_ids=",sorted(mismatches))
        print("spark-026: six PySpark reference contracts passed; Spark=" + spark.version)
    finally:
        try:
            pass
        finally:
            spark.stop()

if __name__ == "__main__":
    main()

# Exercise 1: Implement the pure scalar rule precisely. Inputs/task: ReturnNULL/None unchanged;collapse only space, tab, newline andcarriage return runs, trim ordinary spaces, and translateASCII A-Z to a-z. Preserve otherUnicode code points. Expected: All 12 golden outputs, includingcafÉ,İi, nonbreaking-space-wrapped a and unchanged decomposed e-plus-accent. Verify: Apply the scalar function to every raw fixture value and compare with all golden pairs.
# Exercise 2: Express the same rule with native Spark functions. Inputs/task: Produce id, normalized using translate, regexp_replace andtrim on the label column. PreserveNULL propagation and the exact golden values. Expected: The twelve ordered output pairs equal the golden fixture and normalized has string type. Verify: Assert the full pair list andStringType;do not accept agreement with only one UDF implementation.
# Exercise 3: Wrap the scalar rule with a declared UDF return type. Inputs/task: Create a ScalaString UDF or a PythonStringType scalar UDF with useArrow=False, then return id, normalized. Keep the function pure and validate all outputs. Expected: Every pair matches the same twelve golden values. Python uses the non-Arrow scalar path;Scala stays in the JVM. Verify: Assert all golden pairs and string result type for the enabled language-specific UDF.
# Exercise 4: Locate the execution boundary in physical evidence. Inputs/task: Return the physical plan strings for the built-in and language-specific UDF relations. Identify Python evaluation only where it is actually present. Expected: Python UDF plan containsBatchEvalPython;built-in contains noPython evaluator. Scala UDF expression is present withoutBatchEvalPython orArrowEvalPython. Verify: Assert the language-appropriate markers and print both plans;do not infer a speed ratio from them.
# Exercise 5: Preserve missing, empty and ordinary-text populations. Inputs/task: Classify normalized values as missing, empty or text and count each category. Separately select the identity whose normalized text equals the literal null. Expected: Missing 1, empty 2, text 9. Literal null text belongs only toID 12;unknown value belongs only toID 1. Verify: Assert all category counts and both exact identity selections for built-in and UDF results.
# Exercise 6: Reject a plausible but semantically broader implementation. Inputs/task: Validate a result against the full golden sequence. Deliberately apply general lowercasing and default trimming without interior-whitespace collapse, and require rejection. Expected: The wrong implementation disagrees at least onIDs 4,5,6,9. Python additionally removes the preserved nonbreaking spaces atID 8. Verify: Assert named mismatch identities and that the golden validator raises rather than accepting a visually plausible normalization.

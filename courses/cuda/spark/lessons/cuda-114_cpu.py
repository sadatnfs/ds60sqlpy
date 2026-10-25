"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""


def compatible(spark_scala, jar_scala, host_arch, jar_arch):
    return spark_scala == jar_scala and host_arch == jar_arch


assert compatible("2.13", "2.13", "x86_64", "x86_64")
assert not compatible("2.13", "2.12", "x86_64", "x86_64")
print("CPU compatibility worksheet: mismatched Scala binary line rejected")

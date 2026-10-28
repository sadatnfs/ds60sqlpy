# julia-025: explained reference

The executable reference is `julia-025_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Trace the accumulator

The accumulator is Float64 throughout; the final value is 14.

**Expected observation:** The values are 1,5,14.

## 2. Preserve precision

zero(T) and floating multiplication preserve the specified small-case element arithmetic.

**Expected observation:** The result is Float32(5).

## 3. Change workload size

A larger workload changes the experiment. Multiple observations are needed to compare scaling.

**Expected observation:** Both return four times their length; observed time may vary.

## 4. Diagnose invalid science

Inference concerns types. Scientific input validation is a separate contract.

**Expected observation:** The numerical result is NaN.

## 5. Design a benchmark record

A benchmark record identifies environment and work; a number without these cannot support a transferable claim.

**Expected observation:** Include input, versions, threads, cold/warm boundary and repetitions.

## 6. Transfer to a data pipeline

Phase measurements explain bottlenecks while end-to-end time captures the actual user experience.

**Expected observation:** Separate phases plus end-to-end time.

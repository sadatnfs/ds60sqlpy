fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Decimal128Array};
        use arrow::datatypes::DataType;
        let prices = Decimal128Array::from(vec![125_i128, 250]).with_precision_and_scale(10, 2)?;
        assert_eq!(prices.value(0), 125);
        assert_eq!(prices.data_type(), &DataType::Decimal128(10, 2));
    }

    {
        use arrow::array::{Array, TimestampMillisecondArray};
        use arrow::datatypes::{DataType, TimeUnit};
        let times = TimestampMillisecondArray::from(vec![0_i64, 1000]).with_timezone("UTC");
        assert_eq!(times.value(1), 1000);
        assert_eq!(
            times.data_type(),
            &DataType::Timestamp(TimeUnit::Millisecond, Some("UTC".into()))
        );
    }

    {
        // Task 2: Guided modification
        use arrow::array::{Array, Decimal128Array};
        use arrow::datatypes::DataType;
        let prices =
            Decimal128Array::from(vec![125_i128, 250, -375]).with_precision_and_scale(10, 2)?;
        assert_eq!(prices.value(2), -375);
        assert_eq!(prices.value_as_string(2), "-3.75");
        assert_eq!(prices.data_type(), &DataType::Decimal128(10, 2));
        assert_eq!(prices.iter().flatten().sum::<i128>(), 0);
    }

    {
        // Task 3: Independent construction
        use arrow::datatypes::{DataType, Field, Schema, TimeUnit};
        use std::collections::HashMap;
        let unit = HashMap::from([("unit".to_string(), "kg".to_string())]);
        let mass = Field::new("mass", DataType::Float64, false);
        let mass = mass.with_metadata(unit);
        let precision = DataType::Timestamp(TimeUnit::Millisecond, Some("UTC".into()));
        let time = Field::new("measured_at", precision.clone(), false);
        let schema = Schema::new(vec![mass, time]);
        let recorded = schema.field(0).metadata().get("unit");
        assert_eq!(recorded.map(String::as_str), Some("kg"));
        assert_eq!(schema.field(1).data_type(), &precision);
    }

    {
        // Task 5: Boundary evidence
        use arrow::array::{Array, ArrayRef, Decimal128Array, TimestampMillisecondArray};
        use arrow::datatypes::{DataType, Field, Schema, TimeUnit};
        use arrow::record_batch::RecordBatch;
        use std::sync::Arc;
        let prices =
            Decimal128Array::from(vec![Some(125_i128), None]).with_precision_and_scale(10, 2)?;
        let times =
            TimestampMillisecondArray::from(vec![None, Some(1000_i64)]).with_timezone("UTC");
        assert_eq!((prices.null_count(), times.null_count()), (1, 1));
        assert!(prices.is_null(1) && times.is_null(0));
        let schema = Arc::new(Schema::new(vec![
            Field::new("price", DataType::Decimal128(10, 2), true),
            Field::new(
                "measured_at",
                DataType::Timestamp(TimeUnit::Millisecond, Some("UTC".into())),
                true,
            ),
        ]));
        let good: Vec<ArrayRef> = vec![Arc::new(prices.clone()), Arc::new(times.clone())];
        assert_eq!(RecordBatch::try_new(schema.clone(), good)?.num_rows(), 2);
        let wrong_scale: Vec<ArrayRef> = vec![
            Arc::new(prices.with_precision_and_scale(10, 3)?),
            Arc::new(times),
        ];
        assert!(RecordBatch::try_new(schema, wrong_scale).is_err());
    }
    println!("rust-044: passed");
    Ok(())
}

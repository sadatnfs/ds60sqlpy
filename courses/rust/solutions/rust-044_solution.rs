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
    println!("rust-044: passed");
    Ok(())
}

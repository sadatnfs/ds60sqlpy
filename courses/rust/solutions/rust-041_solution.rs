

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Builder, ListBuilder};
        let mut builder = ListBuilder::new(Int32Builder::new());
        builder.values().append_value(2); builder.values().append_null(); builder.append(true);
        builder.append(true);
        builder.append(false);
        let lists = builder.finish();
        assert_eq!(lists.len(), 3);
        assert_eq!(lists.value_length(0), 2);
        assert_eq!(lists.value_length(1), 0);
        assert!(lists.is_null(2));
    }

    {
        use arrow::array::{Array, StringArray};
        let values = StringArray::from(vec!["first", "middle", "last"]);
        let slice = values.slice(1, 1);
        let typed = slice.as_any().downcast_ref::<StringArray>().unwrap();
        assert_eq!(typed.len(), 1);
        assert_eq!(typed.value(0), "middle");
    }
    println!("rust-041: passed");
    Ok(())
}

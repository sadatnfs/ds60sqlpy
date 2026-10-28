use ballista::datafusion::{
    common::Result,
    prelude::{ParquetReadOptions, SessionContext},
};
use ballista::prelude::*;

#[tokio::main]
async fn main() -> Result<()> {
    let context = SessionContext::remote("df://scheduler:50050").await?;
    context
        .register_parquet(
            "orders",
            "/state/orders.parquet",
            ParquetReadOptions::default(),
        )
        .await?;
    let batches = context.sql("SELECT region,COUNT(*) AS n,SUM(amount) AS total FROM orders GROUP BY region ORDER BY region").await?.collect().await?;
    let rows: usize = batches.iter().map(|batch| batch.num_rows()).sum();
    assert_eq!(rows, 2);
    println!("Actual collected rows: {rows}; reconcile values with the independent fixture oracle");
    Ok(())
}

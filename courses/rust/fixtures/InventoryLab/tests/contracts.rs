use inventory_lab::{render, summarize};

#[test]
fn repeated_names_aggregate_in_sorted_order() {
    let report = summarize(&["b,2", "a,3", "b,4"]);
    assert_eq!(render(&report), "a=3;b=6;rejected=0");
}

#[test]
fn rejected_rows_do_not_become_valid_zero() {
    let report = summarize(&["pear,0", "bad", "apple,-1", "pear,no", ",2"]);
    assert_eq!(report.totals.get("pear"), Some(&0));
    assert_eq!(report.totals.len(), 1);
    assert_eq!(report.rejected, 4);
}

#[test]
fn overflow_preserves_the_previous_valid_total() {
    let report = summarize(&["large,4294967295", "large,1"]);
    assert_eq!(report.totals.get("large"), Some(&u32::MAX));
    assert_eq!(report.rejected, 1);
}

#[test]
fn empty_input_and_extra_fields_are_explicit() {
    assert!(summarize(&[]).totals.is_empty());
    assert_eq!(summarize(&["pear,2,extra"]).rejected, 1);
}

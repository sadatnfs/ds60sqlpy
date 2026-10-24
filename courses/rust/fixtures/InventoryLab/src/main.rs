fn main() {
    let report = inventory_lab::summarize(&["pear,2", "apple,3", "pear,4", "bad"]);
    let text = inventory_lab::render(&report);
    assert_eq!(text, "apple=3;pear=6;rejected=1");
    println!("{text}");
}

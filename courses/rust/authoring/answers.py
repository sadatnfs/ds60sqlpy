"""Reference answers for guide tasks, executed inside the lesson reference.

Each entry maps a lesson number to {task number: answer}. A code answer has `code` (a
block run after the worked examples, in rustfmt's canonical style), `observe` (the
checked observation) and `explain`. A written answer has only `explain`. Tasks without
an entry are reported as having no reference answer yet; `render.py` prints coverage.
"""

ANSWERS = {
    1: {
        3: dict(
            code="""let shelves = 3;
let books_per_shelf = 8;
let capacity = shelves * books_per_shelf;
assert_eq!(capacity, 24);""",
            observe="Three shelves of eight books hold 24 books.",
            explain="The product is written as a calculation, and assert_eq! compares it with 24, a value worked out independently.",
        )
    },
    2: {
        3: dict(
            code="""let deliveries = [3, 5, 2];
let mut total = 0;
for amount in deliveries {
    total += amount;
}
assert_eq!(total, 10);
assert_eq!(deliveries, [3, 5, 2]);""",
            observe="The running total ends at 10 and the input array is unchanged.",
            explain="Only the accumulator is declared mut; the fixed input stays immutable, so the compiler rejects any accidental edit to it.",
        )
    },
    3: {
        3: dict(
            code="""fn total_cents(price: u64, quantity: u64) -> Result<u64, String> {
    price
        .checked_mul(quantity)
        .ok_or_else(|| String::from("total overflows u64"))
}
assert_eq!(total_cents(125, 3), Ok(375));
assert!(total_cents(u64::MAX, 2).is_err());""",
            observe="125 cents times 3 is Ok(375); u64::MAX times 2 is an explicit Err.",
            explain="checked_mul returns None on overflow, and ok_or_else turns that into a named failure instead of a wrapped or saturated total.",
        )
    },
    4: {
        3: dict(
            code="""fn byte_length(text: &str) -> usize {
    text.len()
}
assert_eq!(byte_length("pear"), 4);
assert_eq!(byte_length("é"), 2);
assert_eq!(byte_length(&String::from("café")), 5);""",
            observe="pear has 4 bytes, é has 2 and café has 5.",
            explain="&str accepts both literals and borrowed Strings, and len counts UTF-8 bytes rather than characters.",
        )
    },
    5: {
        3: dict(
            code="""fn classify(value: i32) -> &'static str {
    match value {
        i32::MIN..=-1 => "negative",
        0 => "zero",
        1..=i32::MAX => "positive",
    }
}
assert_eq!(classify(-4), "negative");
assert_eq!(classify(0), "zero");
assert_eq!(classify(9), "positive");""",
            observe="-4, 0 and 9 are classified as negative, zero and positive.",
            explain="The three ranges cover every i32 exactly once, so the match is exhaustive without a catch-all arm that could hide a mistake.",
        )
    },
    6: {
        3: dict(
            code="""fn first_index(values: &[i32], target: i32) -> Option<usize> {
    for (index, value) in values.iter().enumerate() {
        if *value == target {
            return Some(index);
        }
    }
    None
}
assert_eq!(first_index(&[5, 7, 7], 7), Some(1));
assert_eq!(first_index(&[5, 7], 9), None);
assert_eq!(first_index(&[], 1), None);""",
            observe="The first 7 is at index 1; a missing target and an empty slice give None.",
            explain="Option keeps not-found separate from every valid index, and the loop stops at the first match.",
        )
    },
    7: {
        3: dict(
            code="""/// Area of a rectangle; both sides must be at most 65_535.
fn area(width: u32, height: u32) -> u32 {
    assert!(width <= 65_535 && height <= 65_535);
    width * height
}
assert_eq!(area(3, 4), 12);
assert_eq!(area(0, 9), 0);
assert_eq!(area(65_535, 65_535), 4_294_836_225);""",
            observe="3 by 4 gives 12, a zero side gives 0, and the documented maximum still fits in u32.",
            explain="The documented range is exactly the one whose product fits in u32, and the function checks it, so callers cannot reach an overflow.",
        )
    },
    8: {
        3: dict(
            code="""fn shout(mut text: String) -> String {
    text.push('!');
    text
}
let original = String::from("ready");
let louder = shout(original);
assert_eq!(louder, "ready!");""",
            observe="The returned String is ready! and ownership has moved into louder.",
            explain="Taking String by value transfers ownership into the function, which may mutate it and hand ownership back; original can no longer be used.",
        )
    },
    9: {
        3: dict(
            code="""fn last_word(text: &str) -> &str {
    text.split_whitespace().last().unwrap_or("")
}
let sentence = String::from("pear apple");
assert_eq!(last_word(&sentence), "apple");
assert_eq!(last_word(""), "");""",
            observe="The last word of pear apple is apple; empty text gives an empty slice.",
            explain="The returned slice borrows from the input, so the elided lifetime ties the result to text and no new String is allocated.",
        )
    },
    10: {
        3: dict(
            code="""fn swap_ends(values: &mut [i32]) {
    if let Some(last) = values.len().checked_sub(1) {
        values.swap(0, last);
    }
}
let mut values = [1, 2, 3];
swap_ends(&mut values);
assert_eq!(values, [3, 2, 1]);
let mut empty: [i32; 0] = [];
swap_ends(&mut empty);
assert!(empty.is_empty());""",
            observe="[1, 2, 3] becomes [3, 2, 1], and an empty slice is left alone.",
            explain="checked_sub avoids underflow for an empty slice, and swap performs both writes through the one exclusive borrow.",
        )
    },
    11: {
        3: dict(
            code="""fn maximum(values: &[i32]) -> Option<i32> {
    values.iter().copied().max()
}
assert_eq!(maximum(&[3, 9, 4]), Some(9));
assert_eq!(maximum(&[]), None);""",
            observe="The maximum of 3, 9 and 4 is Some(9); an empty slice gives None.",
            explain="Returning Option makes the empty case explicit instead of inventing a sentinel such as i32::MIN.",
        )
    },
    12: {
        3: dict(
            code="""struct Counter {
    value: u32,
    limit: u32,
}
impl Counter {
    fn new(limit: u32) -> Self {
        Self { value: 0, limit }
    }
    fn increment(&mut self) -> bool {
        if self.value == self.limit {
            return false;
        }
        self.value += 1;
        true
    }
}
let mut counter = Counter::new(2);
assert!(counter.increment() && counter.increment());
assert!(!counter.increment());
assert_eq!(counter.value, 2);""",
            observe="Two increments succeed, the third is refused, and the value stays at the limit 2.",
            explain="The fields are private to the defining module, so callers can change the counter only through increment, which checks the limit first.",
        )
    },
    13: {
        3: dict(
            code="""enum Import {
    Pending { queued: usize },
    Completed { rows: usize },
    Rejected { reason: String },
}
fn describe(state: &Import) -> String {
    match state {
        Import::Pending { queued } => format!("pending:{queued}"),
        Import::Completed { rows } => format!("done:{rows}"),
        Import::Rejected { reason } => format!("rejected:{reason}"),
    }
}
assert_eq!(describe(&Import::Pending { queued: 2 }), "pending:2");
assert_eq!(describe(&Import::Completed { rows: 5 }), "done:5");
let rejected = Import::Rejected {
    reason: String::from("bad header"),
};
assert_eq!(describe(&rejected), "rejected:bad header");""",
            observe="The three states render as pending:2, done:5 and rejected:bad header.",
            explain="Each variant carries only the data that makes sense in that state, and the exhaustive match must handle all three.",
        )
    },
    14: {
        3: dict(
            code="""fn first_valid(values: &[i32]) -> Option<i32> {
    values.iter().copied().find(|value| *value >= 0)
}
assert_eq!(first_valid(&[-2, 0, 5]), Some(0));
assert_eq!(first_valid(&[-1, -3]), None);""",
            observe="The first valid item in -2, 0, 5 is Some(0); no valid item gives None.",
            explain="find returns Option, so a valid zero stays distinguishable from having no valid item at all.",
        )
    },
    15: {
        3: dict(
            code="""fn doubled_quantity(text: &str) -> Result<i32, &'static str> {
    let value = parse_quantity(text)?;
    value.checked_mul(2).ok_or("quantity too large")
}
assert_eq!(doubled_quantity("4"), Ok(8));
assert_eq!(doubled_quantity("bad"), Err("not an integer"));
assert_eq!(doubled_quantity("-3"), Err("negative quantity"));""",
            observe="4 doubles to Ok(8); bad text and -3 return their original errors.",
            explain="The ? operator returns the parse error unchanged, so each failure keeps the message of the step that produced it.",
        )
    },
    16: {
        3: dict(
            code="""let (totals, rejected) = import_rows(&["pear,2", "apple,3", "bad"]);
let mut report = String::new();
for (name, total) in &totals {
    report.push_str(&format!("{name}: {total}\\n"));
}
report.push_str(&format!("rejected: {rejected}"));
assert_eq!(report, "apple: 3\\npear: 2\\nrejected: 1");""",
            observe="The report lists apple: 3, pear: 2 and rejected: 1.",
            explain="A BTreeMap iterates in key order, so the report is sorted without a separate sort step, and the rejection count is printed explicitly.",
        )
    },
    17: {
        3: dict(
            code="""trait Formatter {
    fn format(&self, value: u32) -> String;
}
struct Units;
impl Formatter for Units {
    fn format(&self, value: u32) -> String {
        format!("{value} units")
    }
}
let formatter: &dyn Formatter = &Units;
assert_eq!(formatter.format(3), "3 units");
assert_eq!(formatter.format(3), formatter.format(3));""",
            observe="The formatter turns 3 into 3 units, identically on every call.",
            explain="The trait states the contract, and the implementation depends only on its input, so repeated calls agree.",
        )
    },
    18: {
        3: dict(
            code="""struct Pair<T> {
    first: T,
    second: T,
}
impl<T> Pair<T> {
    fn swap(self) -> Pair<T> {
        Pair {
            first: self.second,
            second: self.first,
        }
    }
}
let pair = Pair {
    first: String::from("left"),
    second: String::from("right"),
};
let swapped = pair.swap();
assert_eq!(swapped.first, "right");
assert_eq!(swapped.second, "left");""",
            observe="Swapping (left, right) gives (right, left) without cloning either String.",
            explain="swap takes self by value, so it can move both owned elements into the new pair.",
        )
    },
    19: {
        3: dict(
            code="""fn split_prefix<'a>(text: &'a str, prefix: &str) -> Option<&'a str> {
    text.strip_prefix(prefix)
}
let line = String::from("qty:42");
let rest = {
    let prefix = String::from("qty:");
    split_prefix(&line, &prefix)
};
assert_eq!(rest, Some("42"));""",
            observe='The rest of qty:42 is Some("42"), still usable after the prefix String is dropped.',
            explain="Only text shares the result's lifetime 'a; prefix gets its own shorter lifetime, so the caller can drop it while keeping the result.",
        )
    },
    20: {
        3: dict(
            code="""fn upper_names(names: &[&str]) -> Vec<String> {
    names.iter().map(|name| name.to_uppercase()).collect()
}
let names = ["pear", "fig"];
assert_eq!(upper_names(&names), vec!["PEAR", "FIG"]);
assert_eq!(names, ["pear", "fig"]);""",
            observe="The result is PEAR and FIG, and the borrowed input is unchanged.",
            explain="The function borrows the input slice, the iterator chain is lazy, and collect consumes it into a new owned Vec.",
        )
    },
    21: {
        3: dict(
            code="""fn apply_times(times: usize, mut step: impl FnMut()) {
    for _ in 0..times {
        step();
    }
}
let mut value = 1;
apply_times(3, || value *= 2);
assert_eq!(value, 8);""",
            observe="Doubling three times turns 1 into 8.",
            explain="FnMut allows the closure to mutate its captured value on each call, which Fn would forbid.",
        )
    },
    22: {
        3: dict(
            code="""#[derive(Debug)]
enum ImportError {
    Syntax { line: usize },
    Storage(std::io::Error),
}
impl std::fmt::Display for ImportError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Syntax { line } => write!(f, "syntax error on line {line}"),
            Self::Storage(_) => write!(f, "storage failed"),
        }
    }
}
impl std::error::Error for ImportError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Syntax { .. } => None,
            Self::Storage(cause) => Some(cause),
        }
    }
}
use std::error::Error;
let syntax = ImportError::Syntax { line: 3 };
assert_eq!(syntax.to_string(), "syntax error on line 3");
assert!(syntax.source().is_none());
let cause = std::io::Error::other("disk full");
let storage = ImportError::Storage(cause);
assert_eq!(storage.source().unwrap().to_string(), "disk full");""",
            observe="The syntax error names line 3; the storage error keeps the disk full cause reachable through source.",
            explain="Separate variants let callers fix input or retry storage, and source preserves the underlying io::Error instead of flattening it into a string.",
        )
    },
    23: {
        3: dict(
            code="""mod pricing {
    pub fn total(unit: u32, quantity: u32) -> Option<u32> {
        unit.checked_mul(quantity)
    }
}
assert_eq!(pricing::total(4, 5), Some(20));
assert_eq!(pricing::total(u32::MAX, 2), None);""",
            observe="pricing::total(4, 5) is Some(20); an overflowing total is None.",
            explain="Only the pub function is visible outside the module, so the module can change its internals without breaking callers.",
        )
    },
    24: {
        3: dict(
            code="""fn valid_quantity(value: i32) -> bool {
    (0..=1000).contains(&value)
}
let cases = [(-1, false), (0, true), (1000, true), (1001, false)];
for (input, expected) in cases {
    assert_eq!(valid_quantity(input), expected, "input {input}");
}""",
            observe="All four rows pass, including both edges of the 0 to 1000 range.",
            explain="Each row pairs an input with an independently written expectation, and the message names the failing input.",
        )
    },
    25: {
        3: dict(
            code="""let name = format!("report-{}.txt", std::process::id());
let path = std::env::temp_dir().join(name);
let report = "pear: 3\\napple: 5\\n";
let mut file = std::fs::OpenOptions::new()
    .write(true)
    .create_new(true)
    .open(&path)?;
std::io::Write::write_all(&mut file, report.as_bytes())?;
drop(file);
let restored = std::fs::read_to_string(&path);
std::fs::remove_file(&path)?;
assert_eq!(restored?, report);
assert!(!path.exists());""",
            observe="The report reads back unchanged and the temporary file is removed.",
            explain="`create_new(true)` refuses to open a path that already exists, so the round trip never truncates someone else's file, which `std::fs::write` would do. The file is removed before the read result is checked, so cleanup happens even when the comparison fails.",
        )
    },
    26: {
        3: dict(
            code="""let words = ["pear", "fig", "pear", "apple"];
let mut counts = std::collections::BTreeMap::new();
for word in words {
    *counts.entry(word).or_insert(0) += 1;
}
let report: Vec<String> = counts.iter().map(|(w, n)| format!("{w}={n}")).collect();
assert_eq!(report, ["apple=1", "fig=1", "pear=2"]);""",
            observe="The report is apple=1, fig=1, pear=2, always in that order.",
            explain="A BTreeMap keeps keys sorted, so the output does not depend on hashing or insertion order.",
        )
    },
    27: {
        3: dict(
            code="""let values = [1, 2, 3, 4, 5, 6];
let (left, right) = values.split_at(3);
let (a, b) = std::thread::scope(|scope| {
    let first = scope.spawn(|| left.iter().sum::<i32>());
    let second = scope.spawn(|| right.iter().sum::<i32>());
    (first.join().unwrap(), second.join().unwrap())
});
assert_eq!((a, b), (6, 15));
assert_eq!(a + b, values.iter().sum::<i32>());""",
            observe="The halves sum to 6 and 15, together 21, the same as the sequential sum.",
            explain="Scoped threads may borrow values because scope joins them before returning, and each join hands a result back to the parent.",
        )
    },
    28: {
        3: dict(
            code="""let stock = std::sync::Mutex::new(5_u32);
let reserve = |amount: u32| {
    let mut available = stock.lock().unwrap();
    let granted = amount <= *available;
    if granted {
        *available -= amount;
    }
    granted
};
let results: Vec<bool> = std::thread::scope(|scope| {
    let handles: Vec<_> = (0..4).map(|_| scope.spawn(|| reserve(2))).collect();
    handles
        .into_iter()
        .map(|handle| handle.join().unwrap())
        .collect()
});
assert_eq!(results.iter().filter(|granted| **granted).count(), 2);
assert_eq!(*stock.lock().unwrap(), 1);""",
            observe="Of four concurrent requests for 2 units from a stock of 5, exactly two succeed and 1 unit remains.",
            explain="The check and the decrement happen under one lock guard, so no other thread can reserve between them and the stock never goes negative.",
        )
    },
    29: {
        3: dict(
            code="""let (send, receive) = std::sync::mpsc::sync_channel::<u32>(2);
let producer = std::thread::spawn(move || {
    for quantity in [3, 5, 2] {
        send.send(quantity).unwrap();
    }
});
let mut report = Vec::new();
for quantity in receive {
    report.push(format!("qty={quantity}"));
}
producer.join().unwrap();
assert_eq!(report, ["qty=3", "qty=5", "qty=2"]);""",
            observe="The consumer reports qty=3, qty=5 and qty=2 in order and then stops.",
            explain="sync_channel(2) blocks the producer when two items are waiting, and the receiving loop ends when the producer's sender is dropped.",
        )
    },
    30: {
        3: dict(
            code="""use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
let counter = Arc::new(AtomicUsize::new(0));
let mut handles = Vec::new();
for _ in 0..4 {
    let counter = Arc::clone(&counter);
    handles.push(std::thread::spawn(move || {
        for _ in 0..100 {
            counter.fetch_add(1, Ordering::Relaxed);
        }
    }));
}
for handle in handles {
    handle.join().unwrap();
}
assert_eq!(counter.load(Ordering::Relaxed), 400);""",
            observe="Four threads adding 100 each produce exactly 400.",
            explain="Arc<AtomicUsize> is Send and Sync, so the compiler accepts sharing it; a single counter needs no lock, and joining every thread makes the final load see all updates.",
        )
    },
    31: {
        3: dict(
            code="""use std::cell::RefCell;
use std::rc::{Rc, Weak};
struct Parent {
    name: String,
    children: RefCell<Vec<Rc<Child>>>,
}
struct Child {
    parent: RefCell<Weak<Parent>>,
}
let parent = Rc::new(Parent {
    name: String::from("root"),
    children: RefCell::new(Vec::new()),
});
let child = Rc::new(Child {
    parent: RefCell::new(Weak::new()),
});
*child.parent.borrow_mut() = Rc::downgrade(&parent);
parent.children.borrow_mut().push(Rc::clone(&child));
let found = child.parent.borrow().upgrade().map(|p| p.name.clone());
assert_eq!(found.as_deref(), Some("root"));
assert_eq!(Rc::strong_count(&parent), 1);
drop(parent);
assert!(child.parent.borrow().upgrade().is_none());""",
            observe="The child finds root while the parent lives, the parent keeps one strong count, and after it is dropped the back-reference upgrades to None.",
            explain="The parent owns its children with Rc, while each child refers back with Weak, so the pair forms no reference cycle and the parent can be freed.",
        )
    },
    33: {
        3: dict(
            explain="One possible trace: (1) the caller creates the future and hands it to the executor, which now owns it and keeps it pinned; (2) the executor polls it with a Context whose Waker it supplies; (3) the future registers that waker with the resource it waits on and returns Pending; (4) the resource calls wake, which only schedules the task again; (5) the executor polls once more, the future returns Ready(value), and the executor drops the future and delivers the value to whoever awaits the task. The executor does none of the future's work itself: it owns the future, polls it only when woken, and must drop it on completion or cancellation.",
        )
    },
    34: {
        3: dict(
            code="""/// Returns the first two values, or None when fewer than two exist.
/// Never reads past the end of the slice and never panics.
fn first_two(values: &[i32]) -> Option<(i32, i32)> {
    match values {
        [first, second, ..] => Some((*first, *second)),
        _ => None,
    }
}
assert_eq!(first_two(&[4, 5, 6]), Some((4, 5)));
assert_eq!(first_two(&[4]), None);""",
            observe="first_two returns Some((4, 5)) for three values and None for one.",
            explain="The specification fixes the input, the output and the no-panic guarantee before any implementation. A safe slice pattern already meets it; an unsafe body such as get_unchecked would be considered only if measurement showed a need, with a SAFETY comment proving each index is below the checked length.",
        )
    },
    35: {
        3: dict(
            code="""fn total_cloned(rows: &[String]) -> usize {
    rows.iter().map(|row| row.clone().len()).sum()
}
fn total_borrowed(rows: &[String]) -> usize {
    rows.iter().map(|row| row.len()).sum()
}
let rows: Vec<String> = (0..100).map(|i| format!("row-{i}")).collect();
assert_eq!(total_cloned(&rows), total_borrowed(&rows));""",
            observe="Both versions return the same total, so a benchmark compares only their cost.",
            explain="Plan: first prove the two versions agree, as this check does; then time both in a release build at several input sizes (100, 10,000 and 1,000,000 rows) after a warm-up, repeat each measurement, and report the median and spread together with allocation counts. One run on one machine is not a general performance claim.",
        )
    },
    37: {
        3: dict(
            code="""use arrow::array::{Array, Int32Array, StringArray};
let names = StringArray::from(vec!["pear", "apple", "fig"]);
let quantities = Int32Array::from(vec![2, 5, 1]);
assert_eq!(names.len(), quantities.len());
assert_eq!(names.value(1), "apple");
assert_eq!(quantities.value(1), 5);""",
            observe="Both columns have 3 rows, and row 1 pairs apple with 5.",
            explain="Paired columns describe the same rows only when their lengths match, so the length check comes before reading any position.",
        )
    },
    38: {
        3: dict(
            code="""use arrow::array::{Array, Float64Array};
fn summary(values: &Float64Array) -> (usize, usize, usize) {
    let valid = values.len() - values.null_count();
    let finite = values.iter().flatten().filter(|v| v.is_finite()).count();
    (valid, values.null_count(), finite)
}
let values = Float64Array::from(vec![Some(1.5), None, Some(f64::NAN), Some(2.0)]);
assert_eq!(summary(&values), (3, 1, 2));""",
            observe="Four slots give 3 valid values, 1 null and 2 finite values.",
            explain="Validity and finiteness are different questions: NaN is a valid, non-null value that is not finite, while the null slot has no value at all.",
        )
    },
    39: {
        3: dict(
            code="""use arrow::array::{ArrayRef, Int32Array, StringArray};
use arrow::datatypes::{DataType, Field, Schema};
use arrow::record_batch::RecordBatch;
use std::sync::Arc;
let rows = [("pear", 2), ("apple", -1), ("fig", 4)];
let valid: Vec<_> = rows.iter().filter(|(_, qty)| *qty >= 0).collect();
let names: Vec<&str> = valid.iter().map(|(name, _)| *name).collect();
let quantities: Vec<i32> = valid.iter().map(|(_, qty)| *qty).collect();
let schema = Schema::new(vec![
    Field::new("name", DataType::Utf8, false),
    Field::new("quantity", DataType::Int32, false),
]);
let columns: Vec<ArrayRef> = vec![
    Arc::new(StringArray::from(names)),
    Arc::new(Int32Array::from(quantities)),
];
let batch = RecordBatch::try_new(Arc::new(schema), columns)?;
assert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));""",
            observe="The negative apple row is rejected before construction, leaving a batch of 2 rows and 2 columns.",
            explain="Validation runs on plain rows first, so the batch only ever holds valid data, and try_new still checks that the columns match the schema.",
        )
    },
    40: {
        3: dict(
            code="""use arrow::array::{ArrayRef, AsArray, BooleanArray, Int32Array, StringArray};
use arrow::record_batch::RecordBatch;
use std::sync::Arc;
let names: ArrayRef = Arc::new(StringArray::from(vec!["pear", "fig", "kiwi"]));
let qty: ArrayRef = Arc::new(Int32Array::from(vec![2, 0, 5]));
let batch = RecordBatch::try_from_iter(vec![("name", names), ("qty", qty)])?;
let mask = BooleanArray::from(vec![true, false, true]);
let kept = arrow::compute::filter_record_batch(&batch, &mask)?;
assert_eq!(kept.num_rows(), 2);
let kept_names = kept.column(0).as_string::<i32>();
assert_eq!(kept_names.value(1), "kiwi");""",
            observe="Filtering keeps rows 0 and 2 in every column: pear and kiwi with their quantities.",
            explain="filter_record_batch applies one mask to all columns at once, so names and quantities can never fall out of alignment.",
        )
    },
    41: {
        3: dict(
            code="""use arrow::array::{Array, Int32Builder, ListBuilder};
let rows = [vec![1, 2], vec![], vec![3]];
let mut builder = ListBuilder::new(Int32Builder::new());
for row in &rows {
    for value in row {
        builder.values().append_value(*value);
    }
    builder.append(true);
}
let lists = builder.finish();
assert_eq!(lists.len(), 3);
let lengths: Vec<i32> = (0..3).map(|i| lists.value_length(i)).collect();
assert_eq!(lengths, [2, 0, 1]);""",
            observe="The nested column holds 3 lists with lengths 2, 0 and 1.",
            explain="Child values are appended to one shared buffer and each append(true) closes a row, so the empty middle list is a valid row rather than a null.",
        )
    },
    42: {
        3: dict(
            code="""use arrow::array::{Array, ArrayRef, Int32Array};
use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
use arrow::record_batch::RecordBatch;
use std::sync::Arc;
let values: ArrayRef = Arc::new(Int32Array::from(vec![Some(4), None, Some(6)]));
let batch = RecordBatch::try_from_iter(vec![("qty", values)])?;
let mut bytes = Vec::new();
{
    let mut writer = StreamWriter::try_new(&mut bytes, &batch.schema())?;
    writer.write(&batch)?;
    writer.finish()?;
}
let mut reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
let restored = reader.next().unwrap()?;
assert_eq!(restored.column(0).null_count(), 1);
assert_eq!(restored, batch);""",
            observe="The restored batch equals the original, including its single null.",
            explain="finish writes the end-of-stream marker, and the reader reproduces the validity buffer, so a null stays a null instead of becoming 0.",
        )
    },
    43: {
        3: dict(
            code="""use arrow::array::{Array, AsArray};
use arrow::datatypes::{DataType, Field, Int32Type, Schema};
use std::sync::Arc;
let field = Field::new("quantity", DataType::Int32, true);
let schema = Arc::new(Schema::new(vec![field]));
let input = b"{\\"quantity\\":2}\\n{\\"quantity\\":null}\\n{\\"quantity\\":-1}\\n";
let mut reader = arrow::json::ReaderBuilder::new(schema).build(&input[..])?;
let batch = reader.next().unwrap()?;
let values = batch.column(0).as_primitive::<Int32Type>();
let negative = values.iter().flatten().filter(|v| *v < 0).count();
assert_eq!((values.len(), values.null_count(), negative), (3, 1, 1));""",
            observe="Reading succeeds with 3 rows, 1 null and 1 negative value that the domain check then reports.",
            explain="The schema decides what parses; the domain rule, nonnegative quantities, is a separate check run on the decoded values.",
        )
    },
    44: {
        3: dict(
            code="""use arrow::datatypes::{DataType, Field, Schema, TimeUnit};
use std::collections::HashMap;
let unit = HashMap::from([("unit".to_string(), "kg".to_string())]);
let mass = Field::new("mass", DataType::Float64, false);
let mass = mass.with_metadata(unit);
let precision = DataType::Timestamp(TimeUnit::Millisecond, Some("UTC".into()));
let time = Field::new("measured_at", precision.clone(), false);
let schema = Schema::new(vec![mass, time]);
let recorded = schema.field(0).metadata().get("unit");
assert_eq!(recorded.map(String::as_str), Some("kg"));
assert_eq!(schema.field(1).data_type(), &precision);""",
            observe="The mass field records unit kg and the timestamp field records millisecond UTC precision.",
            explain="Units live in field metadata and time precision in the data type, so both travel with the schema to every consumer.",
        )
    },
    45: {
        3: dict(
            code="""use arrow::array::{ArrayRef, AsArray, Int32Array};
use arrow::datatypes::Int32Type;
use arrow::record_batch::{RecordBatch, RecordBatchIterator};
use std::sync::Arc;
let mut batches = Vec::new();
for chunk in [vec![2, -1], vec![0, 3, -4]] {
    let column: ArrayRef = Arc::new(Int32Array::from(chunk));
    batches.push(RecordBatch::try_from_iter(vec![("qty", column)])?);
}
let schema = batches[0].schema();
let reader = RecordBatchIterator::new(batches.into_iter().map(Ok), schema);
let (mut rows, mut accepted) = (0, 0);
for batch in reader {
    let batch = batch?;
    let values = batch.column(0).as_primitive::<Int32Type>();
    rows += values.len();
    accepted += values.iter().flatten().filter(|v| *v >= 0).count();
}
assert_eq!((rows, accepted, rows - accepted), (5, 3, 2));""",
            observe="Across two batches, 5 rows split into 3 accepted and 2 rejected.",
            explain="Counting per batch while reading keeps memory bounded, and rows minus accepted gives the rejected count without double counting.",
        )
    },
    46: {
        3: dict(
            code="""let inputs = ["2", "x", "5", "-1"];
let mut accepted = 0;
let mut rejected = 0;
for text in inputs {
    match text.parse::<u32>() {
        Ok(_) => accepted += 1,
        Err(_) => rejected += 1,
    }
}
let submitted = inputs.len();
let counts = format!("accepted={accepted} rejected={rejected}");
let event = format!("submitted={submitted} {counts}");
assert_eq!(event, "submitted=4 accepted=2 rejected=2");
assert_eq!(accepted + rejected, submitted);""",
            observe="The event reads submitted=4 accepted=2 rejected=2.",
            explain="The event reports counts only, not the rejected text itself, and the final check proves every submitted record was counted once.",
        )
    },
    47: {
        3: dict(
            code="""use arrow::array::{Array, BooleanArray, Int32Array};
for pattern in 0_u32..16 {
    let mask: Vec<bool> = (0..4).map(|bit| pattern & (1 << bit) != 0).collect();
    let values = Int32Array::from(vec![1, 2, 3, 4]);
    let kept = arrow::compute::filter(&values, &BooleanArray::from(mask.clone()))?;
    let expected = mask.iter().filter(|keep| **keep).count();
    assert_eq!(kept.len(), expected);
}""",
            observe="For all 16 masks over four rows, the filtered length equals the number of true entries.",
            explain="Enumerating every mask of a small size checks the property exhaustively, including the all-false and all-true edge cases.",
        )
    },
    48: {
        3: dict(
            code="""use arrow::array::{ArrayRef, Int32Array, StringArray};
use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
use arrow::record_batch::RecordBatch;
use std::sync::Arc;
let names: ArrayRef = Arc::new(StringArray::from(vec!["apple", "pear"]));
let totals: ArrayRef = Arc::new(Int32Array::from(vec![5, 2]));
let report = RecordBatch::try_from_iter(vec![("name", names), ("total", totals)])?;
let mut bytes = Vec::new();
{
    let mut writer = StreamWriter::try_new(&mut bytes, &report.schema())?;
    writer.write(&report)?;
    writer.finish()?;
}
let mut reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
assert_eq!(reader.next().unwrap()?, report);
assert!(reader.next().is_none());""",
            observe="The two-column report round-trips unchanged and the stream ends after one batch.",
            explain="Comparing whole batches checks the schema and every column together, and the second next() proves the stream was finished explicitly.",
        )
    },
}

# Per-task reasoning. A written answer has `explain` (the approach), `why`, `wrong` (one
# plausible wrong approach and why it fails here) and `verify`. For a task that already
# has executed `code`, only `wrong` and `verify` are added; its code and observation stay.
REASONING = {
    1: {
        1: dict(
            explain='Only two statements print. Example A\'s `println!("{greeting}")` writes `Hello, Rust`; Example B and the `Task 3` block only assert; the last statement prints `rust-001: passed`. So stdout is exactly `Hello, Rust` followed by the marker line.',
            why="`main` runs its statements top to bottom, and a passing `assert_eq!` or `assert_ne!` produces no output. The seat count 24 and the shelf capacity are compared, never printed, so neither number can appear.",
            wrong="Predicting a confirmation line after each assertion, or the value 24 in the output, treats a check as a print. Predicting the marker first ignores that its `println!` is the final statement before `Ok(())`.",
            verify='Run the reference and compare stdout with the two-line prediction. Then change the expected literal in Example A to `"Hello, rust"`: the run panics with an `assert_eq!` failure showing both strings and prints nothing, because the assertion sits before the greeting\'s `println!`.',
        ),
        2: dict(
            explain='Edit the binding to `let greeting = "Hi, Ferris";` and type the expected literal into the check by hand: `assert_eq!(greeting, "Hi, Ferris");`. The two sides come from two separate sources, the code and the requirement.',
            why="Because the expected value is written from the requirement rather than read back from `greeting`, a typo in the binding makes the two strings differ and the program panics before printing a wrong greeting.",
            wrong='Writing `let expected = greeting; assert_eq!(greeting, expected);` compares the binding with itself. It passes for `"Hi, Feris"` or any other text, so the check can never reject a mistake.',
            verify='Misspell only the binding as `"Hi, Feris"` and run: the panic shows `left: "Hi, Feris"` and `right: "Hi, Ferris"`, and no greeting or marker is printed. Fix the spelling and both lines appear.',
        ),
        3: dict(
            wrong="Writing `let capacity = 24;` and asserting 24 copies the answer instead of computing it, so the check would still pass if the operator were wrong. Writing `shelves + books_per_shelf` instead gives 11, which this assertion does reject.",
            verify="Add Example B's style of second check, `assert_ne!(capacity, shelves + books_per_shelf);`, comparing 24 with 11. Then swap `*` for `+` temporarily: the run panics with `left: 11` and `right: 24` before `rust-001: passed`.",
        ),
        4: dict(
            explain="Delete the `}` that closes the `Task 3` block. rustc stops with `error: this file contains an unclosed delimiter` and labels the unmatched `{`. This is a compile-time syntax diagnostic: no executable is built, so not even `Hello, Rust` appears.",
            why="The parser must pair every delimiter before type checking or code generation can start. A panic, by contrast, happens while the program runs and would follow any earlier output such as the greeting.",
            wrong="Classifying it as a runtime crash because the run failed confuses the two kinds of evidence. A panic prints `thread 'main' panicked` after `Hello, Rust`; here nothing ran. Restoring a brace in a different place can also compile while moving the marker `println!` into the wrong block.",
            verify="Run with the brace missing: the output is a compiler error mentioning an unclosed delimiter and contains no program output. Restore the brace in its original position and the greeting and marker print again.",
        ),
        5: dict(
            explain="Wrap the formula as `fn capacity(shelves: u32, books_per_shelf: u32) -> u32 { shelves * books_per_shelf }` and check `assert_eq!(capacity(0, 8), 0);` and `assert_eq!(capacity(1, 8), 8);`.",
            why="Zero shelves hold zero books whatever the per-shelf number, and one shelf holds exactly one shelf's worth. Multiplication gives both results, so these two fixtures pin the formula at its smallest inputs.",
            wrong="Using addition, `shelves + books_per_shelf`, claims an empty bookcase holds 8 books and a single shelf holds 9. Testing only the three-shelf case would catch that too, but would not show that an empty bookcase is handled.",
            verify="Both assertions pass silently and `rust-001: passed` prints. Swap `*` for `+` and the zero-shelf check panics with `left: 8` and `right: 0`.",
        ),
        6: dict(
            explain="Model a library: `let floors = 2; let rooms_per_floor = 3; let shelves_per_room = 4; let books_per_shelf = 8;` then `let rooms = floors * rooms_per_floor;` (6), `let shelves = rooms * shelves_per_room;` (24) and `let books = shelves * books_per_shelf;` (192).",
            why="Each binding names one unit, so each intermediate value has its own hand-worked expectation: 2 times 3 rooms, 6 times 4 shelves, 24 times 8 books. A limitation is that every floor and room must be identical; irregular rooms need a sum over a list instead.",
            wrong="Skipping a level, for example `floors * shelves_per_room * books_per_shelf`, multiplies floors by a per-room figure and yields 64. Writing the whole product as one literal expression hides which level was dropped.",
            verify="Assert every level: `assert_eq!(rooms, 6); assert_eq!(shelves, 24); assert_eq!(books, 192);`. Change `rooms_per_floor` to 5 and the first failing check reports `left: 10`, naming the level that changed.",
        ),
    },
    2: {
        1: dict(
            explain="In Example A, `per_box` is an immutable `i32` and `total` is a mutable `i32`. In Example B, the first `count` is an immutable `&'static str`, the shadowing `count` is an immutable `usize`, and `explicit` is an immutable `u64`.",
            why="Unsuffixed integer literals fall back to `i32` when nothing else constrains them; a string literal has type `&'static str`; the `usize` annotation matches what `len()` returns; and the `_u64` suffix fixes `explicit`. Only `total` is written after initialization, so only it carries `mut`.",
            wrong="Describing `count` as one variable that changed from text to a number misreads shadowing. The second `let` creates a new binding and neither is mutable; writing `count = count.len();` without `let` would be rejected with a type mismatch.",
            verify="Add `fn type_of<T>(_: &T) -> &'static str { std::any::type_name::<T>() }` and print `type_of(&per_box)`, `type_of(&count)` and `type_of(&explicit)`: the pad shows `i32`, `usize` and `u64`.",
        ),
        2: dict(
            explain="Given `let mut per_box = 4; let mut total = 0; total += per_box; total += per_box;`, delete `mut` from `per_box`, which is never written again, and keep it on `total`. The compiler's `variable does not need to be mutable` warning points at exactly that binding.",
            why="`mut` grants permission to reassign or take a mutable borrow. Removing it where no write happens lets the compiler reject a future accidental write instead of silently accepting it.",
            wrong="Removing `mut` from every binding also strips it from `total`, and `total += per_box` then fails with E0384, cannot assign twice to an immutable variable. Silencing the warning with `#[allow(unused_mut)]` keeps the unneeded permission.",
            verify="Run the version with the extra `mut` and read the warning naming `per_box`. Remove it, run again: no warning, and `assert_eq!(total, 8)` still passes.",
        ),
        3: dict(
            wrong="Switching the input to `let deliveries = vec![3, 5, 2];` with the same loop fails to compile: `for amount in deliveries` moves the `Vec`, so the later `assert_eq!(deliveries, ...)` is E0382, borrow of moved value. The array version works because `[i32; 3]` is `Copy`; the `Vec` version needs `for amount in &deliveries`.",
            verify="Run the block: the total is 10 and the input still equals `[3, 5, 2]`. Add `deliveries[0] = 0;` temporarily and the compiler refuses it with E0594, because `deliveries` is not declared mutable.",
        ),
        4: dict(
            explain='The defect is `let mut count = 0; count = String::from("12");`. rustc reports E0308, mismatched types, expected integer, found `String`. `mut` allows a new value of the same type, and the type was fixed as an integer at the declaration. Convert instead: `count = "12".parse()?;`.',
            why="Each binding has one static type for its whole scope; mutability controls whether the value may change, never the type. `parse` produces an integer, and `?` forwards a `ParseIntError` through `main`'s boxed error.",
            wrong='Changing the declaration to `let mut count = String::new();` makes the assignment compile but turns every arithmetic use of `count` into a new error. Shadowing with `let count = String::from("12");` also compiles but hides that the value is now text, not a quantity.',
            verify='Compile the defect and read E0308 pointing at `String::from`. After the fix, `assert_eq!(count, 12);` passes. Changing the text to `"twelve"` makes `?` return the error, so the run ends with an `invalid digit found in string` message instead of the marker.',
        ),
        5: dict(
            explain='Shadow an empty input exactly as Example B does: `let count = ""; let count: usize = count.len(); assert_eq!(count, 0);`. For the accumulator, sum an empty array: `let deliveries: [i32; 0] = []; let mut total = 0; for amount in deliveries { total += amount; } assert_eq!(total, 0);`.',
            why="Empty text has zero bytes, so its length is 0 rather than an error. A loop over zero elements never runs its body, so the accumulator keeps its starting value, 0, which is the identity for addition.",
            wrong='Expecting `"".parse::<i32>()` to give 0 confuses empty with zero. It returns an `Err` whose kind is `Empty`, and calling `.unwrap()` on it panics with `ParseIntError { kind: Empty }`.',
            verify='Run both blocks and add `assert!("".parse::<i32>().is_err());`. All three checks pass silently and `rust-002: passed` prints.',
        ),
        6: dict(
            explain='Use shadowing when the meaning and unit stay the same, and a new name when they change: `let quantity_text = " 12 "; let quantity_text = quantity_text.trim();` then `let quantity: u32 = quantity_text.parse()?;`. Trimming keeps the value text, while parsing turns it into a count.',
            why="The reader can trust that every `quantity_text` is text and every `quantity` is a number, so a units change is visible in the name. A limitation is that long pipelines accumulate names; at that point a small parsing function is clearer.",
            wrong="Following Example B literally, `let quantity = quantity_text.len();` compiles and yields 2, the number of digits, instead of 12. Both are `usize`-compatible values, so only a check on the value exposes the mix-up.",
            verify='Assert `assert_eq!(quantity_text, "12");` and `assert_eq!(quantity, 12);`. Replace `parse()?` with `len() as u32` and the second check panics with `left: 2` and `right: 12`.',
        ),
    },
    4: {
        1: dict(
            explain="The precomposed `é` is U+00E9, encoded in UTF-8 as the two bytes `0xC3 0xA9`. So `len()` returns 2 and `chars().count()` returns 1, exactly as Example B asserts.",
            why="`len` counts bytes of the UTF-8 encoding, and scalars from U+0080 to U+07FF take two bytes. `chars` decodes those bytes back into one `char`.",
            wrong="Predicting `len() == 1` because the glyph looks like one character confuses bytes with scalars. Predicting two scalars is only right if the source holds the decomposed form `e` plus U+0301, which an editor might produce silently.",
            verify="Add `assert_eq!(\"é\".as_bytes(), &[0xC3, 0xA9]);` and `assert_eq!('é' as u32, 0xE9);`. If the first check fails with three bytes, the file contains the decomposed form.",
        ),
        2: dict(
            explain='Write both with escapes so no editor normalizes them: `let crab = "\\u{1F980}";` has `len()` 4 and one scalar, while `let accented = "e\\u{301}";` has `len()` 3 and two scalars, yet it displays as one accented letter.',
            why="Scalars above U+FFFF need four UTF-8 bytes. The combining acute accent U+0301 needs two bytes and follows a one-byte `e`, and `chars` yields it as its own scalar even though a reader sees one grapheme.",
            wrong='Treating `chars().count()` as the visible length makes `accented.chars().take(1)` return just `"e"`, silently dropping the accent. A one-character limit would cut between the letter and its mark.',
            verify='Assert `crab.len() == 4`, `crab.chars().count() == 1`, `accented.len() == 3`, `accented.chars().count() == 2` and `accented.chars().take(1).collect::<String>() == "e"`. All pass, showing scalars are not graphemes.',
        ),
        3: dict(
            wrong='Declaring the parameter as `text: String` breaks the first call: `byte_length("pear")` is E0308, expected `String`, found `&str`. Passing an owned `String` would also move it into the function, so the caller could not use it afterwards. Returning `text.chars().count()` instead gives 4 for `café`, not 5.',
            verify='Run the block, then add `let owned = String::from("café"); assert_eq!(byte_length(&owned), 5); assert_eq!(owned, "café");`. Deref coercion turns `&String` into `&str`, and the final check proves the owner is still usable.',
        ),
        4: dict(
            explain='`text[0]` does not compile: E0277 says `str` cannot be indexed by an integer. The runtime version, `&text[0..1]` on `"é"`, panics with `byte index 1 is not a char boundary`. Fix it with `text.chars().next()` for the first scalar, or `text.get(0..1)` to observe `None` without a panic.',
            why="A `str` is UTF-8 bytes and ranges are byte offsets, so a range must start and end on scalar boundaries. Rust refuses integer indexing because one byte is not a character in multibyte text.",
            wrong='Testing the slice only on `"pear"` passes, because every ASCII letter is one byte. The defect appears only with multibyte input such as the last letter of `"café"`, where `&text[3..4]` panics.',
            verify='Assert `"é".chars().next() == Some(\'é\')`, `"café".get(3..4) == None` and `"café".get(3..5) == Some("é")`. The `é` in `café` occupies bytes 3 and 4, so only the second range is valid.',
        ),
        5: dict(
            explain='Check `assert_eq!("".len(), 0);`, `assert_eq!("".get(0..0), Some(""));`, `assert_eq!("".get(0..1), None);` and `assert_eq!("é".get(1..2), None);`. Every probe goes through `get`, so invalid ranges return `None`.',
            why="An empty range at offset 0 is a valid slice of any string, including the empty one. A range past the end, or one starting inside the two bytes of `é`, is invalid, and `get` reports that as `None` instead of panicking.",
            wrong='Probing with `&text[0..1]` aborts the test instead of observing the boundary: on `""` it panics with an out-of-bounds byte index, and on `"é"` with the char-boundary message, so the later checks never run.',
            verify='Run the four checks plus `assert_eq!("".chars().next(), None);`. All pass and `rust-004: passed` prints.',
        ),
        6: dict(
            explain="For a storage field limited to 16 bytes, count bytes and cut at the last scalar boundary: `fn truncate_bytes(text: &str, max: usize) -> &str { let mut end = max.min(text.len()); while !text.is_char_boundary(end) { end -= 1; } &text[..end] }`. A display limit in visible characters would need graphemes from a segmentation crate in a separately prepared Cargo project.",
            why="`is_char_boundary` is always true at 0 and at `len()`, so the loop stops, and the slice is valid UTF-8 of at most `max` bytes. The elided lifetime ties the returned `&str` to `text`, so no copy is made. A limitation is that it may still cut a combining mark away from its base letter.",
            wrong="`text.chars().take(16).collect::<String>()` limits scalars, not bytes: sixteen crab emoji produce 64 bytes, four times the field size. Writing `&text[..max]` instead panics whenever `max` lands inside a multibyte scalar.",
            verify='Assert `truncate_bytes("café", 4) == "caf"`, `truncate_bytes("café", 5) == "café"`, `truncate_bytes("pear", 10) == "pear"` and `truncate_bytes("\\u{1F980}", 3) == ""`. Each result is a valid `&str` no longer than the limit.',
        ),
    },
    5: {
        1: dict(
            explain='Example A binds `label` to `"present"` because `3 > 0`; the else branch never runs. In Example B, `classify(59)` takes `0..=59` and returns `"retry"`, `classify(60)` takes `60..=100` and returns `"pass"`, and `classify(101)` reaches the wildcard and returns `"invalid"`.',
            why="`if` and `match` are expressions, so the chosen branch's final value becomes the binding. Every branch yields a `&'static str`, which gives `label` and the closure's result one static type.",
            wrong='Reading `0..=59` as exclusive predicts that 59 is not retry. With an exclusive pattern `0..59`, 59 would match neither range and fall to `_`, returning `"invalid"`, not `"pass"`.',
            verify='The existing checks confirm 59, 60 and 101. Add `assert_eq!(classify(0), "retry");` and `assert_eq!(classify(100), "pass");` to confirm both inclusive outer ends.',
        ),
        2: dict(
            explain='Move the threshold to 70 in both ranges: `0..=69 => "retry", 70..=100 => "pass"`. Update the neighbors to `classify(69) == "retry"` and `classify(70) == "pass"`, and keep the 101 check.',
            why="The two ranges still partition 0 to 100 with no gap or overlap, and the checks at 69 and 70 pin the new boundary from both sides.",
            wrong='Editing only the second arm to `70..=100` leaves 60 through 69 unmatched by either range. The wildcard keeps the match exhaustive, so it compiles, and `classify(65)` silently returns `"invalid"`.',
            verify='Add `assert_eq!(classify(65), "retry");`. On the half-edited version it panics with `left: "invalid"` and `right: "retry"`; with both arms changed, all checks pass.',
        ),
        3: dict(
            wrong='Writing the first arm as `i32::MIN..=0` is an off-by-one: 0 matches it first and is classified negative. rustc warns that the later `0` arm is an unreachable pattern, and `assert_eq!(classify(0), "zero")` panics.',
            verify='The block checks -4, 0 and 9. Add the extremes and neighbors: `classify(i32::MIN)` and `classify(-1)` give `"negative"`, `classify(1)` and `classify(i32::MAX)` give `"positive"`.',
        ),
        4: dict(
            explain='The defect is `let label = if count > 0 { "present"; } else { "empty" };`. The semicolon makes the first branch a statement, so that block evaluates to `()`, and rustc reports E0308 because the `if` and `else` branches have incompatible types. Removing the semicolon restores the `&str` value.',
            why="A block's value is its final expression only when no semicolon follows it. With the semicolon, the string is evaluated and discarded, and the branch produces unit.",
            wrong='Making the branches agree by adding a semicolon after `"empty"` too compiles, but `label` becomes `()`. The following `assert_eq!(label, "present")` then fails to compile, because `()` cannot be compared with `&str`.',
            verify='Compile the defect and read the E0308 message about incompatible branch types. Remove the semicolon and `assert_eq!(label, "present");` passes.',
        ),
        5: dict(
            explain='Check both valid endpoints and one value past each: `classify(0) == "retry"`, `classify(100) == "pass"`, `classify(-1) == "invalid"` and `classify(101) == "invalid"`.',
            why="0 and 100 are the inclusive outer ends of `0..=59` and `60..=100`, and -1 and 101 are the nearest values outside them, which only the wildcard catches.",
            wrong='Testing 1 and 99 instead of 0 and 100 passes a classifier written as `1..=59` and `60..=99`, which wrongly sends 0 and 100 to `"invalid"`.',
            verify='Run the four checks. Change `60..=100` to `60..100` temporarily: `classify(100)` panics with `left: "invalid"` and `right: "pass"`. Restore it and all four pass.',
        ),
        6: dict(
            explain="For `enum Order { Draft, Paid, Shipped }`, list every variant: `fn can_cancel(order: &Order) -> bool { match order { Order::Draft | Order::Paid => true, Order::Shipped => false } }`. Keep wildcards for open numeric domains such as scores, where `_` represents invalid input.",
            why="With explicit arms, adding a variant such as `Refunded` makes every incomplete match fail with E0004, non-exhaustive patterns, so each decision is revisited. A limitation is that an enum from another crate marked `#[non_exhaustive]` still requires a wildcard.",
            wrong="Writing `Order::Shipped => false, _ => true` is correct today, but when `Refunded` is added it silently becomes cancellable. The wildcard removes the compiler feedback the lesson's pitfall warns about.",
            verify="Assert `can_cancel(&Order::Paid)` and `!can_cancel(&Order::Shipped)`. Then add `Refunded` temporarily: compilation fails with E0004 naming `Order::Refunded` as not covered. Remove it again.",
        ),
    },
    9: {
        1: dict(
            explain="In Example A, `text` owns the `String` holding `pear`, and `first` and `second` are two `&String` readers of the same allocation. In Example B, `sentence` owns the text, `first_word` receives it as a `&str` parameter, and the returned `&str` is a third view into the same bytes.",
            why="`&text` creates a shared reference without moving anything, and any number of shared references may coexist while no mutable borrow exists. The owner alone frees the allocation when its scope ends, which is why `text` can still be compared with `pear` afterwards.",
            wrong="Calling `first` an owner implies `let first = &text;` moved the string. If it had been written `let first = text;`, the next line `let second = &text;` would be rejected with E0382, borrow of moved value.",
            verify="Add `assert!(std::ptr::eq(first, second));` and `assert_eq!(first.as_ptr(), text.as_ptr());`. Both pass, showing the two readers and the owner point at one allocation.",
        ),
        2: dict(
            explain='After the existing checks, add `let third = &text; assert!(third.starts_with("pe"));`. `starts_with` takes `&self`, so a third shared borrow is enough and nothing is copied.',
            why="Shared borrows can be added freely as long as no code mutates `text` while they are live. The inspection reads the same four bytes the other readers see.",
            wrong="`let third = text.clone();` also passes the check but allocates a second `pear` and inspects the copy, the habit the pitfall warns against. Reaching for `&mut text` instead fails with E0596, because `text` is not declared mutable.",
            verify="Add `assert!(std::ptr::eq(third, &text));`; it passes for the borrow and would fail for the clone, whose bytes live elsewhere. The run then ends with `rust-009: passed`.",
        ),
        3: dict(
            wrong='Splitting on a single space, `text.split(\' \').last()`, looks equivalent but returns the empty piece after a trailing space: for `"pear apple "` it yields `""` instead of `apple`. `split_whitespace` skips runs of whitespace, so it returns the real last word.',
            verify='Add `assert_eq!(last_word("pear apple "), "apple");`, `assert_eq!(last_word("   "), "");` and `assert!(std::ptr::eq(last_word(&sentence), &sentence[5..]));`. The last check proves the result is bytes 5 to 10 of `sentence`, not a new allocation.',
        ),
        4: dict(
            explain='Write `fn make_word() -> &str { let word = String::from("pear"); &word }`. rustc first reports E0106, missing lifetime specifier, because there is no input reference to borrow from. Annotating `-> &\'static str` then produces E0515: the function returns a reference to data owned by the current function.',
            why="`word` is dropped when `make_word` returns, so any reference to it would point at freed memory. A lifetime annotation only describes how long a borrow may be used; it cannot extend the life of the owner.",
            wrong="Accepting the `'static` suggestion as the fix trades E0106 for E0515, since `'static` promises the data lives for the whole program, which a local `String` cannot. The correct change returns ownership: `fn make_word() -> String`.",
            verify='Compile each broken version and read E0106, then E0515. Change the signature to `-> String`, return `String::from("pear")`, and `assert_eq!(make_word(), "pear");` passes.',
        ),
        5: dict(
            explain='Check `first_word("") == ""`, `first_word("   ") == ""` and, for one word, `let single = String::from("pear");` with `first_word(&single) == "pear"` and `last_word(&single) == "pear"`.',
            why='`split_whitespace` yields no items for empty or all-space text, so `unwrap_or("")` supplies the documented empty policy. A single word is both the first and the last, so the two functions must agree on it.',
            wrong='Replacing `unwrap_or("")` with `unwrap()` passes every one-word and two-word case but panics on `""` with `called Option::unwrap() on a None value`, so the empty-text check never completes.',
            verify="Run the checks and add `assert!(std::ptr::eq(first_word(&single), single.as_str()));`: for a single word the borrowed result covers the whole input. All pass before the marker.",
        ),
        6: dict(
            explain='If the caller may drop the input right after parsing, return owned data: `fn parse_name(line: &str) -> String { line.split_whitespace().next().unwrap_or("").to_string() }`. Keep a borrowed `&str` result for callers that hold the whole input in memory, such as a file read once and scanned many times.',
            why="An owned `String` has no lifetime tie to `line`, so the result stays valid after the input buffer is dropped or reused. The cost is one allocation per parsed field, which is the limitation of this choice.",
            wrong='Returning `&str` and then dropping the input fails: `let name = { let line = String::from("pear 3"); first_word(&line) };` is rejected with E0597, `line` does not live long enough, because the view would outlive its owner.',
            verify='Write the same block with `parse_name` instead: it compiles and `assert_eq!(name, "pear");` passes. Switching back to `first_word` reproduces E0597.',
        ),
    },
    11: {
        1: dict(
            explain="`total(&[2, 3, 4])` borrows a temporary array of length 3; `total(&vec![1, 2])` borrows a temporary `Vec<i32>` of length 2; `total(&[])` borrows an empty array. Each reaches `total` as a `&[i32]`. In Example B, `values` owns the `Vec`, its length goes from 0 to 1, and `get` lends an `Option<&i32>`.",
            why="`&[i32; 3]` unsizes to `&[i32]` and `&Vec<i32>` deref-coerces to it, so one parameter type covers both owners. A slice reference is a pointer plus a length, and each temporary lives until the end of its statement.",
            wrong="Treating `with_capacity(10)` as length 10 predicts that `values[5]` is valid. It panics with `index out of bounds: the len is 1 but the index is 5`, because capacity is reserved space, not elements.",
            verify="Add `assert_eq!(values.len(), 1);`, `assert_eq!(values.get(5), None);` and `assert_eq!(std::mem::size_of::<&[i32]>(), 2 * std::mem::size_of::<usize>());`, which shows a slice reference is a pointer and a length.",
        ),
        2: dict(
            explain="With `let data = [2, 3, 4, 5];`, `total(&data[1..3])` covers indices 1 and 2, so it is 3 + 4 = 7. The subslice borrows part of `data` without copying.",
            why="`1..3` is half-open: it includes the start and excludes the end. The slice therefore has length 2 and starts at the element 3.",
            wrong="Reading `1..3` as inclusive predicts 12, which is what `1..=3` gives. Extending the range to `&data[2..5]` panics, because the end 5 is past the length 4.",
            verify="Assert `total(&data[1..3]) == 7` and `total(&data[1..=3]) == 12`, and probe the overrun safely with `assert_eq!(data.get(2..5), None);`.",
        ),
        3: dict(
            wrong="Dropping `.copied()` returns `values.iter().max()`, an `Option<&i32>`, and the signature promising `Option<i32>` is rejected with E0308. Keeping a plain `i32` return with `unwrap_or(i32::MIN)` compiles but makes an empty slice look like a real minimum value.",
            verify="Add `assert_eq!(maximum(&[-5, -2]), Some(-2));`, `assert_eq!(maximum(&vec![4, 4]), Some(4));` and `assert_eq!(maximum(&[i32::MIN]), Some(i32::MIN));`. The last check would be indistinguishable from empty input under the sentinel version.",
        ),
        4: dict(
            explain="The defect is `let mut values = vec![1, 2]; let first = &values[0]; values.push(3); assert_eq!(*first, 1);`. rustc rejects it with E0502: `values` cannot be borrowed as mutable for `push` while `first` still holds a shared borrow that is used afterwards. Copy the element instead, `let first = values[0];`, since `i32` is `Copy`.",
            why="`push` may reallocate the buffer, and with a length and capacity of 2 it must grow, moving the elements. A reference held across that push would point at freed memory, so the borrow checker forbids it.",
            wrong="Calling `values.reserve(10)` before taking the reference, so the push cannot reallocate, does not help. The rule is about overlapping borrows, not capacity, so E0502 is still reported.",
            verify="Compile the defect and read E0502 with its immutable and mutable borrow labels. With the copied value, `assert_eq!(first, 1);` and `assert_eq!(values, [1, 2, 3]);` both pass.",
        ),
        5: dict(
            explain="For empty input, `let empty: Vec<i32> = Vec::new();` with `empty.get(0) == None` and `total(&empty) == 0`. For one element, `let one = vec![7];` with `one.get(0) == Some(&7)`, `one.get(1) == None` and `maximum(&one) == Some(7)`.",
            why="Valid indices run from 0 to one less than `len()`, so `get` at the length returns `None`. The sum of no elements is 0, and the maximum of one element is that element.",
            wrong="Probing with `one[1]` instead of `get` panics with `index out of bounds: the len is 1 but the index is 1`, which aborts the test rather than recording the out-of-range case.",
            verify="Run the five checks and add `assert_eq!(Vec::<i32>::with_capacity(10).get(3), None);`: reserved capacity still has no elements. `rust-011: passed` follows.",
        ),
        6: dict(
            explain="Store a growing list, such as cart items, in a `Vec<T>`; accept read-only input as `&[T]`; and model fixed-size coordinates as an array such as `[i32; 2]`, whose length is part of its type and which needs no heap allocation.",
            why="`Vec` owns and can grow, a slice parameter accepts arrays, vectors and subslices alike, and an array makes a three-number point a type error. A limitation is that an array's length must be known at compile time.",
            wrong="Declaring `fn total(values: &Vec<i32>)` rejects `total(&[2, 3, 4])` with E0308 and cannot take `&data[1..3]`. Storing a point as `Vec<i32>` lets a three-element point appear at run time.",
            verify="Call `total(&cart)`, `total(&point)` and `total(&cart[..1])`; all compile against `&[i32]`. Then write `let point: [i32; 2] = [1, 2, 3];` and the compiler reports a mismatched array length.",
        ),
    },
    12: {
        1: dict(
            explain="`new(stock)` has no receiver: it is an associated constructor that returns a fresh `Inventory`. `stock(&self)` borrows the value read-only to report the count. `reserve(&mut self, amount)` borrows it exclusively because it may lower the stock.",
            why="The receiver states the capability a caller must grant. `&self` works from any binding, while `&mut self` requires a mutable binding and no other live borrows, which is why both examples declare `let mut inventory`.",
            wrong="Dropping `mut` from `let mut inventory` because only methods touch the stock fails at the first `reserve` call with E0596, cannot borrow `inventory` as mutable. Calls to `stock()` on the same binding still compile.",
            verify="Declare `let inventory = Inventory::new(5);` and call `inventory.stock()`: it compiles. Add `inventory.reserve(1)` and read E0596; restore `mut` and both examples pass.",
        ),
        2: dict(
            explain="Add a second impl block: `impl Inventory { fn restock(&mut self, amount: u32) -> bool { match self.stock.checked_add(amount) { Some(total) => { self.stock = total; true } None => false } } }`.",
            why="`checked_add` returns `None` when the sum would exceed `u32::MAX`, 4294967295, and the field is written only in the `Some` arm. A rejected restock therefore leaves the previous stock untouched.",
            wrong="Writing `self.stock += amount;` panics with `attempt to add with overflow` when overflow checks are enabled and silently wraps to a tiny stock when they are not. Either way the method cannot report the rejection.",
            verify="With `let mut inv = Inventory::new(u32::MAX - 1);`, assert `inv.restock(1)` and `inv.stock() == u32::MAX`, then `!inv.restock(1)` and that the stock is still `u32::MAX`.",
        ),
        3: dict(
            wrong="Testing the limit with `self.value > self.limit` is an off-by-one: at 2 of 2 the test is false, so the third call increments to 3 and returns true, and `assert!(!counter.increment())` panics. The `==` check stops exactly at the limit.",
            verify="Run the block, then add `let mut zero = Counter::new(0); assert!(!zero.increment()); assert_eq!(zero.value, 0);`. A zero-limit counter must refuse its very first increment.",
        ),
        4: dict(
            explain="The defect subtracts first: `self.stock -= amount; if self.stock ... { return false; }`. For Example B, 3 minus 4 underflows the `u32`: it panics with `attempt to subtract with overflow` under overflow checks, or wraps to 4294967295 without them. Either way the rejection is not atomic. Check first, or write `match self.stock.checked_sub(amount)` and assign only on `Some`.",
            why="Failure atomicity requires every rejection condition to be decided before the field changes. The helper's `if amount > self.stock { return false; }` runs before the subtraction, so a rejected reserve never touches `stock`.",
            wrong="Swapping in `self.stock = self.stock.saturating_sub(amount);` before the check removes the panic but still mutates: the rejected request drains the stock to 0, and Example B's `assert_eq!(inventory.stock(), 3)` fails with `left: 0`.",
            verify="Run Example B against the subtract-first version and observe the overflow panic or the failed stock check. Restore check-first order and the stock stays 3 after the refused reservation.",
        ),
        5: dict(
            explain="On `Inventory::new(3)`: `reserve(0)` returns true and the stock stays 3; `reserve(3)` returns true and leaves 0; a following `reserve(1)` returns false and the stock stays 0.",
            why="The guard is `amount > self.stock`, so a request equal to the stock passes (3 is not greater than 3) and selling the last units is allowed. Zero passes trivially and subtracts nothing.",
            wrong="Writing the guard as `amount >= self.stock` refuses the exact-stock reservation, so `reserve(3)` returns false and the last three units can never be sold.",
            verify="Assert the three results and the stock after each: 3, 0, 0. Change `>` to `>=` temporarily and the exact-stock assertion panics.",
        ),
        6: dict(
            explain="Take `self` by value when the old state must become unusable: `struct Order { items: Vec<String> }` with `fn submit(self) -> Submitted { Submitted { items: self.items } }`. After `let submitted = order.submit();`, any later use of `order` is a compile error.",
            why="A `self` receiver moves the value into the method, so the compiler, not a runtime flag, rejects editing an order after submission. A limitation is that it does nothing for `Copy` types, where passing `self` copies instead of moving.",
            wrong="Using `fn submit(&mut self)` with a `submitted: bool` field leaves `order` usable, so `add_item` after `submit` compiles and every method needs its own runtime check.",
            verify="Assert `submitted.items.len()` matches the items added. Then add `order.items.len()` after the `submit` call and read E0382, borrow of moved value.",
        ),
    },
    14: {
        1: dict(
            explain="`measured.map(|value| value + 1)` on `Some(0)` returns `Some(1)`. `missing.map(|value| value + 1)` on `None` returns `None` and never calls the closure.",
            why="`map` transforms only the value inside `Some` and passes `None` through unchanged, so absence survives the transformation and zero is treated as an ordinary present value.",
            wrong="Treating `None` like 0 predicts `Some(1)` for both, and treating `Some(0)` as empty predicts `None` for both. Each erases the distinction Example A's `assert_ne!(measured, missing)` establishes.",
            verify="Add `assert_eq!(missing.map(|value| value + 1), None);` and count closure calls: `let mut calls = 0; let _ = missing.map(|value| { calls += 1; value }); assert_eq!(calls, 0);`.",
        ),
        2: dict(
            explain='Render at the display boundary: `fn render(value: Option<i32>) -> String { match value { Some(number) => number.to_string(), None => String::from("unknown") } }`. Then `render(values.get(9).copied())` gives `unknown` and `render(Some(0))` gives `0`.',
            why="The fallback is a label of a different kind from any measurement, so it cannot be mistaken for data, and the match forces both cases to be handled explicitly.",
            wrong="Keeping Example B's `unwrap_or(-1)` and printing the number is ambiguous wherever -1 is a valid reading, such as a temperature. `unwrap_or(0)` is worse here: a missing reading prints the same as the measured zero in Example A.",
            verify='Assert `render(Some(0)) == "0"`, `render(Some(-1)) == "-1"` and `render(None) == "unknown"`. All three strings differ, so every case is distinguishable.',
        ),
        3: dict(
            wrong="Using `find(|value| *value > 0)` treats zero as invalid, so `first_valid(&[-2, 0, 5])` returns `Some(5)` and the first assertion panics. The reference uses `>= 0` because a valid zero must be found.",
            verify="Add `assert_eq!(first_valid(&[]), None);` and `assert_eq!(first_valid(&[0]), Some(0));`. Run the block and `rust-014: passed` prints.",
        ),
        4: dict(
            explain="The defect is `let value = values.get(9).unwrap();` on `[2, 4]`. Index 9 is an ordinary not-found case, yet `unwrap` panics with `called Option::unwrap() on a None value`. Return the absence instead: `fn doubled(values: &[i32], index: usize) -> Option<i32> { let value = values.get(index)?; Some(value * 2) }`.",
            why="`unwrap` asserts an invariant that does not hold here. The `?` operator on an `Option` returns `None` from the function early, so the caller decides what absence means.",
            wrong='Replacing `unwrap()` with `expect("value exists")` only changes the panic message. Replacing it with `unwrap_or_default()` removes the panic but returns 0, which hides the missing value as a fake measurement.',
            verify="Run the defect and read the `None` panic with no marker after it. Then assert `doubled(&[2, 4], 9) == None` and `doubled(&[2, 4], 1) == Some(8)`.",
        ),
        5: dict(
            explain="With `let empty: [i32; 0] = [];`, assert `empty.first() == None` and `first_valid(&empty) == None`. With `let zeros = [0];`, assert `zeros.get(0) == Some(&0)` and `zeros.get(1) == None`.",
            why="`first` and `get` return `Option<&i32>`, so an empty array and an out-of-range index both produce `None`, while a stored zero produces `Some(&0)`.",
            wrong="Testing presence with `values.get(i).copied().unwrap_or(0) != 0` reports the stored zero as missing, collapsing the present-zero and absent cases this task separates.",
            verify="Run the four checks; the run prints `rust-014: passed` only if the present zero and the absent index were kept distinct.",
        ),
        6: dict(
            explain="Keep `Option` when absence is a normal answer, such as a cache miss. Convert to a domain error when the caller needs a reason: `#[derive(Debug, PartialEq)] enum PortError { Missing, NotNumber }` with `fn port(raw: Option<&str>) -> Result<u16, PortError> { let text = raw.ok_or(PortError::Missing)?; text.parse().map_err(|_| PortError::NotNumber) }`.",
            why="`ok_or` turns `None` into a named error at the boundary, and `map_err` keeps a parse failure separate from a missing field. A limitation is the extra error type every caller must match.",
            wrong="Returning `Option<u16>` for the port with `raw?.parse().ok()` collapses a missing field and `port=abc` into the same `None`, so the caller cannot tell the user which problem to fix.",
            verify='Assert `port(None) == Err(PortError::Missing)`, `port(Some("abc")) == Err(PortError::NotNumber)` and `port(Some("8080")) == Ok(8080)`.',
        ),
    },
    16: {
        1: dict(
            explain='Example A: `"pear,2"` splits into `pear` and `2`, parses, and inserts 2; `"apple,3"` inserts 3; `"pear,4"` reads the previous 2 and stores 6. Example B: `"pear,0"` is admitted with 0; `"bad"` has no comma, `"apple,-1"` fails the `u32` parse, and `"pear,no"` fails it too, so `rejected` ends at 3.',
            why="Each `let ... else` either binds the next value or counts a rejection and `continue`s, so a record reaches `totals.insert` only after splitting, parsing, the name check and `checked_add` have all succeeded.",
            wrong='Predicting that `apple` appears with 0, or that `-1` lowers a total, misreads the parse step. `"-1".parse::<u32>()` is an error, so the apple record never reaches the map at all.',
            verify='In Example B add `assert_eq!(totals.get("apple"), None);` and `assert_eq!(totals.len(), 1);`. Both pass: only `pear` was admitted.',
        ),
        2: dict(
            explain="Append `\"pear,1\"` to Example A's input. Pear's total becomes 2 + 4 + 1 = 7, apple stays 3, and `rejected` stays 0.",
            why="The helper reads the previous total with `totals.get(name)`, adds through `checked_add`, and inserts the sum, so a repeated name accumulates instead of starting over.",
            wrong="Predicting 1 assumes the map keeps the last record per key. That is what a simplified loop writing `totals.insert(name.to_owned(), quantity)` would do, discarding the earlier 6.",
            verify='Assert `totals.get("pear") == Some(&7)`, `totals.len() == 2` and `rejected == 0`.',
        ),
        3: dict(
            wrong="Collecting into a `HashMap` instead makes iteration order depend on a randomly seeded hasher, so the report can come out as `pear: 2` before `apple: 3` and the exact-string assertion fails on some runs but not others.",
            verify='Run the block several times; the string is identical each time. Add `"banana,1"` to the input and the expected report becomes `apple: 3`, `banana: 1`, `pear: 2`, then `rejected: 1`, still in key order.',
        ),
        4: dict(
            explain='The defect is `let quantity = quantity.parse::<u32>().unwrap_or(0);` in place of the `let Ok(...) else` line. On Example B it admits `"apple,-1"` and `"pear,no"` as zero quantities, so `apple` appears with 0 and `rejected` drops from 3 to 1.',
            why="A failed parse and a valid `0` both become the number 0, so the import invents an apple record and undercounts rejections. The lesson's rule is that absence, zero and rejection must stay distinct.",
            wrong='Switching to `.unwrap()` removes the invented zeros but panics on `"apple,-1"` with an `InvalidDigit` parse error, aborting the whole import for one bad row instead of counting it.',
            verify="Run Example B with the defect: `assert_eq!(rejected, 3)` panics with `left: 1` and `right: 3`. Restore the `let Ok(quantity) = ... else` form and all checks pass.",
        ),
        5: dict(
            explain='Check `import_rows(&[",3"]).1 == 1` for an empty name and `import_rows(&["pear,2,3"]).1 == 1` for an extra separator. For overflow, `import_rows(&["pear,4294967295", "pear,1"])` keeps `pear` at `u32::MAX` with one rejection. `import_rows(&[])` returns an empty map and 0.',
            why="`split_once` splits only at the first comma, so `2,3` reaches the parser and fails. The trimmed empty name is refused, and `checked_add` returns `None` instead of wrapping, so the second pear row is rejected and the first total is kept.",
            wrong="Using `line.split(',')` and taking the first two pieces would accept `\"pear,2,3\"` as pear 2, silently dropping the third field instead of rejecting a record the fixture format does not allow.",
            verify='Assert each result above, including `totals.get("pear") == Some(&u32::MAX)` for the overflow case. All pass and `rust-016: passed` prints.',
        ),
        6: dict(
            explain="Return a structure: `#[derive(Debug, PartialEq)] enum Rejection { MissingSeparator, BadQuantity, EmptyName, Overflow }` and `struct ImportReport { totals: BTreeMap<String, u32>, rejected: Vec<(usize, Rejection)> }`, recording the one-based line number and category for each refused record.",
            why="Categories can be counted and explained without echoing raw input, which may hold sensitive or very long text. The old `rejected` count is just `rejected.len()`. A limitation is memory that grows with the number of bad rows; a cap or per-category counters bound it.",
            wrong='Collecting `format!("bad line: {line}")` strings copies untrusted input into the report and forces callers to parse messages to count categories.',
            verify="For Example B's input, assert `report.rejected == vec![(2, Rejection::MissingSeparator), (3, Rejection::BadQuantity), (4, Rejection::BadQuantity)]` and that `pear` still totals 0.",
        ),
    },
    17: {
        1: dict(
            explain="`view.cost(4)` goes through the `&dyn Pricer` vtable to `FlatPrice::cost`, giving 3 times 4 = 12. In Example B, `prices[0]` dispatches to `FlatPrice::cost` (12) and `prices[1]` to `CappedPrice::cost`, where 12 is capped at 10.",
            why="A `&dyn Pricer` is a data pointer plus a vtable pointer, and each element carries the vtable of its own concrete type. The call site is the same; the implementation is chosen at run time per element.",
            wrong="Predicting `[12, 12]` because the array holds one type confuses the element type `&dyn Pricer` with the concrete types behind it. Each element still knows it is a `FlatPrice` or a `CappedPrice`.",
            verify="Assert `std::mem::size_of::<&dyn Pricer>() == 2 * std::mem::size_of::<usize>()` to see the two pointers, and `CappedPrice(3, 10).cost(3) == 9` to confirm the cap applies only above 10.",
        ),
        2: dict(
            explain="Add `let premium = FlatPrice(5);` and extend the array to `let prices: [&dyn Pricer; 3] = [&flat, &capped, &premium];`. The consumer `prices.map(|price| price.cost(4))` is unchanged and now yields `[12, 10, 20]`.",
            why="The closure depends only on the `Pricer` contract, so a new value of an existing implementation needs no change in the code that prices.",
            wrong="Dropping the annotation, `let prices = [&flat, &capped, &premium];`, fails with E0308: inference takes `&FlatPrice` from the first element and then finds `&CappedPrice`. Keeping `; 2` with three elements also fails, with a length mismatch.",
            verify="Assert `prices.map(|price| price.cost(4)) == [12, 10, 20]`; the run then reaches `rust-017: passed`.",
        ),
        3: dict(
            wrong="Giving the formatter state, such as a `&mut self` call counter appended to the output, breaks the contract: the second call returns a different string and the `formatter.format(3) == formatter.format(3)` assertion panics.",
            verify='Add `assert_eq!(formatter.format(0), "0 units");` and `assert_eq!(formatter.format(u32::MAX), "4294967295 units");` to cover both ends of the input type.',
        ),
        4: dict(
            explain="Suppose `struct DollarPrice(u32)` implements `cost` as `self.0 * units` with the field meaning dollars, while `FlatPrice` means cents. Both satisfy `fn cost(&self, units: u32) -> u32`, so the compiler accepts both, yet `DollarPrice(3).cost(4)` returns 12 dollars where callers expect 12 cents.",
            why="A trait checks signatures, not meaning. Fix it by putting the unit in the type: `struct Cents(u32);` and `fn cost(&self, units: u32) -> Cents;`, so the dollar implementation must write `Cents(self.0 * units * 100)` explicitly.",
            wrong="Converting at the call site with `if is_dollars { cost * 100 }` requires the consumer to know the concrete type behind `&dyn Pricer`, which defeats the substitution the trait exists for.",
            verify="With the `Cents` return type, assert `DollarPrice(1).cost(4).0 == 400` and `FlatPrice(3).cost(4).0 == 12`. An implementation that forgets the conversion no longer compiles.",
        ),
        5: dict(
            explain="Zero units: `FlatPrice(3).cost(0) == 0` and `CappedPrice(5, 10).cost(0) == 0`. Exact cap: `CappedPrice(5, 10).cost(2) == 10`, with neighbors `cost(1) == 5` and `cost(3) == 10`.",
            why="Any price times zero units is zero, and `min` returns the cap when the raw cost equals it. With a unit price of 5, two units land exactly on 10, so the equality case is actually exercised.",
            wrong="Reusing Example B's `CappedPrice(3, 10)` for the exact-cap test never hits equality: 3 units cost 9 and 4 units cost 12, so no unit count produces exactly 10.",
            verify="Run the five assertions; each prints nothing on success, and the marker follows.",
        ),
        6: dict(
            explain="Keep the core as `fn import_rows(lines: &[&str]) -> ...` with no I/O, and put the trait at the edge: `trait LineSource { fn lines(&self) -> std::io::Result<Vec<String>>; }`, implemented by an in-memory fixture in the pad and by a file reader in a separately prepared Cargo project.",
            why="The core stays deterministic and testable offline, and disk errors stay in the adapter's `io::Result`, separate from validation rejections. A limitation is that loading every line into a `Vec` does not stream very large files.",
            wrong="Making the core take a `std::fs::File` mixes I/O failures into validation and means every test needs a real file. Adding file methods to `Pricer` widens a pricing trait with an unrelated capability.",
            verify="Implement `struct Fixed(Vec<String>);` for `LineSource`, feed its lines into the core and assert the same totals as Example A. The file-backed adapter is checked in the external project.",
        ),
    },
    20: {
        1: dict(
            explain="In Example A, `values.iter()` creates the source, `copied`, `filter` and `map` are adapters, and `collect` is the consumer that drives the chain. In Example B, `into_iter` creates the source and each `next` call is a manual consumption step.",
            why="Adapters only wrap one iterator in another and do no work; a consumer pulls items through the chain. That is why `values` is still four long afterwards: `iter` borrowed it.",
            wrong="Calling `filter` the consumer because it removes items gets the roles backwards. Without `collect`, the filter never runs, and the compiler warns that iterators are lazy and do nothing unless consumed.",
            verify="Write `values.iter().map(|value| value * 10);` as a statement and read the `unused Map that must be used` warning. Restore `collect` and `result == vec![20, 40]` passes.",
        ),
        2: dict(
            explain="Add `.take(1)` after `map`: the result is `vec![20]`. Only two source items are examined: 1 is filtered out, 2 becomes 20, and `take` stops pulling, so 3 and 4 are never visited.",
            why="Iterators are pull-based: `collect` asks `take`, which asks `map`, and so on. Once `take` has yielded one item it returns `None` without asking for more.",
            wrong="Placing `take(1)` before `filter` takes only the first source item, 1, which is odd, so the result is empty. Adapter order changes which items the limit counts.",
            verify="Insert `.inspect(|value| seen.push(*value))` right after `copied()`, with `let mut seen = Vec::new();` above. Assert `result == vec![20]` and `seen == vec![1, 2]`.",
        ),
        3: dict(
            wrong="Ending the function body at `.map(|name| name.to_uppercase())` without `collect` fails with E0308: the body is a lazy `Map` iterator, not the `Vec<String>` the signature promises.",
            verify='Add `assert_eq!(upper_names(&[]), Vec::<String>::new());` and `assert_eq!(upper_names(&["straße"]), vec!["STRASSE"]);`. The second shows `to_uppercase` can change a word\'s length.',
        ),
        4: dict(
            explain='The defect is `values.iter().map(|value| println!("{value}"));`, expecting four lines. Nothing prints, because `map` only builds an adapter. Use `for value in &values { println!("{value}"); }` or `for_each` when the side effect is the point.',
            why="No consumer ever calls `next`, so the closure never runs. rustc flags this with a warning that the unused `Map` must be used, because iterators are lazy.",
            wrong="Forcing execution with `.count()` or `.collect::<Vec<()>>()` does print the lines, but it builds and discards a result purely for its side effects, hiding the intent the lesson's pitfall warns about.",
            verify="Prove laziness: `let mut calls = 0; let lazy = values.iter().map(|value| { calls += 1; value * 10 }); drop(lazy); assert_eq!(calls, 0);`. Replacing `drop(lazy)` with `let total: i32 = lazy.sum();` gives `calls == 4` and `total == 100`.",
        ),
        5: dict(
            explain="Empty input: `let empty: Vec<i32> = Vec::new();` through Example A's chain collects an empty `Vec`. Partial consumption: `let mut iterator = [2, 3, 4].into_iter();` then `iterator.next() == Some(2)`, and `iterator.collect::<Vec<_>>()` returns `vec![3, 4]`.",
            why="A chain over no items calls none of its closures and collects nothing. `collect` starts from the iterator's current position, so an item already taken by `next` is not seen again.",
            wrong="Expecting `collect` to restart and return `[2, 3, 4]` treats the iterator as the array. Calling `iterator.next()` after `collect` fails to compile with E0382, because `collect` took the iterator by value.",
            verify="Assert both results, then add `iterator.next()` after the `collect` and read E0382, use of moved value.",
        ),
        6: dict(
            explain="Sum prices with `iter()`: `let total: u32 = prices.iter().sum();`. Apply a 10 percent discount in place with `iter_mut()`: `for price in prices.iter_mut() { *price -= *price / 10; }`. Move names into a new owner with `into_iter()`: `let registry: Vec<String> = names.into_iter().collect();`.",
            why="Summing only reads, discounting needs exclusive access to each element, and the registry should own the `String`s without cloning them. Each form grants exactly that much access. A limitation is that `into_iter` leaves `names` unusable afterwards.",
            wrong="Using `into_iter()` for the sum consumes `prices`, so the discount loop then fails with E0382. Using `iter()` for the discount fails instead, because `*price -= ...` cannot assign through a `&` reference.",
            verify='With `prices = vec![100, 250]` and `names = vec![String::from("pear")]`, assert `total == 350`, `prices == [90, 225]` and `registry == ["pear"]`.',
        ),
    },
    21: {
        1: dict(
            explain="In Example A, `add` captures `count` by mutable borrow because its body runs `count += value`, so it implements `FnMut` and must be bound with `let mut add`. In Example B, `move` captures `text` by value and the body returns it, so the closure implements only `FnOnce`.",
            why="The compiler infers the capture mode from what the body does with each variable, and the call traits follow: mutation needs `FnMut`, and moving a capture out needs `FnOnce`.",
            wrong="Crediting the `move` keyword for Example B being `FnOnce` is wrong: `move || text.len()` also owns `text` yet is `Fn`, callable any number of times. Returning `text` is what makes it consuming.",
            verify="Pass `consume` to `fn call_twice(f: impl Fn() -> String)` and read E0525, the closure implements `FnOnce` but `Fn` was expected. A `move || owned.len()` closure passes the same kind of `Fn` bound.",
        ),
        2: dict(
            explain="Write `let factor = 3; let scale = |value: i32| value * factor;` then `assert_eq!(scale(2), 6);` twice and `assert_eq!(factor, 3);`.",
            why="The body only reads `factor`, so the closure captures it by shared reference and implements `Fn`. Calling it any number of times with the same input gives the same output.",
            wrong="Adding a call counter, `calls += 1`, inside the closure makes it `FnMut`. It then needs `let mut scale`, and passing it where `Fn` is required fails with E0525.",
            verify="Define `fn twice(f: impl Fn(i32) -> i32) -> (i32, i32) { (f(2), f(2)) }` and assert `twice(scale) == (6, 6)`.",
        ),
        3: dict(
            wrong="Dropping `mut` from the parameter `mut step` fails with E0596: calling an `FnMut` needs `&mut step`. Tightening the bound to `impl Fn()` fails too, because the closure assigns to `value`.",
            verify="Run the block, then add `apply_times(0, || value *= 2);` with an assertion that `value` is unchanged, and a fresh `value = 1` doubled ten times giving 1024.",
        ),
        4: dict(
            explain="Call Example B's closure twice: `let first = consume(); let second = consume();`. rustc reports E0382, use of moved value `consume`, with a note that the closure cannot be invoked more than once because it moves `text` out of its environment. Return `text.clone()` instead to make it repeatable, or call it once.",
            why="An `FnOnce` call takes the closure by value, so after the first call the closure, and the `String` it held, are gone.",
            wrong="Removing the `move` keyword does not help: `|| text` still moves `text` out in its body, so the closure is still `FnOnce` and the second call is still rejected.",
            verify='Compile the two-call version and read E0382 with its note. Change the body to `text.clone()` and assert both calls return `"owned"`.',
        ),
        5: dict(
            explain='No captures: `let double = |value: i32| value * 2;` coerces to a function pointer, `let as_fn: fn(i32) -> i32 = double;`. Borrowed capture: `let name = String::from("pear"); let name_ref = &name; let greet = move || format!("hi {name_ref}");` moves only the reference.',
            why="A closure with no captures has no environment, so it is zero-sized and converts to `fn`. Moving `name_ref` copies a `&String`, so `name` still owns the text and stays usable.",
            wrong="Calling `drop(name)` before `greet()` assumes `move` gave the closure the `String`. It fails with E0505, cannot move out of `name` because it is borrowed, showing the moved reference still depends on its owner.",
            verify='Assert `as_fn(4) == 8`, `std::mem::size_of_val(&double) == 0`, `greet() == "hi pear"` and `name == "pear"`.',
        ),
        6: dict(
            explain="Give the thread owned data: `let rows = vec![2, 3]; let handle = std::thread::spawn(move || rows.iter().sum::<i32>());` and read `handle.join()`. If the caller must keep `rows`, borrow it inside `std::thread::scope(|s| { s.spawn(|| rows.iter().sum::<i32>()); });` instead.",
            why="`spawn` requires a `'static` closure because the thread may outlive the current function, so it must own what it touches. A scope joins every thread before returning, which makes borrowing safe. A limitation of `move` is that `rows` is no longer usable by the caller.",
            wrong="Calling `std::thread::spawn(|| rows.iter().sum::<i32>())` without `move` fails with E0373: the closure may outlive the function but borrows `rows`. Leaking the vector to obtain a `'static` reference silences it at the cost of never freeing the memory.",
            verify="Assert `handle.join().unwrap() == 5` for the move version. For the scoped version, assert the sum is 5 and that `rows == vec![2, 3]` afterwards.",
        ),
    },
    23: {
        1: dict(
            explain="`mod domain` has no `pub`, so it is private to the crate root, which is also where `main` lives and calls it. Inside it, `pub fn double` is public, so any code that can name `domain` can call `domain::double`. Example B's `use domain::double;` is a private import that only adds a shorter local name.",
            why="Rust visibility is relative to modules: a private item is visible in its parent module and that module's descendants, and `pub` opens an item to everything that can reach its parent. `main` is in the parent of `domain`, so it needs only `double` to be `pub`.",
            wrong="Assuming `domain` must be `pub mod` before `main` can use it confuses crate-level privacy with export. That change compiles, but it would only matter for code outside this crate, and it widens the surface for no caller here.",
            verify="Remove `pub` from `double` and read E0603, function `double` is private, at `domain::double(4)`. Restore it and both examples pass.",
        ),
        2: dict(
            explain="Write `mod domain { fn factor() -> i32 { 2 } pub fn double(value: i32) -> i32 { value * factor() } }`. `double(4)` is still 8 and `double(0)` still 0, and `factor` cannot be named from `main`.",
            why="`factor` is private to `domain`, and `double` is in the same module, so it can call the helper while consumers only see the unchanged `pub fn` signature.",
            wrong='Marking the helper `pub fn factor` "just in case" compiles, but it lets `main` write `domain::factor()`. Renaming or inlining the helper later then breaks that caller, which is exactly the accidental surface the lesson warns about.',
            verify="Run both examples, then add `domain::factor();` to `main` and read E0603, function `factor` is private.",
        ),
        3: dict(
            wrong="Returning `unit * quantity` as a plain `u32` hides the overflow: `total(u32::MAX, 2)` panics with attempt to multiply with overflow when overflow checks are on and wraps to 4294967294 otherwise, so the `None` contract cannot be expressed at all.",
            verify="Add the neighbors of the limit: `assert_eq!(pricing::total(65535, 65537), Some(u32::MAX));` and `assert_eq!(pricing::total(65536, 65536), None);`, plus `pricing::total(0, u32::MAX) == Some(0)`.",
        ),
        4: dict(
            explain="Suppose `domain` holds `pub struct Quantity { value: u32 }` with `pub fn new(value: u32) -> Option<Quantity>` that refuses values above 1000, and `pub fn get(&self) -> u32`. A consumer writing `quantity.value` gets E0616, field `value` of struct `Quantity` is private. The fix is to call `quantity.get()`.",
            why="The private field is the representation, and `new` is the only path that checks the 1000 limit. Keeping the field private guarantees every `Quantity` a consumer holds went through that check.",
            wrong="Making the field `pub value` silences E0616, but then `domain::Quantity { value: 5000 }` also compiles, bypassing `new` and producing a quantity the domain promised could not exist.",
            verify="Read E0616 for `.value` and E0451 for a struct literal from `main`. With `get`, assert `domain::Quantity::new(5).unwrap().get() == 5` and `domain::Quantity::new(5000).is_none()`.",
        ),
        5: dict(
            explain="Test only through the public name: `for (input, expected) in [(-3, -6), (0, 0), (4, 8)] { assert_eq!(domain::double(input), expected); }`. No assertion mentions the private `factor` helper from task 2.",
            why="The table pins what callers observe, so the module can rename, inline or delete its helpers and the tests still describe the same contract.",
            wrong="Asserting `domain::factor() == 2` fails to compile from `main` with E0603. Making `factor` public to satisfy the test turns a refactoring detail into API that every later change must preserve.",
            verify="Replace `value * factor()` with `value + value` and delete `factor`. The table still passes and `rust-023: passed` prints.",
        ),
        6: dict(
            explain="In the separately prepared InventoryLab Cargo project, put pure domain code in `src/lib.rs` (for example `pub mod domain;`) and keep argument parsing, file reading and printing in `src/main.rs`, which calls the library by crate name. Dependencies point one way: the binary uses the library, and the library never refers to the binary.",
            why="The library stays free of I/O and testable, and each file in `tests/` compiles as a separate crate that can reach only `pub` library items, so integration tests exercise the real public surface. A limitation is that anything those tests need must be `pub`, which pressures the API to grow.",
            wrong="Keeping the domain logic in `src/main.rs` and adding `tests/report.rs` fails: an integration test links against the library target, and a package with only a binary has no library for the test to `use`.",
            verify="In that project, `cargo test` runs the unit tests and every `tests/*.rs` file, and `cargo run` exercises the binary. The pad cannot show this, because it compiles a single `main.rs`.",
        ),
    },
    24: {
        1: dict(
            explain="The row `(-2, 0)` catches the identity `|value| value` (it returns -2) and `abs` (it returns 2). The row `(0, 0)` catches Example B's `if value <= 0 { 1 }` default. The row `(3, 3)` catches a constant `|_| 0`.",
            why="Each row is a literal written from the clamp rule, not from the expression under test, so a wrong implementation fails the first row where its rule differs.",
            wrong="Claiming `(3, 3)` catches `abs` is wrong: `3_i32.abs()` is 3. Only the negative row separates `abs` from the clamp, so removing it would let that bug through.",
            verify="Replace `input.max(0)` with `input.abs()`; the loop panics on the first row with `left: 2` and `right: 0`. Restore `max(0)` and all rows pass.",
        ),
        2: dict(
            explain="Extend the table to `[(-2, 0), (0, 0), (3, 3), (i32::MIN, 0), (i32::MAX, i32::MAX)]`. `i32::MIN.max(0)` is 0 and `i32::MAX.max(0)` is `i32::MAX`.",
            why="`max` only compares, so the extreme inputs are safe for the implementation, and the expected values are written as constants, so the test performs no arithmetic either.",
            wrong="Writing an expectation such as `-i32::MIN`, or calling `i32::MIN.abs()`, overflows because 2147483648 does not fit in an `i32`. The constant form is rejected at compile time by the deny-by-default arithmetic overflow lint, and `abs` panics with attempt to negate with overflow when checks are on.",
            verify="Run the five-row loop; it passes. Add `assert_eq!(i32::MIN.checked_abs(), None);` to show why the test avoids negation.",
        ),
        3: dict(
            wrong="Writing the range as `(0..1000).contains(&value)` excludes 1000, because `..` is half-open. The `(1000, true)` row then panics with `left: false`, `right: true` and the message `input 1000`.",
            verify="Add `(500, true)` and `(i32::MIN, false)` rows. Temporarily switch to `0..1000` to watch the `input 1000` failure, then restore `0..=1000`.",
        ),
        4: dict(
            explain='The defect is `assert_eq!(valid_quantity(1001), valid_quantity(1001));`. Both sides run the same code, so it passes for any implementation that returns the same answer twice. The fix is a literal expectation: `assert_eq!(valid_quantity(1001), false, "input 1001");`.',
            why="An oracle must come from outside the code under test. Comparing a call with itself only checks determinism, never whether 1001 is accepted or refused.",
            wrong="Computing the expectation as `(0..=1000).contains(&1001)` looks independent, but it copies the implementation's expression, so a shared off-by-one bug would pass on both sides.",
            verify="Break the function to `fn valid_quantity(_: i32) -> bool { true }`. The self-comparison still passes, while the literal assertion panics with `left: true`, `right: false` and `input 1001`.",
        ),
        5: dict(
            explain="Keep Example A's literal table and add a property loop: `for value in [-4, 0, 7, i32::MIN, i32::MAX] { let once = value.max(0); assert_eq!(once.max(0), once); }`.",
            why="Idempotence says clamping twice changes nothing, which every correct clamp satisfies. The literal rows pin where the boundary is, which the property cannot do on its own.",
            wrong="Relying on idempotence alone passes for the identity `|value| value` and for the constant `|_| 0`, since both return the same result when applied twice. Neither is a clamp.",
            verify="Swap in the identity for `max(0)`: the property loop still passes, but the table fails on `(-2, 0)` with `left: -2`, `right: 0`.",
        ),
        6: dict(
            explain="For a change that makes `valid_quantity` return `Result<Quantity, QuantityError>`: unit tests in `#[cfg(test)] mod tests` cover -1, 0, 1000 and 1001. An integration test in `tests/` drives the import through the `pub` API. A `compile_fail` doctest shows code outside the module cannot build `Quantity` directly. A runtime check runs the binary on a fixture file and compares its output.",
            why="Each layer proves something the others cannot: unit tests pin the rule, integration tests pin the public surface, the doctest pins a compile-time guarantee, and the runtime check exercises real file paths. None proves deployment configuration.",
            wrong="Treating a green `cargo test` as proof the binary reads the right file is wrong here: the unit and integration tests pass slices of strings and never open the configured path.",
            verify="Run `cargo test --lib`, `cargo test --test import` and `cargo test --doc` separately in the Cargo project, then `cargo run` on the fixture. In the pad only the assertion run applies, ending with `rust-024: passed`.",
        ),
    },
    26: {
        1: dict(
            explain="Example A's grain is one row per distinct label, identity is exact case-sensitive string equality, duplicates aggregate into a count, and order is the sorted key order. Example B's grain is one entry per distinct name, a duplicate is detected by `insert` returning `false` and not stored again, and no order is promised.",
            why='`BTreeMap` and `HashSet` both compare keys with `Eq`, so `"b"` twice is one identity, while the map\'s value records how many times it appeared and the set records only presence.',
            wrong='Calling Example A\'s grain one row per input record predicts three rows. Three labels produce two keys, because the second `"b"` updates the existing entry.',
            verify='Add `"B"` to Example A\'s labels. Assert `counts.len() == 3` and keys `vec!["B", "a", "b"]`: uppercase is a separate identity and sorts first in byte order.',
        ),
        2: dict(
            explain='Replace the counter with a set and a rejection list: `let mut accepted = BTreeSet::new(); let mut duplicates = Vec::new(); for label in ["b", "a", "b"] { if !accepted.insert(label) { duplicates.push(label); } }`.',
            why='`insert` returns `false` when the label is already present, so the first `"b"` is kept and the second is recorded as rejected instead of being counted.',
            wrong='Writing `counts.insert(label, 1)` is a replace policy, not rejection: the second `"b"` silently overwrites the first and nothing tells the caller a duplicate arrived.',
            verify='Assert `accepted.iter().copied().collect::<Vec<_>>() == vec!["a", "b"]` and `duplicates == vec!["b"]`. With all-distinct labels, `duplicates` stays empty.',
        ),
        3: dict(
            wrong="Writing `*counts.entry(word).or_insert(1) += 1` starts each new word at 1 and then adds 1, so every count is one too high and the assertion fails with `apple=2`, `fig=2`, `pear=3` on the left.",
            verify="Add `assert_eq!(counts.values().sum::<i32>(), 4);` (one per input word) and `assert_eq!(counts.len(), 3);` beside the report check.",
        ),
        4: dict(
            explain="The defect is building the saved report from `HashMap<&str, i32>` iteration. Its default hasher is seeded randomly, so the same counts can be written as `pear=2, apple=1, fig=1` in one run and another order in the next, and saved files differ with no data change.",
            why="`HashMap` promises lookup by key, not any order. Use a `BTreeMap`, as in task 3, or collect the lines and call `report.sort()` before saving.",
            wrong="Inserting the words in sorted order does not fix it: a `HashMap` ignores insertion order entirely, so the output order still depends on hash values.",
            verify='Build the report from a `HashMap`, call `report.sort()`, and assert it equals `["apple=1", "fig=1", "pear=2"]`. Without the sort, the exact comparison can fail on some runs.',
        ),
        5: dict(
            explain='Empty input: `let words: [&str; 0] = [];` through task 3\'s loop gives an empty map and `report == Vec::<String>::new()`. Repeated keys: `["fig", "fig", "fig"]` gives `vec!["fig=3"]`.',
            why="With no input the loop body never runs, so no entry is created. Every repeat goes through `entry` on the same key, so one row carries the whole count.",
            wrong="Writing `let words = [];` without a type fails with E0282, type annotations needed, because an empty array literal gives no element type to infer.",
            verify="Assert both reports and `counts.is_empty()` for the empty case; the run ends with `rust-026: passed`.",
        ),
        6: dict(
            explain="Checking 10,000 incoming SKUs against a 50,000-item `Vec` with `contains` can compare up to 500 million strings. Building a `HashSet` first costs 50,000 insertions and extra memory for its table, then each lookup has expected constant cost; a `BTreeSet` lookup descends a tree only a few nodes deep, so its cost grows with the logarithm of the catalog size, and it keeps sorted order.",
            why="The index pays a one-time construction and memory cost in exchange for cheap repeated lookups. For three lookups the plain scan is cheaper, and hash lookup cost is an expectation, not a worst-case guarantee.",
            wrong="Building the `HashSet` inside the loop, once per SKU, pays the full construction for every lookup and ends up slower than the linear scan it was meant to replace.",
            verify='On a small fixture, `let catalog = vec!["apple", "fig", "pear"];` and an index collected from it, assert `catalog.contains(&sku) == index.contains(&sku)` for `"pear"` and `"kiwi"`. Timing belongs in a release-mode Cargo benchmark, not the pad.',
        ),
    },
    29: {
        1: dict(
            explain="Example A: `try_send(4)` puts 4 in the one-slot buffer (occupancy 1). `try_send(5)` returns `Err(TrySendError::Full(5))`, so 5 comes back to the caller and occupancy stays 1. `recv()` moves 4 to the receiver (occupancy 0). Example B: `move` gives `send` to the worker, which sends 2 and 3, and when its closure ends, `send` is dropped.",
            why="A value is owned by the buffer between send and receive, and a refused value is returned inside the error. Once the last sender is dropped, the receiver still yields buffered items and only then ends.",
            wrong="Expecting `try_send(5)` to wait for space, or to discard 5, misreads the API: `try_send` never blocks, and `Full` hands the value back so the caller decides what to do with it.",
            verify="After Example A's `recv`, add `send.try_send(6)?;` and `assert_eq!(receive.try_recv()?, 6);`: the freed slot accepts one more item.",
        ),
        2: dict(
            explain="With `sync_channel(2)`, `try_send(4)` and `try_send(5)` both succeed, and `try_send(6)` returns `Err(TrySendError::Full(6))`. `recv` then yields 4 and then 5.",
            why="With no receiver waiting, a `sync_channel(n)` buffers exactly n unreceived items, so the number of accepted immediate sends equals the capacity.",
            wrong="Predicting capacity plus one, or that `sync_channel(0)` accepts a single item, is wrong: a zero-capacity channel is a rendezvous, so with no receiver blocked in `recv`, even the first `try_send` reports `Full`.",
            verify="Assert the two `Ok` sends, `matches!(send.try_send(6), Err(TrySendError::Full(6)))` and the 4 then 5 order. Then `let (zero, _keep) = sync_channel::<i32>(0);` and assert `zero.try_send(1)` is `Full(1)`; the `_keep` binding holds the receiver alive.",
        ),
        3: dict(
            wrong="Calling `producer.join().unwrap()` before the receiving loop deadlocks: the buffer holds 3 and 5, the producer blocks sending 2, and `join` waits for a producer that waits for a consumer, so the pad hangs until it times out.",
            verify="Run the block and confirm the report order. Extend the input to `[3, 5, 2, 7]` with `qty=7` appended to the expected report: the bounded buffer still drains and the loop ends.",
        ),
        4: dict(
            explain="The defect: `let extra = send.clone();` in `main` before Example B's worker takes `send`. The worker sends 2 and 3 and drops its sender, but `extra` keeps the channel connected, so `receive.iter().sum()` waits forever after the two values. Fix it with `drop(extra);` before draining, or do not create the clone.",
            why="The receiver ends only when every sender is gone. A clone that never sends still counts as a live producer.",
            wrong="Adding `worker.join()` before the sum does not help: the worker finishes (both values fit in the buffer), but joining it does not drop `extra`, so the iterator still waits.",
            verify="Use `receive.recv_timeout(std::time::Duration::from_millis(100))` after taking 2 and 3: it returns `Err(RecvTimeoutError::Timeout)` while `extra` is alive and `Err(RecvTimeoutError::Disconnected)` after `drop(extra)`.",
        ),
        5: dict(
            explain="No messages: `let (send, receive) = sync_channel::<i32>(1); drop(send);` then `receive.iter().count() == 0` and `receive.recv().is_err()`. Disconnected receiver: create another pair, `drop(receive);` and `send.send(7)` returns `Err(SendError(7))`.",
            why="With no senders and an empty buffer, the receiver reports completion at once. With no receiver, nobody can ever take the value, so `send` fails and returns 7 inside the error instead of losing it.",
            wrong="Writing `let _ = send.send(7);` in a producer discards that error, so work vanishes silently when the consumer has gone. Example B's `.unwrap()` at least panics, naming `SendError`.",
            verify="Assert `send.send(7).unwrap_err().0 == 7` for the disconnected case, and the zero count for the empty case; the marker follows.",
        ),
        6: dict(
            explain="For an inventory import where every row matters, use blocking `send` on a `sync_channel`, so a slow writer slows the reader. For a request path that must answer quickly, use `try_send` and reject on `Full`, returning a retry signal. For telemetry samples, drop deliberately and count the drops. In each case the producer records sent, rejected and dropped counts.",
            why="Each policy states who absorbs overload: the producer waits, the caller retries, or the data is knowingly lost. The counts are the producer's evidence of which happened. A limitation is that capacity does not bound work already started outside the channel.",
            wrong="Switching to an unbounded `channel()` to avoid choosing removes backpressure: when the consumer is slower, the queue and its memory grow until the process fails.",
            verify="With `sync_channel(1)` and no consumer running, `try_send` each of `[1, 2, 3]`, collecting values from `Err(TrySendError::Full(value))`. Assert the rejected list is `vec![2, 3]` and `receive.recv()?` is 1.",
        ),
    },
    32: {
        1: dict(
            explain='Validation is the guard `if name.is_empty() || value < 0`, which looks at one row alone. Accumulation is the `get`, `checked_add` and `insert` sequence, which depends on earlier rows. In Example B, `("", 2)` fails the empty-name check, `("a", -1)` fails the negative check, and `("b", 0)` passes and is inserted as 0, so `report.1` is 2. In Example A, `"b"` becomes 2 and then 6.',
            why="A row can be judged valid in isolation, but whether adding it overflows depends on the running total, so the overflow rejection has to live in the accumulation step.",
            wrong='Moving the overflow check into row validation, for example rejecting values near `i32::MAX`, cannot work: `("b", i32::MAX)` is a valid row on its own and only overflows after an earlier `("b", 1)`.',
            verify='Assert `summarize(&[("b", 1), ("b", i32::MAX)])` keeps `"b"` at 1 with `report.1 == 1`, and that the reverse order keeps `"b"` at `i32::MAX`, also with one rejection.',
        ),
        2: dict(
            explain='Add `fn render(report: &(std::collections::BTreeMap<&str, i32>, usize)) -> String { let mut parts: Vec<String> = report.0.iter().map(|(name, total)| format!("{name}={total}")).collect(); parts.push(format!("rejected={}", report.1)); parts.join(";") }`. `summarize` is unchanged.',
            why="`render` only borrows the report and reads it, and the `BTreeMap` already iterates in key order, so the text is deterministic while the core keeps returning the map and the rejection count.",
            wrong='Changing `summarize` to return the rendered `String` breaks every existing caller: `report.0.get("b")` in Example A then fails with E0609, no field `0` on type `String`.',
            verify='Assert `render(&summarize(&[("b", 2), ("a", 3), ("b", 4)])) == "a=3;b=6;rejected=0"` and that Example B renders as `"b=0;rejected=2"`. Both examples\' original assertions still pass.',
        ),
        3: dict(
            explain="Copy `courses/rust/fixtures/InventoryLab` into your own ignored workspace and, in a prepared Rust environment, run `rustc --version`, `cargo build --locked --offline`, `cargo test --locked --offline` and `cargo run --locked --offline` from the copy.",
            why="`--locked` refuses to change the checked-in Cargo.lock and `--offline` forbids downloads, so success shows the package builds from the standard library alone. `tests/contracts.rs` exercises only the public `summarize` and `render`, so it checks the library surface the executable also uses.",
            wrong="Pasting `src/lib.rs` and `src/main.rs` into the pad fails: the pad compiles one `main.rs`, so `inventory_lab::summarize` names a crate that does not exist there and rustc reports E0433, failed to resolve.",
            verify="`cargo test` reports four passing tests in the `contracts` target (aggregation order, rejected rows, overflow and empty or extra-field input) and zero unit tests for the library and executable targets. `cargo run` prints `apple=3;pear=6;rejected=1`.",
        ),
        4: dict(
            explain='The defect is `summarize` calling `println!("rejected {name}")` for each refused row, or a library method such as `fn print(&self)` that writes the report to stdout. Every adapter now prints whether it wants to or not, and raw input names reach the console. Keep the library returning data and strings, and let `main` decide to print `render(&report)`.',
            why="A reusable core cannot know whether its caller is a terminal, a test or another program, so output belongs to the adapter. Returning values also lets tests assert on exactly what would be shown.",
            wrong="Adding a `verbose: bool` parameter to silence the print still ties the library to stdout, changes the signature every caller must use, and still echoes raw names when it is switched on.",
            verify="With output moved to `main`, assert on `render` results as in task 2. Running the pad shows no lines from `summarize`, only what `main` prints and the `rust-032: passed` marker.",
        ),
        5: dict(
            explain='Empty: `summarize(&[])` gives an empty map and 0. Duplicate: Example A gives `"b"` = 6. Invalid: `("", 2)` and `("a", -1)` add 2 rejections. Overflow: `summarize(&[("b", i32::MAX), ("b", 1)])` keeps `"b"` at `i32::MAX` and counts 1 rejection. Note that `(" ", 1)` is accepted, because this helper checks `is_empty` without trimming, unlike InventoryLab\'s library.',
            why="Each case reaches a different branch: no iterations, the existing-key path, the validation guard, and the `checked_add` returning `None`, which skips the insert and keeps the earlier total.",
            wrong="Expecting the overflow row to wrap to `i32::MIN`, or to replace the total with 1, assumes plain addition or a replace policy. `checked_add` refuses the sum, so the map keeps the last valid total.",
            verify='Assert all four cases plus `summarize(&[(" ", 1)]).0.get(" ") == Some(&1)`, which documents the whitespace gap rather than hiding it.',
        ),
        6: dict(
            explain="Add a second binary, `src/bin/check.rs`, that reads lines from standard input, calls `inventory_lab::summarize` on them and exits with status 1 when `report.rejected > 0`, printing only the counts. It reuses the library's validation and never copies `summarize`.",
            why="Both binaries depend on the same validated library, so a later fix such as trimming names before they are counted reaches both, and the existing integration tests cover the shared contract. A limitation: with two binaries, `cargo run` needs `--bin inventory-lab` or `--bin check`, and `summarize` takes a slice, so input is collected before it is processed.",
            wrong="Copying `summarize` into the new binary to tweak its output creates a second validator that drifts: a later fix to the library's overflow handling would not reach the copy.",
            verify="In the copied project, `cargo run --locked --offline --bin check` with a fixture piped in should print the counts, and `echo $?` shows 1 when any row was rejected. `cargo test --locked --offline` still passes the four contract tests.",
        ),
    },
    46: {
        1: dict(
            explain='Every field is safe: `operation` "fixture-1" is a fixed correlation identifier, `stage` "validate" and `outcome` "rejected" come from small fixed vocabularies, and `count` is a number. None of them carries the content of a submitted record.',
            why="Each field answers what happened, where and how often, without repeating what was submitted. The `&'static str` field type also keeps ordinary runtime strings out, because a borrowed local `String` does not live long enough.",
            wrong="Treating `&'static str` as proof of safety goes too far: `Box::leak` can turn any input into a `&'static str`. The type is a strong hint; the reviewed fixed vocabulary is the actual rule.",
            verify='Try `let input = String::from("token=abc"); Event { operation: &input, stage: "validate", outcome: "rejected", count: 2 }` and read E0597, `input` does not live long enough. The literal-only event still renders `fixture-1 validate rejected count=2`.',
        ),
        2: dict(
            explain='Introduce `#[derive(Clone, Copy)] enum Stage { Validate, Aggregate }` with `fn name(self) -> &\'static str { match self { Stage::Validate => "validate", Stage::Aggregate => "aggregate" } }`, change the field to `stage: Stage` and render `self.stage.name()`.',
            why="An enum closes the set of stages: the only strings that can appear are the two in the `match`, so a new stage is a reviewed code change and never comes from input.",
            wrong="Adding a `detail: String` field to hold text such as the rejected line widens the event to raw input, which is exactly what this lesson's events are designed to exclude.",
            verify='Assert an `Event` with `stage: Stage::Aggregate`, outcome "accepted" and count 3 renders `fixture-1 aggregate accepted count=3`. A misspelled `Stage::Agregate` fails with E0599.',
        ),
        3: dict(
            wrong='Parsing with `parse::<i32>()` accepts `"-1"`, so the counts become accepted 3 and rejected 1 and the event assertion fails, even though a negative quantity is not a valid record.',
            verify='Add `""` as a fifth input: it fails to parse, so the event becomes `submitted=5 accepted=2 rejected=3` and `accepted + rejected == submitted` still holds.',
        ),
        4: dict(
            explain='The defect is an error built as `format!("bad record: {line}")` where the line is `pear,2,token=secret-123`, or `format!("auth failed for {token}")`. The message flows into logs and user output, leaking the secret and an unbounded amount of input. Report position and category instead: `format!("line {number}: bad quantity")`.',
            why="A line number and category are enough to find the record in the source, which already has its own access controls, while the error text itself holds nothing sensitive and has a bounded length.",
            wrong="Truncating the record to its first 20 characters bounds the size but not the leak: for `pear,2,token=secret-123` the kept prefix is `pear,2,token=secret-`, so most of the secret still reaches the log.",
            verify='Assert `message == "line 3: bad quantity"` and `!message.contains("secret")` for an input line containing `token=secret-123`.',
        ),
        5: dict(
            explain='Missing permission: with Example B\'s list, assert `"report:delete"`, `"Report:read"` and `"report:read "` are all refused, and with `let allowed: [&str; 0] = [];` even `"report:read"` is refused. Empty workload: task 3\'s importer with `let inputs: [&str; 0] = [];` produces `submitted=0 accepted=0 rejected=0`.',
            why="`contains` is exact string equality, so case and trailing-space variants are different actions, and an empty allowlist admits nothing. An empty batch still emits an event, so the operator can tell it ran with no work rather than not at all.",
            wrong='Checking `action.starts_with("report:")` to cover both listed actions also admits `"report:delete"`, turning a missing entry into implicit permission.',
            verify='Run the assertions; each refused action is checked like `assert!(!allowed.contains(&"Report:read"))`, and the empty event equals the zero-count string.',
        ),
        6: dict(
            explain="Parse requests into `enum Operation { ReadReport(ReportId), ListReports }`, where `struct ReportId(u32)` comes from `parse::<u32>()`, and check the caller's allowlist before dispatch. The executor `match`es the enum and calls fixed functions. If an external program is unavoidable, use `Command::new` with a fixed program and pass the id through `.arg(id.0.to_string())`, never a shell string.",
            why="Data can only select among reviewed operations and fill typed parameters, so no input can add a new instruction. `.arg` passes one argument without shell interpretation. A limitation is that each new operation needs a code change and review, which is the point.",
            wrong='Running `Command::new("sh").arg("-c").arg(format!("report {id}"))` lets an id of `1; echo injected` run a second command. Rust\'s memory safety does nothing to prevent that.',
            verify='Assert `parse("report:read", "7")` matches `Ok(Operation::ReadReport(ReportId(7)))`, while `parse("report:read", "1; echo injected")` and `parse("report:delete", "7")` are both `Err`. No shell is run in the pad.',
        ),
    },
    3: {
        1: dict(
            explain="For `255_u8` plus 1: `checked_add` returns `None`, `wrapping_add` returns 0 and `saturating_add` returns 255. The in-range control `2_u8.checked_add(3)` returns `Some(5)`, so `checked_add` is not simply refusing everything.",
            why="255 is `u8::MAX`, so the true sum 256 needs a ninth bit. Checked arithmetic reports that the result does not fit, wrapping keeps the low eight bits of 256 (which are all zero), and saturating clamps to the largest representable value.",
            wrong="Predicting that `wrapping_add` gives 256 or panics forgets that its whole purpose is to keep the result inside `u8`. Predicting `Some(255)` for `checked_add` confuses it with saturation.",
            verify="The first three assertions of Example A encode exactly these predictions. Change the expected wrapping result to 255 and the run panics with `left: 0` and `right: 255` before any marker prints.",
        ),
        2: dict(
            code="""assert_eq!(0_u8.checked_sub(1), None);
assert_eq!(0_u8.wrapping_sub(1), 255);
assert_eq!(0_u8.saturating_sub(1), 0);
assert_eq!(5_u8.checked_sub(3), Some(2));
let stock: u32 = 2;
let ordered: u32 = 3;
assert_eq!(stock.checked_sub(ordered), None);""",
            observe="At zero, checked subtraction gives None, wrapping gives 255 and saturating stays at 0; 5 minus 3 is Some(2), and 2 units of stock minus an order of 3 is None.",
            explain="Below zero mirrors the overflow case at the top: wrapping jumps to `u8::MAX`, saturation clamps at the lower bound 0, and only `checked_sub` makes the impossible stock level visible as `None` instead of a plausible count.",
            wrong="Using `saturating_sub` for the stock calculation reports 0 remaining after an order of 3 against a stock of 2, quietly hiding the one unit that could not be supplied.",
            verify="Every assertion passes and `rust-003: passed` prints. Replace the stock check's call with `Some(stock.wrapping_sub(ordered))` and it fails with `left: Some(4294967295)`, a huge u32 instead of a refusal.",
        ),
        4: dict(
            explain="The defect is `let total = price * quantity;` for `u64` money values. A debug build panics with `attempt to multiply with overflow`, but a release build compiles with overflow checks off and silently wraps, so production gets a small wrong total. Replace it with `price.checked_mul(quantity)` and handle `None` explicitly, as task 3 does.",
            why="Overflow checks are a build-profile setting, not part of the program's meaning. Only the explicit `checked_*`, `wrapping_*` or `saturating_*` methods state a policy that holds in every profile.",
            wrong="Adding `#[cfg(debug_assertions)]` tests that expect the panic proves only debug behavior; the release binary still wraps. Switching to `u128` delays the overflow without stating what should happen when it occurs.",
            verify="Compare `std::hint::black_box(u64::MAX).wrapping_mul(2)`, which is `u64::MAX - 1`, with `checked_mul` returning `None`. The pad compiles in debug mode, so the plain `*` version would panic there instead of producing the release value.",
        ),
        5: dict(
            code="""fn accept_quantity(quantity: u32) -> Result<u32, String> {
    if quantity <= 1_000 {
        Ok(quantity)
    } else {
        Err(format!("quantity {quantity} exceeds 1000"))
    }
}
assert_eq!(accept_quantity(0), Ok(0));
assert_eq!(accept_quantity(1_000), Ok(1_000));
assert_eq!(
    accept_quantity(1_001),
    Err(String::from("quantity 1001 exceeds 1000"))
);
assert_eq!(u8::try_from(255_u32), Ok(255));
assert!(u8::try_from(256_u32).is_err());
assert_eq!(300_i32 as u8, 44);""",
            observe="Quantities 0 and 1000 are accepted, 1001 is rejected with a message naming it; converting 255 to u8 succeeds, 256 fails, and an `as` cast turns 300 into 44.",
            explain="The application range 0 to 1000 is narrower than `u32`, so it needs its own check with an inclusive upper bound. The last three lines show the same boundary for type conversion: `try_from` refuses the first value past `u8::MAX`, while `as` keeps the low byte of 300 (300 - 256 = 44).",
            wrong="Writing the guard as `quantity < 1_000` rejects the documented maximum 1000; only the boundary fixture catches it, since every middle value behaves the same under both guards.",
            verify="Run the block. Change the guard to `<` and the second assertion panics with an `Err` naming 1000, showing the off-by-one at the edge.",
        ),
    },
    6: {
        1: dict(
            explain="In Example A, `total` is 0 before the loop. Iteration 1 reads 2 and leaves 2; iteration 2 reads 4 and leaves 6; iteration 3 reads 6 and leaves 12. After the loop, `total` is 12 and `values` still has length 3.",
            why="`for value in &values` yields a shared reference to each element in order, and `total += value` adds through it. The loop borrows rather than consumes the vector, so the length check after it still compiles.",
            wrong="Listing the values 2, 4, 6 as the accumulator's states confuses the element with the running total. Writing `for value in values` would also change the answer to the later check: it moves the vector, and `values.len()` becomes E0382.",
            verify="Add `let mut states = vec![total];` before the loop and `states.push(total);` inside it, then assert `states == vec![0, 2, 6, 12]`.",
        ),
        2: dict(
            code="""let values = [4, -2, 5, -7, 1];
let mut total = 0;
let mut skipped = 0;
for value in values {
    if value < 0 {
        skipped += 1;
        continue;
    }
    total += value;
}
assert_eq!(total, 10);
assert_eq!(skipped, 2);
assert_eq!(
    total,
    values.iter().filter(|value| **value >= 0).sum::<i32>()
);""",
            observe="The non-negative values 4, 5 and 1 sum to 10, two negatives are skipped, and the loop agrees with an independent filter-and-sum.",
            explain="The invariant is that after each iteration `total` equals the sum of the non-negative values seen so far and `skipped` counts the rest. `continue` leaves the accumulator untouched for -2 and -7, and counting them keeps the skip visible.",
            wrong="Clamping with `total += value.max(0)` gets the same 10 but loses the count of discarded readings, so a batch that was mostly negative looks as healthy as a clean one.",
            verify="Run the block. Remove `continue` and the total becomes 1, so the first assertion fails with `left: 1` and `right: 10`.",
        ),
        4: dict(
            explain="The defect is `for index in 0..=values.len() { total += values[index]; }`. With three values the last index is 3, and the run panics with `index out of bounds: the len is 3 but the index is 3`. Use the exclusive range `0..values.len()`, or better, iterate the values directly with `for value in &values`.",
            why="Valid indices of a length-3 vector are 0, 1 and 2. `..=` includes its end, so it produces one index past the last element; direct iteration never produces an index at all.",
            wrong="Subtracting one, `0..=values.len() - 1`, works for three values but underflows `usize` for an empty vector and panics with `attempt to subtract with overflow` before the loop starts.",
            verify="Run the faulty loop on `[2, 4, 6]` and read the panic naming index 3. After the fix, `total` is 12, and running the same loop on an empty vector leaves it 0.",
        ),
        5: dict(
            code="""let empty: [i32; 0] = [];
assert_eq!(empty.iter().position(|value| *value == 8), None);
assert_eq!(empty.iter().sum::<i32>(), 0);
assert_eq!([8].iter().position(|value| *value == 8), Some(0));
assert_eq!([3].iter().position(|value| *value == 8), None);
let repeated = [8, 8, 8];
assert_eq!(repeated.iter().position(|value| *value == 8), Some(0));
assert_eq!(repeated.iter().rposition(|value| *value == 8), Some(2));
assert_eq!(repeated.iter().filter(|value| **value == 8).count(), 3);""",
            observe="An empty slice has no match and sums to 0; a singleton 8 is found at 0 and a singleton 3 is not; in [8, 8, 8] the first match is 0, the last is 2 and there are 3 matches.",
            explain="Each sequence shape exercises a different stop: no iterations, a match on the only element, and early stopping at the first of several matches. `rposition` and the count show that the search really did stop early rather than missing the later copies.",
            wrong="Returning the last matching index by keeping a `found = Some(index)` variable without stopping passes the empty and singleton cases but returns Some(2) for the repeated case.",
            verify="Run the block; every check is silent and `rust-006: passed` prints. Swap `position` for `rposition` in the first repeated check and it fails with `left: Some(2)`.",
        ),
    },
    7: {
        1: dict(
            explain='`double(original)` receives a copy of the `i32` 7, which is why `original` is still 7 afterwards. `starts_with_p(&owned)` borrows the `String` as `&str` through deref coercion, and `starts_with_p("apple")` passes a string literal, which is already a borrowed `&\'static str`. Nothing is moved.',
            why='`i32` implements `Copy`, so passing it by value duplicates the bits. `String` does not, so the function takes a reference; `owned` keeps ownership and the final `assert_eq!(owned, "pear")` compiles.',
            wrong="Saying `owned` is copied into the function would require a `.clone()` that the code does not contain. Saying `original` is borrowed misses that `double` has a value parameter `value: i32`.",
            verify='Change `starts_with_p` to take `text: String` and call it as `starts_with_p(owned)`: the later `assert_eq!(owned, "pear")` is rejected with E0382, borrow of moved value.',
        ),
        2: dict(
            code="""fn labeled_length(label: &str, text: &str) -> String {
    format!("{label}: {} bytes", text.len())
}
let owned = String::from("pear");
assert_eq!(labeled_length("fruit", &owned), "fruit: 4 bytes");
assert_eq!(labeled_length("note", "café"), "note: 5 bytes");
assert_eq!(owned, "pear");""",
            observe="pear is labeled as 4 bytes, café as 5 bytes, and the owned String is still usable afterwards.",
            explain="Both parameters are `&str`, so the function accepts literals and borrowed Strings alike and needs no ownership. The label says bytes because `len` counts UTF-8 bytes, which is why the accented word reports 5.",
            wrong="Labeling the result as characters while still calling `len` gives `note: 5 characters` for the four-letter café; the café fixture exposes the mismatch.",
            verify="Run the block. Change the parameter to `text: String` and the `&owned` call fails with E0308, expected `String`, found `&String`.",
        ),
        4: dict(
            explain="The defect is `fn double(value: i32) -> i32 { value * 2; }`. rustc reports E0308, mismatched types: expected `i32`, found `()`, and points at the body with the help text `remove this semicolon to return this value`. Delete the semicolon so `value * 2` is the block's tail expression.",
            why="A semicolon turns an expression into a statement whose value is discarded, so the block ends with the unit value `()`. The declared return type `i32` makes the compiler reject the mismatch before anything runs.",
            wrong="Adding `return value * 2;` also compiles and is not wrong, but adding `-> ()` or removing the return type to silence the error changes the contract and breaks every caller that uses the result.",
            verify="Compile the defective version and read E0308 with the semicolon hint. Remove the semicolon and `assert_eq!(double(original), 14)` passes again.",
        ),
        5: dict(
            code="""fn labeled_length(text: &str) -> String {
    format!("length={}", text.len())
}
fn area(width: u32, height: u32) -> u32 {
    width * height
}
assert_eq!(labeled_length(""), "length=0");
assert_eq!(labeled_length(&String::new()), "length=0");
assert_eq!(area(0, 0), 0);
assert_eq!(area(0, 65_535), 0);
assert_eq!(area(65_535, 0), 0);""",
            observe="Empty text, as a literal or an empty String, has length 0, and any rectangle with a zero side has area 0.",
            explain="An empty `&str` is a valid input of length 0, not an error. A zero width or height is inside the documented range of the task 3 contract, and the product is 0 on either side, including next to the largest allowed side.",
            wrong="Treating empty input as invalid with `assert!(!text.is_empty())` makes the function panic on a legitimate empty field instead of reporting length 0.",
            verify="Run the block; all five checks pass. Change `area` to return `width + height` and the second area check fails with `left: 65535`.",
        ),
    },
    8: {
        1: dict(
            explain="Before the move, `first` owns a heap buffer holding `pear`. After `let second = first;`, `second` owns that same buffer and `first` is moved-from: it may not be read, and it will not be dropped. At the end of the block only `second` frees the buffer.",
            why="A `String` is a pointer, length and capacity triple that owns its allocation. Assignment copies the triple and transfers ownership, so exactly one owner remains and the buffer is freed exactly once.",
            wrong="Drawing two arrows to the buffer, one from each name, describes a double free waiting to happen. Drawing two buffers describes `clone`, which Example B does explicitly.",
            verify="Record `let address = first.as_ptr();` before the move and assert `second.as_ptr() == address` after it: the bytes did not move, only ownership did.",
        ),
        2: dict(
            explain='Add `assert_eq!(first, "pear");` after `let second = first;`. rustc rejects it with E0382, borrow of moved value: `first`. The diagnostic marks `let second = first;` as `value moved here` and the new line as `value borrowed here after move`, notes that `String` does not implement the `Copy` trait, and suggests `first.clone()`.',
            why="After a move the compiler treats `first` as uninitialized, so any read, even a borrow inside `assert_eq!`, is refused at compile time. No program is built, so no runtime check is reached.",
            wrong="Accepting the suggested `.clone()` reflexively makes the error disappear but changes the design to two buffers; if only reading was needed, borrowing with `let second = &first;` is the honest fix.",
            verify="Save the full E0382 text in your notes, then delete the temporary line; the reference compiles and `rust-008: passed` prints.",
        ),
        4: dict(
            explain="The defect is a reader written as `fn count_p(text: String) -> usize` and called as `count_p(name.clone())` at every site because the caller still needs `name`. Each call allocates and copies the whole buffer just to read it. Change the signature to `fn count_p(text: &str) -> usize` and call `count_p(&name)`.",
            why="The function only reads, so a shared borrow states its real requirement. The caller keeps ownership, nothing is copied, and literals can be passed without allocating.",
            wrong="Removing the clones but keeping `text: String` makes the second call E0382, because the first call moved `name`; the clones were hiding a wrong interface, not a missing copy.",
            verify="After the change, assert `count_p(&name) == count_p(&name)` twice in a row and that `name` is still the original text, with no `.clone()` anywhere in the file.",
        ),
        5: dict(
            code="""let count = 5_i32;
let copied = count;
assert_eq!(count + copied, 10);
let name = String::from("pear");
let address = name.as_ptr();
let moved = name;
assert_eq!(moved.as_ptr(), address);
let cloned = moved.clone();
assert_ne!(cloned.as_ptr(), address);
assert_eq!(moved, cloned);""",
            observe="After copying, both i32 bindings are usable and sum to 10; the moved String keeps its original buffer address, while the clone has a new address with equal contents.",
            explain="`i32` is `Copy`, so `count` stays valid after assignment. Moving the `String` copies only its pointer, length and capacity, so the heap address is unchanged, whereas `clone` allocates a separate buffer holding the same bytes.",
            wrong="Assuming `let moved = name;` copies the text predicts a new address after the move; the address equality check shows it does not.",
            verify='Run the block. Add `assert_eq!(name, "pear");` after the move and compilation fails with E0382, while the equivalent read of `count` compiles.',
        ),
    },
    10: {
        1: dict(
            explain="While `append_mark(&mut text)` runs, the function's parameter `text` is the only path to the String; `main` cannot read or write its own `text` until the call returns. Afterwards the borrow has ended, `main` regains full access and observes `ready!`.",
            why="A `&mut` reference is exclusive for as long as it is live. The borrow lasts only for the call, so the later `assert_eq!` is a new shared borrow that starts after the exclusive one ended.",
            wrong="Thinking the function receives a copy predicts that `main` still sees `ready`; the passing assertion shows the change happened in place through the borrow.",
            verify="Keep the reference alive with `let borrow = &mut text; assert_eq!(text, \"ready\"); borrow.push('!');` and the compiler rejects the read with E0502.",
        ),
        2: dict(
            code="""let mut values = [1, 2, 3, 4];
let (left, right) = values.split_at_mut(2);
left[0] = 9;
right[0] = 8;
values[3] = 7;
assert_eq!(values, [9, 2, 8, 7]);""",
            observe="After the two halves are last used, writing 7 directly into values[3] compiles and the array becomes [9, 2, 8, 7].",
            explain="Non-lexical lifetimes end the borrows held by `left` and `right` after their last use, `right[0] = 8`. The direct write to `values` comes after that point, so it is the only borrow alive when it happens.",
            wrong="Placing `values[3] = 7;` between `left[0] = 9;` and `right[0] = 8;` is rejected with E0506, cannot assign to `values[_]` because it is borrowed, because `right` is still used afterwards and so its borrow of `values` is still live.",
            verify="Run the block. Move the direct write up one line and read the E0506 diagnostic naming the earlier `split_at_mut` borrow.",
        ),
        4: dict(
            explain="The defect is `let first = &mut values; let second = &mut values; first[0] = 1; second[1] = 2;`. rustc reports E0499, cannot borrow `values` as mutable more than once at a time, marking the first borrow, the second borrow and the later use of `first` that keeps it alive. Use `split_at_mut` for disjoint halves, or finish with `first` before creating `second`.",
            why="Two live exclusive references could write the same element, so the rule forbids them regardless of which indices are touched. The compiler does not reason about indices 0 and 1 being different; `split_at_mut` provides that proof through its API.",
            wrong="Adding more `mut`, as in `let mut first = &mut values;`, changes nothing: the conflict is between two borrows of `values`, not about whether the reference bindings are reassignable.",
            verify="Compile the defect and read E0499. Rewrite with `let (first, second) = values.split_at_mut(1); first[0] = 1; second[0] = 2;` and assert the result.",
        ),
        5: dict(
            code="""let mut values = [1, 2, 3];
let (left, right) = values.split_at_mut(0);
assert!(left.is_empty());
right[0] = 7;
let (left, right) = values.split_at_mut(3);
assert!(right.is_empty());
left[2] = 9;
assert_eq!(values, [7, 2, 9]);
assert!(values.split_at_mut_checked(4).is_none());
let mut empty: [i32; 0] = [];
let (left, right) = empty.split_at_mut(0);
assert!(left.is_empty() && right.is_empty());""",
            observe="Splitting at 0 gives an empty left half and splitting at 3 an empty right half; writes through the other half turn [1, 2, 3] into [7, 2, 9], 4 is refused, and an empty slice splits into two empty halves.",
            explain="Both endpoints are valid split points, so each produces one empty half and one half covering the whole slice. `split_at_mut_checked` turns the one-past-the-end index into `None` instead of the panic `split_at_mut(4)` would raise.",
            wrong="Assuming a split at 0 is invalid and guarding with `if mid > 0` skips the legitimate whole-slice case; using `split_at_mut(4)` to probe the far edge panics instead of observing it.",
            verify="Run the block. Replace the checked call with `values.split_at_mut(4)` and the program panics with a `mid > len` message.",
        ),
    },
    13: {
        1: dict(
            explain="`Outcome::Ready` carries only a `u32` count and `Outcome::Failed` carries only a `String` reason. A ready value such as `Outcome::Ready(4)` has no reason field to read, and a failed value has no count, so `render` can only reach `count` in the `Ready` arm and `reason` in the `Failed` arm.",
            why="Each variant declares its own payload, and a `match` arm binds only the fields of the variant it matched. The type system therefore rules out a failed outcome that also claims a count.",
            wrong="Assuming every `Outcome` has both a count and a reason, with one of them empty, describes a struct with optional fields rather than this enum.",
            verify="Try `if let Outcome::Ready(reason) = &value { let _ = reason.len(); }`: it fails with E0599 because `reason` is a `&u32`, not a String.",
        ),
        2: dict(
            code="""enum Status {
    Loading,
    Ready(u32),
    Failed(String),
}
fn describe(value: &Status) -> String {
    match value {
        Status::Loading => String::from("loading"),
        Status::Ready(count) => format!("count:{count}"),
        Status::Failed(reason) => format!("error:{reason}"),
    }
}
assert_eq!(describe(&Status::Loading), "loading");
assert_eq!(describe(&Status::Ready(4)), "count:4");
assert_eq!(
    describe(&Status::Failed(String::from("invalid"))),
    "error:invalid"
);""",
            observe="Loading renders as loading, while Ready(4) and Failed(invalid) still render as count:4 and error:invalid.",
            explain="The new variant has no payload because nothing is known yet. Adding it to the enum without the new arm makes `describe` fail with E0004, non-exhaustive patterns: `&Status::Loading` not covered, which is how the compiler lists every consumer to update.",
            wrong='Adding `_ => String::from("count:0")` instead of a `Loading` arm compiles but reports an unfinished import as a successful one with zero rows.',
            verify="Run the block. Delete the `Status::Loading` arm and read E0004 naming the missing variant.",
        ),
        4: dict(
            explain='The defect is `struct Import { pending: bool, rows: Option<usize>, reason: Option<String> }`. Nothing stops `Import { pending: true, rows: Some(5), reason: Some(String::from("bad header")) }`, which is pending, completed and rejected at once, and every reader must guess which field wins. Replace it with task 3\'s enum, where each state holds only its own data.',
            why="An enum value is exactly one variant, so contradictory combinations cannot be constructed. With optional fields, every consumer repeats the same validity checks and some will forget one.",
            wrong="Adding a `fn is_valid(&self) -> bool` check documents the rule but still lets invalid values be created and passed around before anyone calls it.",
            verify="Construct the contradictory struct and note that it compiles. Then try to give `Import::Pending` a `rows` field in the enum version: E0559, variant has no field named `rows`.",
        ),
        5: dict(
            code="""let cases = [
    (Outcome::Ready(0), "count:0"),
    (Outcome::Ready(u32::MAX), "count:4294967295"),
    (Outcome::Failed(String::new()), "error:"),
    (
        Outcome::Failed(String::from("bad header")),
        "error:bad header",
    ),
];
for (value, expected) in &cases {
    assert_eq!(render(value), *expected);
}""",
            observe="Ready(0) and Ready(u32::MAX) render their counts, an empty failure reason renders as error:, and a real reason is appended after error:.",
            explain="Both declared variants are covered, each with an ordinary and an edge payload. The table borrows every case with `&cases`, so `render` receives a `&Outcome` and no String is moved out of the array.",
            wrong="Testing only `Outcome::Ready(4)` and calling the enum covered leaves the `Failed` arm unexercised, so a typo such as `eror:` would ship unnoticed.",
            verify="Run the block. Change the `Failed` arm of `render` to produce `failed:{reason}` and the third case fails, naming both strings.",
        ),
    },
    15: {
        1: dict(
            explain='For `"3"`, `text.parse()` yields `Ok(3)`, `?` unwraps it to `3`, the sign check passes and the function returns `Ok(3)`. For `"bad"`, `parse` fails, `map_err` replaces the `ParseIntError` with `"not an integer"`, and `?` returns that error at once, so the sign check never runs. For `"-1"`, parsing succeeds with `-1`, and only the domain check `value < 0` rejects it with `"negative quantity"`.',
            why="Syntax is settled before meaning: `?` is the exit for the first stage and the explicit `return Err` is the exit for the second. Each path leaves through exactly one of them, which is why the two reasons never mix.",
            wrong='Reading `"-1"` as a parse failure confuses representation with domain. `-1` is a perfectly valid `i32`; it is the application rule that refuses it.',
            verify='Add `assert_eq!("-1".parse::<i32>(), Ok(-1));` next to Example A: it passes, which shows that the rejection came from the second check.',
        ),
        2: dict(
            code="""const MAX_QUANTITY: i32 = 1_000;
fn bounded_quantity(text: &str) -> Result<i32, &'static str> {
    let value = parse_quantity(text)?;
    if value > MAX_QUANTITY {
        return Err("quantity above maximum");
    }
    Ok(value)
}
assert_eq!(bounded_quantity("1000"), Ok(1_000));
assert_eq!(bounded_quantity("1001"), Err("quantity above maximum"));
assert_eq!(bounded_quantity("bad"), Err("not an integer"));
assert_eq!(bounded_quantity("-1"), Err("negative quantity"));""",
            observe="1000 is accepted, 1001 is rejected as above maximum, and malformed and negative input keep their original reasons.",
            explain="The maximum is an application policy layered on top of `parse_quantity`, so it gets its own function and its own error text. `?` forwards the two existing categories unchanged, and the new check runs only on a value that already passed both.",
            wrong="Folding the limit into the parse step with `text.parse::<i32>().ok().filter(|v| *v <= MAX_QUANTITY)` returns `None` for 1001, for `bad` and for `-1` alike, so the caller can no longer tell a typo from an oversized order.",
            verify="Run the block, then change `1001` to `1000` in the second assertion and watch it fail with `left: Ok(1000)`, which proves the boundary is inclusive.",
        ),
        4: dict(
            explain='The defect is `let quantity = parse_quantity(text).unwrap_or(0);`. Both `"bad"` and `"-1"` become `0`, which is also the result for the legitimate input `"0"`. A total built from such values silently undercounts, and nothing records that any line was rejected.',
            why="Zero is a valid quantity in this domain, so it cannot double as a failure marker. Keeping the `Result` until a boundary that can count or report the error is what preserves the evidence.",
            wrong="Replacing `0` with `-1` as the fallback looks safer but reintroduces the same problem with a magic value that later arithmetic will happily add.",
            verify='Sum `["2", "bad", "3"]` with `unwrap_or(0)` and get `5`; Example B gets the same `5` but also reports one rejection through `inputs.len() - accepted.len()`.',
        ),
        5: dict(
            code="""assert_eq!(parse_quantity(""), Err("not an integer"));
assert_eq!(parse_quantity("0"), Ok(0));
assert_eq!(parse_quantity("-5"), Err("negative quantity"));
assert_eq!(parse_quantity("2147483647"), Ok(i32::MAX));
assert_eq!(parse_quantity("2147483648"), Err("not an integer"));
assert_eq!(parse_quantity(" 3"), Err("not an integer"));""",
            observe="Empty text and a leading space are malformed, zero is accepted, -5 is negative, i32::MAX parses, and one past it is reported as not an integer.",
            explain="`str::parse::<i32>` rejects empty input and surrounding whitespace, so callers must trim deliberately. Overflow is the interesting row: `ParseIntError` knows it is `PosOverflow`, but `map_err(|_| ...)` discards that kind, so a huge number is reported with the same text as a typo.",
            wrong='Assuming `"2147483648"` would wrap to a negative number and be rejected as negative ignores that `parse` checks the range and never wraps.',
            verify='Run the block. Then print `"2147483648".parse::<i32>().unwrap_err().kind()` and see `PosOverflow`, the detail a dedicated error category could keep.',
        ),
    },
    18: {
        1: dict(
            explain="In `larger(3, 8)` both arguments are integer literals, so `T` defaults to `i32`, which implements `Ord`. In the second call `T` is `String`, also `Ord`, and the result is compared with a `&str` through `String`'s `PartialEq<&str>`. In Example B, `values.into_iter()` on an array of `i32` yields `Item = i32` by value, and the annotation `let total: i32` selects `i32: Sum<i32>`. `larger(5, 5)` is again `T = i32`.",
            why="Each call picks one `T` from its arguments, and the only capability the body needs is `>=`, which `Ord` supplies. The iterator's associated `Item` type is fixed by the array, so only the sum's output type had to be stated.",
            wrong='Thinking `larger(3, String::from("x"))` should work because both types are `Ord` misses that the signature uses one `T` for both parameters; the call is E0308, mismatched types.',
            verify="Write `let _: () = larger(3, 8);` and read the E0308 message, which names the inferred type `i32`.",
        ),
        2: dict(
            code="""#[derive(PartialEq, Eq, PartialOrd, Ord)]
struct Version {
    major: u32,
    minor: u32,
}
let picked = larger(
    Version { major: 1, minor: 9 },
    Version { major: 2, minor: 0 },
);
assert_eq!((picked.major, picked.minor), (2, 0));
let patch = larger(
    Version { major: 1, minor: 2 },
    Version {
        major: 1,
        minor: 10,
    },
);
assert_eq!(patch.minor, 10);""",
            observe="Version 2.0 beats 1.9, and 1.10 beats 1.2.",
            explain='Deriving `Ord` compares fields in declaration order, so `major` decides first and `minor` breaks ties. That order happens to match version semantics, and comparing numbers avoids the text trap where `"1.10" < "1.9"`.',
            wrong="Declaring `minor` before `major` still compiles, but the derived order would then rank 1.9 above 2.0.",
            verify="Run the block, then swap the two field declarations and see the first assertion fail with `left: (1, 9)`.",
        ),
        4: dict(
            explain="The defect is a body that uses a capability the signature never promised, such as `fn size<T>(value: T) -> usize { value.len() }`. The compiler rejects it with E0599, no method named `len` found for type parameter `T`, because a caller could choose `T = i32`. A generic body may use only what its bounds guarantee.",
            why="Generic functions are checked once, against their bounds, not separately for each caller's type. That is why a missing bound is reported at the definition rather than at some later call.",
            wrong="Adding `T: Ord` because it is the bound used elsewhere in the lesson does not help: ordering says nothing about length. Take `&str` or `&[U]`, or define a trait that provides `len`.",
            verify="Compile the snippet and read E0599. Change the parameter to `value: &[i32]` and it compiles.",
        ),
        5: dict(
            code="""struct Entry {
    score: u32,
    name: &'static str,
}
impl PartialEq for Entry {
    fn eq(&self, other: &Self) -> bool {
        self.score == other.score
    }
}
impl Eq for Entry {}
impl PartialOrd for Entry {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}
impl Ord for Entry {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.score.cmp(&other.score)
    }
}
let first = Entry {
    score: 7,
    name: "first",
};
let second = Entry {
    score: 7,
    name: "second",
};
assert_eq!(larger(first, second).name, "first");
let low = Entry {
    score: 3,
    name: "low",
};
let high = Entry {
    score: 9,
    name: "high",
};
assert_eq!(larger(low, high).name, "high");
assert_eq!(larger(5, 5), 5);""",
            observe="On a tie the left argument wins, and a strictly larger right argument still wins.",
            explain="The policy is that ties return `left`, because the body tests `left >= right`. Equal integers cannot show which one came back, so the test uses a type whose ordering ignores `name`: two entries can be equal under `Ord` yet distinguishable.",
            wrong="Testing ties only with `larger(5, 5)` passes for both `>=` and `>`, so it cannot detect a change in the policy.",
            verify='Run the block, then change `>=` to `>` in `larger` and the first assertion fails with `left: "second"`.',
        ),
    },
    19: {
        1: dict(
            explain="`left` and `right` are valid from their `let` lines to the end of the block. The call `longer(&left, &right)` borrows both, and because the signature gives the result the same `'a`, the returned `&str` may be used only while both borrows are valid. Here it is used once, inside the `assert_eq!`, and its region ends there, so both owners stay free afterward.",
            why="A single lifetime on all three references asks the compiler for a region inside both inputs' regions. The caller decides where the result is used, and the borrow checker confirms that this use falls within that region.",
            wrong="Drawing the output region as the whole region of `right` because the longer string happens to be `right` ignores that the signature cannot know which input is returned.",
            verify='After the assertion add `let view = longer(&left, &right); drop(left); println!("{view}");` and read E0505, cannot move out of `left` because it is borrowed.',
        ),
        2: dict(
            code="""let first = String::from("pear");
let second = String::from("plum");
let chosen = longer(&first, &second);
assert!(std::ptr::eq(chosen, first.as_str()));
assert_eq!(longer("fig", "kiwi"), "kiwi");
assert_eq!(longer("", ""), "");""",
            observe="With two four-byte inputs the result is the very slice of `first`, and a strictly longer right input still wins.",
            explain="`longer` uses `>=`, so ties return `left`. Comparing text with `assert_eq!` cannot see that, since `pear` and `plum` differ but tie on length; `std::ptr::eq` compares the slice addresses and proves which owner the view borrows.",
            wrong='Testing with `longer("pear", "pear")` and `assert_eq!` passes whichever argument is returned, so it says nothing about the policy.',
            verify="Run the block, then change `>=` to `>` in `longer` and the `ptr::eq` assertion fails.",
        ),
        4: dict(
            explain="The defect is `fn label<'a>() -> &'a str { let local = String::from(\"draft\"); &local }`. It fails with E0515, cannot return reference to local variable `local`: the String is dropped when the function returns, so any reference to it would dangle. The annotation only names a relationship, and nothing the caller passes in owns the data.",
            why="Lifetimes are checked, not granted. A returned reference must borrow from something that outlives the call, which means an input or static data, and `local` is neither.",
            wrong="Writing `-> &'static str` instead changes the promise without changing the storage, so it fails with the same E0515.",
            verify="Compile the snippet and read E0515. Return `String` instead and it compiles, as Example B does.",
        ),
        5: dict(
            code="""assert_eq!(longer("", "x"), "x");
assert_eq!(longer("x", ""), "x");
let outer = String::from("outer value");
let kept = {
    let inner = String::from("in");
    longer(&outer, &inner).to_owned()
};
assert_eq!(kept, "outer value");""",
            observe="An empty input loses to any nonempty one on either side, and the owned copy survives after `inner` leaves scope.",
            explain="Returning `longer(&outer, &inner)` itself from the block is rejected with E0597, `inner` does not live long enough, even though the longer value is `outer`. The signature ties the result to both inputs, so the shorter-lived owner limits it; `to_owned` makes an independent String instead.",
            wrong="Assuming the borrow checker sees at run time that `outer` won and allows the view to escape treats lifetimes as a dynamic property. They are decided from the signature alone.",
            verify="Run the block. Remove `.to_owned()` and read E0597 naming `inner`.",
        ),
    },
    22: {
        1: dict(
            explain='`"bad"` fails `parse`, and `map_err(|_| InputError::Malformed)` turns that into `Malformed` before `?` returns. `"-1"` parses to `-1`, then the sign test returns `Err(InputError::Negative)`. `"3"` passes both stages and returns `Ok(3)`. Empty text and numbers outside the `i32` range also fail `parse`, so they become `Malformed` as well.',
            why="The variant is chosen at the stage that detects the problem: syntax failures in `map_err`, the domain rule in the explicit branch. The caller then decides from the variant, as Example A does with `matches!`.",
            wrong='Mapping `"-1"` to `Malformed` because it contains a sign confuses text shape with the domain rule, since `i32` parses negative numbers normally.',
            verify='Add `assert!(matches!(validated(""), Err(InputError::Malformed)));` to Example A and run it.',
        ),
        2: dict(
            code="""#[derive(Debug)]
enum QuantityError {
    Input(InputError),
    TooLarge { max: i32 },
}
impl From<InputError> for QuantityError {
    fn from(error: InputError) -> Self {
        Self::Input(error)
    }
}
fn bounded(text: &str, max: i32) -> Result<i32, QuantityError> {
    let value = validated(text)?;
    if value > max {
        return Err(QuantityError::TooLarge { max });
    }
    Ok(value)
}
assert_eq!(bounded("40", 50).unwrap(), 40);
assert!(matches!(
    bounded("51", 50),
    Err(QuantityError::TooLarge { max: 50 })
));
let negative = bounded("-1", 50);
assert!(matches!(
    negative,
    Err(QuantityError::Input(InputError::Negative))
));
let malformed = bounded("x", 50);
assert!(matches!(
    malformed,
    Err(QuantityError::Input(InputError::Malformed))
));""",
            observe="40 is accepted, 51 is TooLarge with the limit 50, and the negative and malformed cases keep their original InputError variants.",
            explain="The new category wraps the existing one rather than editing it, and `impl From<InputError>` lets `?` convert automatically. The limit is a value, not a constant baked into the message, so the caller can report it without parsing text.",
            wrong="Returning `Err(InputError::Negative)` for oversized values because it is the nearest existing variant compiles and shows a false message saying the quantity must be nonnegative.",
            verify="Run the block. Remove the `From` impl and the `?` line fails with E0277, `?` couldn't convert the error to `QuantityError`.",
        ),
        4: dict(
            explain='The defect is `if error.to_string().contains("nonnegative") { retry_with_absolute_value() }`. The branch depends on display text written for people, so rewording the message or translating it silently changes program behavior. Match the variant instead: `if let Err(InputError::Negative) = result`.',
            why="`Display` is presentation and the enum is the contract. Variants are checked by the compiler; a substring test still compiles after the message changes and just stops matching.",
            wrong="Comparing the whole string with `==` instead of `contains` is stricter but has the same dependency on wording.",
            verify="Change the `Negative` message to `quantity must be zero or more`: the string branch stops firing with no compiler error, while a `matches!` test still passes.",
        ),
        5: dict(
            code="""assert_eq!(validated("0").unwrap(), 0);
assert!(matches!(validated("abc"), Err(InputError::Malformed)));
assert!(matches!(validated(""), Err(InputError::Malformed)));
assert!(matches!(
    validated("2147483648"),
    Err(InputError::Malformed)
));
assert!(matches!(
    validated("-2147483648"),
    Err(InputError::Negative)
));
assert!(matches!(
    validated("-2147483649"),
    Err(InputError::Malformed)
));""",
            observe="Zero is accepted, letters and empty text are malformed, i32::MIN is negative, and values just outside the i32 range in either direction are malformed.",
            explain="Zero sits on the accepted side of `value < 0`. Out-of-range text never becomes a number, so it lands in `Malformed` rather than in a range category; a real importer might add one, as task 2 did for the upper limit.",
            wrong='Expecting `"-2147483649"` to be `Negative` assumes the sign is checked before the range. Parsing runs first and fails, so the domain check never sees it.',
            verify="Run the block, then change `value < 0` to `value <= 0` and the first assertion fails.",
        ),
    },
    25: {
        1: dict(
            explain="`file` owns the operating system handle; `drop(file)` flushes nothing extra but closes it, and a second `File::open` creates a new temporary handle that is dropped at the end of that statement. `path` is a `PathBuf` that owns only the name. Dropping `path` deletes nothing; the directory entry exists until `std::fs::remove_file(&path)` runs.",
            why="Handle lifetime and file existence are separate resources. Ownership closes handles automatically, but removing a name is a filesystem operation that only an explicit call (or a guard's `Drop`) performs.",
            wrong="Believing `drop(file)` removes the temporary file leaves a stray file in the temporary directory after every run.",
            verify="Comment out the `remove_file` line, run Example A, then check that the file still exists with `assert!(path.exists())`.",
        ),
        2: dict(
            code="""use std::io::Write;
let name = format!("rust-lesson-{}-lines.txt", std::process::id());
let path = std::env::temp_dir().join(name);
let mut file = std::fs::OpenOptions::new()
    .write(true)
    .create_new(true)
    .open(&path)?;
for line in ["pear,3", "fig,7"] {
    writeln!(file, "{line}")?;
}
drop(file);
let text = std::fs::read_to_string(&path);
std::fs::remove_file(&path)?;
let text = text?;
assert_eq!(text, "pear,3\\nfig,7\\n");
assert!(!text.contains('\\r'));
assert_eq!(text.lines().count(), 2);""",
            observe="The file holds exactly pear,3 and fig,7, each followed by a single LF byte, and the path is removed.",
            explain="The policy is one `\\n` after every line, including the last. `writeln!` writes `\\n` on every platform, never `\\r\\n`, so the bytes are the same on Linux and Windows. Reading is kept as a `Result` until after `remove_file`, so a read failure cannot skip the cleanup.",
            wrong='Joining with `lines.join("\\n")` writes no final newline, so appending a third line later glues it onto `fig,7`.',
            verify="Run the block, then switch `writeln!` to `write!` and the first assertion fails with `pear,3fig,7`.",
        ),
        4: dict(
            explain="The defect is `std::fs::read_to_string(\"data/report.txt\")` written on the assumption that it means the repository's `data` folder. A relative path is resolved against the process's current working directory, which is wherever the program was launched: a terminal's directory, an IDE setting, or the worker's scratch directory. Build paths from an explicit base such as a command-line argument or `std::env::temp_dir()`.",
            why="Neither the source file's location nor the project root is part of path resolution. Only the process working directory is, and the caller controls it.",
            wrong="Fixing it by hard-coding an absolute path from your own machine works only there and can point at another user's files elsewhere.",
            verify="Print `std::env::current_dir()?` in the pad and compare it with the folder you assumed.",
        ),
        5: dict(
            code="""use std::io::Read;
let name = format!("rust-lesson-{}-empty.bin", std::process::id());
let path = std::env::temp_dir().join(name);
let file = std::fs::OpenOptions::new()
    .write(true)
    .create_new(true)
    .open(&path)?;
drop(file);
let mut bytes = Vec::new();
let read = std::fs::File::open(&path).and_then(|mut f| f.read_to_end(&mut bytes));
std::fs::remove_file(&path)?;
assert_eq!(read?, 0);
assert_eq!(String::from_utf8(bytes)?, "");
assert!(String::from_utf8(vec![0x63, 0xc3]).is_err());
assert_eq!(String::from_utf8_lossy(&[0x63, 0xff]), "c\\u{fffd}");""",
            observe="An empty file reads zero bytes and decodes to empty text, a truncated two-byte sequence is rejected, and lossy decoding replaces the invalid byte with U+FFFD.",
            explain="Empty input is valid UTF-8, so it decodes cleanly. `0xc3` starts a two-byte character that never finishes, so strict decoding fails, while `from_utf8_lossy` succeeds only by changing the data. The read result is held until the path is removed, so a failed read does not leave the file behind.",
            wrong="Treating an empty file as an error, or using `from_utf8_lossy` everywhere to avoid errors, either rejects valid data or hides corruption.",
            verify="Run the block, then replace `vec![0x63, 0xc3]` with `vec![0x63, 0xc3, 0xa9]` and the rejection assertion fails because the bytes now spell `cé`.",
        ),
    },
    27: {
        1: dict(
            explain="In Example A the outer block owns `values`. The spawned closure only borrows it through `values.iter()`, and `std::thread::scope` guarantees the thread ends before the scope returns. `handle` is a `ScopedJoinHandle` owned by the scope closure, and `join()` consumes it to return the sum. In Example B each of `left` and `right` owns one handle, and each is consumed by its own `join`.",
            why="Joining takes the handle by value, so a result can be collected only once, and the scope's end is the point after which no borrow from the parent may still be in use.",
            wrong="Saying the thread owns `values` would require a `move` closure and would make `values.len()` after the scope fail with E0382.",
            verify="Add `move` before the closure in Example A and read E0382 on `values.len()`.",
        ),
        2: dict(
            code="""let values = [3, 1, 4, 1, 5];
let (left, right) = values.split_at(values.len() / 2);
assert_eq!((left.len(), right.len()), (2, 3));
let total = std::thread::scope(|scope| {
    let low = scope.spawn(|| left.iter().sum::<i32>());
    let high = scope.spawn(|| right.iter().sum::<i32>());
    low.join().expect("left half") + high.join().expect("right half")
});
assert_eq!(total, 14);
assert_eq!(total, values.iter().sum::<i32>());""",
            observe="With five values the halves hold two and three elements, and the threaded total matches the sequential sum, 14.",
            explain="`split_at` returns two non-overlapping borrowed slices, so no element is copied or counted twice. With an odd length, integer division puts the extra element in the right half, which the length assertion records.",
            wrong="Computing the halves as `&values[..mid]` and `&values[mid - 1..]` double-counts one element and still looks plausible on small inputs.",
            verify="Run the block, then change the second slice to start one element earlier and the sequential comparison fails.",
        ),
        4: dict(
            explain="The defect is `std::thread::spawn(move || write_report(rows));` with the returned `JoinHandle` discarded. An unscoped handle that is dropped detaches the thread: `main` can return and end the process before the report is written, and a panic in the worker is never observed. Keep the handle and call `join()`, or use `std::thread::scope`, which joins everything before returning.",
            why="`join` is the only point where completion and panic become visible to the parent. Without it, success is an assumption about timing, not a fact.",
            wrong="Adding `std::thread::sleep(Duration::from_millis(100))` before returning makes it pass on a fast machine and fail under load.",
            verify="Spawn a thread that sleeps 200 ms and then sets an `AtomicBool`, drop its handle, and check the flag immediately: it is still false.",
        ),
        5: dict(
            code="""let empty: [i32; 0] = [];
let (left, right) = empty.split_at(0);
let total = std::thread::scope(|scope| {
    let low = scope.spawn(|| left.iter().sum::<i32>());
    let high = scope.spawn(|| right.iter().sum::<i32>());
    low.join().expect("left half") + high.join().expect("right half")
});
assert_eq!(total, 0);
let previous = std::panic::take_hook();
std::panic::set_hook(Box::new(|_| {}));
let outcome = std::thread::scope(|scope| {
    let worker = scope.spawn(|| -> i32 { panic!("worker failed") });
    worker.join()
});
std::panic::set_hook(previous);
assert!(outcome.is_err());""",
            observe="Two empty partitions sum to 0, and the intentionally panicking worker is reported to the parent as Err from join.",
            explain="Summing an empty slice is 0, so empty partitions need no special case. A worker panic is caught at its `join`, which returns `Err` instead of a value; the parent then decides what that means. The panic hook is silenced only around the deliberate panic and restored afterward, so the test output stays clean.",
            wrong="Writing `worker.join().unwrap_or(0)` turns a crashed worker into a plausible zero, exactly the default success the lesson warns about.",
            verify="Run the block, then remove the `panic!` so the worker returns `1`, and the `is_err` assertion fails.",
        ),
    },
    28: {
        1: dict(
            explain="Shared ownership: one heap allocation holds the `Mutex<i32>`, and `Arc::clone` gives each of the four workers its own `Arc` handle to it, so the strong count is five while they run and drops back to one when the scope ends. Mutable access is a separate path: a worker may change the integer only through the `MutexGuard` returned by `lock()`, and only one guard exists at a time.",
            why="`Arc` answers who keeps the value alive, and `Mutex` answers who may change it now. Example A needs both answers, which is why the type is `Arc<Mutex<i32>>` and not either one alone.",
            wrong="Drawing each `Arc::clone` as a copy of the counter predicts four separate counts of 100. The final 400 shows that all clones point to the same protected integer.",
            verify="Print `Arc::strong_count(&count)` inside one worker and after the scope: the first is greater than 1, the second is 1.",
        ),
        2: dict(
            code="""use std::sync::{Arc, Mutex};
let workers = 5;
let per_worker = 100;
let count = Arc::new(Mutex::new(0));
std::thread::scope(|scope| {
    for _ in 0..workers {
        let count = Arc::clone(&count);
        scope.spawn(move || {
            for _ in 0..per_worker {
                *count.lock().unwrap() += 1;
            }
        });
    }
});
assert_eq!(*count.lock().unwrap(), workers * per_worker);
assert_eq!(Arc::strong_count(&count), 1);""",
            observe="Five workers of 100 increments each produce exactly 500, and only the original Arc remains afterward.",
            explain="The expected total is computed from the same two numbers that drive the loops, so adding a worker cannot leave a stale literal behind. Each increment happens under the lock as one read-modify-write step, which is why no update is lost.",
            wrong="Locking once to read, releasing, and locking again to write the incremented value can lose updates between the two locks, and the total falls below 500 on some runs.",
            verify="Run the block several times; the total is always 500. Change `workers` to 6 and the expectation follows to 600 without another edit.",
        ),
        4: dict(
            explain="The defect is `let from = Mutex::new(10); let to = Mutex::new(0);` with a transfer that does `*from.lock().unwrap() -= 3;` and then, in a separate statement, `*to.lock().unwrap() += 3;`. Between those two statements neither lock is held, so another thread can lock both and see a total of 7 instead of 10. Put the related values in one `Mutex<(i32, i32)>`, as Example B does, so the invariant has one synchronization boundary.",
            why="Each lock protects only its own value. The relationship `from + to == 10` spans both, so it needs a lock that covers both updates at once.",
            wrong="Holding both locks but acquiring them in opposite orders in two different transfer directions closes the gap and introduces a deadlock instead.",
            verify="In one thread, after the first update and before the second, lock both values and assert their sum: it is 7.",
        ),
        5: dict(
            code="""let total = std::sync::Mutex::new(0);
std::thread::scope(|scope| {
    for _ in 0..0 {
        scope.spawn(|| *total.lock().unwrap() += 1);
    }
});
assert_eq!(*total.lock().unwrap(), 0);
let previous = std::panic::take_hook();
std::panic::set_hook(Box::new(|_| {}));
let balances = std::sync::Mutex::new((10, 0));
let crashed = std::thread::scope(|scope| {
    scope
        .spawn(|| -> i32 {
            let mut guard = balances.lock().unwrap();
            guard.0 -= 3;
            panic!("crashed mid-transfer");
        })
        .join()
});
std::panic::set_hook(previous);
assert!(crashed.is_err());
assert!(balances.is_poisoned());
let recovered = match balances.lock() {
    Ok(guard) => *guard,
    Err(poisoned) => *poisoned.into_inner(),
};
assert_eq!(recovered, (7, 0));
assert_ne!(recovered.0 + recovered.1, 10);""",
            observe="Zero operations leave the total at 0. The worker that panics while holding the guard poisons the mutex, and the recovered value is (7, 0), a half-finished transfer.",
            explain="Zero workers is a legal workload, so the result must be the initial value, not an error. Poisoning is the signal that a panic happened inside the critical section; `into_inner` deliberately reads the data anyway, and the last assertion shows why that needs a policy: the invariant is broken.",
            wrong="Recovering with `lock().unwrap_or_else(|p| p.into_inner())` everywhere and carrying on treats (7, 0) as a valid state and silently loses three units.",
            verify="Run the block. Move `guard.0 -= 3;` after the panic (making it unreachable) and the recovered value becomes (10, 0), still poisoned but consistent.",
        ),
    },
    30: {
        1: dict(
            explain="Example A is ownership transfer: `move` puts `text` into the closure, the closure moves into the new thread, and `main` can no longer use `text`; the length comes back as the join result. Example B is about shared access: `Sync` means a `&String` may be used from several threads at once, and `Arc<Mutex<i32>>` is `Send`, so a handle can be given to another thread while the data stays shared.",
            why="`Send` is about moving a value to another thread, while `Sync` is about sharing references to it. A type can satisfy one without the other, so the two questions must be asked separately.",
            wrong="Treating `move` as making a copy for the thread predicts that `text` is still usable in `main`; using it after the spawn is E0382.",
            verify='Add `println!("{text}");` after the spawn in Example A and read E0382, borrow of moved value.',
        ),
        2: dict(
            code="""let readings = vec![4, 8, 15, 16];
let worker = std::thread::spawn(move || {
    let total: i32 = readings.iter().sum();
    (readings.len(), total)
});
assert_eq!(worker.join().unwrap(), (4, 43));""",
            observe="The worker reports four readings with total 43.",
            explain="`move` transfers the whole `Vec`, including its heap buffer, into the worker, which is valid because `Vec<i32>` is `Send`. The worker returns a small derived tuple, so the parent receives results without sharing the vector at all.",
            wrong="Dropping `move` makes the closure borrow `readings`, and `std::thread::spawn` rejects that with E0373 because the thread could outlive the vector.",
            verify="Run the block. Then add `readings.len()` after the spawn and read E0382.",
        ),
        4: dict(
            explain="The defect is `let shared = std::rc::Rc::new(5); std::thread::spawn(move || *shared + 1);`. rustc reports E0277, `Rc<i32>` cannot be sent between threads safely, because `Send` is not implemented for `Rc<i32>`. `Rc` updates its reference count with ordinary, non-atomic arithmetic, so two threads cloning or dropping it could corrupt the count. Use `Arc`, whose count is atomic.",
            why="The marker traits encode which operations are safe across threads, and the compiler derives them from a type's members. `Rc` is deliberately not `Send`, so the rejection is a correct proof failure, not a limitation to work around.",
            wrong="Wrapping the `Rc` in a struct with `unsafe impl Send` silences the error and reintroduces the data race the diagnostic was preventing.",
            verify="Compile the defect and read E0277. Replace `std::rc::Rc` with `std::sync::Arc` and it compiles and returns 6.",
        ),
        5: dict(
            code="""let rows = vec![String::from("a"), String::from("bc")];
let total = std::thread::scope(|scope| {
    let worker = scope.spawn(|| rows.iter().map(String::len).sum::<usize>());
    worker.join().unwrap()
});
assert_eq!(total, 3);
assert_eq!(rows.len(), 2);
let empty: Vec<String> = Vec::new();
let count = std::thread::scope(|scope| scope.spawn(|| empty.len()).join().unwrap());
assert_eq!(count, 0);""",
            observe="The scoped worker reads the borrowed rows and returns 3, the rows are still usable afterward, and an empty input gives 0.",
            explain="A scoped thread may borrow `rows` because the scope cannot return until the thread has finished, so the borrow cannot outlive its owner. `std::thread::spawn` requires a `'static` closure instead: the same borrowing closure is rejected with E0373, and the fix there is `move` plus ownership.",
            wrong="Assuming `'static` means the data must live for the whole program leads to leaking or using global data. It only means the closure holds no borrowed references that could expire.",
            verify="Run the block. Replace `scope.spawn` with `std::thread::spawn` in the first worker and read E0373, closure may outlive the current function.",
        ),
    },
    31: {
        1: dict(
            explain="`list` owns the outer `Node::More(2, ...)`. That node owns a `Box`, which owns the heap node `More(3, ...)`, whose `Box` owns the heap node `End`. Every node has exactly one owner, so the edges form a chain with no sharing. When `list` is dropped, each `Box` drops its node in turn from the head toward `End`.",
            why="`Box<Node>` has a fixed size, the size of one pointer, so `Node` has a finite size even though it is recursive. Unique ownership along the chain means cleanup needs no counting.",
            wrong="Drawing `Node::More(i32, Node)` without the `Box` describes an infinitely sized type; the compiler rejects it with E0072, recursive type has infinite size.",
            verify="Define `enum Bad { End, More(i32, Bad) }` and read E0072, which suggests inserting indirection such as `Box`.",
        ),
        2: dict(
            code="""let list = Node::More(
    1,
    Box::new(Node::More(2, Box::new(Node::More(3, Box::new(Node::End))))),
);
assert_eq!(list.total(), 6);
let extended = Node::More(10, Box::new(list));
assert_eq!(extended.total(), 16);""",
            observe="The three-node list totals 6, and prepending a node with 10 totals 16.",
            explain="`total` adds each value to the total of the rest, so a new node changes the sum by exactly its own value. Prepending moves the whole old list into a new `Box`; nothing is copied, and `list` is no longer usable afterward.",
            wrong="Predicting 10 for the extended list, as if the new head replaced the old one, forgets that `More(10, Box::new(list))` keeps the old nodes as its tail.",
            verify="Run the block. Add `list.total()` after `extended` is built and read E0382, use of moved value.",
        ),
        4: dict(
            explain="The defect is two nodes of type `Rc<RefCell<Peer>>` where each holds an `Rc` to the other. Dropping both local handles lowers each strong count from 2 to 1, never to 0, so neither destructor runs and both allocations leak. Make one direction `Weak`, as a child's back-reference to its parent in task 3 does, so the owning edges form a tree.",
            why="`Rc` frees its value when the strong count reaches zero, and a cycle of strong edges keeps every count at one or more. Safe Rust prevents use after free, but it does not promise freedom from leaks.",
            wrong="Calling `drop` on both handles explicitly does not help: it releases the same two local references that leaving scope would.",
            verify="Keep `let probe = Rc::downgrade(&first);`, drop both handles, and assert `probe.upgrade().is_some()`: the node is still alive.",
        ),
        5: dict(
            code="""assert_eq!(Node::End.total(), 0);
let single = Node::More(-4, Box::new(Node::End));
assert_eq!(single.total(), -4);
let weak = {
    let owner = std::rc::Rc::new(5);
    std::rc::Rc::downgrade(&owner)
};
assert!(weak.upgrade().is_none());
assert_eq!(weak.strong_count(), 0);
let never: std::rc::Weak<i32> = std::rc::Weak::new();
assert!(never.upgrade().is_none());""",
            observe="An empty list totals 0 and a single negative node totals -4. A weak reference whose owner left its block upgrades to None with strong count 0, as does a Weak that never pointed anywhere.",
            explain="`End` is the base case of the recursion, so the empty list needs no special handling. `upgrade` returns an `Option` precisely so that a dead target is an ordinary, checkable outcome rather than a dangling pointer.",
            wrong="Unwrapping `weak.upgrade()` on the assumption that the target is still alive turns a normal absence into a panic.",
            verify="Run the block. Move `owner` out of the inner block so it lives longer and the first `is_none` assertion fails.",
        ),
    },
    33: {
        1: dict(
            explain="`async { 7 }` creates a future value and runs none of its body. `Box::pin` gives it a stable address, which `poll` requires. The single `poll` call runs the body; because nothing inside waits, it finishes and returns `Poll::Ready(7)`, which is completion. In Example B, `pending()` returns `Poll::Pending` on every poll and never completes.",
            why="A future is a state machine that advances only when something polls it. Creation, each poll and completion are separate events, and only an executor (or this one-poll fixture) causes the middle one.",
            wrong="Thinking `async { 7 }` evaluates 7 at creation predicts side effects before any poll. Put a `println!` inside the block and nothing prints until the poll.",
            verify="Add `let mut flag = false; let mut probe = Box::pin(async { flag = true; });` and check that `flag` changes only after `probe.as_mut().poll(&mut context)`.",
        ),
        2: dict(
            code="""use std::future::Future;
use std::task::{Context, Poll, Waker};
let left = async { 3 };
let right = async { 4 };
let mut combined = Box::pin(async { left.await + right.await });
let mut context = Context::from_waker(Waker::noop());
assert_eq!(combined.as_mut().poll(&mut context), Poll::Ready(7));""",
            observe="One poll of the combined future returns Ready(7).",
            explain="`combined` owns `left` and `right` and awaits them one after the other. Both are immediately ready, so a single poll drives all three futures to completion. With a future that could return `Pending`, the same poll would stop at that `.await` and report `Pending`.",
            wrong="Expecting the two inner futures to run in parallel misreads `.await`: inside one async block they run sequentially, and neither runs at all until `combined` is polled.",
            verify="Run the block. Replace `right` with `std::future::pending::<i32>()` and the poll returns `Poll::Pending`.",
        ),
        4: dict(
            explain="The defect is calling an async function such as `save_report(rows);` without `.await` or a runtime. The call only builds a future, which is dropped at the semicolon without ever being polled, so no report is written. rustc warns `unused implementer of Future that must be used` and notes that futures do nothing unless you `.await` or poll them.",
            why="Rust futures are lazy: work happens only during `poll`. Without a consumer there is no poll, so the program silently skips the operation.",
            wrong="Binding the result, `let _pending = save_report(rows);`, removes the warning but still never polls it, so the report is never written.",
            verify="Compile `async fn save() {} fn main() { save(); }` and read the `unused_must_use` warning.",
        ),
        5: dict(
            code="""use std::future::Future;
use std::task::{Context, Poll, Waker};
struct Note<'a>(&'a std::cell::RefCell<Vec<&'static str>>);
impl Drop for Note<'_> {
    fn drop(&mut self) {
        self.0.borrow_mut().push("dropped");
    }
}
let mut context = Context::from_waker(Waker::noop());
let mut ready = Box::pin(async { 1 });
assert_eq!(ready.as_mut().poll(&mut context), Poll::Ready(1));
let mut waiting = Box::pin(std::future::pending::<i32>());
assert_eq!(waiting.as_mut().poll(&mut context), Poll::Pending);
let log = std::cell::RefCell::new(Vec::new());
let mut unfinished = Box::pin(async {
    let _note = Note(&log);
    log.borrow_mut().push("started");
    std::future::pending::<()>().await;
    log.borrow_mut().push("finished");
});
assert_eq!(unfinished.as_mut().poll(&mut context), Poll::Pending);
drop(unfinished);
assert_eq!(*log.borrow(), vec!["started", "dropped"]);""",
            observe="The ready future yields Ready(1), the pending one yields Pending, and the unfinished future logs started and then dropped, but never finished.",
            explain="Dropping a pending future cancels it at its current `.await`: the code after that point never runs, while values the body already created are dropped normally. The log shows both halves, which is why cancellation safety matters when a future has already performed part of its work.",
            wrong="Expecting `finished` in the log assumes a dropped future runs to the end in the background. Nothing polls it after `drop`, so its remaining code is discarded.",
            verify="Run the block. Remove `std::future::pending::<()>().await;` and the first poll returns `Ready(())`, with `finished` logged before `dropped`.",
        ),
    },
    34: {
        1: dict(
            explain="`std::slice::from_raw_parts(pointer, len)` requires that `pointer` is non-null and aligned for `i32`; that it is valid for reading `len * size_of::<i32>()` bytes inside one allocation; that those `len` values are initialized; that nothing mutates them while the returned slice is in use; that the total size is at most `isize::MAX`; and that the chosen lifetime does not outlive the owner. In Example A all of them follow from `values.as_ptr()` on a live array, `values.len()` as the exact length, and no writes before the assertion.",
            why="An `unsafe` block moves these checks from the compiler to the author. Writing each one down and tying it to a fact in the code is what turns `unsafe` from a hope into an argument.",
            wrong="Treating a null check as sufficient misses alignment, length, initialization, aliasing and lifetime. A non-null pointer into freed memory satisfies it and is still undefined behavior.",
            verify="Compare your list with the Safety section of the `std::slice::from_raw_parts` documentation and check that each item is answered by a phrase in Example A's SAFETY comment.",
        ),
        2: dict(
            code="""let values = [2_i32, 3, 4, 5];
let pointer = values.as_ptr();
let length = 2;
assert!(length <= values.len());
// SAFETY: pointer comes from this live initialized array, and length 2 stays within its 4 elements.
let view = unsafe { std::slice::from_raw_parts(pointer, length) };
assert_eq!(view, &[2, 3]);
assert_eq!(view, &values[..length]);""",
            observe="The two-element view reads 2 and 3, the same as the safe slice `&values[..2]`.",
            explain="Shortening the length keeps every precondition: the first two elements are inside the same live, initialized array. The `assert!` documents the bound the SAFETY comment relies on, and the comparison with the safe slice is the oracle.",
            wrong="Increasing the length beyond `values.len()` to read neighboring memory is undefined behavior even if a run happens to print plausible numbers.",
            verify="Run the block. Then change `length` to 5 and the `assert!` fails before the unsafe call can run.",
        ),
        4: dict(
            explain="The defect is `fn data() -> *const i32 { let values = vec![1, 2, 3]; values.as_ptr() }`. It compiles, because raw pointers carry no lifetime, but the `Vec` frees its buffer when the function returns, so any later `from_raw_parts` on that pointer reads freed memory. Return the `Vec` itself, or borrow from storage the caller owns.",
            why="Raw pointers opt out of borrow checking, so the compiler cannot connect the pointer to its owner. The safe version, `-> &[i32]` returning `&values[..]`, is rejected with E0515, which is exactly the error the raw pointer hid.",
            wrong="Checking `!pointer.is_null()` before using it does not help: a pointer to freed memory is usually still non-null.",
            verify="Change the return type to `&'static [i32]` with body `&values[..]` and read E0515, cannot return value referencing local variable `values`.",
        ),
        5: dict(
            code="""let empty: [u64; 0] = [];
let pointer = empty.as_ptr();
assert!(!pointer.is_null() && pointer.is_aligned());
// SAFETY: a zero-length slice needs only a non-null, aligned pointer, which as_ptr provides.
let view = unsafe { std::slice::from_raw_parts(pointer, 0) };
assert!(view.is_empty());
let dangling = std::ptr::NonNull::<u64>::dangling();
// SAFETY: NonNull::dangling is non-null and aligned, which is all a zero-length slice requires.
let also_empty = unsafe { std::slice::from_raw_parts(dangling.as_ptr(), 0) };
assert_eq!(also_empty.len(), 0);
let bytes = [0_u8; 16];
let start = bytes.as_ptr().cast::<u64>();
let next = bytes.as_ptr().wrapping_add(1).cast::<u64>();
assert!(!(start.is_aligned() && next.is_aligned()));""",
            observe="Both zero-length slices are empty and valid, and of two byte addresses one apart, at most one is aligned for u64.",
            explain="A zero-length slice reads no memory, but its pointer must still be non-null and aligned, which is why `NonNull::dangling` exists. Alignment is checked with `is_aligned` on the address alone, without reading through it: a `u64` needs an address that is a multiple of its alignment, and two adjacent byte addresses cannot both be multiples of 8.",
            wrong="Passing `std::ptr::null()` as the pointer of an empty slice, on the reasoning that nothing is read, is undefined behavior, and dereferencing a misaligned `*const u64` to see what happens is undefined behavior too.",
            verify="Run the block. For unaligned data, use `std::ptr::read_unaligned` or `u64::from_ne_bytes` on a copied `[u8; 8]` instead of a cast pointer.",
        ),
    },
    35: {
        1: dict(
            explain="`small` and `large` are both `String` handles: a pointer, a capacity and a length, which is 24 bytes on a 64-bit target, so `size_of_val` reports the same number for both. The text lives in separate heap buffers owned by each handle, about 1 byte for `small` and 1000 bytes for `large`.",
            why="`size_of_val` measures only the inline value. Heap data reached through a pointer is owned by the value but is not part of its inline size.",
            wrong="Concluding that the two strings use the same memory because the sizes match ignores the heap buffers entirely.",
            verify="Assert `std::mem::size_of::<String>() == 3 * std::mem::size_of::<usize>()` and compare `small.capacity()` with `large.capacity()`.",
        ),
        2: dict(
            code="""let mut exact: Vec<i32> = Vec::new();
exact.reserve_exact(10);
let mut loose: Vec<i32> = Vec::new();
loose.reserve(10);
assert_eq!((exact.len(), loose.len()), (0, 0));
assert!(exact.capacity() >= 10 && loose.capacity() >= 10);
exact.extend(0..10);
loose.extend(0..10);
assert_eq!(exact, loose);
let before = exact.capacity();
exact.reserve(0);
assert_eq!(exact.capacity(), before);""",
            observe="Both reserve calls leave the length at 0 while giving at least 10 slots of capacity; after the same ten pushes the two vectors are equal, and reserving 0 more changes nothing.",
            explain="`reserve` may round capacity up for future growth, and `reserve_exact` asks for no extra, but neither creates elements. Length counts initialized values, which is what equality and iteration see; capacity is only allocation.",
            wrong="Asserting `exact.capacity() == 10` relies on an allocator detail that the documentation does not promise; only `>= 10` is guaranteed.",
            verify="Run the block. Then add `assert_eq!(exact[0], 0);` right after `reserve_exact` and the index panics, because no element exists yet.",
        ),
        4: dict(
            explain="The defect is reporting `std::mem::size_of_val(&rows)` for `rows: Vec<String>` as the memory the rows retain. It is 24 bytes whether `rows` holds zero strings or a million, because it counts only the `Vec` handle. Retained memory also includes the buffer of `capacity * size_of::<String>()` bytes and each string's own heap capacity.",
            why="Nested owners each hold their own allocations behind pointers. An inline size can never see them, so an estimate must walk the structure or measure at the allocator.",
            wrong="Switching to `size_of_val(&rows[..])` counts the `String` handles in the buffer but still misses every string's text.",
            verify="Assert that `size_of_val` of a vector of 1000 long strings equals `size_of_val(&Vec::<String>::new())`, then sum `capacity()` over the strings to see the missing part.",
        ),
        5: dict(
            code="""fn checksum_fast(values: &[u32]) -> u64 {
    values.iter().map(|&value| u64::from(value)).sum()
}
fn checksum_oracle(values: &[u32]) -> u64 {
    let mut total = 0_u64;
    for value in values {
        total += u64::from(*value);
    }
    total
}
let empty: Vec<u32> = Vec::new();
let large = vec![u32::MAX; 100_000];
for input in [&empty[..], &[7][..], &large[..]] {
    assert_eq!(checksum_fast(input), checksum_oracle(input));
}
assert_eq!(checksum_fast(&empty), 0);
assert_eq!(checksum_fast(&large), 100_000 * u64::from(u32::MAX));""",
            observe="The empty, single-value and 100,000-value inputs agree between both implementations, with 0 for empty and 429,496,729,500,000 for the large input.",
            explain="The same oracle judges every input size, so a faster version cannot win by changing semantics. Widening to `u64` before adding keeps the large case exact; the large input is where a `u32` accumulator would overflow.",
            wrong="Testing only the large input for speed and the small input for correctness lets a version that overflows on large data pass both checks.",
            verify="Run the block. Change `checksum_fast` to `values.iter().sum::<u32>() as u64` and the large case panics with attempt to add with overflow.",
        ),
    },
    36: {
        1: dict(
            explain='The edition is a per-crate language setting in Cargo.toml, here `edition = "2024"`, and it decides rules such as the tail-expression drop order in Example A and the `Box<[T]>` iteration in Example B. The compiler version is the installed toolchain, for example rustc 1.99.1, which must be new enough to implement that edition but does not change its rules. Dependency versions are the crate releases Cargo selected and recorded in Cargo.lock; InventoryLab\'s lock lists only `inventory-lab 0.1.0` because it has no dependencies.',
            why="The three settings change independently and fail in different ways: an edition change can alter meaning, a toolchain upgrade usually only adds diagnostics or features, and a dependency change can alter behavior without any source edit. Recording each one separately is what makes a build reproducible.",
            wrong='Assuming that a newer rustc compiles code under the newest edition predicts that Example A would fail on an old manifest. A crate with `edition = "2021"` keeps 2021 rules on every newer compiler, which is exactly where Example A is rejected with E0597.',
            verify="Run `rustc --version` and `cargo --version`, read the `edition` line in Cargo.toml and the `[[package]]` entries in Cargo.lock: three separate facts from three separate places.",
        ),
        2: dict(
            explain="Copy `courses/rust/fixtures/InventoryLab` to an ignored workspace and run `cargo build --locked --offline` there. In the reference run, on rustc 1.99.1, Cargo printed `Compiling inventory-lab v0.1.0` and then `Finished dev profile`, and `cargo run --locked --offline` printed `apple=3;pear=6;rejected=1`. `--locked` makes Cargo fail rather than rewrite Cargo.lock, and `--offline` forbids network access, so a success shows that the checked-in graph was already complete.",
            why="A build that is allowed to update the lockfile can succeed with a different graph from the one reviewed. With both flags, success means the exact recorded graph compiled with no download.",
            wrong="Running a plain `cargo build` and committing whatever Cargo.lock it produces turns a verification step into an unreviewed dependency change.",
            verify="Run `git status` on the copied project after the build: Cargo.lock is unchanged, and only the ignored `target` directory is new.",
        ),
        3: dict(
            explain="`cargo test --locked --offline` on the unchanged copy runs three targets: the library and executable unit-test targets report `running 0 tests`, and `tests/contracts.rs` reports `4 passed`. Then rename the public function, `pub fn render` to `pub fn render_report`, and test again. The reference run failed to compile with E0432, `unresolved import inventory_lab::render`, in the integration test and E0425, `cannot find function render in crate inventory_lab`, in the executable. The tests and the binary are clients of the library's public API, so a renamed item breaks them before any assertion runs.",
            why="Integration tests compile against the crate exactly as an external user would, so they detect contract changes, not just wrong values. A rename is a breaking change and needs a major version or a compatibility shim such as a deprecated `render` that calls the new name.",
            wrong="Counting the two zero-test targets as passing evidence inflates the result; only the four integration tests check behavior.",
            verify="Restore the name and run the tests again: four pass. Add `#[deprecated] pub fn render(report: &Report) -> String { render_report(report) }` instead, and the tests compile again with a deprecation warning.",
        ),
        4: dict(
            explain='The defect is adding a dependency to Cargo.toml, for example `tinyjson = "2"`, and then running `cargo build --offline` in an environment where that crate was never downloaded. The reference run failed with `no matching package named tinyjson found` and the note that offline mode can cause surprising resolution failures. Offline mode can only resolve against crates already in the local cache, so the fix is a deliberate preparation step with network access (`cargo fetch`), a lockfile review, and only then the offline build.',
            why="`--offline` answers whether the build can run without the network, not whether the graph is complete. A missing crate is a preparation failure, not a code error, and no source edit will fix it.",
            wrong="Removing `--offline` inside the classroom or a locked-down build to make the error go away replaces a reviewed dependency step with whatever the network returns.",
            verify="Add a dependency that is not in the local cache and run `cargo build --offline`: the error names the package. Remove the line and the build succeeds again with an unchanged Cargo.lock.",
        ),
        5: dict(
            explain="From the copied project directory, run `cargo clean`, then `cargo build --locked --offline`. In the reference run `cargo clean` reported `Removed 158 files, 39.1MiB total`. Afterward the directory held only Cargo.lock, Cargo.toml, README.md, `src` and `tests`, and the clean build compiled `inventory-lab v0.1.0` again from source. `cargo clean` deletes the `target` directory of the package it runs in, so running it in the owned copy touches nothing else.",
            why="A clean build proves the output can be recreated from source plus the lockfile alone, without relying on stale artifacts.",
            wrong="Deleting `target` with `rm -rf` from a guessed path, or running `cargo clean` from a shared parent workspace, risks removing output or files you do not own.",
            verify="List the directory before and after `cargo clean`: only `target` disappears, and `cargo run --locked --offline` again prints `apple=3;pear=6;rejected=1`.",
        ),
    },
    37: {
        1: dict(
            explain="Example A's column has logical length 3 (`len()`), data type `Int32` (from `data_type()`, fixed by the concrete `Int32Array`), and null count 0. Example B's `labels` also has length 3 and null count 0, but its type is `Utf8`, which is variable width: `len()` counts rows, not bytes, so the row `\"é\"` counts as one entry while it stores two UTF-8 bytes.",
            why="Length, type and null count are the metadata every `Array` exposes through the trait, before any typed value access, so they are the first checks when a column is handed over.",
            wrong="Reading `null_count() == 0` as proof that all values are meaningful mixes validity with domain rules: a non-null 0 or an empty string is still present.",
            verify="Assert `values.data_type() == &arrow::datatypes::DataType::Int32` and `labels.data_type() == &arrow::datatypes::DataType::Utf8` next to the existing length assertions.",
        ),
        2: dict(
            code="""use arrow::array::{Array, Int32Array};
let values = Int32Array::from(vec![2, 4, 6, 8]);
assert_eq!(values.len(), 4);
let fourth: i32 = values.value(3);
assert_eq!(fourth, 8);
assert!(values.is_valid(3));
assert_eq!(values.values().iter().sum::<i32>(), 20);""",
            observe="The column has four rows; index 3 returns the plain i32 8, which is valid, and the four values sum to 20.",
            explain="`Int32Array::value` returns an `i32` directly because the concrete type is known, with no casting or `Option`. It does not check validity, which is why the `is_valid` assertion comes next; for a column with nulls, `iter()` returns `Option<i32>` instead.",
            wrong="Calling `values.value(4)` to reach the fourth value uses a one-based index and panics, because index 4 is past the end of a four-row array.",
            verify="Run the block. Then change `value(3)` to `value(4)` and read the out-of-bounds panic.",
        ),
        4: dict(
            explain="The defect is writing something like `use arrow::sql::query;` or expecting `SELECT name FROM batch` to run after linking Arrow. rustc rejects the import with E0432, unresolved import, because the arrow crate has no SQL module. Arrow supplies arrays, schemas, record batches and compute kernels; a SQL planner and executor such as DataFusion is a separate crate that would need its own deliberate dependency setup.",
            why="Arrow standardizes the in-memory columnar format. Query parsing, planning and optimization sit in a layer above it, so selection is written with kernels such as `filter` and `take`.",
            wrong="Assuming the classroom omitted a feature flag and that enabling `sql` would fix it sends the learner looking for an option that does not exist.",
            verify="Compile `use arrow::sql::query;` in the pad and read E0432. Then express the same selection with `arrow::compute::filter` as in chapter 40.",
        ),
        5: dict(
            code="""use arrow::array::{Array, Int32Array, StringArray};
let empty = Int32Array::from(Vec::<i32>::new());
assert_eq!((empty.len(), empty.null_count()), (0, 0));
assert!(empty.is_empty());
assert_eq!(empty.iter().count(), 0);
let labels = StringArray::from(vec!["é", "日本", "a"]);
assert_eq!(labels.len(), 3);
assert_eq!(labels.value(0), "é");
assert_eq!(
    (labels.value(0).len(), labels.value(0).chars().count()),
    (2, 1)
);
assert_eq!(
    (labels.value_length(1), labels.value(1).chars().count()),
    (6, 2)
);""",
            observe="The empty column has length 0, no nulls and nothing to iterate. The text column keeps é and 日本 intact; é is 2 bytes and 1 character, 日本 is 6 bytes and 2 characters.",
            explain="An empty array is a valid column with zero rows, not an error. For text, `value` returns a `&str` slice of UTF-8 bytes chosen by the offsets, so `value_length` and `str::len` count bytes while `chars().count()` counts characters.",
            wrong="Using `value_length` as a character count reports 6 for 日本, which breaks a length limit stated in characters.",
            verify="Run the block. Add `empty.value(0);` and the access panics, because an empty array has no index 0.",
        ),
    },
    38: {
        1: dict(
            explain='In Example A, position 0 is a valid zero: present, known and equal to 0. Position 1 is null, so its validity bit is unset and no value is known. In Example B, position 0 is NaN: valid and present, but its value is the floating-point result "not a number". Position 1 is null again, and position 2 is the only finite value. So zero is data, null is missing data, and NaN is present data outside the finite numbers.',
            why="Validity and floating-point classification are separate layers: the null bitmap says whether a slot holds data, and `is_nan` and `is_finite` describe the value in a valid slot. Each needs its own policy.",
            wrong="Treating NaN as missing because both look empty in a report gives `null_count() == 2` in your head while Arrow reports 1, and a mean that drops NaN silently hides a failed calculation.",
            verify="Assert `values.is_valid(0) && values.value(0).is_nan()` and `values.is_null(1)` on Example B: one present NaN, one null.",
        ),
        2: dict(
            code="""use arrow::array::{Array, Float64Array};
let values = Float64Array::from(vec![Some(f64::NAN), None, Some(2.0), Some(f64::INFINITY)]);
let present: Vec<f64> = values.iter().flatten().collect();
assert_eq!(values.null_count(), 1);
assert_eq!(present.len(), 3);
assert_eq!(present.iter().filter(|value| value.is_finite()).count(), 1);
assert_eq!(
    present.iter().filter(|value| value.is_infinite()).count(),
    1
);
assert_eq!(present.iter().filter(|value| value.is_nan()).count(), 1);""",
            observe="The column now holds one null and three present values: one finite, one infinite and one NaN.",
            explain="Infinity is a present, non-null value, so validity is unchanged and only the finite-value count needs a new category. `is_finite` excludes both NaN and the infinities, which is why the finite count stays at 1 when a valid value is added.",
            wrong="Counting finite values as `len() - null_count()` gives 3 and treats NaN and infinity as usable measurements.",
            verify="Run the block. Replace infinity with `Some(5.0)` and the finite count becomes 2 while the null count stays 1.",
        ),
        4: dict(
            explain="The defect is summing the physical buffer, `values.values().iter().sum::<i32>()`, which also adds whatever is stored in null slots. With `Int32Array::new(vec![5, 99, 4].into(), Some(NullBuffer::from(vec![true, false, true])))` that sum is 108, while the valid values sum to 9. Apply validity first: `values.iter().flatten().sum::<i32>()` or `arrow::compute::sum(&values)`, which returns `Some(9)`.",
            why="Arrow promises nothing about the physical contents of a null slot; only the validity bitmap says which slots hold data. Any aggregate that reads `values()` directly must apply that bitmap itself.",
            wrong="Testing with `Int32Array::from(vec![Some(5), None, Some(4)])` happens to store 0 in the null slot, so the buggy sum looks correct and the defect survives.",
            verify="Build the array with the explicit 99 under the null and compare the two sums: 108 against 9.",
        ),
        5: dict(
            code="""use arrow::array::{Array, Float64Array};
fn counts(values: &Float64Array) -> (usize, usize, usize) {
    let finite = values
        .iter()
        .flatten()
        .filter(|value| value.is_finite())
        .count();
    (
        values.len() - values.null_count(),
        values.null_count(),
        finite,
    )
}
let all_null = Float64Array::from(vec![None, None, None]);
let empty = Float64Array::from(Vec::<f64>::new());
let no_null = Float64Array::from(vec![1.0, f64::NAN, -3.5]);
assert_eq!(counts(&all_null), (0, 3, 0));
assert_eq!(counts(&empty), (0, 0, 0));
assert_eq!(counts(&no_null), (3, 0, 2));
assert!(no_null.nulls().is_none());
assert_eq!(arrow::compute::sum(&all_null), None);""",
            observe="All-null gives (0, 3, 0), empty gives (0, 0, 0) and the no-null column gives (3, 0, 2); it carries no null buffer at all, and the sum of an all-null column is None.",
            explain="All-null and empty both have zero valid values, but only the null count tells them apart: three missing rows are not zero rows. A column without nulls may omit the validity buffer entirely, so code must not assume one exists. `sum` returns `None` when there are no valid values, rather than an invented 0.",
            wrong="Reporting the all-null sum as 0.0 claims a measurement that no row provided.",
            verify="Run the block. Replace one `None` with `Some(0.0)` and the all-null case becomes (1, 2, 1) with a sum of Some(0.0).",
        ),
    },
    39: {
        1: dict(
            explain="The row grain of Example A's batch is one product line: each row pairs a `name` with its `quantity`, and there are two rows, pear with 2 and apple with 3. The schema has two fields in order, `name` of type `Utf8` and `quantity` of type `Int32`, both non-nullable. Column 0 is therefore always the names, which is what the downcast to `StringArray` relies on.",
            why="The schema is the contract that gives each position a name, a type and a nullability rule. Without it the two arrays are just a list of columns with no meaning attached.",
            wrong="Calling this batch the inventory reads more into it than it says: it is one two-row chunk, and nothing in it proves that names are unique or that there are no other batches.",
            verify="Print `batch.schema()` and check the field names, types and `nullable: false` against your description.",
        ),
        2: dict(
            code="""use arrow::array::{Array, ArrayRef, Float64Array, Int32Array, StringArray};
use arrow::datatypes::{DataType, Field, Schema};
use arrow::record_batch::RecordBatch;
use std::sync::Arc;
let schema = Arc::new(Schema::new(vec![
    Field::new("name", DataType::Utf8, false),
    Field::new("quantity", DataType::Int32, false),
    Field::new("price", DataType::Float64, true),
]));
let columns: Vec<ArrayRef> = vec![
    Arc::new(StringArray::from(vec!["pear", "apple"])),
    Arc::new(Int32Array::from(vec![2, 3])),
    Arc::new(Float64Array::from(vec![Some(1.25), None])),
];
let batch = RecordBatch::try_new(schema, columns)?;
assert_eq!((batch.num_rows(), batch.num_columns()), (2, 3));
assert!(batch.schema().field(2).is_nullable());
assert_eq!(batch.column(2).null_count(), 1);""",
            observe="The batch has two rows and three columns, the price field is nullable, and its column holds one null.",
            explain="The new array has the same two rows, so `try_new` accepts it, and the nullable field allows apple's unknown price to be stored as a null instead of a made-up 0.0.",
            wrong="Declaring `price` as non-nullable while the array contains a null fails `try_new` with an error that the column is declared non-nullable but contains a null.",
            verify="Run the block. Change the price field's flag to `false` and `try_new` returns that error.",
        ),
        4: dict(
            explain="The defect is reordering the `columns` vector, for example to quantity first and name second, while the schema still lists `name` then `quantity`. When the types differ, `try_new` returns an error that column types must match the schema, expected Utf8 but found Int32 at column index 0. When the types match, such as two `Int32` fields `quantity` and `price`, the swap is accepted and every row carries quantities under the price label. Build each column next to its field, or use `RecordBatch::try_from_iter` with explicit name and array pairs.",
            why="A batch binds columns to fields by position only. Arrow can catch a type mismatch, but it cannot know that two same-typed arrays have been swapped.",
            wrong="Relying on `try_new` returning `Ok` as proof that the columns are in the right order misses exactly the same-type swap.",
            verify="Swap two `Int32` columns under fields `quantity` and `price`, build the batch, and read the column called `price`: it holds the quantities.",
        ),
        5: dict(
            code="""use arrow::array::{ArrayRef, Int32Array, StringArray};
use arrow::datatypes::{DataType, Field, Schema};
use arrow::record_batch::RecordBatch;
use std::sync::Arc;
let schema = Arc::new(Schema::new(vec![
    Field::new("name", DataType::Utf8, false),
    Field::new("quantity", DataType::Int32, false),
]));
let wrong_type: Vec<ArrayRef> = vec![
    Arc::new(StringArray::from(vec!["pear"])),
    Arc::new(StringArray::from(vec!["2"])),
];
assert!(RecordBatch::try_new(schema.clone(), wrong_type).is_err());
let wrong_length: Vec<ArrayRef> = vec![
    Arc::new(StringArray::from(vec!["pear", "fig"])),
    Arc::new(Int32Array::from(vec![2])),
];
assert!(RecordBatch::try_new(schema.clone(), wrong_length).is_err());
let no_rows: Vec<ArrayRef> = vec![
    Arc::new(StringArray::from(Vec::<&str>::new())),
    Arc::new(Int32Array::from(Vec::<i32>::new())),
];
let empty = RecordBatch::try_new(schema.clone(), no_rows)?;
assert_eq!((empty.num_rows(), empty.num_columns()), (0, 2));
assert_eq!(empty.schema(), schema);""",
            observe="A text array under the Int32 field and a one-row column beside a two-row column are both rejected; the zero-row batch is accepted and keeps both columns and the full schema.",
            explain="Type and length checks are the structural invariants `try_new` enforces, so both broken inputs return errors instead of a coerced or truncated batch. Zero rows breaks neither invariant, and the schema still describes what a nonempty batch would contain.",
            wrong="Treating the zero-row batch as an error, or skipping its schema, loses the column definitions a later empty result still needs.",
            verify="Run the block. Print the two errors with `{:?}` to see the type and length messages separately.",
        ),
    },
    40: {
        1: dict(
            explain="`filter` returns one output row for each true mask position, in input order, so Example A produces 2 rows, 2 then 6. `take` returns one output row for each index, in index order, so Example B produces 3 rows, 6, 2, 6. Filter can only keep or drop rows; take can reorder and repeat them.",
            why="The output row count is the number of trues for `filter` and the number of indices for `take`. That rule predicts both results before running anything.",
            wrong="Expecting `take` to deduplicate indices or to keep input order predicts [2, 6] for Example B and misses the repeated row that can double-count an aggregate.",
            verify="Assert `result.len()` in each example: 2 for filter, 3 for take.",
        ),
        2: dict(
            code="""use arrow::array::{Array, BooleanArray, Int32Array};
let values = Int32Array::from(vec![2, 4, 6]);
let mask = BooleanArray::from(vec![true, true, false]);
let expected: Vec<i32> = values
    .values()
    .iter()
    .zip([true, true, false])
    .filter(|(_, keep)| *keep)
    .map(|(value, _)| *value)
    .collect();
let result = arrow::compute::filter(&values, &mask)?;
let typed = result.as_any().downcast_ref::<Int32Array>().unwrap();
assert_eq!(typed.values().to_vec(), expected);
assert_eq!(expected, vec![2, 4]);""",
            observe="With the last position switched to false, the kernel keeps 2 and 4, matching the result derived with a plain iterator.",
            explain="The independent derivation zips the values with the same decisions and keeps the true positions, so it shares no code with the kernel. The `unwrap` on the downcast is justified here because `filter` on an `Int32Array` returns an array of the same type.",
            wrong="Changing only the expected vector and not the mask makes the test check your edit, not the kernel.",
            verify="Run the block. Set the mask to all false and both the kernel and the derivation produce an empty result.",
        ),
        4: dict(
            explain="The defect is `let names = filter(&names, &mask)?;` followed by building a batch from the filtered names and the original, unfiltered `quantities`. If the lengths differ, `RecordBatch::try_new` fails with an error that all columns in a record batch must have the same length. If a later step pads or trims to make them equal, every row pairs a name with another row's quantity. Filter the whole batch with `arrow::compute::filter_record_batch(&batch, &mask)`, as in task 3.",
            why="A row is the set of values at one position across all columns. Selection is a row decision, so it must apply the same mask to every column at once.",
            wrong="Filtering each column separately with the same mask works, but it is easy to miss a column when the schema grows; the batch-level kernel cannot miss one.",
            verify="Build a batch from one filtered and one unfiltered column and read the length error; then use `filter_record_batch` and assert that every column has `num_rows()` values.",
        ),
        5: dict(
            code="""use arrow::array::{Array, BooleanArray, Int32Array, UInt32Array};
use arrow::compute::TakeOptions;
let values = Int32Array::from(vec![2, 4, 6]);
let none = arrow::compute::filter(&values, &BooleanArray::from(vec![false; 3]))?;
assert_eq!((none.len(), none.data_type()), (0, values.data_type()));
let all = arrow::compute::filter(&values, &BooleanArray::from(vec![true; 3]))?;
assert_eq!(all.as_any().downcast_ref::<Int32Array>().unwrap(), &values);
let checked = TakeOptions { check_bounds: true };
let bad = UInt32Array::from(vec![0, 5]);
assert!(arrow::compute::take(&values, &bad, Some(checked.clone())).is_err());
let fine = UInt32Array::from(vec![1]);
let taken = arrow::compute::take(&values, &fine, Some(checked))?;
assert_eq!(
    taken
        .as_any()
        .downcast_ref::<Int32Array>()
        .unwrap()
        .value(0),
    4
);""",
            observe="An all-false mask gives an empty Int32 column, an all-true mask returns a copy equal to the input, and a checked take with index 5 returns an error while index 1 returns 4.",
            explain="Empty selection is a valid result with the same type, not a failure. With `check_bounds: true`, `take` validates every index and reports an out-of-range one as an error that the caller can handle, instead of relying on the input being correct.",
            wrong="Calling `take` with `None` options on indices from an untrusted source assumes they were already validated, so an out-of-range index is no longer reported as a handled error.",
            verify="Run the block. Print the error from the bad take with `{:?}`; it names index 5 and the three available entries.",
        ),
    },
    41: {
        1: dict(
            explain="Example A has all three states. Row 2 is a parent null: `append(false)` marks the whole list missing, so `is_null(2)` is true. Row 1 is an empty list: it is valid, with `value_length(1) == 0`. Row 0 is a valid list of length 2 whose second child is null: the list is present, and the child array has its own validity bit unset for that element.",
            why="A list column has two validity layers, one for each list row and one in the child array for each element. Each state answers a different question: is the list known, does it have elements, and is a given element known.",
            wrong="Reading `value_length(2) == 0` as an empty list misses that row 2 is null; the length of a null row carries no meaning.",
            verify="Assert `lists.values().null_count() == 1` and `lists.null_count() == 1`: one child null and one parent null, counted separately.",
        ),
        2: dict(
            code="""use arrow::array::{Array, AsArray, Int32Builder, ListBuilder};
use arrow::datatypes::Int32Type;
let mut builder = ListBuilder::new(Int32Builder::new());
builder.values().append_value(2);
builder.values().append_null();
builder.append(true);
builder.append(true);
builder.append(false);
builder.values().append_value(7);
builder.values().append_value(9);
builder.append(true);
let lists = builder.finish();
assert_eq!(lists.len(), 4);
assert!(lists.is_valid(3));
assert_eq!(lists.value_length(3), 2);
let added = lists.value(3);
let children = added.as_primitive::<Int32Type>();
assert_eq!(children.null_count(), 0);
assert_eq!(children.values().to_vec(), vec![7, 9]);""",
            observe="The column now has four rows; row 3 is valid, holds two children, and those children are 7 and 9 with no nulls.",
            explain="Child values go into the shared child builder first, and `append(true)` closes them into the next list row. `value(3)` returns that row's children as their own array, so the new row is checked independently of the null child in row 0.",
            wrong="Calling `append(true)` before appending 7 and 9 closes an empty row 3 and gives the next row the two children, so `value_length(3)` is 0.",
            verify="Run the block. Move `builder.append(true);` above the two `append_value` calls and the row-3 assertions fail.",
        ),
        4: dict(
            explain="The defect is a missing-data check written as `lists.value_length(i) == 0`, or as a count of rows with no elements reported as missing. In Example A it flags both row 1, which is a known, empty list, and row 2, which is null. Check `lists.is_null(i)` for missing rows and `value_length(i) == 0` only on valid rows.",
            why="Empty and missing mean different things: a customer with no orders is not a customer whose orders are unknown. Arrow keeps them apart through the validity bitmap, and the code has to read it.",
            wrong="Replacing nulls with empty lists before the count makes the two cases agree by erasing the information that distinguished them.",
            verify="Count `(0..lists.len()).filter(|&i| lists.is_null(i))` and compare it with the zero-length count on Example A: 1 null against 2 rows of length zero.",
        ),
        5: dict(
            code="""use arrow::array::{Array, StringArray};
let values = StringArray::from(vec![Some("first"), None, Some("middle"), Some("last")]);
let nothing = values.slice(2, 0);
assert_eq!((nothing.len(), nothing.null_count()), (0, 0));
let tail = values.slice(1, 3);
let typed = tail.as_any().downcast_ref::<StringArray>().unwrap();
assert_eq!(typed.len(), 3);
assert!(typed.is_null(0));
assert_eq!(typed.value(1), "middle");
assert_eq!(
    typed.iter().collect::<Vec<_>>(),
    vec![None, Some("middle"), Some("last")]
);
let end = values.slice(values.len(), 0);
assert!(end.is_empty());""",
            observe="A zero-length slice is empty with no nulls. The slice starting at source offset 1 reads the null at its index 0 and middle at its index 1, and a zero-length slice at the very end is also valid.",
            explain="Slicing changes where index 0 starts for both values and validity, so the null that was at source position 1 is at slice position 0. A zero-length slice is legal anywhere up to `len()` and contains nothing.",
            wrong="Indexing the slice with source positions, `typed.value(2)` for middle, reads last instead.",
            verify="Run the block. Then try `values.slice(3, 2)`, which runs past the end, and it panics because a slice must stay within the array.",
        ),
    },
    42: {
        1: dict(
            explain="`StreamWriter::try_new` writes the schema message first, which tells a reader the field `quantity` and its `Int32` type. `writer.write(&batch)` appends one record batch message holding the two values. `writer.finish()` appends the end-of-stream marker. On the reading side, `StreamReader::try_new` reads and checks the schema, the first `next()` returns the batch, and the second `next()` returns `None` because the stream ended.",
            why="The stream is framed as one schema, then zero or more batches, then an end marker. Every operation in Example A corresponds to exactly one of those parts.",
            wrong="Thinking `try_new` on the writer writes nothing until the first batch predicts that a stream with no batches is empty bytes. Task 5 shows the schema is still there.",
            verify="Print `bytes.len()` after `try_new`, after `write` and after `finish`: the buffer grows at each step.",
        ),
        2: dict(
            code="""use arrow::array::{ArrayRef, Int32Array};
use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
use arrow::record_batch::RecordBatch;
use std::sync::Arc;
let first = RecordBatch::try_from_iter(vec![(
    "quantity",
    Arc::new(Int32Array::from(vec![2, 3])) as ArrayRef,
)])?;
let second = RecordBatch::try_from_iter(vec![(
    "quantity",
    Arc::new(Int32Array::from(vec![5])) as ArrayRef,
)])?;
assert_eq!(first.schema(), second.schema());
let mut bytes = Vec::new();
{
    let mut writer = StreamWriter::try_new(&mut bytes, &first.schema())?;
    writer.write(&first)?;
    writer.write(&second)?;
    writer.finish()?;
}
let reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
let mut batches = 0;
let mut rows = 0;
for batch in reader {
    let batch = batch?;
    batches += 1;
    rows += batch.num_rows();
}
assert_eq!((batches, rows), (2, 3));""",
            observe="The reader yields two batches holding three rows in total.",
            explain="One schema message is followed by two batch messages, so the reader reports each batch separately and does not merge them. The `?` on every yielded item means a damaged message stops the count instead of being skipped.",
            wrong="Counting rows from only the first `next()` reports 2 and treats one batch as the whole stream.",
            verify="Run the block. Remove `writer.write(&second)?;` and the result becomes (1, 2).",
        ),
        4: dict(
            explain="Two related defects. First, using `bytes` while the writer still borrows it, for example passing `bytes.clone()` to a reader before the writer's block ends, is rejected with E0502, because the writer holds a mutable borrow. Second, dropping the writer without `finish()`: in the reference run the reader then returned the one batch and `None`, exactly like a complete stream, so the missing end marker went unnoticed. Cutting 10 bytes off the stream instead made the reader return an error, failed to fill whole buffer, and code that iterates with `.flatten()` or `filter_map(Result::ok)` silently drops that error and reports a short result.",
            why="The reader can only judge the bytes it receives. Calling `finish()` is the writer's statement that the stream is complete, and handling every `Result` from the reader is the only way a truncated message becomes visible.",
            wrong="Assuming that a successful readback proves the writer called `finish()` is wrong here: the unfinished stream read back the same batch.",
            verify="Write one batch without `finish()`, truncate the last 10 bytes, and iterate with `?`: the reader returns the I/O error instead of a silent short count.",
        ),
        5: dict(
            code="""use arrow::array::{ArrayRef, Int32Array};
use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
use arrow::record_batch::RecordBatch;
use std::io::Cursor;
use std::sync::Arc;
assert!(StreamReader::try_new(Cursor::new(Vec::<u8>::new()), None).is_err());
assert!(StreamReader::try_new(Cursor::new(vec![0xFF_u8; 8]), None).is_err());
let template = RecordBatch::try_from_iter(vec![(
    "quantity",
    Arc::new(Int32Array::from(vec![1])) as ArrayRef,
)])?;
let schema = template.schema();
let mut bytes = Vec::new();
{
    let mut writer = StreamWriter::try_new(&mut bytes, &schema)?;
    writer.write(&template.slice(0, 0))?;
    writer.finish()?;
}
let mut reader = StreamReader::try_new(Cursor::new(bytes), None)?;
assert_eq!(reader.schema(), schema);
let empty = reader.next().unwrap()?;
assert_eq!(empty.num_rows(), 0);
assert!(reader.next().is_none());""",
            observe="Empty bytes and eight bytes of 0xFF are both rejected, while a stream with a valid schema and one zero-row batch reads back that schema, one empty batch and then the end.",
            explain='Malformed framing fails at `try_new`, before any batch is produced. A zero-row batch is valid data: the stream still carries the schema, so a consumer can tell "no rows" from "no stream".',
            wrong="Treating the empty-batch stream as an error, or treating the malformed bytes as zero rows, erases the difference between a valid empty result and a broken input.",
            verify="Run the block. Remove the `writer.write` line and the reader yields no batch at all, with the schema still intact.",
        ),
    },
    43: {
        1: dict(
            explain="The CSV reader in Example A expects comma-separated text with one header line, enabled by `with_header(true)`, and then one record per line with exactly the declared fields, `name` as `Utf8` and `quantity` as `Int32`. The JSON reader in Example B expects newline-delimited JSON: one complete object per line, with keys matched to field names, here a nullable `quantity`. Both take the schema from you instead of guessing it, and both return batches of at most 8 rows.",
            why="Framing decides how bytes split into records and fields, and the schema decides how each field is decoded. Stating both makes a type or format surprise an error, not a silent change.",
            wrong='Passing a JSON array such as `[{"quantity":2}]` to the newline-delimited reader assumes the two JSON formats are interchangeable; it expects separate objects, not one enclosing array.',
            verify="Remove `with_header(true)` from Example A and the header line is parsed as data, failing to decode `quantity` as an `Int32`.",
        ),
        2: dict(
            code="""use arrow::array::{Array, AsArray};
use arrow::datatypes::{DataType, Field, Schema};
use std::sync::Arc;
let schema = Arc::new(Schema::new(vec![
    Field::new("name", DataType::Utf8, false),
    Field::new("quantity", DataType::Int32, false),
]));
let input = b"name,quantity\\n\\"pear, ripe\\",2\\napple,3\\n";
let mut reader = arrow::csv::ReaderBuilder::new(schema)
    .with_header(true)
    .build(std::io::Cursor::new(&input[..]))?;
let batch = reader.next().unwrap()?;
let names = batch.column(0).as_string::<i32>();
assert_eq!(batch.num_rows(), 2);
assert_eq!(names.value(0), "pear, ripe");
assert_eq!(names.len(), 2);""",
            observe="The quoted field becomes the single value pear, ripe, and the batch still has two rows of two columns.",
            explain="The CSV parser treats a comma inside double quotes as part of the value and removes the quotes, so the row keeps exactly two fields. That rule is part of the CSV format, which is why a real parser is needed here.",
            wrong="Expecting three fields from the first record counts every comma, as a plain split would; the parser would instead report an error if a row truly had an extra field.",
            verify="Run the block. Remove the quotes around `pear, ripe` and the reader returns an error for the extra field.",
        ),
        4: dict(
            explain='The defect is reusing InventoryLab\'s `line.split_once(\',\')` on general CSV. For the record `"pear, ripe",2` it returns the name `"pear` and the quantity ` ripe",2`, which fails to parse, so a valid row is counted as rejected. It also keeps quotes in names, cannot handle a newline inside a quoted value and ignores the header. Use `arrow::csv::ReaderBuilder` with an explicit schema, as in Example A and task 2.',
            why="InventoryLab documents its format as a deliberately simple two-field fixture, not quoted CSV. Moving that parser to a different input format changes its contract without changing its code.",
            wrong="Switching to `rsplit_once(',')` happens to fix this one row but still mishandles quotes in the last field and escaped quotes.",
            verify='Evaluate `"\\"pear, ripe\\",2".split_once(\',\')` and compare it with the task 2 result: the split gives two broken pieces, the parser gives `pear, ripe` and 2.',
        ),
        5: dict(
            code="""use arrow::array::Array;
use arrow::datatypes::{DataType, Field, Schema};
use std::io::Cursor;
use std::sync::Arc;
let schema = Arc::new(Schema::new(vec![
    Field::new("name", DataType::Utf8, false),
    Field::new("quantity", DataType::Int32, true),
]));
let bad = b"name,quantity\\npear,2\\nfig,x\\n";
let mut reader = arrow::csv::ReaderBuilder::new(schema.clone())
    .with_header(true)
    .build(Cursor::new(&bad[..]))?;
assert!(reader.next().unwrap().is_err());
let input = b"name,quantity\\npear,2\\nfig,\\nkiwi,4\\n";
let reader = arrow::csv::ReaderBuilder::new(schema)
    .with_header(true)
    .with_batch_size(2)
    .build(Cursor::new(&input[..]))?;
let mut sizes = Vec::new();
let mut nulls = 0;
for batch in reader {
    let batch = batch?;
    sizes.push(batch.num_rows());
    nulls += batch.column(1).null_count();
}
assert_eq!(sizes, vec![2, 1]);
assert_eq!(nulls, 1);""",
            observe="The text x in an Int32 column makes the reader return an error. The three valid rows arrive as batches of 2 and 1, with the empty quantity for fig read as one null.",
            explain="A parse error is reported for the batch containing it, so the caller must decide what happens to the whole input. An empty field in a nullable column is an explicit null, not 0, and a batch size of 2 makes the third record start a second batch.",
            wrong="Reading only the first batch and reporting 2 rows treats the first chunk as the whole file.",
            verify="Run the block. Print the error with `{:?}`; it names the value x, the type Int32 and line 2.",
        ),
    },
    44: {
        1: dict(
            explain="In Example A the stored coefficient is the integer 125. The scale 2, from the type `Decimal128(10, 2)`, says the decimal point sits two digits from the right. The represented amount is therefore 125 times 10 to the power of minus 2, which is 1.25. Precision 10 limits the coefficient to at most 10 digits.",
            why="Decimal types store exact integers and carry the scale in the type, so the same coefficient means a different amount under a different scale. Only the coefficient and scale together state the amount.",
            wrong="Reading `prices.value(0)` as the price gives 125, a hundred times too large, because it returns the coefficient.",
            verify='Assert `prices.value_as_string(0) == "1.25"` next to `prices.value(0) == 125`.',
        ),
        2: dict(
            code="""use arrow::array::{Array, Decimal128Array};
use arrow::datatypes::DataType;
let prices =
    Decimal128Array::from(vec![125_i128, 250, -375]).with_precision_and_scale(10, 2)?;
assert_eq!(prices.value(2), -375);
assert_eq!(prices.value_as_string(2), "-3.75");
assert_eq!(prices.data_type(), &DataType::Decimal128(10, 2));
assert_eq!(prices.iter().flatten().sum::<i128>(), 0);""",
            observe="The new coefficient -375 reads as -3.75 under the same scale, the type is still Decimal128(10, 2), and the three coefficients sum to 0.",
            explain="The sign belongs to the coefficient and the scale applies to every value in the column, so a negative amount needs no special handling. Because all three values share scale 2, their coefficients can be added directly: 1.25 + 2.50 - 3.75 = 0.",
            wrong="Storing -3.75 as `-375` in a column with scale 3 means -0.375; a value's coefficient is only correct under its column's scale.",
            verify="Run the block. Change the scale to 3 and `value_as_string(2)` reports -0.375.",
        ),
        4: dict(
            explain="Reading milliseconds as seconds means taking the raw value of a `Timestamp(Millisecond)` column, such as 1000 from Example B, and treating it as seconds, which places the event 1000 seconds after the epoch instead of 1 second. Casting with `arrow::compute::cast` to `Timestamp(Second, None)` converts correctly and gives 1, while a cast to `Int64` returns the raw 1000. Losing decimal scale is the same mistake for decimals: casting `Decimal128(10, 2)` 1.25 to `Int64` gives 1, and reading the coefficient with `value` gives 125. Convert through the logical type and keep the unit or scale in the schema.",
            why="The unit and the scale live in the data type, not in the stored integer. Any step that keeps the integer but drops the type also drops that meaning.",
            wrong="Dividing by 1000 by hand after reading the raw value works for one column but repeats the unit rule in every consumer, and the next one to forget it is wrong again.",
            verify="Cast the Example B column to `Timestamp(Second, None)` and to `Int64` and compare the results for row 1: 1 and 1000.",
        ),
        5: dict(
            code="""use arrow::array::{Array, ArrayRef, Decimal128Array, TimestampMillisecondArray};
use arrow::datatypes::{DataType, Field, Schema, TimeUnit};
use arrow::record_batch::RecordBatch;
use std::sync::Arc;
let prices =
    Decimal128Array::from(vec![Some(125_i128), None]).with_precision_and_scale(10, 2)?;
let times = TimestampMillisecondArray::from(vec![None, Some(1000_i64)]).with_timezone("UTC");
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
assert!(RecordBatch::try_new(schema, wrong_scale).is_err());""",
            observe="Each column holds one null, the matching batch builds with two rows, and the same coefficients relabeled with scale 3 are rejected by the schema.",
            explain="Nulls in decimal and timestamp columns are validity, exactly as in integer columns; they are not zero amounts or the epoch. The schema check compares full data types, so a different scale is a type mismatch even though the stored integers are identical.",
            wrong="Filling the null price with 0 and the null time with 0 invents a free item measured at 1970-01-01.",
            verify="Run the block. Print the mismatch error; it names Decimal128(10, 2) as expected and Decimal128(10, 3) as found.",
        ),
    },
    45: {
        1: dict(
            explain="`values.chunks(2)` over five values yields three chunks: [1, 2], [3, 4] and [5]. After the first chunk `rows` is 2 and `total` is 3; after the second, 4 and 10; after the third, which is partial, 5 and 15. Only the two counters survive between chunks.",
            why="Each step adds the chunk's own length and sum, so the final counters equal the totals of the whole input whatever the chunk boundaries are.",
            wrong="Assuming every chunk has two rows predicts six rows after three chunks; the last chunk has only the one remaining value.",
            verify="Print `batch.len()` and the running counters inside the loop: 2, 2, 1 and (2, 3), (4, 10), (5, 15).",
        ),
        2: dict(
            code="""let values = [1_i32, 2, 3, 4, 5];
let mut results = Vec::new();
for size in 1..=6 {
    let mut rows = 0;
    let mut total = 0;
    let mut chunks = 0;
    for batch in values.chunks(size) {
        chunks += 1;
        rows += batch.len();
        total += batch.iter().sum::<i32>();
    }
    assert_eq!(chunks, values.len().div_ceil(size));
    results.push((rows, total));
}
assert!(results.iter().all(|result| *result == (5, 15)));""",
            observe="Every chunk size from 1 to 6 gives 5 rows and a total of 15, while the number of chunks follows the ceiling of 5 divided by the size.",
            explain="Chunk size changes how many steps run and how large each step is, never which values are counted. Testing sizes larger than the input, here 6, covers a single partial chunk too.",
            wrong="Computing the chunk count as `values.len() / size` misses the partial final chunk; for size 2 it predicts 2 chunks, not 3.",
            verify="Run the block. Replace `div_ceil(size)` with `/ size` and the assertion fails at size 2.",
        ),
        4: dict(
            explain="The defect is `let batches: Vec<RecordBatch> = reader.collect::<Result<_, _>>()?;` followed by the accounting loop, in a pipeline described as bounded-memory. Collecting keeps every batch alive at once, so peak memory grows with the whole input, and the batch size only controls how it is cut up. Process each batch inside `for batch in reader`, keep only counters, and drop the batch at the end of the iteration, as task 3 does.",
            why="Bounded memory depends on how much data is alive at the same time. Streaming holds one batch at a time; collecting holds all of them, so the claim is only true for the first design.",
            wrong="Reducing the batch size while still collecting makes each batch smaller but keeps every row in memory.",
            verify="Count live batches: a counter incremented on creation and decremented on drop peaks at 1 while streaming and at the number of batches when collecting.",
        ),
        5: dict(
            code="""fn account(values: &[i32], size: usize) -> (usize, usize, usize) {
    let (mut rows, mut accepted) = (0, 0);
    for batch in values.chunks(size) {
        rows += batch.len();
        accepted += batch.iter().filter(|value| **value >= 0).count();
    }
    (rows, accepted, rows - accepted)
}
assert_eq!(account(&[], 2), (0, 0, 0));
assert_eq!(account(&[-1, -2], 2), (2, 0, 2));
assert_eq!(account(&[1, 2, 3, -4, 0], 2), (5, 4, 1));
assert_eq!([1, 2, 3, -4, 0].chunks(2).last(), Some(&[0][..]));""",
            observe="Empty input gives (0, 0, 0), an all-rejected batch gives two rows with zero accepted, and five values in chunks of two end with the partial batch [0], which is still accepted.",
            explain="Every case keeps rows equal to accepted plus rejected. The empty case shows the counters start correctly, the all-rejected case shows rejection is counted rather than dropped, and the partial final batch shows the last short chunk is processed.",
            wrong="Skipping a batch that produced no accepted rows also skips its rejected rows, so the all-rejected case would report (0, 0, 0).",
            verify="Run the block. Add `if batch.len() < size { continue; }` inside the loop and the partial-batch case loses its final 0.",
        ),
    },
    47: {
        1: dict(
            explain="The property `a + b == b + a` holds for mathematical integers, and Example A only checks it under assumptions that keep `i32` addition equal to that. Both values lie in 0 to 9, so every sum is at most 18 and cannot overflow `i32`. The loops enumerate all 100 pairs, so the test is exhaustive for that domain, and equality on `i32` is exact.",
            why="Outside its stated domain the property no longer describes this code: near `i32::MAX`, `a + b` panics in debug builds, so the law depends on the range limit.",
            wrong="Concluding that addition is commutative for every `i32` from this test generalizes past the domain it enumerated.",
            verify="Change the ranges to include `i32::MAX` and run in a debug build: the first overflowing pair panics with attempt to add with overflow.",
        ),
        2: dict(
            code="""let mut checked = 0;
for a in 0_u8..=u8::MAX {
    for b in 0_u8..=u8::MAX {
        let wide = u16::from(a) + u16::from(b);
        let expected = u8::try_from(wide).ok();
        assert_eq!(a.checked_add(b), expected);
        checked += 1;
    }
}
assert_eq!(checked, 65_536);""",
            observe="All 65,536 pairs of u8 quantities agree with a wider oracle: checked_add returns the sum when it fits and None when it does not.",
            explain="The `u8` domain is small enough to enumerate completely, and the oracle adds in `u16`, which cannot overflow for two `u8` values, then checks whether the result fits back into `u8`. The oracle never calls `checked_add`, so the test does not reuse the implementation it judges.",
            wrong="Testing only small values such as 1 + 2 never reaches the overflow boundary, so an implementation that wraps would pass.",
            verify="Run the block. Replace `a.checked_add(b)` with `Some(a.wrapping_add(b))` and the assertion fails at 1 + 255.",
        ),
        4: dict(
            explain="The defect is a sort test that only asserts `output.windows(2).all(|pair| pair[0] <= pair[1])`. An implementation that returns an empty vector, a vector of one repeated value, or the input with a duplicate removed passes it, because all of those are sorted. Add the multiplicity check from Example B, or compare the result with a trusted oracle such as a clone sorted by `sort_unstable`.",
            why="Sorting has two obligations: the output is ordered, and it is a permutation of the input. A property that checks only the first is too weak to reject an implementation that loses data.",
            wrong="Adding `output.len() == input.len()` alone still accepts `[1, 1, 1, 1]` for the input `[3, 1, 3, 2]`.",
            verify="Feed the order-only test a fake sort that returns `Vec::new()`: it passes. Run Example B's multiplicity loop on the same output and it fails.",
        ),
        5: dict(
            code="""use arrow::array::{Array, Int32Array};
fn report(values: &Int32Array) -> (usize, usize, i64) {
    let total = values.iter().flatten().map(i64::from).sum();
    (values.len(), values.null_count(), total)
}
let fixtures = [
    ("empty", Int32Array::from(Vec::<i32>::new()), (0, 0, 0)),
    ("duplicate", Int32Array::from(vec![4, 4, 1]), (3, 0, 9)),
    ("all null", Int32Array::from(vec![None, None]), (2, 2, 0)),
];
for (name, values, expected) in &fixtures {
    assert_eq!(report(values), *expected, "fixture {name}");
}""",
            observe="The empty, duplicate and all-null fixtures each produce their recorded report, and a failure would name the fixture.",
            explain="Each fixture is stored with its name and expected result, so it keeps guarding against the defect it represents: duplicates must both count, and an all-null column must report two rows and two nulls rather than looking like the empty input.",
            wrong="Deleting a fixture after its bug is fixed lets the same defect return unnoticed.",
            verify="Run the block. Change `report` to deduplicate values before summing and the duplicate fixture fails with its name in the message.",
        ),
    },
    48: {
        1: dict(
            explain="Example A has five positions. 2 is valid and nonnegative, so accepted. Position 1 is null and counted by `null_count`. 3 is accepted. -1 is valid but negative, so rejected. 0 is valid and nonnegative, so accepted. That gives 3 accepted with sum 5, 1 null and 1 rejected, and 3 + 1 + 1 equals the 5 submitted positions.",
            why="Each position falls into exactly one category, so the three counts must add up to the input length. That identity is what the last assertion checks.",
            wrong="Rejecting 0 together with the negatives treats a valid zero as bad data and reports 2 accepted, 2 rejected.",
            verify="Assert `accepted.len() + values.null_count() + 1 == values.len()` with the rejected count computed from the data, not written as a literal.",
        ),
        2: dict(
            code="""use arrow::array::{Array, Int32Array};
let input = [Some(2), None, Some(3), Some(-1), Some(0), Some(4)];
let values = Int32Array::from(input.to_vec());
let accepted: Vec<i32> = values
    .iter()
    .flatten()
    .filter(|value| *value >= 0)
    .collect();
let (mut sum, mut kept, mut nulls, mut rejected) = (0, 0, 0, 0);
for item in input {
    match item {
        None => nulls += 1,
        Some(value) if value < 0 => rejected += 1,
        Some(value) => {
            sum += value;
            kept += 1;
        }
    }
}
assert_eq!((accepted.iter().sum::<i32>(), accepted.len()), (sum, kept));
assert_eq!((values.null_count(), rejected), (nulls, 1));
assert_eq!((sum, kept, nulls, rejected), (9, 4, 1, 1));""",
            observe="Adding 4 gives a report of sum 9, four accepted, one null and one rejected, and the Arrow calculation matches a plain match-based derivation.",
            explain="The derivation classifies the original Rust values with one `match`, without Arrow or `filter`, so agreement is evidence about the Arrow path rather than a repeat of it. The new value only changes the accepted sum and count.",
            wrong="Updating the expected numbers by hand from the old report, 5 + 4 and 3 + 1, checks arithmetic, not the program.",
            verify="Run the block. Change the new value to `Some(-4)` and the derivation reports sum 5 with two rejected, so the assertion expecting one rejected value fails.",
        ),
        4: dict(
            explain="Take the null-as-zero defect: computing the report with `values.values().iter().filter(|value| **value >= 0)` reads the physical buffer, so Example A's null slot, which holds 0, is counted as an accepted 0. The report becomes 4 accepted, sum 5, 0 nulls, and the sum hides the error because the inserted value is zero. Count through `values.iter()`, which yields `None` for the null, and keep the accounting identity accepted + null + rejected = length as an assertion.",
            why="The physical buffer has a slot for every row, including nulls, and Arrow does not promise what a null slot contains. Only iteration that applies validity separates missing data from a real zero.",
            wrong="Checking only the sum misses this defect entirely, since adding a zero leaves it at 5. The counts are what expose it.",
            verify="Run the buggy count on Example A and compare: 4 accepted against the correct 3, with the same sum.",
        ),
        5: dict(
            code="""use arrow::array::{Array, Int32Array};
fn report(values: &Int32Array) -> Result<(i32, usize, usize, usize), String> {
    let mut sum = 0_i32;
    let (mut accepted, mut rejected) = (0, 0);
    for value in values.iter().flatten() {
        if value < 0 {
            rejected += 1;
            continue;
        }
        sum = sum.checked_add(value).ok_or("total overflows i32")?;
        accepted += 1;
    }
    Ok((sum, accepted, values.null_count(), rejected))
}
assert_eq!(report(&Int32Array::from(Vec::<i32>::new()))?, (0, 0, 0, 0));
assert_eq!(report(&Int32Array::from(vec![None, None]))?, (0, 0, 2, 0));
assert_eq!(report(&Int32Array::from(vec![-1, -2]))?, (0, 0, 0, 2));
assert!(report(&Int32Array::from(vec![i32::MAX, 1])).is_err());
let parsed: Result<Vec<i32>, _> = ["2", "x"].iter().map(|text| text.parse::<i32>()).collect();
assert!(parsed.is_err());""",
            observe="Empty, all-null and all-rejected inputs give three different reports, an overflowing total returns an error, and the malformed text x fails before it can reach the column.",
            explain="All three non-error cases have a sum of 0, so only the counts tell them apart. Overflow returns an error instead of a wrapped or panicking total, and malformed input is rejected at parsing, where the text is still available to report.",
            wrong="Using `sum += value` makes the overflow case panic in debug builds and wrap silently in release builds, so the report would depend on the build profile.",
            verify="Run the block. Replace `checked_add` with `wrapping_add` and the overflow case returns a negative sum instead of an error.",
        ),
    },
}

for _lesson, _tasks in REASONING.items():
    for _task, _fields in _tasks.items():
        ANSWERS.setdefault(_lesson, {}).setdefault(_task, {}).update(_fields)

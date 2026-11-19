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
std::fs::write(&path, report)?;
let restored = std::fs::read_to_string(&path);
std::fs::remove_file(&path)?;
assert_eq!(restored?, report);
assert!(!path.exists());""",
            observe="The report reads back unchanged and the temporary file is removed.",
            explain="The file is removed before the read result is checked, so cleanup happens even when the comparison fails.",
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

use std::collections::BTreeMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Report {
    pub totals: BTreeMap<String, u32>,
    pub rejected: usize,
}

/// Parse a deliberately simple name,quantity fixture, not general quoted CSV.
/// Reject malformed, empty-name, negative and overflowing records.
pub fn summarize(lines: &[&str]) -> Report {
    let mut report = Report {
        totals: BTreeMap::new(),
        rejected: 0,
    };
    for line in lines {
        let Some((name, quantity)) = line.split_once(',') else {
            report.rejected += 1;
            continue;
        };
        let Ok(quantity) = quantity.parse::<u32>() else {
            report.rejected += 1;
            continue;
        };
        if name.trim().is_empty() {
            report.rejected += 1;
            continue;
        }
        let previous = report.totals.get(name).copied().unwrap_or(0);
        let Some(total) = previous.checked_add(quantity) else {
            report.rejected += 1;
            continue;
        };
        report.totals.insert(name.to_owned(), total);
    }
    report
}

pub fn render(report: &Report) -> String {
    let totals = report
        .totals
        .iter()
        .map(|(name, total)| format!("{name}={total}"))
        .collect::<Vec<_>>()
        .join(";");
    format!("{totals};rejected={}", report.rejected)
}

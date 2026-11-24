fn larger<T: Ord>(left: T, right: T) -> T {
    if left >= right { left } else { right }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(larger(3, 8), 8);
        assert_eq!(larger(String::from("apple"), String::from("pear")), "pear");
    }

    {
        let values = [2, 3, 4];
        let total: i32 = values.into_iter().sum();
        assert_eq!(total, 9);
        assert_eq!(larger(5, 5), 5);
    }

    {
        // Task 2: Guided modification
        #[derive(PartialEq, Eq, PartialOrd, Ord)]
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
        assert_eq!(patch.minor, 10);
    }

    {
        // Task 3: Independent construction
        struct Pair<T> {
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
        assert_eq!(swapped.second, "left");
    }

    {
        // Task 5: Boundary evidence
        struct Entry {
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
        assert_eq!(larger(5, 5), 5);
    }
    println!("rust-018: passed");
    Ok(())
}

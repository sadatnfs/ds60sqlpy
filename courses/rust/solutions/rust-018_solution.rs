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
    println!("rust-018: passed");
    Ok(())
}

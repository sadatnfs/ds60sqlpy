fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2_i32, 3, 4];
        let pointer = values.as_ptr();
        // SAFETY: pointer comes from this live initialized array; length is exact; no mutation overlaps.
        let view = unsafe { std::slice::from_raw_parts(pointer, values.len()) };
        assert_eq!(view, &[2, 3, 4]);
    }

    {
        let values = [2, 3, 4];
        let view = &values[..];
        assert_eq!(view.iter().sum::<i32>(), 9);
    }

    {
        // Task 3: Independent construction
        /// Returns the first two values, or None when fewer than two exist.
        /// Never reads past the end of the slice and never panics.
        fn first_two(values: &[i32]) -> Option<(i32, i32)> {
            match values {
                [first, second, ..] => Some((*first, *second)),
                _ => None,
            }
        }
        assert_eq!(first_two(&[4, 5, 6]), Some((4, 5)));
        assert_eq!(first_two(&[4]), None);
    }
    println!("rust-034: passed");
    Ok(())
}

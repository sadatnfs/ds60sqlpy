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
        // Task 2: Guided modification
        let values = [2_i32, 3, 4, 5];
        let pointer = values.as_ptr();
        let length = 2;
        assert!(length <= values.len());
        // SAFETY: pointer comes from this live initialized array, and length 2 stays within its 4 elements.
        let view = unsafe { std::slice::from_raw_parts(pointer, length) };
        assert_eq!(view, &[2, 3]);
        assert_eq!(view, &values[..length]);
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

    {
        // Task 5: Boundary evidence
        let empty: [u64; 0] = [];
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
        assert!(!(start.is_aligned() && next.is_aligned()));
    }
    println!("rust-034: passed");
    Ok(())
}

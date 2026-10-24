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
    println!("rust-034: passed");
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::io::{Read, Write};
        let path = std::env::temp_dir().join(format!("rust-lesson-{}-a.txt", std::process::id()));
        let mut file = std::fs::OpenOptions::new()
            .write(true)
            .read(true)
            .create_new(true)
            .open(&path)?;
        file.write_all("café".as_bytes())?;
        drop(file);
        let mut actual = String::new();
        std::fs::File::open(&path)?.read_to_string(&mut actual)?;
        std::fs::remove_file(&path)?;
        assert_eq!(actual, "café");
    }

    {
        let valid = String::from_utf8(vec![0x63, 0x61, 0x66, 0xc3, 0xa9])?;
        assert_eq!(valid, "café");
        assert!(String::from_utf8(vec![0xff]).is_err());
    }
    println!("rust-025: passed");
    Ok(())
}

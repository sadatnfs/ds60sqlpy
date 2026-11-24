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

    {
        // Task 2: Guided modification
        use std::io::Write;
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
        assert_eq!(text, "pear,3\nfig,7\n");
        assert!(!text.contains('\r'));
        assert_eq!(text.lines().count(), 2);
    }

    {
        // Task 3: Independent construction
        let name = format!("report-{}.txt", std::process::id());
        let path = std::env::temp_dir().join(name);
        let report = "pear: 3\napple: 5\n";
        let mut file = std::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&path)?;
        std::io::Write::write_all(&mut file, report.as_bytes())?;
        drop(file);
        let restored = std::fs::read_to_string(&path);
        std::fs::remove_file(&path)?;
        assert_eq!(restored?, report);
        assert!(!path.exists());
    }

    {
        // Task 5: Boundary evidence
        use std::io::Read;
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
        assert_eq!(String::from_utf8_lossy(&[0x63, 0xff]), "c\u{fffd}");
    }
    println!("rust-025: passed");
    Ok(())
}

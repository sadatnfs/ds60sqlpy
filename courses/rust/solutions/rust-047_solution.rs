fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut pairs = 0;
        for a in 0_i32..10 {
            for b in 0_i32..10 {
                assert_eq!(a + b, b + a);
                pairs += 1;
            }
        }
        assert_eq!(pairs, 100);
    }

    {
        let original = vec![3, 1, 3, 2];
        let mut sorted = original.clone();
        sorted.sort();
        assert!(sorted.windows(2).all(|pair| pair[0] <= pair[1]));
        for value in 1..=3 {
            assert_eq!(
                original.iter().filter(|item| **item == value).count(),
                sorted.iter().filter(|item| **item == value).count()
            );
        }
    }

    {
        // Task 2: Guided modification
        let mut checked = 0;
        for a in 0_u8..=u8::MAX {
            for b in 0_u8..=u8::MAX {
                let wide = u16::from(a) + u16::from(b);
                let expected = u8::try_from(wide).ok();
                assert_eq!(a.checked_add(b), expected);
                checked += 1;
            }
        }
        assert_eq!(checked, 65_536);
    }

    {
        // Task 3: Independent construction
        use arrow::array::{Array, BooleanArray, Int32Array};
        for pattern in 0_u32..16 {
            let mask: Vec<bool> = (0..4).map(|bit| pattern & (1 << bit) != 0).collect();
            let values = Int32Array::from(vec![1, 2, 3, 4]);
            let kept = arrow::compute::filter(&values, &BooleanArray::from(mask.clone()))?;
            let expected = mask.iter().filter(|keep| **keep).count();
            assert_eq!(kept.len(), expected);
        }
    }

    {
        // Task 5: Boundary evidence
        use arrow::array::{Array, Int32Array};
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
        }
    }
    println!("rust-047: passed");
    Ok(())
}

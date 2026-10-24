enum Node {
    End,
    More(i32, Box<Node>),
}
impl Node {
    fn total(&self) -> i32 {
        match self {
            Self::End => 0,
            Self::More(value, next) => value + next.total(),
        }
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let list = Node::More(2, Box::new(Node::More(3, Box::new(Node::End))));
        assert_eq!(list.total(), 5);
    }

    {
        let owner = std::rc::Rc::new(String::from("value"));
        let weak = std::rc::Rc::downgrade(&owner);
        assert!(weak.upgrade().is_some());
        drop(owner);
        assert!(weak.upgrade().is_none());
    }
    println!("rust-031: passed");
    Ok(())
}

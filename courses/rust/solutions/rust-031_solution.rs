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

    {
        // Task 3: Independent construction
        use std::cell::RefCell;
        use std::rc::{Rc, Weak};
        struct Parent {
            name: String,
            children: RefCell<Vec<Rc<Child>>>,
        }
        struct Child {
            parent: RefCell<Weak<Parent>>,
        }
        let parent = Rc::new(Parent {
            name: String::from("root"),
            children: RefCell::new(Vec::new()),
        });
        let child = Rc::new(Child {
            parent: RefCell::new(Weak::new()),
        });
        *child.parent.borrow_mut() = Rc::downgrade(&parent);
        parent.children.borrow_mut().push(Rc::clone(&child));
        let found = child.parent.borrow().upgrade().map(|p| p.name.clone());
        assert_eq!(found.as_deref(), Some("root"));
        assert_eq!(Rc::strong_count(&parent), 1);
        drop(parent);
        assert!(child.parent.borrow().upgrade().is_none());
    }
    println!("rust-031: passed");
    Ok(())
}

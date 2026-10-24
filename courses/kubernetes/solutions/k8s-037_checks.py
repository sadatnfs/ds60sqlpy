REQUIRED={'api','controller','application','data'}
def accepted(row):return all(row.get(k)=='pass' for k in REQUIRED)

def main():
    a={k:'pass' for k in REQUIRED}
    b={'api':'pass','controller':'unavailable','application':'unavailable','data':'missing'}
    assert accepted(a) and not accepted(b)
    assert not accepted({**a,'data':'wrong-hash'})
    assert accepted({**a,'stack':'qualified-symbolic-B'})
    print('k8s-037 synthetic compatibility gates passed; no version pair or upgrade qualified')

if __name__ == "__main__":
    main()

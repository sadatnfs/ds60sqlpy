def eligible(node,tolerate=False):return node['zone']=='a' and (not node['dedicated'] or tolerate)

def main():
    nodes=[{'name':'a','zone':'a','dedicated':False},{'name':'b','zone':'b','dedicated':False},{'name':'c','zone':'a','dedicated':True}]
    assert [n['name'] for n in nodes if eligible(n)]==['a']
    assert [n['name'] for n in nodes if eligible(n,True)]==['a','c']
    assert sum(eligible(n) for n in nodes)==1
    print('k8s-026 limited synthetic placement predicate passed; no Nodes inspected or edited')

if __name__ == "__main__":
    main()

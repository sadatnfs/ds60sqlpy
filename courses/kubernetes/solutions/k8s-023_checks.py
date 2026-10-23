def main():
    route={'host':'lesson.local','prefix':'/version','backend':'hello','port':8080}
    assert '/version'.startswith(route['prefix']) and not '/other'.startswith(route['prefix'])
    status={'accepted':True,'resolved':True,'backend_ready':False}
    assert status['accepted'] and status['resolved'] and not status['backend_ready']
    assert route['host']!='wrong.local'
    print('k8s-023 synthetic routing/TLS identity reasoning passed; no listener created')

if __name__ == "__main__":
    main()

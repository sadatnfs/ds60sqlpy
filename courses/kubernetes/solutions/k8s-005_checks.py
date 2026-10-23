def main():
    status={'phase':'Running','ready':False,'restart_count':0,'uid':'pod-a'}
    assert status['phase']=='Running' and not status['ready']
    restarted={**status,'restart_count':1}
    replaced={**status,'uid':'pod-b'}
    assert restarted['uid']==status['uid'] and restarted['restart_count']==1
    assert replaced['uid']!=status['uid']
    assert {'waiting_reason':'ErrImageNeverPull'}['waiting_reason']!='CrashLoopBackOff'
    print('k8s-005 synthetic lifecycle distinctions passed; no cluster observation inferred')

if __name__ == "__main__":
    main()

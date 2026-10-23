from datetime import datetime

def seconds(later,earlier):
    a=datetime.fromisoformat(later.replace('Z','+00:00'));b=datetime.fromisoformat(earlier.replace('Z','+00:00'))
    if a.tzinfo is None or b.tzinfo is None:raise ValueError('timezone required')
    result=(a-b).total_seconds()
    if result<0:raise ValueError('reversed milestones')
    return result

def finished(service_ok,data_ok):return service_ok and data_ok

def main():
    elapsed=seconds('2026-01-01T12:01:30Z','2026-01-01T12:00:00Z')
    loss=seconds('2026-01-01T11:59:50Z','2026-01-01T11:59:30Z')
    assert elapsed==90 and loss==20 and elapsed<=120 and loss<=30
    assert not finished(True,False) and finished(True,True)
    print('k8s-041 synthetic RTO/RPO arithmetic and missing-step control passed')

if __name__ == "__main__":
    main()

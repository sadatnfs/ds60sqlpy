"""tf-028: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf
import tempfile,json,subprocess,sys,textwrap
from pathlib import Path

def make_state():
    w=tf.Variable(0.,dtype=tf.float32); opt=tf.keras.optimizers.Adam(.1); opt.build([w]); return w,opt
def step(w,opt):
    with tf.GradientTape() as tape: loss=(w-2)**2
    opt.apply_gradients([(tape.gradient(loss,w),w)])


def verify():
    # Exercise 1: Create nontrivial optimizer state
    w,opt=make_state(); step(w,opt); step(w,opt)
    assert int(opt.iterations)==2 and float(w)>0

    # Exercise 2: Save both state components
    temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name)
    checkpoint=tf.train.Checkpoint(weight=w,optimizer=opt); prefix=checkpoint.save(str(folder/'state'))
    assert Path(prefix+'.index').is_file()

    # Exercise 3: Calculate the uninterrupted control
    saved=float(w); step(w,opt); expected=float(w)
    assert int(opt.iterations)==3 and expected!=saved

    # Exercise 4: Restore in a fresh process
    program=textwrap.dedent("""
    import json,sys,tensorflow as tf
    w=tf.Variable(0.,dtype=tf.float32); opt=tf.keras.optimizers.Adam(.1); opt.build([w])
    c=tf.train.Checkpoint(weight=w,optimizer=opt); c.restore(sys.argv[1]).assert_consumed()
    with tf.GradientTape() as tape: loss=(w-2)**2
    opt.apply_gradients([(tape.gradient(loss,w),w)])
    print(json.dumps({'weight':float(w),'iterations':int(opt.iterations)}))
    """)
    compile(program, "checkpoint-child", "exec")
    result=subprocess.run([sys.executable,'-c',program,prefix],check=False,capture_output=True,text=True,timeout=60)
    if result.returncode: raise RuntimeError('child process failed: '+result.stderr)
    restored=json.loads(result.stdout.strip().splitlines()[-1])
    np.testing.assert_allclose(restored['weight'],expected,atol=1e-6,rtol=0); assert restored['iterations']==3

    # Exercise 5: Expose a weights-only restart
    weights_only,fresh=make_state(); weights_only.assign(saved); step(weights_only,fresh)
    assert abs(float(weights_only)-expected)>1e-6 and int(fresh.iterations)==1

    # Exercise 6: Verify cleanup
    temporary.cleanup(); assert not folder.exists()
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

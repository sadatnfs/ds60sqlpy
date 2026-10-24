"""tf-032: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf
import tempfile,json,subprocess,sys,textwrap
from pathlib import Path




def verify():
    # Exercise 1: Create a fixed inference model
    model=tf.keras.Sequential([tf.keras.Input(shape=(1,)),tf.keras.layers.Dense(1,use_bias=False,kernel_initializer=tf.keras.initializers.Constant(2.))])
    x=np.array([[1.],[3.]],dtype='float32'); expected=model(x).numpy()
    np.testing.assert_array_equal(expected,[[2],[6]])

    # Exercise 2: Round-trip .keras
    temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); keras_path=folder/'model.keras'; model.save(keras_path)
    loaded=tf.keras.models.load_model(keras_path)
    np.testing.assert_allclose(loaded(x).numpy(),expected,atol=1e-6,rtol=0)

    # Exercise 3: Export an inference endpoint
    export_path=folder/'inference'; model.export(export_path)
    exported=tf.saved_model.load(str(export_path))
    np.testing.assert_allclose(exported.serve(tf.constant(x)).numpy(),expected,atol=1e-6,rtol=0)

    # Exercise 4: Check both in a fresh process
    program=textwrap.dedent("""
    import json,sys,tensorflow as tf
    x=tf.constant([[1.],[3.]])
    a=tf.keras.models.load_model(sys.argv[1])(x).numpy().tolist()
    exported=tf.saved_model.load(sys.argv[2])
    b=exported.serve(x).numpy().tolist()
    print(json.dumps([a,b]))
    """)
    compile(program, "checkpoint-child", "exec")
    result=subprocess.run([sys.executable,'-c',program,str(keras_path),str(export_path)],capture_output=True,text=True,check=False,timeout=60)
    if result.returncode: raise RuntimeError('child process failed: '+result.stderr)
    a,b=json.loads(result.stdout.strip().splitlines()[-1])
    np.testing.assert_allclose(a,expected,atol=1e-6,rtol=0); np.testing.assert_allclose(b,expected,atol=1e-6,rtol=0)

    # Exercise 5: Check a new batch length
    new=loaded(np.array([[0.],[2.],[4.]],dtype='float32')).numpy()
    assert new.shape==(3,1); np.testing.assert_array_equal(new[:,0],[0,4,8])

    # Exercise 6: Remove only owned artifacts
    temporary.cleanup(); assert not folder.exists()
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

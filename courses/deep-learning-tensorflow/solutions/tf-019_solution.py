"""tf-019: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Compute local differences
    image=tf.reshape(tf.range(1,10,dtype=tf.float32),(1,3,3,1)); kernel=tf.reshape(tf.constant([1.,0.,0.,-1.]),(2,2,1,1))
    out=tf.nn.conv2d(image,kernel,strides=1,padding='VALID')
    np.testing.assert_array_equal(out.numpy().reshape(2,2),np.full((2,2),-4))

    # Exercise 2: Rotate the kernel
    rot=tf.reverse(kernel,axis=[0,1]); changed=tf.nn.conv2d(image,rot,strides=1,padding='VALID')
    np.testing.assert_array_equal(changed.numpy().reshape(2,2),np.full((2,2),4))

    # Exercise 3: Count output positions
    assert tuple(out.shape)==(1,2,2,1)
    assert tuple(tf.nn.conv2d(image,kernel,strides=2,padding='VALID').shape)==(1,1,1,1)

    # Exercise 4: Trace one pixel influence
    changed_image=image.numpy().copy(); changed_image[0,0,0,0]+=10
    delta=tf.nn.conv2d(changed_image,kernel,strides=1,padding='VALID').numpy()-out.numpy()
    np.testing.assert_array_equal(delta.reshape(2,2),[[10,0],[0,0]])

    # Exercise 5: Count shared parameters
    layer=tf.keras.layers.Conv2D(2,2,use_bias=False); layer(image)
    assert layer.count_params()==8

    # Exercise 6: Add a constant image offset
    offset=tf.nn.conv2d(image+100,kernel,strides=1,padding='VALID')
    np.testing.assert_array_equal(offset.numpy(),out.numpy())
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

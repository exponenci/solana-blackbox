import os
import sys
import inspect


currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 


from serializer import Serializer


def test_serialization():
    ser = Serializer()

    data = [4, 3, 6, 7]
    ser_data = ser.serialize(data, 'INT32')
    exp_res = b'\x04\x00\x00\x00\x03\x00\x00\x00\x06\x00\x00\x00\x07\x00\x00\x00'
    assert ser_data == exp_res

    data = [1.02, 3.14, 6.57, 734.2]
    ser_data = ser.serialize(data, 'DOUBLE')
    exp_res = b'R\xb8\x1e\x85\xebQ\xf0?\x1f\x85\xebQ\xb8\x1e\t@H\xe1z\x14\xaeG\x1a@\x9a\x99\x99\x99\x99\xf1\x86@'
    assert ser_data == exp_res

    data = b'hello, i am super-aboba!'
    ser_data = ser.serialize(data, 'STRING')
    exp_res = b'hello, i am super-aboba!'
    assert ser_data == exp_res


def test_deserialization():
    ser = Serializer()
    
    data = b'\x04\x00\x00\x00\x03\x00\x00\x00\x06\x00\x00\x00\x07\x00\x00\x00'
    deser_data = ser.deserialize(data, 'INT32')
    exp_res = [4, 3, 6, 7]
    assert deser_data == exp_res

    data = b'R\xb8\x1e\x85\xebQ\xf0?\x1f\x85\xebQ\xb8\x1e\t@H\xe1z\x14\xaeG\x1a@\x9a\x99\x99\x99\x99\xf1\x86@'
    deser_data = ser.deserialize(data, 'DOUBLE')
    exp_res = [1.02, 3.14, 6.57, 734.2]
    assert deser_data == exp_res

    data = b'hello, i am super-aboba!'
    ser_data = ser.deserialize(data, 'STRING')
    exp_res = [104, 101, 108, 108, 111, 44, 32, 105, 32, 97, 109, 32, 115, 117, 112, 101, 114, 45, 97, 98, 111, 98, 97, 33]
    # print(''.join(list(map(chr, exp_res)))) # can use this to be ensure
    assert ser_data == exp_res
    

if __name__ == '__main__':
    test_serialization()
    test_deserialization()

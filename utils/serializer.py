import array
from enum import Enum


class Serializer():
    """ Used for serializing/deserializing data for tcp connections"""
    
    class SocketDtype(Enum):
        """ Types to be shared are listed here.
            can be edited
        """
        INT32 = 1
        DOUBLE = 2
        STRING = 3

    def match_str2enum(self, dtype: str) -> SocketDtype:
        """
            returns data type in Enum from string
        """
        return self.SocketDtype[dtype]

    def serialize(self, data, dtype):
        """ 
            returns array binary data to be shared according to data 
            and it's type 
        
            # data - list of dtype values
            # returns bytes
        """
        if type(dtype) == str:
            dtype = self.match_str2enum(dtype)
        typecode = 'b'
        if dtype == self.SocketDtype.INT32:
            typecode = 'I' # now I = at least 16 bits, find way to make it explicit 32 bits
        elif dtype == self.SocketDtype.DOUBLE:
            typecode = 'd'
        elif dtype == self.SocketDtype.STRING:
            typecode = 'B'
        data_bytes = array.array(typecode, data).tobytes()
        return data_bytes

    def deserialize(self, data, dtype):
        """ 
            returns list of result data recieved according to data 
            and it's type 
        """
        if type(dtype) == str:
            dtype = self.match_str2enum(dtype)
        typecode = 'b'
        if dtype == self.SocketDtype.INT32:
            typecode = 'I'
        elif dtype == self.SocketDtype.DOUBLE:
            typecode = 'd'
        elif dtype == self.SocketDtype.STRING:
            typecode = 'B'
        sequence = array.array(typecode, data)
        return sequence.tolist()

import struct
import sys


class Chunk(object):
    def __init__(self, ident, data_size):
        self._ident = ident
        self._data_size = data_size

    @property
    def ident(self):
        return self._ident

    @property
    def data_size(self):
        return self._data_size
 
    @staticmethod
    def hex_char(c):
        return '{:02X}'.format(struct.unpack('B', str(c))[0])

    @staticmethod
    def hex_string(data):
        return ':'.join(map(Chunk.hex_char, data))


class DataChunk(Chunk):
    def __init__(self, ident, data):
        Chunk.__init__(self, ident, len(data))
        self._data = data

    @property
    def data(self):
        return self._data
 
    def __str__(self):
        def f(c):
            s = str(c)
            return c if s.isalnum() else self.hex_char(c)
        data_as_string = ':'.join(map(f, self._data))
        return "ID: {} DLen: {} Data: {}".format(self._ident, len(self._data), data_as_string)


class ParentChunk(Chunk):
    def __init__(self, ident, data, maker):
        Chunk.__init__(self, ident, len(data))
        self._name = data[0:4]
        self._children = []
        data = data[4:]
        while len(data) > 0:
            child = maker.create(data) 
            self._children.append(child)
            data = data[8 + child.data_size:]

    @property
    def name(self):
        return self._name
    
    @property
    def children(self):
        return self._children

    def __str__(self):
        return "ID: {} Name: {} DLen: {} Children: \n{}".format(self._ident, self._name, self._data_size, "\n\t".join(map(str, self._children)))


class ChunkCreator:
    def __init__(self):
        pass

    def from_file(self, file_name):
        with open(file_name, 'rb') as f:
            bytes = f.read()
        return self.create(bytes)

    def create(self, bytes):
        ident = bytes[0:4]
        length = struct.unpack('<I', bytes[4:8])[0]
        data = bytes[8:8+length]
        return self.create_chunk(ident, data) 

    def create_chunk(self, ident, data):
        if ident == 'LIST' or ident == 'RIFF':
            return ParentChunk(ident, data, self)
        else:
            return DataChunk(ident, data)

    @staticmethod
    def unpack_32(bytes):
        return struct.unpack('<I', bytes[0:4])[0]

    @staticmethod
    def unpack_16(bytes):
        return struct.unpack('<H', bytes[0:2])[0]

    @staticmethod
    def unpack_8(bytes):
        return struct.unpack('B', bytes[0:1])[0]

if __name__ == "__main__":
    c = ChunkCreator()
    print c.from_file(sys.argv[1])

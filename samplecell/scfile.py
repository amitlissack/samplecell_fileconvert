import sys
import struct
from riff import ChunkCreator, DataChunk
from collections import namedtuple


class SCModel:
    def __init__(self):
        pass


class SCIns(SCModel):
    def __init__(self):
        SCModel.__init__(self)        


class SCMix(SCModel):
    def __init__(self):
        SCModel.__init__(self)


class StringChunk(DataChunk):
    def __init__(self, ident, data):
        DataChunk.__init__(self, ident, data)
        self._string= data

    @property
    def string(self):
        return self._string

    def __str__(self):
        return "{} Chunk: {}".format(self.ident, self._string)


class FpthChunk(DataChunk):
    def __init__(self, ident, data):
        DataChunk.__init__(self, ident, data)
        self._files = []
 
        num = SCChunkCreator.unpack_32(data[0:4])
        data = data[4:]
        for i in range(num):
            l = SCChunkCreator.unpack_32(data[0:4])
            self._files.append(data[4:4+l])
            data = data[4+l:]
 
    @property
    def files(self):
        return _files

    def __str__(self):
        return "{} Chunk: {} Files {}".format(self.ident, len(self._files), ", ".join(self._files))


class KeySChunk(DataChunk):

    SampleData = namedtuple('SampleData', ['index', 'un4_1', 'channel', 'un6_3', 'file_name', 'unX_4'])
 
    def __init__(self, ident, data):
        DataChunk.__init__(self, ident, data)
        self._sub = []

        num = SCChunkCreator.unpack_32(data[0:4])
        size = SCChunkCreator.unpack_32(data[4:8])
        self._mem = SCChunkCreator.unpack_32(data[8:12])
        data = data[12:]
        for i in range(num):
            #self._sub.append(data[0:size])
            index=SCChunkCreator.unpack_32(data[0:4])
            un4_1=SCChunkCreator.unpack_32(data[4:8])
            channel=SCChunkCreator.unpack_32(data[8:12])
            un6_3=self.hex_string(data[12:18])
            file_name_size=SCChunkCreator.unpack_8(data[18:19])
            file_name=data[19:19+file_name_size]
            unX_4=self.hex_string(data[19+file_name_size:size])
            sd = KeySChunk.SampleData(index, un4_1, channel, un6_3, file_name, unX_4)
            self._sub.append(sd)
            data = data[size:]

    def in_all(self, buffs):
        sets = [set(enumerate(x)) for x in buffs ]
        in_all = reduce(lambda x, y: x & y, sets)
 
        return in_all

    @property
    def mem(self):
        return self._mem
    def __str__(self):
        in_all = self.in_all(self._sub)
        def at(i, v):
            if (i, v) in in_all:
                return "  "
            else:
                return self.hex_char(v)
        def f(sub):
            return ":".join([at(i, v) for (i, v)  in enumerate(sub)])
        #return "{} Chunk: {} Mem:\n{}".format(self.ident, self.mem, "\n".join(map(f, self._sub)))
        return "{} Chunk: {} Mem:\n{}".format(self.ident, self.mem, "\n".join(map(str, self._sub)))


class KeyPChunk(KeySChunk):

    KeyRange = namedtuple('KeyRange', ['end_key', 'zones'])
    VelZone = namedtuple('VelZone', ['file_index1', 'filed_index2', 'un1_8', 'key'])

    def __init__(self, ident, data):
        DataChunk.__init__(self, ident, data)
        num_key_zones = SCChunkCreator.unpack_16(data)
        self._header = data[2:6]
 
        data = data[6:]
        self._sub = []
        while len(data) > 0:
            end_key = SCChunkCreator.unpack_32(data[0:4])
            num_zones = SCChunkCreator.unpack_16(data[4:6])
            vel_zones = []

            for i in range(num_zones):
                ds = 6 + (i*18)
                zone_data = data[ds:ds+18]
                fi1 = SCChunkCreator.unpack_32(zone_data[0:4])
                fi2 = SCChunkCreator.unpack_32(zone_data[4:8])
                un1_8 = self.hex_string(zone_data[8:16])
                key = SCChunkCreator.unpack_16(zone_data[16:18])
                vz=self.VelZone(fi1, fi2, un1_8, key)
                vel_zones.append(vz)

            data = data[6+(num_zones*18):]
            kr=self.KeyRange(end_key, vel_zones)
            self._sub.append(kr)

    def __str__(self):
        return "{} Chunk: {} Header: \n{}".format(self.ident, 
            self.hex_string(self._header), "\n".join(map(str, self._sub)))
        #s = KeySChunk.__str__(self)
        #return "{} \n\tHeader: {}".format(s, self.hex_string(self._header))


class SCChunkCreator(ChunkCreator):
   
    ident_clazz = {
        'FPTH': FpthChunk,
        'INAM': StringChunk,
        'ANNO': StringChunk,
        'KeyS': KeySChunk,
        'KeyP': KeyPChunk
    }

    
    def create_chunk(self, ident, data):
        
        clazz = self.ident_clazz.get(ident)
        if clazz is not None:
            return clazz(ident, data)          
        else:
            return ChunkCreator.create_chunk(self, ident, data)
    

if __name__ == "__main__":
    riff_file = SCChunkCreator()
    sc = riff_file.from_file(sys.argv[1])
 
    print sc

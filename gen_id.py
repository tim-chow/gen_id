import time
import random
import math

#the default begin of epoch is 2015-01-01 00:00:00
gen_epoch = lambda epoch='2015-01-01 00:00:00': \
        time.mktime(time.strptime(epoch, '%Y-%m-%d %H:%M:%S'))
EPOCH = gen_epoch()
#set the begin of epoch
def set_epoch(epoch):
    global EPOCH
    EPOCH = gen_epoch(epoch)
    return EPOCH

RADICES = '0123456789-_abcdefghijklmnopqrstuvwxyz' \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def set_radices(radices):
    assert isinstance(radices, basestring) and \
            all(ch for ch in radices if ord(ch) < 128) and \
            len(set(radices)) == len(radices) == 64

    global RADICES
    RADICES = radices

gen_random = lambda set_of_chars, num_of_chars: "".join(random.sample(
    set_of_chars * (1 + num_of_chars/len(set_of_chars)), num_of_chars))

def convert_to_64(integer):
    global RADICES
    bstring = bin(integer)[2:]
    bstring = bstring.rjust(int(math.ceil(len(bstring)/6.))*6, '0')
    return "".join([RADICES[int(bstring[ind * 6: (ind + 1) *6], 2)]
        for ind in range(len(bstring) / 6)])

def invert_to_10(string64):
    global RADICES
    return int("".join([bin(RADICES.index(ch))[2:].rjust(6, '0') 
                for ch in string64]), 2)

class GenID:
    def __init__(self, ip_addr, timestamp=None, gen_suffix=None):
        #only support IPv4
        self.ip_addr = ip_addr
        self.timestamp = (timestamp or time.time()) - EPOCH
        self.gen_suffix = gen_suffix

    def get_id(self):
        global RADICES

        seconds = int(self.timestamp)
        million_seconds = int((self.timestamp - seconds) * 1000)
        self.part_time = convert_to_64(seconds).rjust(5, RADICES[0]) + \
                        convert_to_64(million_seconds).rjust(2, RADICES[0])
        self.part_ip = convert_to_64(int("".join(map(
                        lambda i : bin(int(i))[2:].rjust(8, "0"), 
                        self.ip_addr.split(".")[2:]))[-12:], 2)).rjust(2, RADICES[0])
        self.part_random = gen_random(RADICES, 4)
        self.part_suffix = self.gen_suffix() if callable(self.gen_suffix) else ''

        self._id = self.part_time + self.part_ip + self.part_random + self.part_suffix
        return self._id

class InverseID:
    def __init__(self, ID):
        self._id = ID
        self._do_inverse()

    def _do_inverse(self):
        self.part_time_second = invert_to_10(self._id[0:5]) + int(EPOCH)
        self.part_time_million = invert_to_10(self._id[5:7])
        self.part_ip = int(bin(invert_to_10(self._id[7:9]))[2:][-8:], 2)
        self.part_random = self._id[9:13]
        self.part_suffix = self._id[13:]

    def __str__(self):
        return "seconds:{0.part_time_second}, \
million seconds:{0.part_time_million} \
last partion of ip address:{0.part_ip}, \
random:{0.part_random}, \
suffix:{0.part_suffix}".format(self)

if __name__ == "__main__":
    import functools
    gen_suffix = functools.partial(gen_random, RADICES, 3)
    o = GenID('112.124.222.223', gen_suffix=gen_suffix)
    id_ = o.get_id()
    print(id_)
    print(InverseID(id_))

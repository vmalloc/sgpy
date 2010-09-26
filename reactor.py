
class Reactor(object):
    _DEFAULT_START_INDEX = 0
    _DEFAULT_END_INDEX = 0xff

    def __init__(self, device, 
                 queue_size=sg.SG_MAX_QUEUE, 
                 start_index=_DEFAULT_START_INDEX,
                 end_index=_DEFAULT_END_INDEX):
        if end_index - start_index < queue_size:
            raise ValueError("index range (end - start) must be bigger then queue size")
        self._device = device
        self._queue_size = queue_size
        self._start_index = start_index
        self._end_index = end_index
        self._index = start_index
        
    def _nextIndex(self):
        index = self._index
        self._index += 1
        assert self._index <= self._end_index
        if self._index == self._end_index:
            self._index = self._start_index
        return index

    def process(self, ios):
        
        self._device.read(sg.SgIoHdrSize

class WaveSegment:
    __slots__ = ('index', 'start_time', 'end_time', 'frames')

    def __init__(self, index, start_time, end_time):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.frames = []

    def __repr__(self):
        return f"WaveSegment(index={self.index}, start_time={self.start_time}, " \
               f"end_time={self.end_time}, frames={len(self.frames)})"


class DQFile:
    __slots__ = ('ifo', 'file', 'dq_cat', 'shift', 'invert', 'c4')

    def __init__(self, ifo, file, dq_cat, shift, invert, c4):
        self.ifo = ifo
        self.file = file
        self.dq_cat = dq_cat
        self.shift = shift
        self.invert = invert
        self.c4 = c4

    def __repr__(self):
        return f"DQFile(ifo={self.ifo}, file={self.file}, dq_cat={self.dq_cat}, " \
               f"shift={self.shift}, invert={self.invert}, c4={self.c4})"


class SLag:
    __slots__ = ('job_id', 'slag_id', 'seg_id')

    def __init__(self, job_id, slag_id, seg_id):
        self.job_id = job_id  # job id : sequential progressive number
        self.slag_id = slag_id  # slag id vector : [0]=jobId - [1]=1/0 1=header slag - [2,..,nIFO+1] ifo slag
        self.seg_id = seg_id  # seg id vector : [0,..,nIFO-1] ifo segment number

    def __repr__(self):
        return f"SLag(job_id={self.job_id}, slag_id={self.slag_id}, seg_id={self.seg_id})"


class FrameFile:
    __slots__ = ('ifo', 'path', 'start_time', 'duration')

    def __init__(self, ifo, path, start_time, duration):
        self.ifo = ifo
        self.path = path
        self.start_time = start_time
        self.duration = duration

    def __repr__(self):
        return f"FrameFile(ifo={self.ifo}, path={self.path}, " \
               f"start_time={self.start_time}, duration={self.duration})"
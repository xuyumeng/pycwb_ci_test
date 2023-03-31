class SparseTimeFrequencySeries:
    """SparseSeries class

    :param core: bool, whether to use core functions
    """

    def __init__(self, core=None, wavelet=None, sparse_lookup=None,
                 sparse_type=None, sparse_index=None, sparse_map_00=None, sparse_map_90=None,
                 rate=0, w_rate=0, start=0, stop=0, edge=0,
                 time_halo=0, layer_halo=0, net_delay=0):
        self.wavelet = wavelet
        self.core = core
        self.sparse_lookup = sparse_lookup  # store the index pointer to the layers
        self.sparse_type = sparse_type  # store pixel type 1/0  core/halo
        self.sparse_index = sparse_index  # store pixel index
        self.sparse_map_00 = sparse_map_00  # store pixel 00 map
        self.sparse_map_90 = sparse_map_90  # store pixel 90 map

        self.rate = rate
        self.w_rate = w_rate
        self.start = start
        self.stop = stop
        self.edge = edge

        self.time_halo = time_halo
        self.layer_halo = layer_halo
        self.net_delay = net_delay

    def resize(self):
        """Resize the sparse map

        :param size: new size
        :type size: int
        """
        self.core = []
        self.sparse_lookup = []
        self.sparse_type = []
        self.sparse_index = []
        self.sparse_map_00 = []
        self.sparse_map_90 = []

    def set_map(self, tf_map):
        """Set the map

        :param tf_map: time-frequency map
        :type tf_map: TimeFrequencySeries
        """
        self.wavelet = tf_map.wavelet.lightweight_dump()
        self.wavelet.allocate(tf_map.data)
        self.time_halo = tf_map.wavelet.time_delay_filter_size()

        self.rate = tf_map.data.sample_rate
        self.w_rate = tf_map.w_rate
        self.start = tf_map.start
        self.stop = tf_map.stop
        self.edge = tf_map.edge

    def set_halo(self, max_tau=0.042, layer_halo=1, time_halo=-1):
        """Set the halo

        For each core pixels (if layerHalo = 1) the following pixels are saved

            core      = '.'
            extraHalo = '++++++++'
            timeHalo  = 'xxxx'

            ++++++++xxxx xxxx++++++++
            ++++++++xxxx.xxxx++++++++
            ++++++++xxxx xxxx++++++++

        :param max_tau: delay time (sec) is stored in net_Delay used to compute extraHalo = net_Delay*sparseRate
        :type max_tau: float
        :param layer_halo: number of layers above and below each core pixel is stored in layerHalo the total number of layers in the halo is 2*layerHalo+1
        :type layer_halo: int
        :param time_halo: number of slice on the right and on the left each core pixel is stored in timeHalo the total number of pixels on the time axis is 2*(timeHalo+extraHalo)+1 The default value is -1 : the value is automatically selected from the associated TF map with WDM::getTDFsize() method.
        :type time_halo: int
        """
        self.resize()
        self.layer_halo = layer_halo
        self.net_delay = max_tau
        if time_halo >= 0:
            self.time_halo = time_halo

    def add_core(self, ifo_id, cluster):
        """ Add core pixels of the detector ID=ifoID contained in the pwc netcluster with index ID

        :param ifo_id: detector ID
        :type ifo_id: int
        :param cluster: netcluster
        :type cluster: Cluster
        """

        r = int(self.w_rate + 0.1)

        # skip rejected clusters
        if cluster.cluster_status == 1:
            return False

        # loop over pixels
        for pixel in cluster.pixels:
            # skip pixel with bad rate, TODO: why the rate can be bad?
            if int(pixel.rate + 0.01) != r:
                continue

            # store pixel index
            self.core.append(pixel.data[ifo_id].index)

    def update_sparse_table(self):
        """
        Use the core pixels and halo parameters to update the sparse maps with core+halo pixels

        :return:
        """
        if self.time_halo == 0 and self.layer_halo == 0:
            return

        extra_halo = int(self.net_delay * self.w_rate) + 8  # init extra halo : WARNING value 8 ad hoc - to be fixed
        h_slice = self.time_halo + extra_halo  # halo slices
        layer_halo = self.layer_halo  # halo layers

        cluster = []
        n_layer = self.wavelet.max_level # number of WDM layers
        n_slice = self.wavelet.size_at_zero_layer  # number of samples in wavelet layer

        for core_pixel in self.core:
            # i,j index of the core pixel
            l = core_pixel // n_slice
            t = core_pixel % n_slice

            # Calculate the starting and ending indices for the time and layer axes
            start_t = max(0, t - h_slice)
            start_l = max(0, l - layer_halo)
            end_t = min(n_slice - 1, t + h_slice)
            end_l = min(n_layer - 1, l + layer_halo)

            # Calculate the block indices in 1D array
            cluster += [ i * n_slice + j for i in range(start_l, end_l + 1) for j in range(start_t, end_t + 1)]

        cluster = sorted(set(cluster))
        self.sparse_index = cluster
        self.sparse_map_00 = [self.wavelet.get_map_00(i) for i in cluster]
        self.sparse_map_90 = [self.wavelet.get_map_90(i) for i in cluster]





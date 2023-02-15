import os
from pycwb import logger_init
from pycwb.config import Config, CWBConfig
from pycwb.modules.read_data import read_from_gwf, generate_noise


def cwb_2g(config='./config.ini', user_parameters='./user_parameters.yaml'):
    logger_init()

    # load user parameters
    cwb_config = CWBConfig(config)
    cwb_config.export_to_envs()
    config = Config(user_parameters)

    data = generate_injected(config)

    dc_data = [i.crop(931158200 - i.start_time, i.end_time - 931158600) for i in data]

    from pycwb.utils import convert_pycbc_timeseries_to_wavearray
    wavearray = [convert_pycbc_timeseries_to_wavearray(d) for d in dc_data]

    from pycwb.modules.data_conditioning import regression, whitening
    data_reg = [regression(config, wavearray[i]) for i in range(len(config.ifo))]
    data_w_reg = [whitening(config, data_reg[i]) for i in range(len(config.ifo))]
    tf_map = [d['TFmap'] for d in data_w_reg]

    # initialize network
    from pycwb.modules.coherence import create_network
    net, wdm_list = create_network(1, config, data_w_reg)

    # calculate coherence
    from pycwb.modules.coherence import coherence
    sparse_table_list, cluster_list = coherence(config, net, tf_map, wdm_list)

    # supercluster
    from pycwb.modules.super_cluster import supercluster
    supercluster(config, net, wdm_list, cluster_list, sparse_table_list)


def generate_injected(config):
    # load noise
    start_time = 931158100
    noise = [generate_noise(f_low=30.0, sample_rate=1024.0, duration=600, start_time=start_time, seed=i)
             for i, ifo in enumerate(config.ifo)]

    # generate injection from pycbc
    from pycbc.waveform import get_td_waveform
    hp, hc = get_td_waveform(approximant="IMRPhenomPv3",
                             mass1=20,
                             mass2=20,
                             spin1z=0.9,
                             spin2z=0.4,
                             inclination=1.23,
                             coa_phase=2.45,
                             distance=500,
                             delta_t=1.0 / noise[0].sample_rate,
                             f_lower=20)
    declination = 0.65
    right_ascension = 4.67
    polarization = 2.34
    gps_end_time = 931158400
    from pycwb.modules.read_data import project_to_detector
    strain = project_to_detector(hp, hc, right_ascension, declination, polarization, config.ifo, gps_end_time)

    # inject signal into noise and convert to wavearray
    injected = [noise[i].add_into(strain[i]) for i in range(len(config.ifo))]

    return injected


def read_from_config(config):
    data = []
    for i in range(len(config.ifo)):
        # read path string from the files in config.frFiles
        filenames = ""
        with open(config.frFiles[i], 'r') as f:
            filenames = f.read()
        # read data from the files
        data.append(read_from_gwf(i, config, filenames, config.channelNamesRaw[i]))
    return data
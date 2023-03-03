import copy
import time
import numpy as np
import ROOT
import logging
from pycwb.config import Config
from pycwb.modules.netcluster import select_clusters, copy_metadata
from pycwb.modules.netevent import Event

logger = logging.getLogger(__name__)


def likelihood(config: Config, net: ROOT.network,
               sparse_table_list: list,
               pwc_list: list,
               cluster: ROOT.netcluster,
               wdm_list: list[ROOT.WDM(np.double)]):
    """
    calculate likelihood
    :param config:
    :param net:
    :param strain_list:
    :param wdm_list:
    :return:
    """

    timer_start = time.perf_counter()

    # set low-rate TD filters
    for k in range(config.nRES):
        wdm_list[k].setTDFilter(config.TDSize, config.upTDF)
    net.setDelayIndex(config.TDRate)

    # load sparse table
    # cout << "Loading sparse TF map ... " << endl;
    logger.info("Loading sparse TF map ... ")
    for n in range(config.nIFO):
        pD = net.getifo(n)
        pD.sclear()
        # for(int i=0; i<nRES; i++) {
        for i in range(config.nRES):
            pD.vSS.push_back(sparse_table_list[i][n])

    n_events = 0
    events = []
    for j in range(int(net.nLag)):
        cycle = net.wc_List[j].shift
        pwc = net.getwc(j)
        # pwc = copy.deepcopy(pwc_list[0])
        # pwc.clear()
        pwc.cData.clear()
        copy_metadata(pwc, pwc_list[j])
        # pwc.print()

        # print header

        logger.info("-------------------------------------------------------")
        logger.info("-> Processing %d clusters in lag=%d" % (pwc.cList.size(), cycle))
        logger.info("   ----------------------------------------------------")

        nmax = -1  # load all tdAmp
        npixels = 0  # total loaded pixels per lag
        nevents = 0  # total recontructed events per lag
        nselected_core_pixels = 0
        nrejected_weak_pixels = 0  # remove weak glitches
        nrejected_loud_pixels = 0  # remove loud glitches
        for k in range(pwc_list[j].cList.size()):  # loop over the cluster list
            # Decoupling: copy_metadata(pwc, pwc_list[j])
            select_clusters(pwc, pwc_list[j], k)
            cid = pwc.get("ID", 0, 'S', 0)  # get cluster ID
            if not cid.size():
                continue

            id = int(cid.data[cid.size() - 1] + 0.1)
            pwc.setcore(False, id)
            pwc.loadTDampSSE(net, 'a', config.BATCH, config.BATCH)  # attach TD amp to pixels

            lag = j

            ID = 0
            if net.pattern > 0:
                selected_core_pixels = net.likelihoodWP(config.search, lag, ID, ROOT.nullptr, config.Search)
            else:
                selected_core_pixels = net.likelihood2G(config.search, lag, ID, ROOT.nullptr)
            logger.info("Selected core pixels: %d" % selected_core_pixels)

            event = Event()
            event.output(net, k + 1, 0)
            events.append(event)

            rejected_weak_pixels = 0
            rejected_loud_pixels = 0

            detected = (net.getwc(j).sCuts[k] == -1)
            # Decoupling: detected = (net.getwc(j).sCuts[0] == -1)

            # print reconstructed event
            logger.info("   cluster-id|pixels: %5d|%d" % (k + 1, int(pwc.size() - npixels)))
            if detected:
                logger.info("\t -> SELECTED !!!")
                # print("-------------------------------------------------------")
                # print(event.dump())
                # print("-------------------------------------------------------")
            else:
                logger.info("\t <- rejected    ")

            # if(detected) nevents++
            # npixels=pwc->size();
            if detected:
                nevents += 1
            npixels = pwc.size()
            # Decoupling: remove above line

            pwc.clean(k+1)
        n_events += nevents

    # timer
    timer_end = time.perf_counter()
    logger.info("-------------------------------------------------------")
    logger.info("Total events: %d" % n_events)
    logger.info("Total time: %.2f s" % (timer_end - timer_start))
    logger.info("-------------------------------------------------------")

    return events


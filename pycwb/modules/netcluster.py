def append_cluster(cluster, c, n_max):
    skip = n_max == -2

    for c_id, clist in enumerate(c.cList):
        if not skip:
            for i in cluster.pList:
                i.clean()
        new_cluster_id = cluster.cList.size() + 1
        for pixel in c.pList[clist[0]: clist[-1] + 1]:
            pixel.clusterID = new_cluster_id
            cluster.pList.push_back(pixel)
            # TODO: orate and crate
        cluster.sCuts.push_back(0)
        cluster.cList.push_back(clist)
        cluster.cRate.push_back(c.cRate[c_id])
        cluster.cTime.push_back(c.cTime[c_id])
        cluster.cFreq.push_back(c.cFreq[c_id])
        cluster.sArea.push_back(c.sArea[c_id])
        cluster.p_Map.push_back(c.p_Map[c_id])
        cluster.nTofF.push_back(c.nTofF[c_id])
        cluster.p_Ind.push_back(c.p_Ind[c_id])
import pycwb
import os, glob


def create_frame_noise(gROOT, ROOT):
    pycwb_path = os.path.dirname(os.path.abspath(pycwb.__file__))

    gROOT.LoadMacro(f"{pycwb_path}/shared/CreateFramesNOISE.C")
    ROOT.CreateFramesNOISE()


def setup_sim_data(detectors, working_dir=os.getcwd()):
    for det in detectors:
        with open(f"{working_dir}/input/{det}.frames", 'w') as t:
            t.write(glob.glob(f"{working_dir}/frames/*/{det}*.gwf")[0])

    with open(f'{working_dir}/input/inspiral.in', 'w') as t:
        t.write("931158200    931158600\n")
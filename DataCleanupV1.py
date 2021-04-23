import pandas as pd
import numpy as np
import os
import tkinter as tk
import nmrglue as ng
from tkinter import filedialog as fd
from natsort import os_sorted

root = tk.Tk()

#Section allows for user to select crystal of intrest so further functions can grab an axis out of selected file
direct = fd.askdirectory(parent = root, title = 'Please select a crystal directory')
print('working with files in ' + direct)
root.destroy()
os.chdir(direct)

#sets axis in crystal of intrest to a list of these axis
subdirs = []
for (dirpath, dirnames, filenames) in os.walk(direct):
    subdirs.extend(dirnames)
    print(subdirs)
    break

#asks for Nuc of intrest and runs the parsing funtion for each axis as pulled from previous section
nuc = ["Li7", "P31"]
ang= [ 0, np.pi/12, 2 * np.pi/12, 3 * np.pi/12, 4 * np.pi/12, 5 * np.pi/12, 6 * np.pi/12, 7 * np.pi/12, 8 * np.pi/12, 9 * np.pi/12, 10 * np.pi/12, 11 * np.pi/12, np.pi]

def ppm_to_Hz(ppm, refFrqMHz):
    return((ppm * refFrqMHz) + (refFrqMHz * 1e6))

"""
This Function takes in the name of an axis folder and a String naming a Nucleus(Li7 or P31)
returns a dataframe with the colombs of the Angle, and (Real intensity and the Resonance Frequency location) of each of the files peak/max intensity value
"""
def compileMax(folder, nucleus):
    os.chdir(direct + "\\" + folder)
    txtFiles = os_sorted([x for x in os.listdir() if '.txt' in x and nucleus in x and folder in x])

    #Decleration of Variables and Dataframes
    df_out = pd.DataFrame(columns = ["Angle", "Real", "Hz"])
    peakPos= []
    realIntensityVal= []

    if nucleus == ("P31"):
        vunit = "Hz"
    if nucleus == ("Li7"):
        vunit = "ppm"

    print(folder)

    #reads each text file in axis folder and appends Real intensity to the declared list and its position in whichever unit the text file already has(ppm or Hz)
    for f in txtFiles:
        df =  pd.read_csv(
            f , sep="\\t", skiprows=2, engine="python")

        realIntensityVal.append(df["Real"].max())
        peakPos.append(df[vunit][df["Real"].idxmax()])


    df_out["Angle"] = ang
    df_out["Real"] = realIntensityVal

    #Checks nucleus to see wether Res Frq needs to be converted to Hz and once converted is added to Hz colum of output dataframe
    if nucleus == ("P31"):
        df_out["Hz"] = peakPos

    if nucleus == ("Li7"):
        dic, data = ng.tecmag.read(f.strip(".txt") + ".tnt")
        ppm_in_Hz = []
        for i in peakPos:
            ppm_in_Hz.append(ppm_to_Hz(i, dic["ob_freq"][0]))
        df_out["Hz"] = ppm_in_Hz

    return(df_out)

#Reads list of Nuclei and outputs a csv file in the the axis parent folder
for n in nuc:

    df_final = pd.DataFrame(ang, columns = ['Rotation Angle (rads)'])

    for fol in subdirs:

        df_final.insert(1, fol, compileMax(fol, n)["Hz"], True)

        df_final.to_csv(direct + "\\"  + n + os.path.basename(direct) + ".csv", header = False,  index=False)

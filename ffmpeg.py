from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime
import subprocess
from shutil import rmtree
import logging
from time import time

load_dotenv()


infolder = Path(os.getenv("CONV_IN_PATH")).resolve()
outfolder = Path(os.getenv("CONV_OUT_PATH")).resolve()
tempfolder = Path(os.getenv("CONV_TMP_PATH")).resolve() / "zonemerger"


def make_outfolder(monitor_left:int, monitor_right:int) -> Path:
    p = outfolder / f"{monitor_left}_{monitor_right}"
    if not p.exists():
        os.mkdir(str(p))
    else:
        if not p.is_dir():
            os.unlink(str(p))
            os.mkdir(str(p))
    return p


def init():
    if not tempfolder.exists():
        os.mkdir(str(tempfolder))


def cleanup():
    rmtree(str(tempfolder))


def combine(monitor_left, monitor_right):
    # make a 600s black file to replace missing files with
    blackfile = tempfolder / "black600.mp4"
    if not blackfile.exists():
        com = f"ffmpeg -y -f lavfi -i \"color=black:s=1920x1080:r=25\" -c:v libx264 -t 600 {blackfile} ;"
        subprocess.run(com, shell=True)
    # clear trash
    tmp = tempfolder / "tmp"
    if tmp.exists():
        rmtree(str(tmp))
    # cap all videos to 10 minutes
    capped_l = []
    capped_r = []
    for l, r in zip(monitor_left, monitor_right):
        pl = cap_at_600s(l)
        pr = cap_at_600s(r)
        if pl.exists() and pr.exists():
            capped_l.append(pl)
            capped_r.append(pr)
        elif pl.exists():
            capped_l.append(pl)
            capped_r.append(blackfile)
            print("no Right ! :()")
        elif pr.exists():
            capped_l.append(blackfile)
            capped_r.append(pr)
            print("no Left ! :()")
    # combine the monitors individually
    if not capped_l:
        # no files found!
        return
    vidlist_l = tmp / "vidlist_l.txt"
    with open(vidlist_l, "w") as f:
        f.writelines([f"file {c}\n" for c in capped_l])
    vidlist_r = tmp / "vidlist_r.txt"
    with open(vidlist_r, "w") as f:
        f.writelines([f"file {c}\n" for c in capped_r])

    com = "ffmpeg -f concat -safe 0 -i {} -c copy {};"
    out_l = tmp / "out_l.mp4"
    out_r = tmp / "out_r.mp4"
    subprocess.run(com.format(vidlist_l, out_l), shell=True)
    subprocess.run(com.format(vidlist_r, out_r), shell=True)
    # finally, merge the videos side by side
    of = make_outfolder(monitor_left[0]["MonitorId"], monitor_right[0]["MonitorId"])
    outname = monitor_left[0]["StartDateTime"].strftime("%Y_%m_%d-%H_%M_output.mp4")
    outf = of / outname
    com = f"ffmpeg -y {os.getenv('CONV_HWACCEL')} -i {out_l} -i {out_r} -filter_complex hstack {os.getenv('CONV_ENCODING')} {outf};"
    logging.info(f"Running: {com}")
    start = time()
    subprocess.run(com, shell=True)
    logging.info(f"ffmpeg command done, took {time()-start:.1f} seconds")


def fix_length(mon:int, day:datetime, event_a:dict, event_b:dict) -> list:
    raise DeprecationWarning(" Not used DEADCODE ")
    vid_a = event_a["DefaultVideo"]
    #vid_b = event_b["DefaultVideo"]
    infile_a = infolder / str(mon) / day.strftime("%Y-%m-%d") / vid_a.split("-")[0] / vid_a
    #infile_b = infolder / str(mon) / day.strftime("%Y-%m-%d") / vid_b.split("-")[0] / vid_b
    end_a = event_a["EndDateTime"]
    start_b = event_b["StartEndTime"]
    if end_a < start_b:
        # video to short. create a black screen and append to existing video
        seconds = (start_b - end_a).total_seconds()
        blackfile = outfolder / f"empty_{seconds}.mp4"
        if not blackfile.exists():
            command = f"ffmpeg -f lavfi -i \"color=black:s=1920x1080:r=25\" -c:v libx264 -t {seconds} {blackfile}"
            subprocess.run(command)
        return [infile_a, blackfile]
    elif end_a > start_b:
        # video to long, remove overtime
        pass
    else:
        # perfect length, do nothing
        return [infile_a]


def cap_at_600s(event):
    monitor = event["MonitorId"]
    video = event["DefaultVideo"]
    day = event["StartDateTime"]
    infile = infolder / str(monitor) / day.strftime("%Y-%m-%d") / video.split("-")[0] / video
    tmp = tempfolder / "tmp"
    if not tmp.exists():
        os.mkdir(str(tmp))
    outfile = tmp / video
    command = f"ffmpeg -v quiet -sseof -600 -i {infile} -c copy {outfile};"
    subprocess.run(command, shell=True)
    return outfile


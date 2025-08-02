# -*- encoding: utf-8 -*-

import os
import pandas as pd
import re


def time_bands(t: int) -> int:
    # t < 10e2:		7
    # 10e2 <= t < 10e3:	6
    # 10e3 <= t < 10e4:	5
    # 10e4 <= t < 10e5:	4
    # 10e5 <= t < 10e6:	3
    # 10e6 <= t < 10e7: 2
    # 10e7 <= t:	1
    if t < 10**2:
        return 7
    elif 10**2 <= t < 10**3:
        return 6
    elif 10**3 <= t < 10**4:
        return 5
    elif 10**4 <= t < 10**5:
        return 4
    elif 10**5 <= t < 10**6:
        return 3
    elif 10**6 <= t < 10**7:
        return 2
    else:
        return 1


def trans_depth(d: str) -> int:
    ptn = re.compile(r"約([0-9].*)km")
    if d == "ごく浅い":
        return 0
    else:
        depth = int(re.findall(ptn, d)[0])
        return depth * -1


if __name__ == "__main__":

    YEAR_FROM = 2025

    df = pd.read_csv(os.path.join("data", "data_in_21pages.csv"), encoding="cp932", parse_dates=["happened_time"])
    df = df[["lon", "lat", "happened_time", "intensity_scale", "magnitude_scale", "depth"]]

    # sort time by ascending
    df = df.sort_values(by="happened_time").reset_index(drop=True)

    # calculate diff seconds of happened_time and band them in range
    df["diff_time"] = df["happened_time"].diff()
    df["diff_sec"] = df["diff_time"].map(lambda t: t.days * 86400 + t.seconds)
    df["diff_bands"] = df["diff_sec"].map(lambda t: time_bands(t))

    # translate depth in word to in number
    df["depth_km"] = df["depth"].map(lambda d: trans_depth(d))

    # filter the requirement year range
    df = df[df["happened_time"].dt.year >= YEAR_FROM].reset_index(drop=True)

    # count times happened at same location
    df["lon_lat"] = df[["lon", "lat"]].apply(lambda x: f"{x.lon}_{x.lat}", axis=1)
    times_dict = df["lon_lat"].value_counts().to_dict()
    df["times"] = [times_dict[_] for _ in df["lon_lat"]]

    df = df[["lon", "lat", "happened_time", "intensity_scale", "magnitude_scale", "depth_km", "diff_bands", "times"]]
    df.to_csv(os.path.join("data", f"data_{YEAR_FROM}_formatted.csv"), index=False, encoding="cp932")


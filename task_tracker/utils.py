# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_utils.ipynb.

# %% auto 0
__all__ = ['save_trial', 'load_trial', 'transcribe_audio_to_task', 'get_duration_in_s_from_timestamps', 'get_colors',
           'create_cumulative_bar_plots', 'create_cumulative_tie_plots', 'create_cumulative_dataframe',
           'create_timeline', 'create_cumulative_pie_plots_per_lane', 'create_cumulative_bar_plots_per_lane',
           'get_number_of_columns']

# %% ../nbs/03_utils.ipynb 3
import time
import datetime
from typing import List
from pathlib import Path
import pickle

from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import speech_recognition as sr

# %% ../nbs/03_utils.ipynb 4
def save_trial(trial):
    pickled_trial = pickle.dumps(trial)
    with open(trial.out_dir.joinpath("trial.p"), 'wb') as file:
        pickle.dump(pickled_trial, file)

# %% ../nbs/03_utils.ipynb 6
def load_trial(tasks_dir):
    loaded_trial = None
    for file in Path(tasks_dir).iterdir():
        if file.suffix == ".p":
            with open(file, 'rb') as pickled_file:
                loaded_pickled_trial = pickle.load(pickled_file)
            loaded_trial = pickle.loads(loaded_pickled_trial)
    if loaded_trial is None:
        raise FileNotFoundError("No pickle file found in this directory!")
    return loaded_trial

# %% ../nbs/03_utils.ipynb 8
def transcribe_audio_to_task(task, r, file, trial):
    duration = get_duration_in_s_from_timestamps(task.start_time, task.end_time)
    with file as source:
        start = get_duration_in_s_from_timestamps(trial.start_time, task.start_time)
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.record(source, offset=start, duration=duration)
    try:
        description = r.recognize_google(audio, language="de-DE")
    except sr.UnknownValueError:
        description = []
    task.add_description(description)

# %% ../nbs/03_utils.ipynb 9
def get_duration_in_s_from_timestamps(start_time_stamp, end_time_stamp=None):
    if end_time_stamp is None:
        end_time_stamp = round(time.time(), 4)
    return datetime.timedelta(seconds=end_time_stamp-start_time_stamp).total_seconds()

# %% ../nbs/03_utils.ipynb 10
def get_colors(task_names, palette_name="colorblind"):
    if len(task_names) > 20:
        palette_name = "husl"
    cmap = sns.color_palette(palette_name, len(task_names))
    colors = {name : color for name, color in zip(task_names, cmap)}
    return colors

# %% ../nbs/03_utils.ipynb 11
def create_cumulative_bar_plots(d, task_names, colors, bar_height = 1):
    artist_dict = {"Pause": None}
    
    fig, ax = plt.subplots()
    for task in task_names:
        if task != "Pause":
            task_subset = d.loc[d["task_name"]==task, :]
            height = task_subset.sum()["duration_in_s"]
            plt.bar(task, height, color=colors[task])
    ax.set_ylabel("cumulative time [s]")
    ax.set_xlabel("tasks")
    plt.legend(artist_dict.values(), artist_dict.keys())
    plt.close()
    return fig

# %% ../nbs/03_utils.ipynb 12
def create_cumulative_tie_plots(d, task_names, colors, bar_height = 1):
    artist_dict = {"Pause": None}

    fig, ax = plt.subplots()
    pieces = {}
    for task in task_names:
        if task != "Pause":
            task_subset = d.loc[d["task_name"]==task, :]
            pieces[task] = task_subset.sum()["duration_in_s"]
    plt.pie(pieces.values(), labels = [f"{key}\n{pieces[key].round(2)}s" for key in pieces],  colors=colors.values()) #, explode = [0.1]*len(pieces),
    plt.close()
    return fig

# %% ../nbs/03_utils.ipynb 13
def create_cumulative_dataframe(d, task_names=None):
    pieces = {}
    task_names = d["task_name"].unique()
    
    for task in task_names:
        if task != "Pause":
            task_subset = d.loc[d["task_name"]==task, :]
            pieces[task] = task_subset.sum()["duration_in_s"]
    return pd.DataFrame(pieces, index=["cumulative time [s]"])

# %% ../nbs/03_utils.ipynb 14
def create_timeline(d, task_names, colors, bar_height = 1):
    artist_dict = {"Pause": None}

    fig, ax = plt.subplots()
    for task_number in d["task_number"].unique():
        task = d.loc[(d["task_number"]==task_number) & (d["task_name"]!="Pause"), :]
        task_start_time = task.loc[: , "start_time"]
        task_duration = get_duration_in_s_from_timestamps(task.loc[: , "start_time"].values[0], task.loc[: , "end_time"].values[0])
        task_name = task.loc[: , "task_name"]
        lane = task.loc[: , "lane"]
        artist_dict[task_name.values[0]] = plt.barh(lane, task_duration, bar_height, left=task_start_time, color=colors[task_name.values[0]])
        pauses = d.loc[(d["task_number"]==task_number) & (d["task_name"]=="Pause"), :]
        for pause in pauses.index:
            pause_start_time = pauses.loc[pause , "start_time"]
            pause_duration = pauses.loc[pause , "duration_in_s"]
            artist_dict["Pause"] = plt.barh(lane, pause_duration, bar_height, left=pause_start_time, color = "grey", alpha = 0.5)
    ax.set_xlabel("time [s]")
    ax.set_ylabel("Tasks")
    plt.legend(artist_dict.values(), artist_dict.keys())
    plt.close()
    return fig

# %% ../nbs/03_utils.ipynb 15
def create_cumulative_pie_plots_per_lane(dataframe_per_subtasks):
    cols, rows = get_number_of_columns(len(dataframe_per_subtasks.columns))
    fig = plt.figure(figsize = (rows*6, 4*cols))
    gs = GridSpec(cols, rows)

    i = 0
    n = 0
    for col in dataframe_per_subtasks.columns:
        ax = plt.subplot(gs[n, i])
        ax.pie(dataframe_per_subtasks.loc[:, col].dropna(), labels = [f'{key}\n{value.round(2)}s' for key, value in zip(dataframe_per_subtasks.loc[:, col].dropna().keys(), dataframe_per_subtasks.loc[:, col].dropna().values)])
        ax.set_title(f"{col}\nCumulative duration [s]")
        if i + 1 < rows:
            i += 1
        else:
            i = 0
            n += 1

    plt.close()
    return fig

# %% ../nbs/03_utils.ipynb 16
def create_cumulative_bar_plots_per_lane(dataframe_per_subtasks):
    cols, rows = get_number_of_columns(len(dataframe_per_subtasks.columns))
    
    fig = plt.figure(figsize = (rows*6, 4*cols))
    gs = GridSpec(cols, rows)

    i = 0
    n = 0
    for col in dataframe_per_subtasks.columns:
        ax = plt.subplot(gs[n, i])
        ax.bar([f'{key}' for key in dataframe_per_subtasks.loc[:, col].dropna().keys()], dataframe_per_subtasks.loc[:, col].dropna())
        ax.set_title(f"{col}\nCumulative duration [s]")
        if i + 1 < rows:
            i += 1
        else:
            i = 0
            n += 1
    plt.close()
    return fig

# %% ../nbs/03_utils.ipynb 17
def get_number_of_columns(columns, plots_in_one_row = 4):
    min_cols = columns//plots_in_one_row
    if columns%plots_in_one_row != 0:
        cols = min_cols + 1
    else:
        cols = min_cols
    return cols, plots_in_one_row

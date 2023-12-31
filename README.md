# task-tracker

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Install

Task-tracker is available on pip!

``` sh
pip install task-tracking==0.0.2
```

## How to use

*Example on how to use task-tracker on a `lasagne recipe`.*

<div>

> **Note**
>
> You can find the notebook and the results of the `lasagne recipe` at
> <https://github.com/KonKob/task-tracker/blob/main/test_data>.

</div>

------------------------------------------------------------------------

### This is how the landing page looks like after completing a trial:

![landing
page](https://github.com/KonKob/task-tracker/blob/main/media/landing_page.png?raw=true)

- Whenever the trial is started here, an audio recording is started,
  that can be transcribed after completion of the trial.

- At the right you see the timeline of tasks over the session so far.
  You can update it at any time.

- In the middle of the landing page, you can add a description manually
  to running or finished tasks.

- The proband metadata can be saved at any time by clicking
  `Export proband metadata`.

- To pause all tasks, you can click `Start pause for all` during a
  running trial.

### The proband metadata can be entered in the following mask:

![proband
metadata](https://github.com/KonKob/task-tracker/blob/main/media/proband_metadata.png?raw=true)

### Tasks, that you want to track, are shown in different tabs.

![task
page](https://github.com/KonKob/task-tracker/blob/main/media/task_page.png?raw=true)

- Whenever you click on a task, this task is started and another task
  running in this tab is ended. You can end a task by clicking
  `No task running` as well.

- If you find, that you forgot a tasks, you can add it by entering the
  name in the grey line `Other` and then clicking the grey button
  `Other`.

- To pause a task, just hit `Start pause`.

------------------------------------------------------------------------

### Exporting the results creates excel files.

``` python
#from task_tracker.utils import load_trial
#trial = load_trial("../test_data/2023-08-07_17.43.23_0000_Chef/")
#trial.tasks_dataframe.head()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead th {
        text-align: right;
    }
</style>

|     | lane               | duration_in_s | task_number | task_name | start_time | end_time | description_0 |
|-----|--------------------|---------------|-------------|-----------|------------|----------|---------------|
| 0   | Kitchen appliances | 1.3528        | 12          | Pause     | 203.6099   | 204.9627 | 220°C         |
| 1   | Kitchen appliances | 52.8952       | 6           | Stove     | 89.5415    | 142.4367 | NaN           |
| 2   | Kitchen appliances | 111.9687      | 12          | Oven      | 142.4370   | 255.7585 | 220°C         |
| 3   | Ingredients        | 28.0470       | 0           | Onions    | 10.3749    | 38.4219  | NaN           |
| 4   | Ingredients        | 19.8456       | 2           | Carrots   | 39.5850    | 59.4306  | NaN           |

</div>

### For visualization, several plots are created.

#### The cumulative duration spent in certain tasks can be shown as bar and tie plots.

![cumulative duration of tasks in
trial](https://github.com/KonKob/task-tracker/blob/main/test_data/2023-08-07_17.43.23_0000_Chef/2023-08-07_17.47.39_cumulative_tie_plots.png?raw=true)

#### It can also be shown, how much time was spent in tasks running in parallel to other tasks.

![tie plot per
task](https://github.com/KonKob/task-tracker/blob/main/test_data/2023-08-07_17.43.23_0000_Chef/2023-08-07_17.47.39_pie_plots_per_lane.png?raw=true)

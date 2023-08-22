# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_interfaces.ipynb.

# %% auto 0
__all__ = ['Main_Interface', 'Proband_Interface', 'Sub_Interface', 'Correct_Transcription_Interface']

# %% ../nbs/02_interfaces.ipynb 3
import time
import datetime
from abc import ABC, abstractmethod, abstractproperty
from typing import List
from pathlib import Path

import ipywidgets as widgets
import seaborn as sns
from scipy.io.wavfile import read

from .trial_components import Trial, Task, Segment, Coding_Category
from .utils import create_timeline, save_trial, load_trial

# %% ../nbs/02_interfaces.ipynb 4
class Main_Interface():
    """
    The main interface, with which the user interacts.
    Contains a landing page, several `Sub_Interface`objects and the `Proband_Interface`.
    """
    def __init__(self, trial):
        self.all_paused = False
        self.trial = trial
        self.interfaces = self._create_sub_interfaces(self.trial.task_dict)
        self.pause_button = self._create_pause_button()
        self.proband_interface = self._create_proband_interface(trial.demographic_dict)
        export_proband_button = self._create_proband_export_button()
        start_trial_button = self._create_start_trial_button()
        self.description_task_dropdown, add_description_button, self.description_field, self.descriptions_dropdown = self._create_description_widgets(trial.descriptions_preset)
        self.current_status, self.graphical_output, update_status = self._create_trial_overview()
        self.main_interface = self._create_main_interface(self.pause_button, export_proband_button, start_trial_button, self.description_task_dropdown, add_description_button, self.description_field, self.descriptions_dropdown, self.current_status, self.graphical_output, update_status)
        self.gui = self._merge_interfaces_into_gui(self.interfaces, self.main_interface, self.proband_interface)
        self.all_children = self.gui.children
        self.all_titles = self.gui.titles
        self.not_running_children = (self.gui.children[0], self.gui.children[-1])
        self.not_running_titles = ["Main", "Proband"]
        self.gui.children = self.not_running_children
        self.gui.titles = self.not_running_titles
        self.trial_running = False
        
    def _on_add_description_button_clicked(self, b):
        if self.description_task_dropdown.value is not None:
            task_name, task_number = self.description_task_dropdown.value.split("_")
            for task in self.trial.history.current_tasks.values():
                if task is not None:
                    if task.task_number == int(task_number):
                        task.add_description(self.description_field.value + self.descriptions_dropdown.value, round(time.time(), 4)-self.trial.start_time)
            for lane in self.trial.history.tasks:
                for task in self.trial.history.tasks[lane]:
                    if task is not None:
                        if task.task_number == int(task_number):
                            task.add_description(self.description_field.value + self.descriptions_dropdown.value, round(time.time(), 4)-self.trial.start_time)
            self.description_field.value = ""
            self.descriptions_dropdown.value = ""
        else:
            print("You didn't select a task!")
    
    def _on_update_status_button_clicked(self, b):
        d = self.trial.history.export_tasks()
        
        task_names = d["task_name"].unique()
        for task_name in task_names:
            if task_name not in self.trial.colors:
                self.trial.colors[task_name] = sns.colors.xkcd_rgb["black"]
                
        fig = create_timeline(d=d, task_names = d["task_name"].unique(), colors = self.trial.colors)
        filename = self.trial.out_dir.joinpath("timeline.png")
        fig.savefig(filename)
        file = open(filename, "rb")
        self.graphical_output.value = file.read()
        self.description_task_dropdown.options=(f"{task.task_name}_{task.task_number}" for task in list(self.trial.history.current_tasks.values()) + [task for lane in self.trial.history.tasks.values() for task in lane] if task is not None)
        active_tasks = [(lane, self.trial.history.current_tasks[lane].task_name) for lane in self.trial.history.current_tasks if self.trial.history.current_tasks[lane] is not None]
        self.current_status.value = f"Active tasks: {active_tasks}" if active_tasks else "No tasks running"
        
    def _create_trial_overview(self):
        current_status = widgets.Label("No tasks running")
        graphical_output = widgets.Image()
        layout = widgets.Layout(width="100%", height="100px")
        update_button = widgets.Button(description="Update trial overview", icon = "refresh", layout=layout, style={"font_size": "15px"})
        update_button.on_click(self._on_update_status_button_clicked)
        return current_status, graphical_output, update_button  
        
    def _create_description_widgets(self, descriptions_preset):
        description_task_dropdown = widgets.Dropdown(description="Select task", style = {'description_width': 'initial'})
        layout = widgets.Layout(width="100%", height="100px")
        add_description_button = widgets.Button(description="Add description to selected task!", layout = layout, icon = "plus", style={"font_size": "15px"})
        add_description_button.on_click(self._on_add_description_button_clicked)
        description_field = widgets.Textarea(description="Enter description here!", style = {'description_width': 'initial'})
        description_field.layout.width = "100%"
        description_field.layout.height = "275px"
        descriptions_dropdown = widgets.Dropdown(description="Select description", options = [""] + descriptions_preset, style = {'description_width': 'initial'})
        return description_task_dropdown, add_description_button, description_field, descriptions_dropdown
        
    def _create_start_trial_button(self):
        layout = widgets.Layout(width="100%", height="100px")
        if not self.trial.started:
            start_button = widgets.Button(description="Start trial", layout=layout, style={"font_size": "25px"})
            start_button.style.button_color = "green"
        else:
            start_button = widgets.Button(description="Trial ended", layout=layout, style={"font_size": "25px"}, disabled=True)
            start_button.style.button_color = "firebrick"
            self.pause_button.disabled = True
        start_button.on_click(self._on_start_button_clicked)
        return start_button
    
    def _on_start_button_clicked(self, b):
        if not self.trial.started:
            self.gui.children = self.all_children
            self.gui.titles = self.all_titles
            self.trial.set_start_time()
            if not self.trial.audio_record.running:
                self.trial.audio_record.start()
            b.style.button_color = "firebrick"
            b.description = "End trial"
            self.pause_button.disabled = False
        else:
            if self.trial.audio_record.running:
                self.trial.audio_record.end()
            self.gui.children = self.not_running_children
            self.gui.titles = self.not_running_titles
            b.disabled = True
            b.description = "Trial ended"
            self.pause_button.disabled = True
            self.pause_button.disabled = True
            self.trial.end_trial()
            for lane in self.trial.history.current_tasks:
                    if self.trial.history.current_tasks[lane] is not None:
                        if self.trial.history.current_tasks[lane].running:
                            self.trial.history.current_tasks[lane].end()
                            self.trial.history.add_current_task_to_history(lane)
                            for pause in self.trial.history.current_tasks[lane].pauses:
                                self.trial.history.add_pause(pause)
                        self.trial.history.current_tasks[lane] = None
        
    def _create_proband_interface(self, demographics):
        return Proband_Interface(demographics)
    
    def _create_sub_interfaces(self, tasks):
        if type(tasks) == list:
            interfaces = {"Tasks": Sub_Interface(tasks, self.trial)}
        else:
            interfaces = {task: Sub_Interface(tasks[task], self.trial, lane=task) for task in tasks}
        return interfaces
    
    def _create_main_interface(self, pause_button, export_proband_button, start_trial_button, description_task_dropdown, add_description_button, description_field, descriptions_dropdown, current_status, graphical_output, update_status):
        status = widgets.VBox([current_status, graphical_output, update_status], layout=widgets.Layout(width="50%", height="100%", border='solid thin', margin="5px", align_items = "center"))
        buttons = widgets.VBox([pause_button, export_proband_button, start_trial_button], layout=widgets.Layout(width="25%", height="100%", border='solid thin', margin="5px", align_items = "center"))
        descriptions = widgets.VBox([description_task_dropdown, description_field, descriptions_dropdown, add_description_button], layout=widgets.Layout(width="25%", height="100%", border='solid thin', margin="5px", align_items = "center"))
        return widgets.HBox([buttons, descriptions, status])
    
    def _merge_interfaces_into_gui(self, interfaces, main_interface, proband_interface):
        children = [main_interface] + [interface.interface for interface in interfaces.values()] + [proband_interface.interface]
        tab = widgets.Tab()
        tab.children = children
        tab.titles = ["Main"] + list(interfaces.keys()) + ["Proband"]
        return tab
    
    def _create_pause_button(self):
        layout = widgets.Layout(width="100%", height="100px")
        pause_button = widgets.Button(description="Start pause for all", layout=layout, style={"font_size": "25px"}, disabled=True)
        pause_button.style.button_color = "gold"
        pause_button.on_click(self._on_pause_button_clicked)
        return pause_button
    
    def _create_proband_export_button(self):
        layout = widgets.Layout(width="100%", height="100px")
        proband_button = widgets.Button(description="Export proband information", layout=layout, style={"font_size": "20px"})
        proband_button.style.button_color = "darkgray"
        proband_button.on_click(self._on_proband_button_clicked)
        return proband_button
    
    def _on_proband_button_clicked(self, b):
        self.proband_interface.export_values_to_proband(self.trial.proband)
        b.description = "Update proband information"
    
    def _on_pause_button_clicked(self, b):
        if not self.all_paused:
            b.description = "End pause for all"
            b.icon = "circle"
            b.style.button_color = "firebrick"
            for task in self.trial.history.current_tasks.values():
                if task is not None:
                    if task.running:
                        if not task.currently_paused:
                            task.pause_start()
            self.all_paused = True
            self.gui.children = self.not_running_children
            self.gui.titles = self.not_running_titles
        else:
            for task in self.trial.history.current_tasks.values():
                if task is not None:
                    if task.running:
                        if task.currently_paused: # derzeit wird die pause gestoppt auch wenn schon vor der globalen pause pausiert war
                            task.pause_end()
            b.description = "Start pause for all"
            b.style.button_color = "gold"
            b.icon = ""
            self.all_paused = False
            self.gui.children = self.all_children
            self.gui.titles = self.all_titles

# %% ../nbs/02_interfaces.ipynb 5
class Proband_Interface():
    """
    Interface to acquire metadata related to the proband.
    The metadata can be saved to the `Proband` object.
    """
    def __init__(self, demographics, n_in_one_row = 4):
        self.widget_dict = self._create_demographics(demographics)
        self.interface = self._arrange_widgets(self.widget_dict, n_in_one_row)
    
    def _create_demographics(self, demographics):
        style = {'description_width': 'initial'}
        return {name: getattr(widgets, typ)(description=name, style=style, options=options) for name, typ, options in zip(demographics["descriptions"], demographics["widget_types"], demographics["values"])}
    
    def _arrange_widgets(self, widget_list, n_in_one_row):
        hbox_elements = []
        for i in range(1, len(widget_list)//n_in_one_row+2):
            hbox_elements.append(widgets.HBox(list(widget_list.values())[(n_in_one_row*(i-1)):(n_in_one_row*i)]))
        return widgets.VBox(hbox_elements)
    
    def export_values_to_proband(self, proband):
        for widget in self.widget_dict:
            proband.set_metadata(self.widget_dict[widget].value, widget)

# %% ../nbs/02_interfaces.ipynb 6
class Sub_Interface():
    """
    Interface to record `Task`-objects. Corresponds to one Tab in `Main_Interface`.
    """
    def __init__(self, tasks: List, trial: Trial, lane = "Tasks"):
        self.trial = trial
        self.n_in_one_row = 5
        self.buttons = self._create_task_buttons(tasks)
        self.pause_button = self._create_pause_button()
        self.lane = lane
        self.new_text = self._create_new_task_text()
        self.interface = self._create_interface(self.buttons, self.new_text, self.pause_button)
        self.trial.history.current_tasks[self.lane] = None
        
    def _create_interface(self, buttons, text, pause):
        tasks_vbox = self._arrange_widgets(list(self.buttons.values()), self.n_in_one_row)
        return widgets.VBox([tasks_vbox, text, pause])
        
    def _arrange_widgets(self, widget_list, n_in_one_row):
        hbox_elements = []
        for i in range(1, len(widget_list)//n_in_one_row+2):
            hbox_elements.append(widgets.HBox(widget_list[(n_in_one_row*(i-1)):(n_in_one_row*i)]))
        return widgets.VBox(hbox_elements)
        
    def _create_task_buttons(self, tasks):
        layout = widgets.Layout(width=f"{100/self.n_in_one_row}%", height="100px")
        task_buttons = {task: widgets.Button(description = task, layout=layout, style={"font_size": "15px"}) for task in tasks}
        for button in task_buttons.values():
            button.on_click(self._on_task_button_clicked)
        task_buttons["Sonstige"] = widgets.Button(description = "Other", layout=layout, style={"font_size": "15px"})
        task_buttons["Sonstige"].on_click(self._on_new_task_button_clicked)
        task_buttons["Sonstige"].style.button_color = "darkgray"
        task_buttons["Keine neue Aufgabe"] = widgets.Button(description = "No task running", layout=layout, icon = "circle", style={"font_size": "15px"})
        task_buttons["Keine neue Aufgabe"].style.button_color = "firebrick"
        task_buttons["Keine neue Aufgabe"].on_click(self._on_end_task_no_new_task_button_clicked)
        return task_buttons
    
    def _create_pause_button(self):
        layout = widgets.Layout(width="100%", height="100px")
        pause_button = widgets.Button(description = "Start pause", disabled = False, layout=layout, style={"font_size": "25px"})
        pause_button.on_click(self._on_pause_button_clicked)
        pause_button.style.button_color = "gold"
        return pause_button
    
    def _on_new_task_button_clicked(self, b):
        self.buttons["Sonstige"].description = self.new_text.value
        self._on_task_button_clicked(b)
        
    def _create_new_task_text(self):
        layout = widgets.Layout(width="100%", height="100px")
        t = widgets.Text("Other", layout=layout)
        t.style.background = "darkgrey"
        return t
    
    def _on_end_task_no_new_task_button_clicked(self, b):
        for button in self.buttons.values():
            button.icon = ""
        self.pause_button.icon = ""
        if self.trial.history.current_tasks[self.lane] is not None:
            if self.trial.history.current_tasks[self.lane].running:
                self.trial.history.current_tasks[self.lane].end()
                self.pause_button.description = "Start pause"
                self.trial.history.add_current_task_to_history(self.lane)
                for pause in self.trial.history.current_tasks[self.lane].pauses:
                    self.trial.history.add_pause(pause)
        self.trial.history.current_tasks[self.lane] = None
        b.icon = "circle"
        
    def _on_pause_button_clicked(self, b):
        if self.trial.history.current_tasks[self.lane] is not None:
            if self.trial.history.current_tasks[self.lane].currently_paused:
                self.trial.history.current_tasks[self.lane].pause_end()
                self.pause_button.description = "Start pause"
                self.pause_button.icon = ""
            else:
                self.trial.history.current_tasks[self.lane].pause_start()
                self.pause_button.description = "End pause"
                self.pause_button.icon = "circle"
                
        
    def _on_task_button_clicked(self, b):
        for button in self.buttons.values():
            button.icon = ""
        self.pause_button.icon = ""
        if self.trial.start_time is None:
            self.trial.set_start_time()
        if self.trial.history.current_tasks[self.lane] is not None:
            if self.trial.history.current_tasks[self.lane].running:
                self.trial.history.current_tasks[self.lane].end()
                self.pause_button.description = "Start pause"
                self.trial.history.add_current_task_to_history(self.lane)
                for pause in self.trial.history.current_tasks[self.lane].pauses:
                    self.trial.history.add_pause(pause)
        b.icon = "circle"
        self.trial.history.current_tasks[self.lane] = Task(task_number=self.trial.task_number, task_name = b.description, lane = self.lane, trial_start_time=self.trial.start_time)
        self.trial.history.current_tasks[self.lane].start()
        self.trial.task_number +=1

# %% ../nbs/02_interfaces.ipynb 7
class Correct_Transcription_Interface():
    """
    Interface to easily check and correct audio transcriptions.
    """
    
    def __init__(self, trial, coding_categories = []):
        self.coded_categories = {}
        self.trial = trial
        samplerate, array = read(trial.audio_record.filename)
        self.coding_categories = ["Nicht ausgewählt"] + coding_categories
        self.segments = [Segment(start_time=segment["start"], end_time=segment["end"], text=segment["text"], ide=i, array_slice=array[int(segment["start"]*samplerate) : int(segment["end"]*samplerate)], tasks=trial.history.tasks, trial=self.trial) for i, segment in enumerate(trial.audio_record.transcription["segments"]) if segment["text"]]
        added_descriptions = [segment.text for segment in self.segments]
        for lane in trial.history.tasks:
            for task in trial.history.tasks[lane]:
                for start_time in task.description:
                    if task.description[start_time] not in self.trial.audio_record.transcription and task.description[start_time] not in added_descriptions:
                        self.segments.append(Segment(start_time=start_time, end_time=start_time, text=task.description[start_time], ide="manuell", array_slice=[], tasks=trial.history.tasks, trial=self.trial))
                        added_descriptions.append(task.description[start_time])
        self.i = 0
        self.description_i = 0
        self.update_current_segment()
        self.interface = self._initialize_widgets()
        
    def _initialize_widgets(self):
        layout = widgets.Layout(width="100%", height="100px")
        go_back_button = widgets.Button(description="Go back!", icon = "arrow-left", layout=layout, style={"font_size": "25px"})
        go_back_button.on_click(self._on_go_back_button_clicked)
        delete_button = widgets.Button(description="Delete segment!", icon="trash", layout=layout, style={"font_size": "25px"})
        delete_button.on_click(self._on_delete_button_clicked)
        set_new_text_button = widgets.Button(description="Replace with new text!", icon="pen", layout=layout, style={"font_size": "25px"})
        set_new_text_button.on_click(self._on_set_new_text_button_clicked)
        play_audio_button = widgets.Button(description="Play recording!", icon = "play", layout=layout, style={"font_size": "25px"})
        play_audio_button.on_click(self._on_play_audio_button_clicked)
        next_description_button = widgets.Button(description=">")
        next_description_button.on_click(self._on_next_description_button_clicked)
        prev_description_button = widgets.Button(description="<")
        prev_description_button.on_click(self._on_prev_description_button_clicked)
        save_button = widgets.Button(description="Save trial", icon="download", layout=layout, style={"font_size": "25px"})
        save_button.on_click(self._on_save_button_clicked)
        
        self.category_dropdown = widgets.Dropdown(options=self.coding_categories, description = "Select Coding Categorie", style = {'description_width': 'initial'}, layout = widgets.Layout(width="100%", height="30px"))
        self.category_text = widgets.Text(description = "New category", style = {'description_width': 'initial'}, layout = widgets.Layout(width="100%", height="30px"))
        new_category = widgets.VBox([self.category_dropdown, self.category_text])
        
        self.select_category_dropdown = widgets.Dropdown(options=["Nicht ausgewählt"], description = "Select Coding Categorie", style = {'description_width': 'initial'}, layout = widgets.Layout(width="100%", height="30px"))
        update_problem_text_button = widgets.Button(description = "Update problem text")
        update_problem_text_button.on_click(self._on_update_problem_text_button_clicked)
        self.problem_text = widgets.Textarea(value="", description="Text of the currently selected existing problem", disabled=True, style = {'description_width': 'initial', "font_size": "25px"})
        self.problem_text.layout.width = "100%"
        self.problem_text.layout.height = "150px"
        select_category = widgets.VBox([self.select_category_dropdown, update_problem_text_button, self.problem_text])
        
        category_tab = widgets.Tab([new_category, select_category])
        category_tab.titles = ["Add to new category", "Select existing category"]
        
        self.new_text_field = widgets.Textarea(description="Enter new text here:", value=self.current_segment.text, style = {'description_width': 'initial', "font_size": "25px"})
        self.new_text_field.layout.width = "100%"
        self.new_text_field.layout.height = "150px"
        self.description = widgets.Label(f"Start time: {self.current_segment.start_time} ID: {self.current_segment.id} / {len(self.segments)-1}", style = {'description_width': 'initial', "font_size": "25px"})
        self.previous_next_segment = widgets.Label(f"ID {self.i+1}: {self.segments[self.i+1].text}", style = {'description_width': 'initial'})
        
        return widgets.VBox([widgets.HBox([prev_description_button, next_description_button, self.previous_next_segment]), self.description, self.new_text_field, widgets.HBox([go_back_button, delete_button, set_new_text_button, play_audio_button]), save_button, category_tab])
    
    
    def _on_update_problem_text_button_clicked(self, b):
        if self.select_category_dropdown.value != "Nicht ausgewählt":
            self.problem_text.value = self.coded_categories[self.select_category_dropdown.value].text
    
    def update_widgets(self):
        self.description.value = f"Start time: {self.current_segment.start_time} ID: {self.current_segment.id} / {len(self.segments)-1}"
        self.new_text_field.value = self.current_segment.text
        self.category_dropdown.value = "Nicht ausgewählt"
        self.select_category_dropdown.value = "Nicht ausgewählt"
        self.category_text.value = ""
        self.problem_text.value = ""
        if self.i < len(self.segments) - 1:
            self.description_i = self.i+1
            self.previous_next_segment.value = f"ID {self.description_i}: {self.segments[self.description_i].text}"
            
    def _on_next_description_button_clicked(self, b):
        if self.description_i < len(self.segments) - 1:
            self.description_i += 1
            self.previous_next_segment.value = f"ID {self.description_i}: {self.segments[self.description_i].text}"
        
    def _on_prev_description_button_clicked(self, b):
        if self.description_i > 0:
            self.description_i -= 1
            self.previous_next_segment.value = f"ID {self.description_i}: {self.segments[self.description_i].text}"

    def update_current_segment(self):
        self.current_segment = self.segments[self.i]
        
    def count_up(self):
        if self.i < len(self.segments) - 1:
            self.i += 1
        else:
            raise UserWarning("Finished trial!")
            
    def count_down(self):
        if self.i > 0:
            self.i -= 1
        else:
            raise UserWarning("First segment reached!")
            
    def _on_go_back_button_clicked(self, b):
        self.count_down()
        self.update_current_segment()
        self.update_widgets()
    
    def _on_delete_button_clicked(self, b):
        self.current_segment.delete_text()
        self.count_up()
        self.update_current_segment()
        self.update_widgets()
    
    def _on_set_new_text_button_clicked(self, b):
        self.current_segment.replace_text(self.new_text_field.value)
        category, category_num = self.get_category()
        if category is not None:
            if (category, category_num) not in self.coded_categories:
                self.coded_categories[(category, category_num)] = Coding_Category(self.current_segment, category)
                self.select_category_dropdown.options = ["Nicht ausgewählt"] + list(self.coded_categories.keys())
            else:
                self.coded_categories[(category, category_num)].add_segment(self.current_segment)
        self.count_up()
        self.update_current_segment()
        self.update_widgets()
    
    def _on_play_audio_button_clicked(self, b):
        self.current_segment.play_segment()
        
    def _on_save_button_clicked(self, b):
        for lane in self.trial.history.tasks:
            for task in self.trial.history.tasks[lane]:
                if type(task)==Task:
                    for key in self.coded_categories:
                        category = self.coded_categories[key]
                        for segment in category.segments:
                            if (segment.start_time > task.start_time and segment.start_time < task.end_time) or (segment.start_time < task.start_time and segment.end_time > task.start_time):
                                if not hasattr(task, "categories"):
                                    task.categories = {"start_time": [], "text": [], "categories": [], "task": [], "proband": []}
                                if category.start_time not in task.categories["start_time"]:
                                    task.categories["start_time"].append(category.start_time)
                                    task.categories["text"].append(category.text)
                                    task.categories["categories"].append(category.category)
                                    task.categories["task"].append(task.task_name)
                                    task.categories["proband"].append(self.trial.proband.proband_ID)
                            
        self.trial.tasks_dataframe = self.trial.history.export_tasks()
        self.trial.tasks_dataframe.to_excel(self.trial.out_dir.joinpath(f"{time.strftime('%Y-%m-%d_%H.%M.%S', self.trial.end_struct_time)}_tasks.xlsx"))
        save_trial(self.trial)
        
    def get_category(self):
        if self.select_category_dropdown.value != "Nicht ausgewählt":
            category, category_num = self.select_category_dropdown.value
        else:
            if not self.category_text.value:
                if self.category_dropdown.value == "Nicht ausgewählt":
                    category = None
                    category_num = None
                else:
                    category = self.category_dropdown.value
                    category_num = len(self.coded_categories) + 1
            else:
                category = self.category_text.value
                if category not in self.coding_categories:
                    self.coding_categories.append(category)
                    self.category_dropdown.options = self.coding_categories
                category_num = len(self.coded_categories) + 1
        return category, category_num

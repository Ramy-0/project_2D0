import flet as ft
import pendulum as pdm
from classes import TaskNode, TaskFolder, Database
from functions import saveDatabaseCSV, loadDatabaseCSV, getChildrenDFS, getParentChain, printTreeDFS
from graphics.gui_themeHandler import get_theme_catppuccin
from regex_extractor import get_info_re
import pendulum as pnd
from typing import Callable, Optional

app_page = None

# @ft.control
class TaskControl(ft.Container):
    # task: TaskNode | TaskFolder = None
    def __init__(self, task:TaskNode|TaskFolder):
        super().__init__()
        self.task=task
        # print(self.task)
        # print(repr(self.task.due_date), type(self.task.due_date))

        self.content = ft.Column(
            controls= [
                ft.Row(
                    controls=[
                        ft.Text(
                            # value= getParentChain(self.task) + '/' + self.task.name
                            spans=[
                                ft.TextSpan(getParentChain(self.task) + '/'),
                                ft.TextSpan(self.task.name, style=ft.TextStyle(weight=ft.FontWeight.BOLD) )
                            ],
                        ),
                        ft.Container(expand=True),  # blankspace
                        ft.Checkbox(
                            label="",
                            value=(self.task.completion == 1.0)
                        ) if type(self.task) == TaskNode else ft.Container(),    # blank
                        ]
                    ),
                ft.Row(
                    controls=[
                        ft.Container(width=20), # indentation basically
                        ft.Container(
                            content = ft.Text(
                                    value=self.task.desc,
                                    
                                    size = 12,
                                    italic= False,
                            ),
                            width=550

                        ),
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Button(
                            content=f"duedate: {pdm.parse(self.task.due_date).format('YYYY/MM/DD - HH:mm') if self.task.due_date else 'None'}", 
                            disabled= True if type(self.task) == TaskFolder else False,   # logic for taskfolder to be implemented
                            on_click=lambda e:show_dueDateTime_dialoge(self.task)
                            ),
                        # ft.Button(
                        #     content=f"duetime: {pdm.parse(self.task.due_date).time().format('HH:mm') if self.task.due_date else 'None'}", 
                        #     disabled=False
                        #     ),
                        ft.Button(
                            content=f"priority: {['None','Low','Mid','High'][int(self.task.priority)]}", 
                            disabled=False,
                            # on_click=lambda e:handle_selectedTask_priority_change(e, self.task)
                            on_click=lambda e: show_priority_dialoge(self.task)
                            ) if self.task.priority is not None else ft.Container(),
                    ]
                )
                ],
            )
        self.on_click = self.set_selectedTask

    def set_selectedTask(self):
        global selected_task
        selected_task = self
        # print(f"selected task changed to {self.task}")
        global parent_text
        parent_text.value = getParentChain(self.task)+'/'+self.task.name
        parent_text.update()

# @ft.control
class DateTimePicker(ft.Column):
    # task: TaskNode = None
    # label: str = "Due"
    # on_change: Optional[Callable] = None

    def __init__(self, task: TaskNode|TaskFolder, label: str = "Due", on_change: Optional[Callable] = None):
        super().__init__(tight = True)
        self.task = task
        self.label = label
        self.on_change_cb = on_change
        self._date = None
        self._time = None
        self._text = ft.Text(value = self._format())
        self.controls = [
                ft.Row(
                    controls = [
                        ft.TextButton("Date", on_click=self._pick_date),
                        ft.TextButton("Time", on_click=self._pick_time),
                        ],
                    wrap = True,
                    ),
                self._text,
                ]
        if self.task.due_date:
            date = pnd.parse(self.task.due_date)
            self._date, self._time = date.date(), date.time()

    def _format(self):
        if not self.task.due_date:
            return f"{self.label}: not set"
        date = pnd.parse(self.task.due_date)
        return f"{self.label}: {date.format('YYYY/MM/DD HH:mm')} ({date.diff_for_humans()})"

    def _pick_date(self, e):
        self.page.show_dialog(
                ft.DatePicker(
                    value = pnd.parse(self.task.due_date).date() if self.task.due_date != '' else None,
                    on_change = self._date_changed,
                    )
                )

    def _pick_time(self, e):
        self.page.show_dialog(
                ft.TimePicker(
                    value = pnd.parse(self.task.due_date).time() if self.task.due_date != '' else None,
                    on_change = self._time_changed,
                    )
                )

    def _date_changed(self, e):
        self._date = pnd.instance(e.control.value)
        self._commit()

    def _time_changed(self, e):
        self._time = pnd.time(e.control.value.hour, e.control.value.minute)
        self._commit()

    def _commit(self):
        date = self._date or pnd.today("local")
        time = self._time or pnd.time(9, 0)
        print("committing", date, time)
        self.task.due_date = pnd.datetime(
                date.year, date.month, date.day, time.hour, time.minute, tz="local"
                ).isoformat(' ')
        print(self.task.due_date, '|', getattr(self.task, "duedate", "no duedate attr"))
        self._text.value = self._format()
        self.update()
        if self.on_change_cb:
            self.on_change_cb()

def change_selectedTask(task):
    if task != None:
        global selected_task
        global parent_text
        if isinstance(task,Database):
            selected_task = None
            parent_text.value = '~'
        else:
            selected_task = task
            # print(f"selected task changed to {task}")
            parent_text.value = getParentChain(task)+'/'+task.name
        parent_text.update()

def set_parent():
    pass
        
def refresh_tasks():
    # logic yet to be implemeted
    # pass
    tasks_view.controls = []
    init_tasks()

def init_tasks():
    for task in tasks_list:
        if isinstance(task, Database):
            # dont write the database name duh
            continue
        tasks_view.controls.append(TaskControl(
            task=task
        ))

def render_tasks():
    '''renders the database on the gui'''
    print("RENDERINGTHEFUCKINGTASKS")
    tasks_view.controls = []    # removes the old tasks
    global task_list
    tasks_list = getChildrenDFS(tasks_database) # get the list of the tasks
    for task in tasks_list:
        if isinstance(task, Database):
            continue
        tasks_view.controls.append(TaskControl(
            task = task
        ))
    tasks_view.update()

def add_task():
    global task_duedate
    global tasks_database

    task_name = task_textField.value
    task_desc = task_descTextField.value
    print("parent: ", selected_task.task.name if selected_task!=None else '~')
    print("name: ", task_name)
    task_desc, task_dict = get_info_re(task_desc)
    if task_duedate is None and task_duetime is None:
        task_duedate = task_dict["deadline"]
    task_priority = task_dict['priority']
    print("desc: ", task_desc)
    print("time: ", task_duetime)
    task = TaskNode(name=task_name, desc=task_desc, due_date=task_duedate, priority=task_priority)
    if selected_task == None:
        tasks_database.add_child(task)
    else:
        selected_task.task.add_child(task)
    print(repr(task))
    printTreeDFS(tasks_database)
    saveDatabaseCSV(tasks_database, force=True)
    reset_task_input()
    tasks_database = loadDatabaseCSV(database_path, force=True)
    render_tasks()

def reset_task_input():
    if task_textField is not None:  # make sure it is initialized first
        task_textField.value = ''
        task_textField.update()
    if task_descTextField is not None:
        task_descTextField.value = ''
        task_descTextField.update()
    change_selectedTask(tasks_database)
    global task_duedate
    task_duedate = None
    if task_dateButton is not None:
        task_dateButton.content = f'duedate: {task_duedate}'
        task_dateButton.update()
    global task_duetime
    task_duetime = None
    if task_timeButton is not None:
        task_timeButton.content = f'duetime: {task_duetime}'
        task_timeButton.update()

def handle_task_duetime_change(e):
    global task_duetime
    task_duetime = e.control.value
    print("time changed:", task_duetime)

    if task_timeButton is not None:
        task_timeButton.content = f"duetime: {task_duetime}"
        task_timeButton.update()

def handle_task_duedate_change(e):
    global task_duedate
    task_duedate = e.control.value.date()   # remove the time from the datetime
    print("date changed:", task_duedate)

    if task_dateButton is not None:
        task_dateButton.content = f"duedate: {task_duedate}"
        task_dateButton.update()

def handle_selectedTask_duetime_change(e, task):
    pass

def handle_selectedTask_priority_change(e, task):
    print(task)

def show_priority_dialoge(task):
    # if priority == None:
    #     priority = 0
    
    task_priority_radioGroup = ft.RadioGroup(
            value = task.priority,
            content = ft.Column(
                [
                    ft.Radio(value=0, label='None'),
                    ft.Radio(value=1, label='Low'),
                    ft.Radio(value=2, label='Mid'),
                    ft.Radio(value=3, label='High')
                ],
                tight = True,
                )
            )

    task_priorityPicker = ft.AlertDialog(
            title = ft.Text("task priority"),
            content = task_priority_radioGroup,
            actions = [
                ft.TextButton("cancel", on_click=lambda e: app_page.pop_dialog()),
                ft.TextButton("confirm", on_click=lambda e:handle_priority_change(task, task_priority_radioGroup.value)), 
                ],
            modal = False,
            )

    app_page.show_dialog(task_priorityPicker)

def show_dueDateTime_dialoge(task):
    print("opening the date time dialog")
    # date_panel = ft.Container(
    #         content = ft.Column(
    #             ft.Text("duedate"),
    #             ft.DatePicker()
    #             ),
    #         padding = 20,
    #         border_radius = 10,
    #         width = 250,
    #         )
    # time_panel = ft.Container(
    #         content = ft.Column(
    #             ft.Text("duetime"),
    #             ft.TimePicker()
    #             ),
    #         padding = 20,
    #         border_radius = 10,
    #         width = 250,
    #         )
    #
    # app_page.show_dialog(ft.AlertDialog(
    #     content = ft.Row(
    #         controls = [date_panel, ft.VerticalDivider(), time_panel]
    #         )
    #     ))
    app_page.show_dialog(
            ft.AlertDialog(
                title = ft.Text("due date and time"),
                content = DateTimePicker(task = task, on_change = on_due_changed)
                )
            )

def on_due_changed():
    saveDatabaseCSV(tasks_database, force = True)
    render_tasks()

def handle_priority_change(task, priority):
    print(task, priority)
    task.priority = priority    # super high level coding here :)
    saveDatabaseCSV(tasks_database, force = True)
    render_tasks()
    app_page.pop_dialog()

title_text = ft.Text(value='2140', size=40, align=ft.Alignment.CENTER, font_family="TitleFont")
task_duedate = None
task_duetime = None
task_timeButton = None
task_dateButton = None
task_timePicker = ft.TimePicker(on_change=handle_task_duetime_change)
task_datePicker = ft.DatePicker(on_change=handle_task_duedate_change)
task_textField = ft.TextField(hint_text="task", expand=True)
add_floatingButton = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_task)
parent_text = ft.Text(value='~', italic=True)
tasks_view = ft.Column(height=400, scroll=ft.ScrollMode.AUTO, expand_loose=True)    # may need to be implemeted in chunks in the future in order to avoid an error when closing the gui when rendering the BIG database, but we can ignore this problem for now due to the typically small size of the database 
database_path = "Database 1_2.csv"
tasks_database = loadDatabaseCSV(database_path)
tasks_list = getChildrenDFS(tasks_database)
selected_task = None    # the task the use is currently selecting
parent_floatingButton = ft.FloatingActionButton(icon=ft.Icons.ACCOUNT_TREE, on_click=lambda:change_selectedTask(tasks_database))


def main(page:ft.Page):
    global app_page
    app_page = page
    page.title = "2140"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.window_width = 400
    page.window_hight = 600
    page.window_resizable = True
    page.padding = 20
    page.fonts = {
        "TitleFont" : "graphics/fonts/jetstream.otf",
        "ContMonoFontLatin" : "graphics/fonts/JetBrainsMono-VariableFont_wght.ttf",
        "ContMonoFontArabic" : "graphics/fonts/Hasubi-Mono[wght].ttf"
    }
    ContFontStack = "ContMonoFontLatin,ContMonoFontArabic"
    
    page.theme, flavor = get_theme_catppuccin('frappe')
    page.theme.font_family = "ContMonoFontLatin"

    global task_timeButton
    task_timeButton = ft.Button(content=f"duetime: {task_duetime}", on_click=lambda _: page.show_dialog(task_timePicker))
    global task_dateButton
    task_dateButton = ft.Button(content=f"duedate: {task_duedate}", on_click=lambda _: page.show_dialog(task_datePicker))

    global task_descTextField
    task_descTextField = ft.TextField(hint_text="desc", expand=True, multiline=True)
    task_descFields = ft.ExpansionTile(
        title="desc",
        controls=[
            task_descTextField,
            ft.Row(controls=[
                task_timeButton,
                task_dateButton
            ],
            ),
        ],
    )

    view = ft.Column(
        width=600,
        scroll=ft.ScrollMode.AUTO,
        # height=600,
        expand=True,
        controls=[
            # title_text,
            ft.Row(
                controls=[
                    parent_floatingButton,
                    parent_text,
                    task_textField,
                    add_floatingButton
                ],
            ),
            task_descFields,
            ft.Divider(),
        tasks_view
        ],
    )

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(view)

    render_tasks()

if __name__ == "__main__":
    # ft.app(target=main) is deprecated
    ft.run(main=main)

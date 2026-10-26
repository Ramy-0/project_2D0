from __future__ import annotations
import random
import string
from pathlib import Path

import pendulum as pdm
from pendulum import DateTime
from pendulum.parsing.exceptions import ParserError

# from functions import printTreeDFS, saveDatabaseCSV, loadDatabaseCSV

class TaskNode:
    '''
    A class representing a task node in a task management system. Each task node has a name, description, unique identifier, priority, creation date, due date, parent node, and a list of child nodes.
    '''
    def __init__(self,name: str, desc:str='', id:str=None, priority:int=0, created_at:DateTime=pdm.now(), due_date:DateTime=None, parent:TaskNode|TaskFolder|Database=None, completion:float=0.0):
        self.name = name
        self.desc = desc                # needed for regex
        self.created_at = created_at    # default to the current timestamp if not provided
        if id is None:
            # generate a unique id based on the type (TaskNode, TaskFolder, Database) and the current timestamp and a random string of 10 characters in the format of 'TN:YYYY-MM-DD:random_string' where random_string is a random string of 10 characters consisting of letters and digits
            self.id = 'TN:' + self.created_at.format('YYYY-MM-DD:HHmmss') +':' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        else:
            self.id = id
        self.priority = priority        # 0: unassigned, 1: low, 2: medium, 3: high
        self.due_date = due_date        # leave as None if not provided meaning no due date, can be set later
        self.parent = parent            # the parent node of the current task node, can be a TaskNode, TaskFolder, or Database
        self.children = []              # a list to hold child TaskNodes
        self.completion = completion    # the percentage of completion of the task node, a float between 0 and 1

    def add_child(self, child: TaskNode):
        '''
        Adds a child TaskNode to the current TaskNode's children list and sets the parent of the child to the current TaskNode.
        '''
        if child in self.children:
            raise ValueError(f"Child with id {child.id} already exists in children of node with id {self.id}")
        elif child.parent is not None:
            raise ValueError(f"Child with id {child.id} already has a parent with id {child.parent.id}")
        else:
            self.children.append(child)
            child.parent = self
            child.set_properties_from_parent()  # set properties of the child based on the parent node

    def add_parent(self, parent):
        parent.add_child(self)

    def remove_child(self, child: TaskNode):
        '''
        Removes a child TaskNode from the current TaskNode's children list and sets the parent of the child to None.
        '''
        try:
            self.children.remove(child)
            child.parent = None
        except ValueError:
            raise ValueError(f"Child with id {child.id} not found in children of node with id {self.id}")

    def set_properties_from_parent(self):
        '''
        Sets the properties of the current TaskNode based on its parent node.
        called in add_child method of the parent node to ensure that the child node inherits properties from the parent node if they are not set.
        '''
        if self.parent:
            if self.priority == 0:  # if priority is unassigned, inherit from parent
                self.priority = self.parent.priority
            if self.due_date is None:  # if due date is not set, inherit from parent
                self.due_date = self.parent.due_date

    def set_property(self, property:str, value:any):
        if property in ['name', 'desc'] and isinstance(value, str):
            setattr(self, property, value)
        elif property in ['parent'] and (isinstance(value, TaskNode) or isinstance(value, TaskFolder) or isinstance(value, Database)):
            setattr(self, property, value)
        elif property in ['completion'] and isinstance(value, float):
            setattr(self, property, value)
        elif property in ['creation_time', 'duedate'] and isinstance(value, DateTime):
            setattr(self, property, value)
        else:
            raise AttributeError(f"the attribute {value} is either unmutable or doesn't exist")

    def __repr__(self):
        # the verbose version
        return f"TaskNode(\n\tname={self.name},\n\tid={self.id},\n\tpriority={self.priority},\n\tcreated_at={self.created_at},\n\tdue_date={self.due_date},\n\tparent_id={self.parent.id if self.parent else None},\n\tchildren_count={len(self.children)},\n\tcompletion={self.completion}\n)"

    def __str__(self):
        # the concise version
        return f"TaskNode: {self.name} (ID: {self.id})"

class TaskFolder(TaskNode):
    '''
    A class representing a task folder in a task management system. Inherits from TaskNode and can contain other TaskNodes or TaskFolders as children.
    It have some unique properties and methods like not being able to have a due date or 
    '''
    def __init__(self, name:str, desc:str='', id:str=None, priority:int=0, created_at:DateTime=None, parent:TaskFolder|Database=None):
        if id is None:
            # generate a unique id based on the type (TaskNode, TaskFolder, Database) and the current timestamp and a random string of 10 characters in the format of 'TF:YYYY-MM-DD:random_string' where random_string is a random string of 10 characters consisting of letters and digits
            id = 'TF:' + pdm.now().format('YYYY-MM-DD:HHmmss') +':' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        if created_at is None:
            created_at = pdm.now()
        super().__init__(name=name, desc=desc, id=id, priority=priority, created_at=created_at, due_date=None, parent=parent)
        self.due_date = None

    def __repr__(self):
        # the verbose version
        return f"TaskFolder(\n\tname={self.name},\n\tid={self.id},\n\tcreated_at={self.created_at},\n\tparent_id={self.parent.id if self.parent else None},\n\timmediate_children_count={len(self.children)}\n)"

    def __str__(self):
        # the concise version
        return f"TaskFolder: {self.name} (ID: {self.id})"

    def add_child(self, child: TaskNode|TaskFolder):
        super().add_child(child)
        # add any additional logic specific to TaskFolder if needed
    
    def bequeath(self):
        '''
        meaning: to pass on property, money, or personal possessions to someone through a legal will after you die, neat innit?
        '''
        pass


class Database(TaskFolder):
    '''
    A class representing a database in a task management system. It can contain TaskNodes and TaskFolders as children.
    Acts as the parent node of the entire task hierarchy, child to none (line goes hard), and can have multiple TaskNodes and TaskFolders as children.
    '''
    def __init__(self, name:str, desc:str='', id:str=None, path:str=None, created_at:DateTime=pdm.now()):
        # self.created_at = created_at    # default to the current timestamp if not provided
        if id is None:
            # generate a unique id based on the type (TaskNode, TaskFolder, Database) and the current timestamp and a random string of 10 characters in the format of 'DB:YYYY-MM-DD:random_string' where random_string is a random string of 10 characters consisting of letters and digits
            self.id = 'DB:' + pdm.now().format('YYYY-MM-DD:HHmmss') +':' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        else:
            self.id = id
        if path is None:
            self.path = str(Path.cwd()) + '/' + f"{name}"   # default to current working directory if not provided
        else:
            self.path = path
        if not self.path.endswith('.csv'):
            self.path += '.csv'
        # self.path = path if path else str(Path.cwd())   # default to current working directory if not provided
        super().__init__(name=name, desc=desc, id=self.id, parent=None)  # Database has no parent

    def __repr__(self):
        # the verbose version
        return f"Database(\n\tname={self.name},\n\tid={self.id},\n\tcreated_at={self.created_at},\n\tpath={self.path},\n\tfile_name={self.file_name},\n\timmediate_children_count={len(self.children)}\n)"

    def __str__(self):
        # the concise version
        return f"Database: {self.name} (ID: {self.id})"

    def add_child(self, child: TaskNode|TaskFolder):
        '''
        Adds a child TaskNode or TaskFolder to the current Database's children list and sets the parent of the child to the current Database.
        '''
        if child in self.children:
            raise ValueError(f"Child with id {child.id} already exists in children of database with id {self.id}")
        elif child.parent is not None:
            raise ValueError(f"Child with id {child.id} already has a parent with id {child.parent.id}")
        else:
            self.children.append(child)
            child.parent = self
            child.set_properties_from_parent()  # set properties of the child based on the parent node

def main():
    pass
    # _test_loadDB()
    # _test_createDB()

#       FUBAR leave the testing in test.py for the time being
# def _test_createDB():
#     task1 = TaskNode(name="Task 1", desc="This is task 1", priority=2)
#     task2 = TaskNode(name="Task 2", desc="This is task 2", priority=1)
#     task1.add_child(task2)
#     task3 = TaskNode(name="Task 3", desc="This is task 3")
#     task2.add_child(task3)
#     task4 = TaskNode(name="Task 4", desc="This is task 4")
#     task1.add_child(task4)
#     task5 = TaskNode(name="Task 5", desc="This is task 5")
#     task4.add_child(task5)

#     taskfolder1 = TaskFolder(name="Folder 1", desc="This is folder 1")
#     taskfolder1.add_child(task1)
#     database1 = Database(name="Database 1", desc="This is database 1")
#     database1.add_child(taskfolder1)
    
#     print("DFS Print:")
#     printTreeDFS(database1)
#     saveDatabaseCSV(database1, force=True)

# def _test_loadDB():
#     database1 = loadDatabaseCSV('Database 1.csv')
#     print("DFS Print:")
#     printTreeDFS(database1)

if __name__ == "__main__":
    main()
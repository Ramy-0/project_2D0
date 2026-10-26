from __future__ import annotations
from typing import TYPE_CHECKING
# from bigtree import Node as BTNode

# if TYPE_CHECKING:
#     from classes import TaskNode, TaskFolder, Database

import csv
import os
from collections import deque

from classes import TaskNode, TaskFolder, Database      # dont import * to avoid looping imports

def getChildrenDFS(parent_node, depth:int=0, max_depth:int=0) -> list:
    """
    Depth-First Search (DFS) algorithm to traverse a tree structure of TaskNodes and TaskFolders.
    
    Args:
        parent_node (TaskNode or TaskFolder): The starting node for the DFS traversal.
        depth (int): The current depth of the traversal. Default is 0.
        max_depth (int): The maximum depth to traverse. Default is 0 for no limit.
    """
    if max_depth != 0 and depth > max_depth:
        return # break the recursion if the maximum depth is exceeded
    result = [parent_node]
    for child in parent_node.children:
        result.extend(getChildrenDFS(child, depth + 1, max_depth))
    return result

def printTreeDFS(parent_node, depth:int=0, max_depth:int=0, is_root:bool=True):
    """
    Depth-First Search (DFS) algorithm to traverse a tree structure of TaskNodes and TaskFolders and print the nodes.
    
    Args:
        parent_node (TaskNode or TaskFolder): The starting node for the DFS traversal.
        depth (int): The current depth of the traversal. Default is 0.
        max_depth (int): The maximum depth to traverse. Default is 0 for no limit.
        is_root (bool): Indicates if the current node is the root of the tree. Default is True.
    """
    if max_depth != 0 and depth > max_depth:
        return # break the recursion if the maximum depth is exceeded
    print("  " * depth + str(parent_node))
    for child in parent_node.children:
        printTreeDFS(child, depth + 1, max_depth, is_root=False)

# def saveDatabase(database: Database, force:bool=False):
#     """
#     Saves the database to a file. If the file already exists, it will not overwrite it unless force is True.
    
#     Args:
#         database (Database): The database object to save.
#         force (bool): If True, will overwrite the existing file. Default is False.
#     """
#     if os.path.exists(database.path) and not force:
#         raise FileExistsError(f"File {database.path} already exists. Use force=True to overwrite.")
#     with open(database.path, 'wb') as f:
#         pickle.dump(database, f)

databaseHeader = ['ID', 'Name', 'Description', 'Type', 'Parent ID', 'Priority', 'CreationDate', 'DueDate', 'Status']

def saveDatabaseCSV(database: Database, force:bool=False):
    '''
    Saves the database to a CSV file. If the file already exists, it will not overwrite it unless force is True.
    
    Args:
        database (Database): The database object to save.
        force (bool): If True, will overwrite the existing file. Default is False.
    '''
    if os.path.exists(database.path) and not force:
        raise FileExistsError(f"File {database.path} already exists. Use force=True to overwrite.")
    if os.path.exists(database.path) and force:
        pass
    with open(database.path if database.path.endswith('.csv') else database.path+'.csv', 
              'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(databaseHeader)
        for node in getChildrenDFS(database):
            node_type = type(node).__name__
            parent_id = node.parent.id if node.parent else None
            writer.writerow([node.id, node.name, node.desc, node_type, parent_id, node.priority, node.created_at, node.due_date, node.completion])

def loadDatabaseCSV(path:str, force:bool=False) -> Database:
    '''
    Loads the database from a CSV file

    Args:
        path (str): The path to the database file
        force (bool): If True, creates a new database if the file does not exist
    '''
    if not os.path.exists(path) and not force:
        raise FileNotFoundError(f"File ({path}) does not exist.")

    # keep track of the end nodes on the tree
    endNodes = set()

    with open(path, 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip the heading
        row = next(reader)
        # print(row)
        database = Database(name=row[1], desc=row[2], id=row[0], path=path, created_at=row[6])
        for row in reader:
            # Note dont add the parent HERE!!!
            if row[3] == 'TaskNode':
                node = TaskNode(name=row[1], desc=row[2], id=row[0], priority=int(row[5]), created_at=row[6], due_date=row[7], completion=float(row[8]))
            elif row[3] == 'TaskFolder':
                node = TaskFolder(name=row[1], desc=row[2], id=row[0], priority=int(row[5]), created_at=row[6])


            # get the parent
            parent = getNodebyID(database, row[4])    # the parent ID is saved in col 5
            # add the node to its parent
            parent.add_child(node)

            # # update the endNodes
            # if parent in endNodes:
            #     endNodes.remove(parent)
            #     endNodes.add(node)
        
        return database

def addNodeinDatabaseCSV(node:TaskNode|TaskFolder, database:Database=None, path:str=None, force:bool=False) -> None:
    if path is None:
        if database is None:
            raise TypeError("no database or path given")
        else:
            path = database.path
    if node.parent in ['', '~', None] or isinstance(node.parent, Database):
        # the parent is the database (the allfather node)
        # append the task in the end of the file
        with open(path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                node.id, 
                node.name, 
                node.desc, 
                type(node).__name__, 
                node.parent.id if node.parent else None, 
                node.priority, 
                node.created_at, 
                node.due_date, 
                node.completion
                ])

def getNodebyID(database:Database, id:str):
    '''
    breadth first search to get the node with the given ID
    '''
    # print(database)
    if id == database.id:
        return database
    queue = deque()     # queue (fist to come fisrt to serve and deque should be faster)
    queue.append(database)
    while queue:    # while queue not empty
        queue_children = queue.popleft().children
        for child in queue_children:
            queue.append(child)
            if child.id == id:
                return child

    # if no node has the id
    print(f"{id} not found")

def listIDXByID(List:list, ID:str) -> int:
    '''
    return the index from a list of nodes from the id attribute 
    '''
    for node in List:
        if node.id == ID:
            return List.index(node)

    raise 

def getParentChain(node:TaskNode|TaskFolder):
    parent_list = []
    target_node = node
    while target_node.parent:
        if isinstance(target_node.parent, Database):
            parent_list.append('~')
            break
        if target_node.parent == '~' or target_node == '':
            # in case we got the database in accident
            break
        target_node = target_node.parent
        parent_list.append(target_node.name)

    return '/'.join(parent_list[::-1])

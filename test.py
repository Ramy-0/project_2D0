from classes import TaskNode, TaskFolder, Database
from functions import *

def test_1():
    database = loadDatabaseCSV(path='Database 1.csv')
    printTreeDFS(database)
    database.path = 'Database 1_2'
    database.name = 'dummy'
    database.add_child(TaskNode(name = 'Task 6', due_date='2026-09-29 11:49:20.271102+03:00'))
    saveDatabaseCSV(database=database)

def test_2():
    database = loadDatabaseCSV(path='Database 1.csv')
    printTreeDFS(database)
    task_3 = getNodebyID(database=database ,id='TN:2026-09-20:131605:WTCOKyQDbm')
    print(task_3)
    print(getParentChain(database))

def test_3():
    db = loadDatabaseCSV("Database_1000_tasks.csv")
    printTreeDFS(db)

def test_4():
    db = loadDatabaseCSV("Database 1_2.csv")
    task_8 = TaskNode('task 8', desc='trying the adding logic', parent=db)
    addNodeinDatabaseCSV(task_8, path='Database 1_2.csv')

if __name__ == "__main__":
    # test_4()
    test_3()
    pass

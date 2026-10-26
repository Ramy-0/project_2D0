import fire
from functions import *

class Tools:
    def print_tree(database_path:str):
        print(str(database_path))
        return getChildrenDFS(loadDatabaseCSV(path=database_path))

if __name__ == "__main__":
    fire.Fire(Tools)
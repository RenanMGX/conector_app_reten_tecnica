import os
import re
from Entities.dependencies.functions import P
from typing import List, Dict
from copy import deepcopy

class CodExtrator:
    @property
    def codes(self) -> List[Dict[str,str]]:
        return self.__codes
    
    @property
    def list_codes(self) -> list:
        try:
            codes = []
            if self.__codes:
                for code in self.__codes:
                    codes.append(code['n_doc'])
            return codes
        except:
            return []
                
    def __init__(self) -> None:
        self.__codes = []
    
    @staticmethod
    def file(file_path:str) -> dict:
        if (os.path.exists(file_path)) and (os.path.isfile(file_path)):
            file_path = os.path.basename(file_path)
            if (cod:=re.search(r'[0-9]{10}', file_path)):
                print(P(f"o codigo {cod.group()} foi extraido com sucesso do arquivo '{os.path.basename(file_path)}'", color='green'))
                
                centro:str
                if (x:=re.search(r'[A-z]{1}[0-9]{3}', file_path)):
                    centro = x.group()
                else:
                    return {}
                
                id:str
                if (x:=re.search(r'[0-9]+(?=-Rete)', file_path)):
                    id = x.group()
                else:
                    return {}
                
                return {"id": id, "div": centro, "n_doc": cod.group()}
            print(P(f"não foi encontrador nenhum codigo do arquivo {os.path.basename(file_path)}", color='red'))
        else:
            print(P(f"o arquivo '{file_path}' não é valido!", color='red'))
        return {}
        
    def folder(self, folder_path:str):
        result:list = []
        if (os.path.exists(folder_path)) and (os.path.isdir(folder_path)):
            for file in os.listdir(folder_path):
                file = os.path.join(folder_path, file)
                temp = CodExtrator.file(file)
                if temp:
                    result.append(temp)
        self.__codes = result
        return self

if __name__ == "__main__":
    pass

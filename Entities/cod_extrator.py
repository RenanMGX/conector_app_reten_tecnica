import os
import re
from patrimar_dependencies.functions import P
from typing import List, Dict
from copy import deepcopy
from datetime import datetime

class Codigo:
    @property
    def file_path(self) -> str:
        return self.__file_path
    
    @property
    def file_name(self) -> str:
        return os.path.basename(self.file_path)
    
    @property
    def number(self) -> str:
        if (x:=re.search(r'(?<=[- ])[0-9]{10}', self.file_name)):
            return x.group()
        return ""
    
    @property
    def divisao(self) -> str:
        if (x:=re.search(r'(?<=_)[A-z]{1}[0-9]{3}', self.file_name)):
            return x.group()
        elif (x:=re.search(r'(?<=[0-9]_)[A-z0-9]{1}[0-9]{3}', self.file_name)):
            return x.group()
        return ""
    
    @property
    def id(self) -> str:
        if (x:=re.search(r'[0-9]+(?=-Rete)', self.file_name)):
            return x.group()
        return ""
    
    @property
    def attribuicao(self) -> str:
        try:
            if self.__attribuicao:
                date = datetime.strptime(self.__attribuicao, "%Y-%m-%d %H:%M:%S").replace(year=datetime.now().year)
                return date.strftime('%Y/%m/%d')
        except:
            pass
        return ""
    
    @property
    def nome_pagador(self) -> str:
        return self.__nome_pagador
    
    @property
    def data_lancamento(self) -> str:
        try:
            if self.__data_lancamento:
                data = datetime.strptime(self.__data_lancamento, "%Y-%m-%d %H:%M:%S")
                return data.strftime("%Y/%m/%d")
            #return self.__data_lancamento
        except:
            pass
        return ""
    
    def __init__(self, file_path:str) -> None:
        self.__file_path:str = file_path
        self.__attribuicao:str = ""
        self.__nome_pagador:str = ""
        self.__data_lancamento:str = ""
        self.processado:bool = False
        
    def __repr__(self) -> str:
        return f"{self.id}/{self.divisao}/{self.number}"
        
    def isValid(self) -> bool:
        if (self.id) and (self.divisao) and (self.number):
            return True
        return False
    
    def registrar_pagamento(self, *, atribuicao:str, nome_pagador:str) -> None:
        self.__attribuicao = atribuicao
        self.registrar_nome(nome_pagador)
        
    def registrar_data_lancamento(self, data) -> None:
        self.__data_lancamento = data    
        
    def registrar_nome(self, nome) -> None:
        self.__nome_pagador = nome
        
    def esta_pago(self) -> bool:
        if (self.attribuicao) and (self.nome_pagador):
            return True
        return False

class CodExtrator:
    @property
    def codes(self) -> List[Codigo]:
        return self.__codes
    
    @property
    def list_codes(self) -> list:
        try:
            codes = []
            if self.__codes:
                for code in self.__codes:
                    codes.append(code.number)
            return codes
        except:
            return []
                
    def __init__(self) -> None:
        self.__codes = []
    
    @staticmethod
    def file(file_path:str) -> Codigo|None:
        if (os.path.exists(file_path)) and (os.path.isfile(file_path)):
            cod = Codigo(file_path)
            if cod.isValid():
                print(P(f"o codigo {cod.number} foi extraido com sucesso do arquivo '{cod.file_name}'", color='green'))
                return cod
            print(P(f"não foi encontrador nenhum codigo do arquivo {cod.file_name}", color='red'))
        
    def folder(self, folder_path:str):
        result:List[Codigo] = []
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

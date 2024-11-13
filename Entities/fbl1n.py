from .dependencies.sap import SAPManipulation
from .dependencies.config import Config
from .dependencies.credenciais import Credential
from time import sleep
from copy import deepcopy
import pandas as pd
from .cod_extrator import CodExtrator
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Entities.dependencies.functions import P
from .cod_extrator import Codigo
from typing import List
from getpass import getuser
import os
from .dependencies.functions import Functions
import numpy as nb

class FBL1N(SAPManipulation):
    def __init__(self) -> None:
        crd:dict = Credential(Config()['credential']['sap']).load()
        super().__init__(user=crd['user'], password=crd['password'], ambiente=crd['ambiente'])
        
    @SAPManipulation.start_SAP
    def consultar_pagamentos(self, codes:CodExtrator, *, delete_plan_excel:bool=True) -> List[Codigo]:
        if (not codes.codes) or (not codes.list_codes):
            print(P("Sem arquivos para pesquisar", color='yellow'))
            self.fechar_sap()
            return []
        
        self.session.findById("wnd[0]/tbar[0]/okcd").text = "/n fbl1n"
        self.session.findById("wnd[0]").sendVKey(0)
        
        self.session.findById("wnd[0]/usr/ctxtKD_BUKRS-LOW").text = "*"
        
        self.session.findById("wnd[0]/usr/radX_AISEL").select()
        self.session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = (datetime.now() - relativedelta(months=3)).strftime('%d.%m.%Y')
        self.session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = datetime.now().strftime('%d.%m.%Y')        
        
        self.session.findById("wnd[0]/tbar[1]/btn[16]").press()
        self.session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/btn%_%%DYN011_%_APP_%-VALU_PUSH").press()
        
        pd.DataFrame(codes.list_codes).to_clipboard(header=False, index=False)        
        self.session.findById("wnd[1]/tbar[0]/btn[24]").press()
        self.session.findById("wnd[1]/tbar[0]/btn[8]").press()
        #self.session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/btn%_%%DYN011_%_APP_%-VALU_PUSH").press()
        self.session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/ctxt%%DYN015-LOW").text = "KC"
        
        self.session.findById("wnd[0]/usr/ctxtPA_VARI").text = "RENTENRPA"
        
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        
        self.session.findById("wnd[0]").sendVKey(16)
        self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        
        temp_file:str = os.path.join(f"C:\\Users\\{getuser()}\\Downloads", datetime.now().strftime('reten_tecnica-%d%m%Y%H%M%S.xlsx'))
        self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = os.path.dirname(temp_file)
        self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = os.path.basename(temp_file)
        
        self.session.findById("wnd[1]/tbar[0]/btn[0]").press()  
        
        sleep(3)
        Functions.fechar_excel(temp_file)
        self.fechar_sap()

        _codes:List[Codigo] = deepcopy(codes.codes)
        
        df = pd.read_excel(temp_file, dtype=str)
        for row,value in df.iterrows():
            try:
                for code in _codes:
                    if (value['Divisão'].lower() == code.divisao.lower()) and (value['Nº documento'] == code.number):
                        code.registrar_nome(value['Nome do usuário'])
                        code.registrar_data_lancamento(value['Data de lançamento'])
                        if (not value['Doc.compensação'] is nb.nan) and (not value['Data de compensação'] is nb.nan):
                            code.registrar_pagamento(atribuicao=value['Atribuição'], nome_pagador=value['Nome do usuário'])
                            break
            except:
                import traceback
                print(traceback.format_exc())
                pass
        
        try:
            if delete_plan_excel:
                os.unlink(temp_file)
        except:
            pass
        
        return _codes
        
if __name__ == "__main__":
    pass
    
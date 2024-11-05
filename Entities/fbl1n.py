from .dependencies.sap import SAPManipulation
from .dependencies.config import Config
from .dependencies.credenciais import Credential
from time import sleep
from copy import deepcopy
from pandas import DataFrame
from .cod_extrator import CodExtrator
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Entities.dependencies.functions import P

class FBL1N(SAPManipulation):
    def __init__(self) -> None:
        crd:dict = Credential(Config()['credential']['crd']).load()
        super().__init__(user=crd['user'], password=crd['password'], ambiente=crd['ambiente'])
        
    @SAPManipulation.start_SAP
    def start(self, codes:CodExtrator):
        if (not codes.codes) or (not codes.list_codes):
            print(P("Sem arquivos para pesquisar", color='yellow'))
            self.fechar_sap()
            return
        
        self.session.findById("wnd[0]/tbar[0]/okcd").text = "/n fbl1n"
        self.session.findById("wnd[0]").sendVKey(0)
        
        self.session.findById("wnd[0]/usr/ctxtKD_BUKRS-LOW").text = "*"
        
        self.session.findById("wnd[0]/usr/radX_AISEL").select()
        self.session.findById("wnd[0]/usr/ctxtSO_BUDAT-LOW").text = (datetime.now() - relativedelta(months=6)).strftime('%d.%m.%Y')
        self.session.findById("wnd[0]/usr/ctxtSO_BUDAT-HIGH").text = datetime.now().strftime('%d.%m.%Y')        
        
        self.session.findById("wnd[0]/tbar[1]/btn[16]").press()
        self.session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/btn%_%%DYN011_%_APP_%-VALU_PUSH").press()
        DataFrame(codes.list_codes).to_clipboard(header=False, index=False)        
        self.session.findById("wnd[1]/tbar[0]/btn[24]").press()
        self.session.findById("wnd[1]/tbar[0]/btn[8]").press()
        #self.session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/btn%_%%DYN011_%_APP_%-VALU_PUSH").press()
        self.session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/ctxt%%DYN015-LOW").text = "KC"
        
        self.session.findById("wnd[0]/usr/ctxtPA_VARI").text = "/PATRIMAR"
        
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        
        _codes = deepcopy(codes.codes) 
        
        count = 4
        while True:
            try:
                n_doc:str = self.session.findById(f"wnd[0]/usr/lbl[63,{count}]").text # numero Documento
                div:str = self.session.findById(f"wnd[0]/usr/lbl[14,{count}]").text # Divisão
                atrib:str = self.session.findById(f"wnd[0]/usr/lbl[101,{count}]").text # Atribuição
                for code in _codes:
                    if (code['div'].lower() == div.lower()) and (code['n_doc'] == n_doc):
                        if atrib:
                            code['atrib'] = atrib
            except:
                #import traceback
                #print(traceback.format_exc())
                break
            count+=1
        
        return _codes
        
if __name__ == "__main__":
    pass
    DataFrame().to_clipboard
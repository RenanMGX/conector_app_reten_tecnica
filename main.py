from Entities.dependencies.arguments import Arguments
from Entities.fbl1n import FBL1N
from Entities.cod_extrator import CodExtrator
from Entities.sharepoint import SharePoint
from Entities.dependencies.logs import Logs
import os
import shutil
from Entities.dependencies.functions import P        
from Entities.dependencies.config import Config

class Execute:
    delete_file:bool=True
    
    @staticmethod
    def start():
        
        target_folder_path:str = Config()['paths']['target_folder']
        if not os.path.exists(target_folder_path):
            raise Exception(f"O caminho '{target_folder_path}' é invalido!")
        
        print(P("Listando arquivos na pasta"))
        files = CodExtrator().folder(target_folder_path)
        if not files.codes:
            print(P("Nenhum arquivo encontrado para consultar!"))
            Logs().register(status='Report', description="Nenhum arquivo encontrado para consultar!")
            return
        
        print(P("consultando pagamentos no SAP"))
        files = FBL1N().consultar_pagamentos(files, delete_plan_excel=True)
        #files = [x for x in files if x.esta_pago()]
        if not files:
            print(P("Nenhum Pago para Lançar no Aplicativo!"))
            Logs().register(status='Report', description="Nenhum Pago para Lançar no Aplicativo!")
            return
        print(P("Consulta Finalizada"))
        
        
        print(P("Iniciando api do Sharepoint"))
        sharepoint = SharePoint()
        #import pdb;pdb.set_trace()
        for file in files:
            #import pdb;pdb.set_trace()
            if not file.processado:
                continue
            sharepoint.alterar(file.id, coluna='AprovacaoCentral', valor='Aprovado')
            sharepoint.alterar(file.id, coluna='ResponsavelCentral', valor=file.nome_pagador)
            if file.data_lancamento:
                sharepoint.alterar(file.id, coluna='ConclusaoCentral', valor=file.data_lancamento)

            
            if file.esta_pago():
                print(P(f"O arquivo {file.file_name} está compensado!",color="green"))
                sharepoint.alterar(file.id, coluna='AprovacaoFinanceiro', valor='Aprovado')
                #import pdb;pdb.set_trace()
                if file.attribuicao:
                    sharepoint.alterar(file.id, coluna='ConclusaoFinanceiro', valor=file.attribuicao)
                
                
                try:
                    if Execute.delete_file:
                        os.unlink(file.file_path)
                    else:
                        path_folder_pagos:str = os.path.join(target_folder_path, 'Compensado')
                        if not os.path.exists(path_folder_pagos):
                            os.makedirs(path_folder_pagos)
                        shutil.move(file.file_path, path_folder_pagos)
                except:
                    Logs().register(status='Report', description=f"Não foi possivel mover o arquivo para a pasta {file.file_path} para a pasta pagos")
        
        print(P("Finalizado!", color='yellow'))
        
    @staticmethod
    def start_delete_file_off() -> None:
        Execute.delete_file = False
        Execute.start()
if __name__ == "__main__":
    Arguments({
        'start': Execute.start,
        'start_delete_file_off': Execute.start_delete_file_off
    })

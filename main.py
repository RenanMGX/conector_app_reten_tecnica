from Entities.fbl1n import FBL1N
from Entities.cod_extrator import CodExtrator
from Entities.sharepoint import SharePoint
from Entities.dependencies.arguments import Arguments
from Entities.dependencies.logs import Logs
import os
import shutil
from Entities.dependencies.functions import P

class Execute:
    @staticmethod
    def start():
        target_folder_path:str = r"R:\Conector APP reten tecnica - consulta SAP fin\#material\Arquivos"
        if not os.path.exists(target_folder_path):
            raise Exception(f"O caminho '{target_folder_path}' é invalido!")
        
        print(P("Listando arquivos na pasta"))
        files = CodExtrator().folder(target_folder_path)
        if not files.codes:
            print(P("Nenhum arquivo encontrado para consultar!"))
            Logs().register(status='Report', description="Nenhum arquivo encontrado para consultar!")
            return
        
        print(P("consultando pagamentos no SAP"))
        files = FBL1N().consultar_pagamentos(files)
        files = [x for x in files if x.esta_pago()]
        if not files:
            print(P("Nenhum Pago para Lançar no Aplicativo!"))
            Logs().register(status='Report', description="Nenhum Pago para Lançar no Aplicativo!")
            return
        print(P("Consulta Finalizada"))
        
        path_folder_pagos:str = os.path.join(target_folder_path, 'Pagos')
        if not os.path.exists(path_folder_pagos):
            os.makedirs(path_folder_pagos)
        
        print(P("Iniciando api do Sharepoint"))
        sharepoint = SharePoint()
        for file in files:
            print(P(f"O arquivo {file.file_name} esta pago!"))
            sharepoint.alterar(file.id, coluna='AprovacaoFinanceiro', valor='Aprovado')
            sharepoint.alterar(file.id, coluna='ResponsavelFinanceiro', valor=file.nome_pagador)
            try:
                shutil.move(file.file_path, path_folder_pagos)
            except:
                Logs().register(status='Report', description=f"Não foi possivel mover o arquivo para a pasta {file.file_path} para a pasta pagos")
        
        print(P("Finalizado", color='red'))
        
        

if __name__ == "__main__":
    Arguments({
        'start': Execute.start
    })

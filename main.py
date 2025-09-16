from Entities.fbl1n import FBL1N
from Entities.cod_extrator import CodExtrator
from Entities.sharepoint import SharePoint
import os
import shutil
from patrimar_dependencies.functions import P
from patrimar_dependencies.sharepointfolder import SharePointFolders
from botcity.maestro import * # type: ignore

class ExecuteAPP:
    delete_file:bool=True
    
    @staticmethod
    def start(*, 
            maestro:BotMaestroSDK|None = None,
            target_folder_path:str,
            sap_user:str, 
            sap_password:str, 
            sap_ambiente:str,
            azure_client_id:str,
            azure_client_secret:str,
            sharepoint_url:str,
            sharepoint_lista:str,
        ):
        
        #target_folder_path:str = target_folder_path
        if not os.path.exists(target_folder_path):
            raise Exception(f"O caminho '{target_folder_path}' é invalido!")
        
        print(P("Listando arquivos na pasta"))
        files = CodExtrator().folder(target_folder_path)
        if not files.codes:
            print(P("Nenhum arquivo encontrado para consultar!"))
            
            if not maestro is None:
                maestro.new_log_entry(
                    activity_label="SAP-Conector_APP_Retencao_Tecnica",
                    values={
                        "Texto": "Nenhum arquivo encontrado para consultar!"
                    }
                )                            

            return
        
        print(P("consultando pagamentos no SAP"))
        files = FBL1N(
                sap_user=sap_user,
                sap_password=sap_password,
                sap_ambiente=sap_ambiente
            ).consultar_pagamentos(files)
        
        #files = [x for x in files if x.esta_pago()]
        if not files:
            print(P("Nenhum Pago para Lançar no Aplicativo!"))
            
            if not maestro is None:
                maestro.new_log_entry(
                    activity_label="SAP-Conector_APP_Retencao_Tecnica",
                    values={
                        "Texto": "Nenhum Pago para Lançar no Aplicativo!"
                    }
                )                            
            
            return
        print(P("Consulta Finalizada"))
        
        
        print(P("Iniciando api do Sharepoint"))
        sharepoint = SharePoint(
                client_id=azure_client_id,
                client_secret=azure_client_secret,
                sharepoint_url=sharepoint_url,
                sharepoint_lista=sharepoint_lista
            )
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
                    if ExecuteAPP.delete_file:
                        os.unlink(file.file_path)
                    else:
                        path_folder_pagos:str = os.path.join(target_folder_path, 'Compensado')
                        if not os.path.exists(path_folder_pagos):
                            os.makedirs(path_folder_pagos)
                        shutil.move(file.file_path, path_folder_pagos)
                except:
                    if not maestro is None:
                        maestro.new_log_entry(
                            activity_label="SAP-Conector_APP_Retencao_Tecnica",
                            values={
                                "Texto": f"Não foi possivel mover o arquivo para a pasta {file.file_path} para a pasta pagos"
                            }
                        )                            
        
        print(P("Finalizado!", color='yellow'))
        
    # @staticmethod
    # def start_delete_file_off() -> None:
    #     Execute.delete_file = False
    #     Execute.start()
if __name__ == "__main__":
    from patrimar_dependencies.credenciais import Credential
    
    crd_azure:dict = Credential(
        path_raiz=SharePointFolders(r'RPA - Dados\CRD\.patrimar_rpa\credenciais').value,
        name_file="Azure-APP-RetencaoTecnica"
    ).load()
    
    crd_sap:dict = Credential(
        path_raiz=SharePointFolders(r'RPA - Dados\CRD\.patrimar_rpa\credenciais').value,
        name_file="SAP_PRD"
    ).load()
    
    ExecuteAPP.start(
        target_folder_path=r'\\server008\G\ARQ_PATRIMAR\WORK\Notas Fiscais Digitalizadas\RETENÇÃO TÉCNICA',
        azure_client_id=crd_azure['client_id'],
        azure_client_secret=crd_azure['client_secret'],
        sharepoint_url="https://patrimar.sharepoint.com/sites/controle",
        sharepoint_lista="RetencaoTecnica",
        sap_user=crd_sap['user'],
        sap_password=crd_sap['password'],
        sap_ambiente=crd_sap['ambiente']
    )
    
import pandas as pd
import os

from typing import Literal
from patrimar_dependencies.functions import Functions
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.runtime.paths.resource_path import ResourcePath

class SharePoint:
    @property
    def df(self) -> pd.DataFrame:
        try:
            return self.__df
        except AttributeError:
            self.consultar()
            return self.__df
    
    @property
    def download_path(self):
        download_path:str = os.path.join(os.getcwd(), "Attachments_Download")
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        return download_path
    
    def __init__(self, *, sharepoint_email:str, sharepoint_password:str, sharepoint_url:str, sharepoint_lista:str) -> None:        
        url = sharepoint_url
        lista = sharepoint_lista
        
        self.__ctx_auth = AuthenticationContext(url)
        if self.__ctx_auth.acquire_token_for_user(sharepoint_email, sharepoint_password):
            self.__ctx = ClientContext(url, self.__ctx_auth)
        else:
            raise PermissionError("não foi possivel acessar a lista")
        
        self.__lista = self.__ctx.web.lists.get_by_title(lista)
        
        self.consultar()
        
    def consultar(self, with_attachment:bool=False):
        items = self.__lista.get_items().expand(["AttachmentFiles"])
        self.__ctx.load(items)
        self.__ctx.execute_query()
        
        self.limpar_pasta_download() if with_attachment else None
        
        list_valid = []
        while True:
            for item in items:
                if not item.properties.get('AprovacaoJuridico'):
                    if with_attachment:
                        path_attachment_download = []
                        if item.properties['NumChamadoZendesk']:
                            continue
                        if item.properties['Attachments']:
                            attachment_files = item.attachment_files
                            self.__ctx.load(attachment_files)
                            self.__ctx.execute_query()
                            for attachment_file in attachment_files:
                                file_name = os.path.join(self.download_path, f"{item.properties.get('ID')}-{attachment_file.properties['FileName']}")
                                path_attachment_download.append(file_name)
                                with open(file_name, 'wb')as _file_handle:
                                    attachment_file.download(_file_handle)
                                    self.__ctx.execute_query()
                                
                        item.properties['Attachment_Path'] = path_attachment_download
                                    
                    list_valid.append(item.properties)
            
            if not items._next_request_url:
                break
            
            next_request_url = items._next_request_url
            # Remove a parte da URL base, que pode ser algo como "https://patrimar.sharepoint.com/sites/controle/_api"
            service_root = self.__ctx.service_root_url()
            if next_request_url.startswith(service_root): #type: ignore
                next_request_url = next_request_url[len(service_root):]            
            
            items = ListItemCollection(self.__ctx, ResourcePath(next_request_url))#type: ignore
            self.__ctx.load(items)
            self.__ctx.execute_query()                        
                    
        self.__df = pd.DataFrame(list_valid)
            
        return self
    
    def coletar_arquivos_controle(self):
        items = self.__lista.get_items().expand(["AttachmentFiles"])
        self.__ctx.load(items)
        self.__ctx.execute_query()
        
        self.limpar_pasta_download()
                
        list_valid = []
        while True:
            for item in items:
                if item.properties.get('RegistroArquivoControle'):
                    continue            
                if "Aprovado" in str(item.properties.get('AprovacaoControle')):
                    path_attachment_download = []
                    if item.properties['Attachments']:
                        attachment_files = item.attachment_files
                        self.__ctx.load(attachment_files)
                        self.__ctx.execute_query()
                        for attachment_file in attachment_files:
                            file_name = os.path.join(self.download_path, f"{item.properties.get('ID')}-{attachment_file.properties['FileName']}")
                            path_attachment_download.append(file_name)
                            with open(file_name, 'wb')as _file_handle:
                                attachment_file.download(_file_handle)
                                self.__ctx.execute_query()
                                        
                    item.properties['Attachment_Path'] = path_attachment_download
                                            
                    list_valid.append(item.properties)
                    
            if not items._next_request_url:
                break
            
            next_request_url = items._next_request_url
            # Remove a parte da URL base, que pode ser algo como "https://patrimar.sharepoint.com/sites/controle/_api"
            service_root = self.__ctx.service_root_url()
            if next_request_url.startswith(service_root): #type: ignore
                next_request_url = next_request_url[len(service_root):]            
            
            items = ListItemCollection(self.__ctx, ResourcePath(next_request_url))#type: ignore
            self.__ctx.load(items)
            self.__ctx.execute_query()                        
                                
        self.__df = pd.DataFrame(list_valid)    
        
        return self
            
    def alterar(self, id, *, valor:str, coluna:str) -> None:
        item_to_update = self.__lista.get_item_by_id(id)
        
        # Atualizando os campos do item
        item_to_update.set_property(coluna, valor)
        
        #item_to_update.set_property("OutroCampo", "Novo Valor")
        item_to_update.update()
            
        # Executando a atualização no servidor
        self.__ctx.execute_query()
        
        self.consultar()
        
    def limpar_pasta_download(self) -> None:
        for file in os.listdir(self.download_path):
            file:str = os.path.join(self.download_path, file)
            
            if os.path.isfile(file):
                try:
                    os.unlink(file)
                except PermissionError as error:
                    print(error)
                    Functions.fechar_excel(file)
                    os.unlink(file)    

if __name__ == "__main__":
    pass

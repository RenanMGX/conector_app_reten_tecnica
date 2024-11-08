from typing import Dict

default:Dict[str, Dict[str,object]] = {
    'credential': {
        'sharepoint': 'Microsoft-RPA',
        'sap': 'SAP_PRD',
        'url': 'https://patrimar.sharepoint.com/sites/controle',
        'lista': 'RetencaoTecnica'
    },
    'paths': {
      'target_folder': r"R:\Conector APP reten tecnica - consulta SAP fin\#material\Arquivos"
    },
    
    'log': {
        'hostname': 'Patrimar-RPA',
        'port': '80',
        'token': ''
    }
}
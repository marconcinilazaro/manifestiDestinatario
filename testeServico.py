from flask import Flask, request
import requests
from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.processamento.serializacao import SerializacaoXML
from pynfe.processamento.assinatura import AssinaturaA1
from pynfe.entidades.evento import EventoManifestacaoDest
from pynfe.entidades.fonte_dados import _fonte_dados
import datetime
from lxml import etree
import os
import re
import json


app = Flask(__name__)

@app.route('/teste')
def hello():
    return 'Teste OK'

@app.route('/manifestarDestinatario',  methods=['POST'])
def manifestarDestinatario():
    data = request.json
    pasta_destino = '/certificado'  # Pasta de destino para salvar o arquivo
    try:
        url =  data.get('certificado') #"https://armazenamentowebtron.blob.core.windows.net/certificados/30985777000113.pfx"
        response = requests.get(url)
        if response.status_code == 200:
            # Verifica se a pasta de destino existe, caso contrário, cria-a
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)

            nome_arquivo = url.split('/')[-1]  # Obtém o nome do arquivo a partir da URL
            certificado = os.path.join(pasta_destino, nome_arquivo)  # Gera o caminho completo para o arquivo

            with open(certificado, 'wb') as file:
                file.write(response.content)
            print(f'O arquivo foi salvo  com sucesso.')
        else:
            print(f'Falha ao baixar o arquivo. Código de status: {response.status_code}')
            
        senha =  data.get('senha') #'996637392'
        uf =  data.get('uf')#'AN'
        homologacao = False
        cnpj =  data.get('cnpj') #'30985777000113' 
        chave =  data.get('chave') #'51210275315333002829550010015253571017410061'
        modelo = data.get('modelo') # modelo='nfce' ou 'nfe'
        operacao = data.get('operacao')   #2- numero da operacao
        manif_dest = EventoManifestacaoDest(
            cnpj=cnpj,  # cnpj do destinatário
            chave=chave, # chave de acesso da nota
            data_emissao=datetime.datetime.now(),
            uf=uf,
            operacao=operacao  # - numero da operacao
            )

        # serialização
        serializador = SerializacaoXML(_fonte_dados, homologacao=homologacao)

        print(serializador)

        nfe_manif = serializador.serializar_evento(manif_dest)


        # assinatura
        a1 = AssinaturaA1(certificado, senha)
        xml = a1.assinar(nfe_manif)

        con = ComunicacaoSefaz(uf, certificado, senha, homologacao)
        envio = con.evento(modelo=modelo, evento=xml)  # modelo='nfce' ou 'nfe'   
            # Imprime o resultado
        print(envio.text)
        
                # Expressão regular para extrair o resultado entre as tags
        motivo = "<xMotivo>(.*?)</xMotivo>"
        cStat = "<cStat>(.*?)</cStat>"

        # Procura por correspondências usando a expressão regular
        resultadoMotivo = re.findall(motivo, envio.text)
        resultadoCStat = re.findall(cStat, envio.text)
        aux = 0
        result = []
        for resultadoMotivos in resultadoMotivo:
            item = {
                "id": aux,
                "motivo": resultadoMotivos,
                "cstat": resultadoCStat[aux]   
            }
            result.append(item)
            print(resultadoMotivos + ' - ' + resultadoCStat[aux] )
            aux+= 1
        
        return result  
        
        
    except requests.exceptions.RequestException as e:
        print(f'Falha na solicitação: {e}')

    except requests.exceptions.HTTPError as e:
        print(f'Erro de status HTTP: {e}')

    except Exception as e:
        print(f'Ocorreu um erro inesperado: {e}')
if __name__ == '__main__':
    app.run()
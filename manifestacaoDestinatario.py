from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.processamento.serializacao import SerializacaoXML
from pynfe.processamento.assinatura import AssinaturaA1
from pynfe.entidades.evento import EventoManifestacaoDest
from pynfe.entidades.fonte_dados import _fonte_dados
import datetime
from lxml import etree

certificado =  "D:\sefazpy\certificado.pfx"
senha = '996637392'
uf = 'mt'
homologacao = False
CNPJ = '30985777000113' 
CHAVE = '51230542188988000104550010000000231339045001'

manif_dest = EventoManifestacaoDest(
	cnpj='30985777000113',  # cnpj do destinatário
	chave='51230542188988000104550010000000231339045001', # chave de acesso da nota
	data_emissao=datetime.datetime.now(),
	uf='AN',
	operacao=2  # - numero da operacao
    )

# serialização
serializador = SerializacaoXML(_fonte_dados, homologacao=homologacao)

nfe_manif = serializador.serializar_evento(manif_dest)


# assinatura
a1 = AssinaturaA1(certificado, senha)
xml = a1.assinar(nfe_manif)
# print(a1.key)
# print(a1.cert)

con = ComunicacaoSefaz(uf, certificado, senha, homologacao)



envio = con.evento(modelo='nfe', evento=xml)  # modelo='nfce' ou 'nfe'

print(envio.text)
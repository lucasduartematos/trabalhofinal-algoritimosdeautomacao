import os

import gspread
import requests
import telegram
import pandas as pd
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
from tchan import ChannelScraper
from bs4 import BeautifulSoup


TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode="w") as arquivo:
  arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
api = gspread.authorize(conta)
planilha = api.open_by_key("194kfy5ezKLuREJV7UO5mlEkZSYbUMaUQC2q5hi-XKb4")
sheet = planilha.worksheet("robo_lucasduarte_bot")
app = Flask(__name__)

menu = """
<a href="/">Página inicial</a> | <a href="/noticias">NOTÍCIAS INDÍGENAS</a> | <a href="/sobre">Sobre</a> | <a href="/contato">Contato</a>
<br>
"""

@app.route("/")
def index():
  return menu + "Olá, seja bem-vindo(a) ao site de notícias indígenas do jornalista Lucas Duarte"

@app.route("/sobre")
def sobre():
  return menu + "Robô de notícias indígenas: A análise de dados é uma ferramenta poderosa para a compreensão de tendências e padrões em diversos setores da sociedade. No contexto dos povos indígenas, a análise de notícias diárias pode ajudar a identificar padrões de violação de direitos humanos e a mapear a presença dessas comunidades em diferentes regiões. Nesse sentido, a utilização do método de raspagem em Python pode ser uma ferramenta valiosa para coletar e analisar notícias diárias sobre indígenas."

@app.route("/contato")
def contato():
  return menu + "Mais informações: lucasduartematos@gmail.com"
  
@app.route("/noticias")
def noticias_indigenas():
  requisicao=requests.get('https://www.cnnbrasil.com.br/tudo-sobre/indigenas/')
  html=BeautifulSoup(requisicao.content)
  manchetes_indigenas=site.findAll('li',{'class':'home__list__item'})
  lista_noticias=[]
  for noticia in manchetes_indigenas:
    manchete=noticia.text
    link=noticia.find('a').get('href') 
    lista_noticias.append([manchete, link])
  df=pd.DataFrame(lista_noticias, columns=['Manchete','Link'])
  return df


# Autenticando a API do Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('path/to/credentials.json', scope)
client = gspread.authorize(creds)

# Abrindo a planilha existente
planilha = client.open('robo_lucasduarte_bot').sheet1

# Adicionando novas linhas à planilha
novas_linhas = [['Manchete 1', 'Link 1'], ['Manchete 2', 'Link 2']]
planilha.add_rows(len(novas_linhas))
for i, linha in enumerate(novas_linhas):
    planilha.update(f'A{i+2}:B{i+2}', [linha])



  def processa_mensagens():
  # Seria interessante tratarmos duas possíveis exceções:
  # 1- caso a sheet não exista, criá-la
  # 2- caso a célula não esteja preenchida, preenchê-la com 0

  # Pega na planilha do sheets o último update_id
  update_id = int(sheet.get("A1")[0][0])
  # Parâmetros de uma URL - também são chamados de query strings
  resposta = requests.get(f"https://api.telegram.org/bot{token}/getUpdates?offset={update_id + 1}")
  dados = resposta.json()["result"]  # lista de dicionários (cada dict é um "update")
  print(f"Temos {len(dados)} novas atualizações:")
  mensagens = []
  for update in dados:
    update_id = update["update_id"]
    if "message" not in update:
      print(f"ERROR: not a menssagem: {update}")
      continue
    # Extrai dados para mostrar mensagem recebida
    first_name = update["message"]["from"]["first_name"]
    sender_id = update["message"]["from"]["id"]
    if "text" not in update["message"]:
      continue  # Essa mensagem não é um texto!
    message = update["message"]["text"]
    chat_id = update["message"]["chat"]["id"]
    datahora = str(datetime.datetime.fromtimestamp(update["message"]["date"]))
    if "username" in update["message"]["from"]:
      username = update["message"]["from"]["username"]
    else:
      username = "[não definido]"
    print(f"[{datahora}] Nova mensagem de {first_name} @{username} ({chat_id}): {message}")
    mensagens.append([datahora, "recebida", username, first_name, chat_id, message])
    # Define qual será a resposta e envia
    if message == "/start":
      texto_resposta = "Olá! Seja bem-vinda(o). *Digite* /noticias para ver as últimas."

    elif message.lower().strip() in ["/noticias", "/notícias"]:  # Tratamento da mensagem
      noticias = captura_ultimas_noticias()
      texto_resposta = "Encontrei as seguintes notícias sobre indígenas:\n"
      for noticia in noticias:
        texto_resposta += f"- {noticia['title']} ({noticia['url']})\n"

    else:
      texto_resposta = "Não entendi!"
    nova_mensagem = {"chat_id": chat_id, "text": texto_resposta}
    requests.post(f"https://api.telegram.org./bot{token}/sendMessage", data=nova_mensagem)
    mensagens.append([datahora, "enviada", username, first_name, chat_id, texto_resposta])
  # Atualiza planilha do sheets com último update processado
  sheet.append_rows(mensagens)
  sheet.update("A1", update_id)
  
  import time

while True:
  processa_mensagens()
  time.sleep(5)

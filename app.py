import os

import gspread
import requests
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
from tchan import ChannelScraper
import pandas as pd
import csv

TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode="w") as arquivo:
  arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
api = gspread.authorize(conta)
planilha = api.open_by_key("1ZDyxhXlCtCjMbyKvYmMt_8jAKN5JSoZ7x3MqlnoyzAM")
sheet = planilha.worksheet("Sheet1")
app = Flask(__name__)

menu = """
<a href="/">Página inicial</a> | <a href="/promocoes">PROMOÇÕES</a> | <a href="/sobre">Sobre</a> | <a href="/contato">Contato</a>
<br>
"""

@app.route("/")
def index():
  return menu + "Olá, mundo! Esse é meu site. (Álvaro Justen)"

@app.route("/sobre")
def sobre():
  return menu + "Aqui vai o conteúdo da página Sobre"

@app.route("/contato")
def contato():
  return menu + "Aqui vai o conteúdo da página Contato"
  
  
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
      texto_resposta = "Encontrei as seguintes notícias:\n"
      for noticia in noticias:
        texto_resposta += f"- {noticia['title']} ({noticia['url']})\n"

    elif message.lower().strip() in ["/promocoes", "/promoções", "/promocões", "/promoçoes"]:  # Tratamento da mensagem
      promocoes = ultimas_promocoes()
      texto_resposta = "Encontrei as seguintes promoções no @promocoeseachadinhos:\n"
      for promocao in promocoes:
        texto_resposta += f"- {promocao}\n"

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

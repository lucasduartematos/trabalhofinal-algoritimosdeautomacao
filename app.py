import os

import gspread
import requests
import pandas as pd
import telegram
from flask import Flask, request
from flask import Flask, Response
from flask import Response
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
<a href="/">Página inicial</a> | <a href="/noticias">Notícias Indígenas</a> | <a href="/sobre">Sobre</a> | <a href="/contato">Contato</a>
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
  manchetes_indigenas=html.findAll('li',{'class':'home__list__item'})
  lista_noticias=[]
  for noticia in manchetes_indigenas:
    manchete=noticia.text
    link=noticia.find('a').get('href') 
    lista_noticias.append([manchete, link])
  df=pd.DataFrame(lista_noticias, columns=['Manchete','Link'])
  tabela_html = df.to_html()
  return Response(tabela_html, mimetype='text/html')

def planilha(df):
  lista = df.values.tolist()
  sheet.append_rows(lista)
  return "Planilha escrita!"

@app.route("/noticias", methods=["POST"])
def telegram_bot():
    update = request.json
    chat_id = update["message"]["chat"]["id"]
    message = update["message"]["text"]
    
    if message == "/noticias":
        # Raspa as últimas 5 notícias do site da CNN
        noticias = noticias_indigenas()
        ultimas_noticias = noticias[:5]
        
        # Envia as últimas 5 notícias via webhook do Telegram
        for noticia in ultimas_noticias:
            nova_mensagem = {
                "chat_id": chat_id,
                "text": f"{noticia['Manchete']}\n{noticia['Link']}",
            }
            resposta = requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
            print(resposta.text)
    else:
        nova_mensagem = {
            "chat_id": chat_id,
            "text": f"Você enviou a mensagem: <b>{message}</b>",
            "parse_mode": "HTML",
        }
        resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
        print(resposta.text)
    
    return "ok"

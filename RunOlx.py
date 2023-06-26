import subprocess
import os
import shlex
import webbrowser
import http.server
import socketserver
import json

# Solicita ao usuário para digitar um valor
url = input("Digite ou cole a URL da página inicial: ")

user_max_pages = input("Digite quantas páginas você deseja monitorar: ")

user_max_value = input("Digite qual o valor máximo que deseja pagar: ")

# Obtém o caminho completo do arquivo spyder.py
caminho_spyder = 'spiders\spider.py'

# Escapa corretamente os caracteres especiais no valor
url_escaped = shlex.quote(url)

# Constrói o comando
comando = f'scrapy runspider {caminho_spyder} -a "{url_escaped}" -a valor2="{user_max_value}" -a valor3="{user_max_pages}"'

# Executa o comando no terminal
os.system(comando)

novoComando = f'python -m http.server --bind 127.0.0.1'

print("")
print("")
print("")

print("Tudo OK! você pode ver os itens capturados no link a seguir: http://127.0.0.1:8000/index.html")

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == '/delete_all_items':
            self.delete_all_items()
        else:
            super().do_GET()

    def delete_all_items(self):
        file = os.path.join(os.getcwd(), 'output.json')
        print(file)
        with open(file, 'w') as file:
            file.write(json.dumps([]))
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'All items deleted')

httpd = socketserver.TCPServer(('', 8000), MyHandler)
httpd.serve_forever()

# Executa o comando no terminal
# os.system(novoComando)



# # Define o navegador desejado (nesse caso, o Google Chrome)
# navegador = "google-chrome"

# # Abre o arquivo HTML no navegador especificado
# webbrowser.get(navegador).open("file://" + os.path.join(os.getcwd(), 'index.html'))


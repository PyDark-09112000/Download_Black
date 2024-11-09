from browser import document, html, ajax
import json

def download_json(url):
    def on_complete(req):
        if req.status == 200 or req.status == 0:
            data = json.loads(req.text)
            show_content(data)
        else:
            print(f"Erro ao baixar o JSON: {req.status}")
    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('GET', url, True)
    req.send()

def show_content(data):
    content = document["content"]
    content.clear()
    for item in data:
        content <= html.DIV(f"Nome do Arquivo: {item['fileName']}", Class="file-name")
        content <= html.DIV(f"Descrição: {item['fileDescription']}", Class="file-description")
        content <= html.IMG(src=item['imageUrl'], width=200, height=200)
        if "videoUrl" in item:
            content <= html.A("Video do Jogo", href=item['videoUrl'], target="_blank", Class="button")
        if "magnetUris" in item:
            content <= html.DIV("Magnet Links:", Class="magnet-label")
            for magnet in item["magnetUris"]:
                content <= html.A(magnet["name"], href=magnet["uri"], target="_blank", Class="button")
        if "browserUris" in item:
            content <= html.DIV("Browser Links:", Class="browser-label")
            for browser in item["browserUris"]:
                content <= html.A(browser["name"], href=browser["uri"], target="_blank", Class="button")

def update_json_url(event=None):
    url = document["json-url"].value
    if url:
        download_json(url)
    else:
        print("Erro: O campo de URL do JSON está vazio ou contém um link inválido. Por favor, insira um link válido.")

document["json-url"].bind("keypress", lambda event: update_json_url() if event.keyCode == 13 else None)

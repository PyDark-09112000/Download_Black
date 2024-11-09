import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO

# URL do JSON raw inicial
default_url = ""

def download_json(url):
    """Função para baixar o JSON"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def download_image(image_url):
    """Função para baixar uma imagem a partir de uma URL"""
    response = requests.get(image_url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def open_link(url):
    """Função para abrir um link no navegador padrão"""
    import webbrowser
    webbrowser.open(url)

def create_file_name_label(parent, text, row, column, padx=0, pady=10, sticky="w"):
    """Função para criar um label de nome de arquivo com parâmetros ajustáveis"""
    file_name_label = tk.Label(parent, text=text, font=("Helvetica", 16, "bold"), bg=bg_color, fg=fg_color)
    file_name_label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return file_name_label

def create_image_label(parent, image_url, row, column, padx=0, pady=10, sticky="w"):
    """Função para criar um label de imagem com parâmetros ajustáveis"""
    image = download_image(image_url)
    image.thumbnail((200, 200))
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(parent, image=photo, bg=bg_color)
    image_label.image = photo  # Manter referência da imagem para evitar garbage collection
    image_label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return image_label

def create_video_button(parent, video_url, row, column, padx=10, pady=10, sticky="w"):
    """Função para criar um botão de vídeo com parâmetros ajustáveis"""
    video_button = ttk.Button(parent, text="Video do Jogo", command=lambda: open_link(video_url), style="Rounded.TButton")
    video_button.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return video_button

def create_navigation(parent, data, letter, search_text, page, total_pages):
    """Função para criar a navegação de página"""
    nav_frame = tk.Frame(parent, bg=bg_color)
    nav_frame.grid(row=0, column=0, pady=10, sticky="ew")

    if page > 1:
        prev_button = ttk.Button(nav_frame, text="Página Anterior", command=lambda: navigate_page(data, letter, search_text, page - 1), style="Rounded.TButton")
        prev_button.pack(side=tk.LEFT, padx=5)

    page_label = tk.Label(nav_frame, text=f"Página {page} de {total_pages}", font=("Helvetica", 14), bg=bg_color, fg=fg_color)
    page_label.pack(side=tk.LEFT, padx=5)

    if page < total_pages:
        next_button = ttk.Button(nav_frame, text="Próxima Página", command=lambda: navigate_page(data, letter, search_text, page + 1), style="Rounded.TButton")
        next_button.pack(side=tk.LEFT, padx=5, pady=5)

def show_content(data, letter=None, search_text="", page=1):
    """Função para exibir as imagens e links de download em um painel"""
    for widget in content_frame.winfo_children():
        widget.destroy()

    global current_page
    current_page = page

    filtered_data = [item for item in data if (not letter or item["fileName"].startswith(letter)) and (not search_text or search_text.lower() in item["fileName"].lower())]
    total_pages = (len(filtered_data) + items_per_page - 1) // items_per_page

    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    page_data = filtered_data[start_index:end_index]

    # Adicionar navegação de página no topo
    create_navigation(content_frame, data, letter, search_text, page, total_pages)

    row = 1
    for item in page_data:
        item_frame = tk.Frame(content_frame, bg=bg_color)
        item_frame.grid(row=row, column=0, pady=10, sticky="w")
        item_frame.columnconfigure(0, weight=1)

        separator_title = ttk.Separator(item_frame, orient='horizontal')
        separator_title.grid(row=0, column=0, pady=5, sticky="ew")

        create_file_name_label(item_frame, item["fileName"], row=1, column=0, padx=200, pady=10, sticky="w")

        file_description_label = tk.Label(item_frame, text=item["fileDescription"], wraplength=600, bg=bg_color, fg=fg_color)
        file_description_label.grid(row=2, column=0, pady=5, sticky="w")

        create_image_label(item_frame, item["imageUrl"], row=3, column=0, padx=190, pady=10, sticky="w")

        if "videoUrl" in item:
            create_video_button(item_frame, item["videoUrl"], row=4, column=0, padx=245, pady=10, sticky="w")

        if "magnetUris" in item:
            magnet_label = tk.Label(item_frame, text="Magnet Links:", font=("Helvetica", 14), bg=bg_color, fg=fg_color)
            magnet_label.grid(row=5, column=0, pady=5, padx=231, sticky="w")
            for i, magnet in enumerate(item["magnetUris"]):
                magnet_button = ttk.Button(item_frame, text=magnet["name"], command=lambda url=magnet["uri"]: open_link(url), style="Rounded.TButton")
                magnet_button.grid(row=6 + i, column=0, pady=2, padx=110, sticky="w")

        if "browserUris" in item:
            browser_label = tk.Label(item_frame, text="Browser Links:", font=("Helvetica", 14), bg=bg_color, fg=fg_color)
            browser_label.grid(row=6 + len(item.get("magnetUris", [])), column=0, pady=5, padx=230, sticky="w")
            for i, browser in enumerate(item["browserUris"]):
                browser_button = ttk.Button(item_frame, text=browser["name"], command=lambda url=browser["uri"]: open_link(url), style="Rounded.TButton")
                browser_button.grid(row=7 + len(item.get("magnetUris", [])) + i, column=0, pady=2, padx=110, sticky="w")

        row += 4 + len(item.get("magnetUris", [])) + len(item.get("browserUris", []))

    # Adicionar navegação de página no final
    nav_frame = tk.Frame(content_frame, bg=bg_color)
    nav_frame.grid(row=row, column=0, pady=10, sticky="ew")

    if page > 1:
        prev_button = ttk.Button(nav_frame, text="Página Anterior", command=lambda: navigate_page(data, letter, search_text, page - 1), style="Rounded.TButton")
        prev_button.pack(side=tk.LEFT, padx=5)

    page_label = tk.Label(nav_frame, text=f"Página {page} de {total_pages}", font=("Helvetica", 14), bg=bg_color, fg=fg_color)
    page_label.pack(side=tk.LEFT, padx=5)

    if page < total_pages:
        next_button = ttk.Button(nav_frame, text="Próxima Página", command=lambda: navigate_page(data, letter, search_text, page + 1), style="Rounded.TButton")
        next_button.pack(side=tk.LEFT, padx=5, pady=5)

def navigate_page(data, letter, search_text, page):
    """Função para navegar entre páginas e rolar para o topo"""
    show_content(data, letter, search_text, page)
    canvas.yview_moveto(0)

def reset_content():
    """Função para redefinir o conteúdo e voltar à página inicial"""
    show_content(data_json, page=1)

def update_json_url():
    """Função para atualizar o URL do JSON e recarregar o conteúdo"""
    global data_json
    new_url = url_entry.get()
    if not new_url.strip() or new_url.strip() == "Seu Link .json":
        print("Erro: O campo de URL do JSON está vazio ou contém um link inválido. Por favor, insira um link válido.")
        return
    try:
        data_json = download_json(new_url)
        show_content(data_json, page=1)
    except Exception as e:
        print(f"Erro ao baixar o JSON: {e}")

def on_mouse_wheel(event):
    """Função para rolar o canvas com o mouse"""
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def main():
    global root, content_frame, bg_color, fg_color, data_json, search_entry, canvas, current_page, items_per_page, url_entry

    current_page = 1
    items_per_page = 20

    try:
        root = tk.Tk()
        root.title("Download Black")
        root.state('zoomed')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 12), foreground="white")
        style.configure("Rounded.TButton", font=("Helvetica", 10), background="#0b57cf", foreground="white", borderwidth=0)
        style.map("Rounded.TButton", background=[("active", "#0b57cf")], relief=[("pressed", "flat")])

        bg_color = "#1a1c1b"
        fg_color = "white"
        root.configure(bg=bg_color)

        # Frame para o título
        title_frame = tk.Frame(root, bg=bg_color)
        title_frame.pack(side=tk.TOP, fill=tk.X, anchor="w")

        title_label = tk.Label(title_frame, text="DOWNLOAD BLACK", font=("Helvetica", 24, "bold"), bg=bg_color, fg=fg_color)
        title_label.pack(side=tk.LEFT, padx=145, pady=10)

        # Frame para o botão Home
        home_frame = tk.Frame(root, bg=bg_color)
        home_frame.pack(side=tk.TOP, fill=tk.X, anchor="w")

        home_button = ttk.Button(home_frame, text="Home", command=reset_content, style="Rounded.TButton")
        home_button.pack(side=tk.LEFT, padx=253, pady=5)

        # Frame para letras e barra de pesquisa
        header_frame = tk.Frame(root, bg=bg_color)
        header_frame.pack(side=tk.TOP, fill=tk.X, anchor="w")

        letters_frame = tk.Frame(header_frame, bg=bg_color)
        letters_frame.pack(side=tk.LEFT, anchor="w")

        letters = ["#", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        
        row = 0
        col = 0
        for letter in letters:
            button = ttk.Button(letters_frame, text=letter, command=lambda l=letter: show_content(data_json, l, page=1), style="Rounded.TButton")
            button.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            col += 1
            if col == 6:
                col = 0
                row += 1

        search_frame = tk.Frame(root, bg=bg_color)
        search_frame.pack(side=tk.TOP, pady=10, anchor="w")

        search_label = tk.Label(search_frame, text="Pesquisar:", font=("Helvetica", 14), bg=bg_color, fg=fg_color)
        search_label.pack(side=tk.LEFT, padx=5)

        search_entry = tk.Entry(search_frame, font=("Helvetica", 14), width=30)
        search_entry.pack(side=tk.LEFT, padx=5)

        search_button = ttk.Button(search_frame, text="🔍", command=lambda: show_content(data_json, search_text=search_entry.get(), page=1), style="Rounded.TButton")
        search_button.pack(side=tk.LEFT, padx=5)

        # Frame para entrada de URL do JSON
        url_frame = tk.Frame(root, bg=bg_color)
        url_frame.pack(side=tk.TOP, pady=10, anchor="w")

        url_label = tk.Label(url_frame, text="URL do JSON:", font=("Helvetica", 14), bg=bg_color, fg=fg_color)
        url_label.pack(side=tk.LEFT, padx=5)

        url_entry = tk.Entry(url_frame, font=("Helvetica", 14), width=30)
        url_entry.pack(side=tk.LEFT, padx=5)
        url_entry.insert(0, "Seu Link .json")

        update_button = ttk.Button(url_frame, text="Atualizar", command=update_json_url, style="Rounded.TButton")
        update_button.pack(side=tk.LEFT, padx=5)

        # Frame para o conteúdo com barra de rolagem
        canvas = tk.Canvas(root, bg=bg_color, highlightthickness=0)  # Remover borda branca
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=bg_color)

        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mouse wheel to scroll
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        # Não tentar baixar o JSON inicial se o campo estiver vazio
        if default_url:
            data_json = download_json(default_url)
            show_content(data_json, page=1)

        root.mainloop()
    except Exception as e:
        print(f"Erro ao executar o script: {e}")

if __name__ == "__main__":
    main()
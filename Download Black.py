import requests
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip  # Importar o pyperclip para copiar para a área de transferência

def download_json(url):
    """Função para baixar o JSON"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def open_link(url):
    """Função para abrir um link no navegador padrão"""
    import webbrowser
    webbrowser.open(url)

def copy_to_clipboard(text):
    """Função para copiar texto para a área de transferência"""
    pyperclip.copy(text)
    root.after(100, show_copy_popup)  # Exibir o popup após 100ms

def show_copy_popup():
    """Função para mostrar o popup de 'Link Copiado!'"""
    messagebox.showinfo("Link Copiado", "O seu link foi copiado!")

def create_file_name_label(parent, text):
    """Função para criar um label de nome de arquivo"""
    file_name_label = tk.Label(
        parent, text=text, font=("Helvetica", 16, "bold"), bg=bg_color, fg=fg_color
    )
    file_name_label.pack(anchor="w", pady=5)

def create_magnet_links(parent, magnet_uris):
    """Função para criar links de magnet com botão de copiar"""
    if magnet_uris:
        magnet_label = tk.Label(
            parent, text="Magnet Links:", font=("Helvetica", 14), bg=bg_color, fg=fg_color
        )
        magnet_label.pack(anchor="w", pady=5)
        for magnet in magnet_uris:
            magnet_button = ttk.Button(
                parent, text="Abrir Link", command=lambda url=magnet: open_link(url), style="Rounded.TButton"
            )
            magnet_button.pack(anchor="w", pady=2)

            # Botão para copiar o link
            copy_button = ttk.Button(
                parent, text="Copiar Link", command=lambda url=magnet: copy_to_clipboard(url), style="Rounded.TButton"
            )
            copy_button.pack(anchor="w", pady=2)

def show_content(data, letter_filter=None, page=1):
    """Função para exibir as imagens e links de download em um painel"""
    for widget in content_frame.winfo_children():
        widget.destroy()

    global current_page, current_letter_filter
    current_page = page
    current_letter_filter = letter_filter

    filtered_data = apply_filters(data['downloads'], letter_filter)
    total_items = len(filtered_data)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_index = (page - 1) * items_per_page
    end_index = min(start_index + items_per_page, total_items)
    page_data = filtered_data[start_index:end_index]

    for item in page_data:
        item_frame = tk.Frame(content_frame, bg=bg_color, pady=10)
        item_frame.pack(fill=tk.X)

        create_file_name_label(item_frame, item["title"])

        file_description_label = tk.Label(
            item_frame,
            text=f"Tamanho: {item['fileSize']} | Data de Upload: {item['uploadDate']}",
            wraplength=800,
            bg=bg_color,
            fg=fg_color,
        )
        file_description_label.pack(anchor="w", pady=5)

        create_magnet_links(item_frame, item["uris"])

        # Linha divisória
        divider = tk.Frame(content_frame, bg="gray", height=1)
        divider.pack(fill=tk.X, pady=5)

    create_navigation(content_frame, page, total_pages)

def apply_filters(downloads, letter_filter):
    """Função para filtrar os downloads com base na pesquisa e letra"""
    search_query = search_var.get().strip().lower()
    filtered = downloads
    if letter_filter and letter_filter != "#":
        filtered = [item for item in filtered if item['title'].upper().startswith(letter_filter)]
    elif letter_filter == "#":
        filtered = [item for item in filtered if not item['title'][0].isalpha()]
    if search_query:
        filtered = [item for item in filtered if search_query in item['title'].lower()]
    return filtered

def create_navigation(parent, page, total_pages):
    """Função para criar a navegação de página"""
    nav_frame = tk.Frame(parent, bg=bg_color)
    nav_frame.pack(fill=tk.X, pady=10)

    if page > 1:
        prev_button = ttk.Button(
            nav_frame, text="Página Anterior", command=lambda: navigate_page(page - 1), style="Rounded.TButton"
        )
        prev_button.pack(side=tk.LEFT, padx=5)

    page_label = tk.Label(
        nav_frame, text=f"Página {page} de {total_pages}", font=("Helvetica", 14), bg=bg_color, fg=fg_color
    )
    page_label.pack(side=tk.LEFT, padx=5)

    if page < total_pages:
        next_button = ttk.Button(
            nav_frame, text="Próxima Página", command=lambda: navigate_page(page + 1), style="Rounded.TButton"
        )
        next_button.pack(side=tk.LEFT, padx=5)

def navigate_page(page):
    """Função para navegar entre páginas e rolar para o topo"""
    show_content(data_json, current_letter_filter, page)
    canvas.yview_moveto(0)

def reset_content():
    """Função para redefinir o conteúdo e voltar à página inicial"""
    search_var.set("")
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
        reset_content()
    except Exception as e:
        print(f"Erro ao baixar o JSON: {e}")

def search_and_update():
    """Função para buscar e atualizar a exibição com base na pesquisa"""
    show_content(data_json, current_letter_filter, page=1)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def create_gog_download_button(parent):
    """Função para criar o botão de GOG Download"""
    gog_button = ttk.Button(
        parent, text="Início", command=reset_content, style="Rounded.TButton"
    )
    gog_button.pack(side=tk.LEFT, padx=10, pady=5)

def main():
    global root, content_frame, bg_color, fg_color, data_json, canvas, current_page, items_per_page, url_entry, search_var, current_letter_filter, canvas_frame

    current_page = 1
    current_letter_filter = None
    items_per_page = 20

    root = tk.Tk()
    root.title("GOG Downloader")
    root.geometry("1024x768")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TLabel", font=("Helvetica", 12), foreground="white")
    style.configure(
        "Rounded.TButton",
        font=("Helvetica", 10),
        background="#0b57cf",
        foreground="white",
        borderwidth=0,
    )
    style.map("Rounded.TButton", background=[("active", "#0b57cf")], relief=[("pressed", "flat")])

    bg_color = "#1a1c1b"
    fg_color = "white"
    root.configure(bg=bg_color)

    # Título
    title_frame = tk.Frame(root, bg=bg_color)
    title_frame.pack(side=tk.TOP, fill=tk.X)

    title_label = tk.Label(title_frame, text="GOG Downloader", font=("Helvetica", 18, "bold"), bg=bg_color, fg=fg_color)
    title_label.pack(side=tk.LEFT, padx=10, pady=10)

    # Botão "Início"
    button_frame = tk.Frame(root, bg=bg_color)
    button_frame.pack(side=tk.TOP, fill=tk.X)
    create_gog_download_button(button_frame)

    # Entrada de URL
    url_frame = tk.Frame(root, bg=bg_color)
    url_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    url_entry = ttk.Entry(url_frame, width=50)
    url_entry.insert(0, "Seu Link .json")
    url_entry.pack(side=tk.LEFT, padx=10)

    url_button = ttk.Button(url_frame, text="Carregar JSON", command=update_json_url, style="Rounded.TButton")
    url_button.pack(side=tk.LEFT, padx=5)

    # Barra de pesquisa
    search_frame = tk.Frame(root, bg=bg_color)
    search_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=50)
    search_entry.pack(side=tk.LEFT, padx=10)

    search_button = ttk.Button(search_frame, text="Pesquisar", command=search_and_update, style="Rounded.TButton")
    search_button.pack(side=tk.LEFT, padx=5)

    # Letras organizadas em 6x5
    letters_frame = tk.Frame(root, bg=bg_color)
    letters_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    letters = ["#", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    row = 0
    col = 0
    for letter in letters:
        button = ttk.Button(
            letters_frame,
            text=letter,
            command=lambda l=letter: show_content(data_json, l, page=1),
            style="Rounded.TButton"
        )
        button.grid(row=row, column=col, padx=5, pady=5)
        col += 1
        if col == 6:
            col = 0
            row += 1

    # Painel de conteúdo com scroll
    canvas_frame = tk.Frame(root, bg=bg_color)
    canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(canvas_frame, bg=bg_color, highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    content_frame = tk.Frame(canvas, bg=bg_color)
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Carregando JSON inicial
    try:
        data_json = download_json("https://example.com/your-data.json")
        reset_content()
    except Exception as e:
        print(f"Erro ao carregar o JSON inicial: {e}")

    root.mainloop()

if __name__ == "__main__":
    main()

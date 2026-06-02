import os
print(os.getcwd())
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import time
import socket
from datetime import datetime, timedelta

from onvio_automation import run_onvio_upload
from logger_config import logger, config

# Tentativa de importar suporte Drag and Drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False


class OnvioUploaderApp:

    def __init__(self, root):

        self.root = root
        self.root.title("ONVIO Batch Uploader v5.4")
        self.root.geometry("750x850")
        self.root.resizable(False, False)

        self.bg_color = "#f4f4f9"
        self.primary_color = "#0056b3"

        self.root.configure(bg=self.bg_color)

        # ---------------- STYLE ----------------
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview.Heading",
            background="#e0e0e0",
            foreground="black",
            font=("Arial", 10, "bold"),
            relief="solid",
            borderwidth=1
        )

        style.configure(
            "Custom.Treeview",
            background="white",
            fieldbackground="white",
            foreground="black",
            rowheight=35,
            relief="solid",
            borderwidth=1
        )

        style.layout(
            "Custom.Treeview",
            [('Custom.Treeview.treearea', {'sticky': 'nswe'})]
        )

        style.map(
            "Custom.Treeview",
            background=[('selected', '#0078d7')],
            foreground=[('selected', 'white')]
        )

        # ---------------- TíTULO ----------------
        tk.Label(
            root,
            text="ONVIO Batch Uploader",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        ).pack(pady=10)

        # ---------------- CONEXÃO ----------------
        self.conn_frame = tk.LabelFrame(
            root,
            text="Passo 1: Conexão",
            bg=self.bg_color,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )

        self.conn_frame.pack(
            pady=5,
            padx=20,
            fill="x"
        )

        self.connect_button = tk.Button(
            self.conn_frame,
            text="🔌 FAZER CONEXÃO",
            command=self.open_chrome_debug,
            bg="#6c757d",
            fg="white",
            font=("Arial", 10, "bold"),
            pady=5
        )

        self.connect_button.pack(fill="x")

        self.conn_status_label = tk.Label(
            self.conn_frame,
            text="Status: Desconectado",
            bg=self.bg_color,
            fg="red",
            font=("Arial", 9, "italic")
        )

        self.conn_status_label.pack(pady=5)

        # ---------------- ARQUIVOS ----------------
        self.file_frame = tk.LabelFrame(
            root,
            text="Passo 2: Arraste os Boletos (PDFs) e Informe o Código",
            bg=self.bg_color,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )

        self.file_frame.pack(
            pady=5,
            padx=20,
            fill="both",
            expand=True
        )

        self.drop_label = tk.Label(
            self.file_frame,
            text="📁 ARRASTE OS PDFs AQUI",
            bg="#e9ecef",
            fg="#495057",
            font=("Arial", 9, "italic"),
            pady=10,
            bd=2,
            relief="groove"
        )

        self.drop_label.pack(fill="x", pady=5)

        # ---------------- TABELA ----------------
        self.tree_container = tk.Frame(
            self.file_frame,
            bg="#cccccc",
            bd=1,
            relief="solid"
        )

        self.tree_container.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.tree = ttk.Treeview(
            self.tree_container,
            columns=(
                "Arquivo",
                "Código",
                "Vencimento",
                "Status"
            ),
            show="headings",
            height=6,
            style="Custom.Treeview"
        )

        self.tree.heading(
            "Arquivo",
            text="Nome do Arquivo",
            anchor="center"
        )

        self.tree.heading(
            "Código",
            text="Cód. Cliente",
            anchor="center"
        )

        self.tree.heading(
            "Vencimento",
            text="Vencimento",
            anchor="center"
        )

        self.tree.heading(
            "Status",
            text="Status",
            anchor="center"
        )

        self.tree.column(
            "Arquivo",
            width=350,
            anchor="w"
        )

        self.tree.column(
            "Código",
            width=100,
            anchor="center"
        )

        self.tree.column(
            "Vencimento",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "Status",
            width=120,
            anchor="center"
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ---------------- SCROLLBAR ----------------
        self.scrollbar = ttk.Scrollbar(
            self.tree_container,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        # ---------------- BOTÕES ----------------
        btn_frame = tk.Frame(
            self.file_frame,
            bg=self.bg_color
        )

        btn_frame.pack(
            fill="x",
            pady=5
        )

        tk.Button(
            btn_frame,
            text="Adicionar Arquivos",
            command=self.browse_files,
            bg=self.primary_color,
            fg="white",
            padx=10
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Limpar Lista",
            command=self.clear_list,
            bg="#dc3545",
            fg="white",
            padx=10
        ).pack(side="left", padx=5)

        # ---------------- INSTRUÇÕES ----------------
        self.info_frame = tk.LabelFrame(
            root,
            text="📌 Instruções de Uso e Segurança",
            bg="#fff3cd",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=10
        )

        self.info_frame.pack(
            pady=5,
            padx=20,
            fill="x"
        )

        instructions = (
            "• NÃO minimize a janela do Chrome durante o processo.\n"
            "• NÃO use o mouse ou teclado enquanto o robô estiver digitando.\n"
            "• Monitor Duplo: Você pode trabalhar na outra tela, "
            "mas evite clicar no Chrome do robô.\n"
            "• O robô automatiza: Busca > Upload > Renomear "
            "(mês/ano) > Vencimento."
        )

        tk.Label(
            self.info_frame,
            text=instructions,
            bg="#fff3cd",
            justify="left",
            font=("Arial", 9),
            fg="#856404"
        ).pack(anchor="w")

        # ---------------- CONFIRMAÇÃO ----------------
        self.confirm_var = tk.BooleanVar(value=False)

        self.confirm_check = tk.Checkbutton(
            root,
            text="Confirmo que todos os dados na lista estão corretos",
            variable=self.confirm_var,
            bg=self.bg_color,
            font=("Arial", 10, "bold"),
            command=self.toggle_upload_button
        )

        self.confirm_check.pack(pady=5)

        # ---------------- BOTÃO UPLOAD ----------------
        self.upload_button = tk.Button(
            root,
            text="CONFIRMAR E INICIAR UPLOAD EM LOTE",
            command=self.start_batch_upload,
            font=("Arial", 11, "bold"),
            bg="#28a745",
            fg="white",
            relief="flat",
            state="disabled",
            pady=12
        )

        self.upload_button.pack(
            pady=10,
            fill="x",
            padx=20
        )

        # ---------------- STATUS BAR ----------------
        self.status_var = tk.StringVar(
            value="Aguardando conexão..."
        )

        tk.Label(
            root,
            textvariable=self.status_var,
            bg="#ddd",
            font=("Arial", 8),
            anchor="w",
            padx=10
        ).pack(side="bottom", fill="x")

        # ---------------- VARIÁVEIS ----------------
        self.files_data = []
        self.chrome_online = False

        threading.Thread(
            target=self.monitor_chrome,
            daemon=True
        ).start()

        logger.info("Aplicação ONVIO Uploader iniciada.")

    # ---------------- ADICIONAR ARQUIVO ----------------
    def add_to_list(self, file_path):

        if file_path.lower().endswith('.pdf'):

            # evita duplicados
            if any(f['path'] == file_path for f in self.files_data):
                logger.info(
                    f"Arquivo {file_path} já está na lista."
                )
                return

            popup = tk.Toplevel(self.root)
            popup.title("Dados do Documento")
            popup.geometry("400x430")
            popup.resizable(False, False)
            popup.grab_set()

            file_name = os.path.basename(file_path)

            tk.Label(
                popup,
                text="Arquivo selecionado:",
                font=("Arial", 9, "bold")
            ).pack(pady=(10, 0))

            tk.Label(
                popup,
                text=file_name,
                font=("Arial", 9),
                wraplength=320,
                justify="center",
                fg="#0056b3"
            ).pack(pady=(0, 10))

            # ---------------- CÓDIGO ----------------
            tk.Label(
                popup,
                text="Código do cliente:",
                font=("Arial", 10, "bold")
            ).pack()

            code_var = tk.StringVar()

            code_entry = tk.Entry(
                popup,
                textvariable=code_var,
                font=("Arial", 11),
                justify="center"
            )

            code_entry.pack(pady=5)

            # ---------------- DATA ----------------
            tk.Label(
                popup,
                text="Vencimento:",
                font=("Arial", 10, "bold")
            ).pack(pady=(10, 0))

            now = datetime.now()

            # Variável checkbox
            last_month_var = tk.BooleanVar(value=False)

            def update_dates():

                current_date = datetime.now()

                if last_month_var.get():
                    # boleto do mês passado

                    # nome = mês passado
                    boleto_month = (
                        current_date.replace(day=1)
                        - timedelta(days=1)
                    )

                    # vencimento = mês atual
                    due_month = current_date

                else:
                    # boleto normal

                    # nome = mês atual
                    boleto_month = current_date

                    # vencimento = próximo mês
                    due_month = (
                        current_date.replace(day=1)
                        + timedelta(days=32)
                    )

                month_var.set(
                    due_month.strftime("%m")
                )

                year_var.set(
                    due_month.strftime("%Y")
                )

                file_month_var.set(
                    boleto_month.strftime("%m/%Y")
                )

            # Checkbox
            check_last_month = tk.Checkbutton(
                popup,
                text="Boleto do mês passado",
                variable=last_month_var,
                command=update_dates
            )

            check_last_month.pack(pady=5)

            # nome do boleto
            tk.Label(
                popup,
                text="Novo nome do boleto:",
                font=("Arial", 9, "bold")
            ).pack()

            file_month_var = tk.StringVar()

            file_month_entry = tk.Entry(
                popup,
                textvariable=file_month_var,
                justify="center",
                state="readonly",
                width=10
            )

            file_month_entry.pack(pady=(0, 8))

            # frame data
            date_frame = tk.Frame(popup)
            date_frame.pack(pady=5)

            # DIA
            tk.Label(
                date_frame,
                text="Dia"
            ).grid(row=0, column=0)

            day_var = tk.StringVar(value="25")

            day_entry = tk.Entry(
                date_frame,
                textvariable=day_var,
                width=5,
                justify="center"
            )

            day_entry.grid(
                row=1,
                column=0,
                padx=5
            )

            # MÊS automático
            tk.Label(
                date_frame,
                text="Mês"
            ).grid(row=0, column=1)

            month_var = tk.StringVar()

            month_entry = tk.Entry(
                date_frame,
                textvariable=month_var,
                width=5,
                justify="center",
                state="readonly"
            )

            month_entry.grid(
                row=1,
                column=1,
                padx=5
            )

            # ANO automático
            tk.Label(
                date_frame,
                text="Ano"
            ).grid(row=0, column=2)

            year_var = tk.StringVar()

            year_entry = tk.Entry(
                date_frame,
                textvariable=year_var,
                width=7,
                justify="center",
                state="readonly"
            )

            year_entry.grid(
                row=1,
                column=2,
                padx=5
            )

            update_dates()

            tk.Label(
                popup,
                text="Apenas o dia pode ser alterado",
                font=("Arial", 8),
                fg="gray"
            ).pack()

            code_entry.focus()

            def confirmar():

                code = code_var.get().strip()
                day = day_var.get().strip()

                month = month_var.get().strip()
                year = year_var.get().strip()

                new_name = file_month_var.get()

                if not code:
                    messagebox.showwarning(
                        "Aviso",
                        "Informe um código."
                    )
                    return

                try:

                    day_int = int(day)

                    if not 1 <= day_int <= 31:
                        raise ValueError()

                    due_date = (
                        f"{day_int:02d}/"
                        f"{month}/"
                        f"{year}"
                    )

                    datetime.strptime(
                        due_date,
                        "%d/%m/%Y"
                    )

                except ValueError:

                    messagebox.showwarning(
                        "Data inválida",
                        "Informe um dia válido."
                    )

                    return

                item_id = self.tree.insert(
                    "",
                    "end",
                    values=(
                        file_name,
                        code,
                        due_date,
                        "Pendente"
                    )
                )

                self.files_data.append({
                    'id': item_id,
                    'path': file_path,
                    'code': code,
                    'due_date': due_date,
                    'new_name': new_name
                })

                self.toggle_upload_button()

                logger.info(
                    f"Arquivo {file_name} "
                    f"adicionado com código "
                    f"{code}, nome "
                    f"{new_name} "
                    f"e vencimento "
                    f"{due_date}."
                )

                popup.destroy()

            tk.Button(
                popup,
                text="Confirmar",
                command=confirmar,
                bg="#28a745",
                fg="white",
                font=("Arial", 10, "bold"),
                width=15
            ).pack(pady=20)

            popup.bind(
                "<Return>",
                lambda event: confirmar()
            )

    # ---------------- LIMPAR LISTA ----------------
    def clear_list(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.files_data = []

        self.toggle_upload_button()

        logger.info("Lista limpa.")

    # ---------------- DRAG AND DROP ----------------
    def handle_drop(self, event):

        files = self.root.tk.splitlist(event.data)

        for f in files:
            self.add_to_list(f)

        self.status_var.set(
            f"{len(self.files_data)} arquivos na lista."
        )

    # ---------------- BROWSER ----------------
    def browse_files(self):

        filenames = filedialog.askopenfilenames(
            filetypes=[("PDF files", "*.pdf")]
        )

        for f in filenames:
            self.add_to_list(f)

    # ---------------- BOTÃO ----------------
    def toggle_upload_button(self):

        state = (
            "normal"
            if self.chrome_online
            and self.files_data
            and self.confirm_var.get()
            else "disabled"
        )

        self.upload_button.config(state=state)

    # ---------------- CHROME ----------------
    def is_chrome_running(self):

        try:

            with socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            ) as s:

                s.settimeout(0.5)

                return (
                    s.connect_ex(
                        ('127.0.0.1', config['chrome_debug_port'])
                    ) == 0
                )

        except Exception as e:

            logger.error(
                f"Erro ao verificar Chrome: {e}"
            )

            return False

    # ---------------- MONITOR ----------------
    def monitor_chrome(self):

        while True:

            is_running = self.is_chrome_running()

            if is_running != self.chrome_online:

                self.chrome_online = is_running

                self.root.after(
                    0,
                    self.update_conn_ui,
                    is_running
                )

            time.sleep(1.5)

    # ---------------- UPDATE UI ----------------
    def update_conn_ui(self, is_running):

        if is_running:

            self.conn_status_label.config(
                text="Status: Conectado",
                fg="green"
            )

            self.connect_button.config(
                text="✅ NAVEGADOR PRONTO",
                state="disabled",
                bg="#28a745"
            )

        else:


             self.conn_status_label.config(
                  text="Status: Desconectado",
                  fg="red"
             )
             

             self.connect_button.config(
                  text="🔌 FAZER CONEXÃO",
                  state="normal",
                  bg="#6c757d"
             )

        self.toggle_upload_button()

    # ---------------- ABRIR CHROME ----------------
    def open_chrome_debug(self):

        try:

            chrome_path = os.path.join(
                os.environ.get(
                    "PROGRAMFILES",
                    "C:\\Program Files"
                ),
                "Google\\Chrome\\Application\\chrome.exe"
            )

            if not os.path.exists(chrome_path):

                chrome_path = os.path.join(
                    os.environ.get(
                        "PROGRAMFILES(X86)",
                        "C:\\Program Files (x86)"
                    ),
                    "Google\\Chrome\\Application\\chrome.exe"
                )

            if not os.path.exists(chrome_path):

                messagebox.showerror(
                    "Erro",
                    "Chrome não encontrado."
                )

                return

            user_data_dir = config['chrome_user_data_dir']

            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)

            command = (
                f'"{chrome_path}" '
                f'--remote-debugging-port='
                f'{config["chrome_debug_port"]} '
                f'--user-data-dir="{user_data_dir}"'
            )

            subprocess.Popen(command, shell=True)

            messagebox.showinfo(
                "Conexão",
                "Chrome aberto em modo de depuração."
            )

            logger.info("Chrome iniciado em modo debug.")

        except Exception as e:

            messagebox.showerror(
                "Erro",
                f"Falha ao abrir Chrome: {e}"
            )

            logger.critical(
                f"Erro ao abrir Chrome: {e}",
                exc_info=True
            )

    # ---------------- START UPLOAD ----------------
    def start_batch_upload(self):

        if not self.files_data:
            return

        self.upload_button.config(state="disabled")
        self.confirm_check.config(state="disabled")

        threading.Thread(
            target=self.process_batch,
            daemon=True
        ).start()

    # ---------------- PROCESSAMENTO ----------------
    def process_batch(self):

        total = len(self.files_data)

        for i, file_info in enumerate(self.files_data):

            new_name = file_info['new_name']

            current_file_name = os.path.basename(
                file_info['path']
            )

            self.root.after(
                0,
                lambda text=f"Enviando {i+1}/{total}: {current_file_name}...":
                self.status_var.set(text)
            )

            self.root.after(
                0,
                lambda f=file_info, n=current_file_name:
                self.tree.item(
                    f['id'],
                    values=(
                        n,
                        f['code'],
                        f['due_date'],
                        "Enviando..."
                    )
                )
            )

            success, message = run_onvio_upload(
                file_info['path'],
                new_name,
                file_info['due_date'],
                file_info['code']
            )

            status = (
                "Sucesso"
                if success
                else f"Erro: {message[:20]}..."
            )

            self.root.after(
                0,
                lambda f=file_info,
                       n=current_file_name,
                       s=status:
                self.tree.item(
                    f['id'],
                    values=(
                        n,
                        f['code'],
                        f['due_date'],
                        s
                    )
                )
            )

            if success:
                logger.info(
                    f"Arquivo processado: "
                    f"{current_file_name}"
                )
            else:
                logger.error(
                    f"Erro ao processar "
                    f"{current_file_name}: {message}"
                )

        self.root.after(
            0,
            lambda: self.status_var.set(
                "Processamento finalizado."
            )
        )

        self.root.after(
            0,
            lambda: messagebox.showinfo(
                "Fim do Processo",
                "Todos os arquivos foram processados."
            )
        )

        self.confirm_var.set(False)

        self.confirm_check.config(state="normal")

        self.toggle_upload_button()

        logger.info("Processamento concluído.")


# ---------------- MAIN ----------------
if __name__ == "__main__":

    if HAS_DND:

        root = TkinterDnD.Tk()

        app = OnvioUploaderApp(root)

        root.drop_target_register(DND_FILES)

        root.dnd_bind(
            '<<Drop>>',
            lambda e: app.handle_drop(e)
        )

    else:

        root = tk.Tk()

        app = OnvioUploaderApp(root)

    root.mainloop()

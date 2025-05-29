import flet as ft
import sqlite3
import bcrypt
import os
from datetime import datetime

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

os.makedirs(ASSETS_DIR, exist_ok=True)

def criar_tabela_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
        )
    ''')
    conn.commit()
    conn.close()

def criar_tabela_eventos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id_data INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            cor TEXT,
            id_usuario INTEGER,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
        )
    ''')
    conn.commit()
    conn.close()

def criar_tabela_mensagens():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensagens (
            id_mensagem INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            conteudo TEXT NOT NULL,
            id_remetente INTEGER NOT NULL,
            id_destinatario INTEGER NOT NULL,
            FOREIGN KEY(id_remetente) REFERENCES usuarios(id_usuario),
            FOREIGN KEY(id_destinatario) REFERENCES usuarios(id_usuario)
        )
    ''')

def criar_admin_padrao():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    senha_hash = bcrypt.hashpw("a".encode('utf-8'), bcrypt.gensalt())
    senha_hash2 = bcrypt.hashpw("b".encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('''
            INSERT INTO usuarios (username, email, senha_hash, role)
            VALUES (?, ?, ?, ?),
                   (?, ?, ?, ?)
        ''', ("admin", "admin@admin", senha_hash, "admin",
              "user", "user@user", senha_hash2, "user"))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def verificar_login(username, senha):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id_usuario, senha_hash, role 
        FROM usuarios 
        WHERE username = ?
    ''', (username,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado and bcrypt.checkpw(senha.encode('utf-8'), resultado[1]):
        return resultado[0], resultado[2]  # Retorna (id_usuario, role)
    return None, None

def main(page: ft.Page):
    page.title = "Sistema de Autenticação"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def criar_header():
        return ft.AppBar(
            leading=ft.Image(src="icon.png"),
            title=ft.Text("projeto_agua"),
            center_title=True,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda _: page.go("/login")
                )
            ]
        )

    def criar_nav_bar(role):
        return ft.Column(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.HOME,
                    on_click=lambda _: page.go(f"/{role}/home")
                ),
                ft.IconButton(
                    icon=ft.Icons.CALENDAR_MONTH,
                    on_click=lambda _: page.go(f"/{role}/calendar")
                ),
                ft.IconButton(
                    icon=ft.Icons.MESSAGE,
                    on_click=lambda _: page.go(f"/{role}/messages")
                ),
            ]
        )

    def criar_conteudo(titulo, role, extra_controls=None):
        return ft.View(
            controls=[
                criar_header(),
                criar_nav_bar(role),
                ft.Text(titulo, size=24, weight="bold"),
                *(extra_controls or []),
            ]
        )

    def rotear(route):
        page.views.clear()
        role = page.session.get("user_role")

        if page.route == "/login":
            page.views.append(
                ft.View(
                    "/login",
                    [
                        ft.Text("Login", size=30, weight="bold"),
                        ft.TextField(label="Usuário", autofocus=True),
                        ft.TextField(label="Senha", password=True),
                        ft.ElevatedButton("Entrar", on_click=efetuar_login),
                        ft.Text("", color=ft.Colors.RED)
                    ]
                )
            )
        elif role:
            if "/home" in page.route:
                now = datetime.now()
                page.views.append(
                    criar_conteudo(
                        titulo=f"Home {role.capitalize()}",
                        role=role,
                        extra_controls=[
                            ft.Text(f"{now.strftime("%B %d, %Y")}"),
                            ft.Image(src="")
                        ],
                    )
                )
            elif "/calendar" in page.route:
                page.views.append(
                    criar_conteudo(
                        titulo=f"Calendar {role.capitalize()}",
                        role=role,
                        extra_controls=[]
                    )
                )
            else:
                page.views.append(
                    criar_conteudo(
                        titulo=f"Messages {role.capitalize()}",
                        role=role,
                        extra_controls=[

                        ]
                    )
                )
        page.update()

    def efetuar_login(e):
        username = page.views[0].controls[1].value
        senha = page.views[0].controls[2].value
        user_id, role = verificar_login(username, senha)
        
        if role:
            page.session.set("user_id", user_id)
            page.session.set("user_role", role)
            page.go(f"/{role}/home")
        else:
            page.views[0].controls[-1].value = "Credenciais inválidas!"
            page.update()

    # Inicialização
    criar_tabela_usuarios()
    criar_tabela_eventos()
    criar_admin_padrao()
    page.on_route_change = rotear
    page.go("/login")

ft.app(target=main, assets_dir=ASSETS_DIR, view=ft.AppView.FLET_APP)
import flet as ft
import sqlite3
import bcrypt
import os
from datetime import datetime

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'projeto_agua', 'src', 'database.db')
ASSETS_DIR = os.path.join(BASE_DIR, 'projeto_agua', 'src', 'assets')

# Criar diretórios se não existirem
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
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

    def criar_nav_bar(role):
        return ft.AppBar(
            title=ft.Text("Projeto Água"),
            actions=[
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
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda _: page.go("/login")
                ),
            ]
        )

    def criar_calendario(role):
        date_picker = ft.DatePicker()
        eventos_container = ft.Column()
        
        def carregar_eventos(e):
            eventos_container.controls.clear()
            if date_picker.value:
                data = date_picker.value.strftime("%Y-%m-%d")
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT titulo, descricao, cor 
                    FROM eventos 
                    WHERE data = ? AND id_usuario = ?
                ''', (data, page.session.get("user_id")))
                
                for titulo, descricao, cor in cursor.fetchall():
                    eventos_container.controls.append(
                        ft.Card(
                            ft.Container(
                                ft.Column([
                                    ft.Text(titulo, weight="bold"),
                                    ft.Text(descricao),
                                ]),
                                bgcolor=cor or ft.Colors.BLUE_GREY_100,
                                padding=10,
                                border_radius=5
                            ),
                            margin=5
                        )
                    )
                conn.close()
                
                if not eventos_container.controls:
                    eventos_container.controls.append(
                        ft.Text("Nenhum evento para esta data", italic=True)
                    )
                page.update()

        date_picker.on_change = carregar_eventos
        page.overlay.append(date_picker)

        return ft.Column([
            ft.ElevatedButton(
                "Selecionar Data",
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda _: date_picker.pick_date()
            ),
            ft.Text("Eventos:", weight="bold"),
            eventos_container,
            ft.ElevatedButton(
                "Novo Evento",
                on_click=lambda _: abrir_dialogo_evento(date_picker)
            )
        ])

    def abrir_dialogo_evento(date_picker):
        if not date_picker.value:
            page.snack_bar = ft.SnackBar(ft.Text("Selecione uma data primeiro!"))
            page.snack_bar.open = True
            page.update()
            return

        titulo = ft.TextField(label="Título")
        descricao = ft.TextField(label="Descrição", multiline=True)
        cor = ft.Dropdown(
            label="Cor",
            options=[
                ft.dropdown.Option(ft.Colors.GREEN_100, "Verde"),
                ft.dropdown.Option(ft.Colors.BLUE_100, "Azul"),
                ft.dropdown.Option(ft.Colors.RED_100, "Vermelho"),
            ]
        )

        def salvar_evento(e):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO eventos (data, titulo, descricao, cor, id_usuario)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                date_picker.value.strftime("%Y-%m-%d"),
                titulo.value,
                descricao.value,
                cor.value,
                page.session.get("user_id")
            ))
            conn.commit()
            conn.close()
            
            dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Evento salvo com sucesso!"))
            page.snack_bar.open = True
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Novo Evento - {date_picker.value.strftime('%d/%m/%Y')}"),
            content=ft.Column([titulo, descricao, cor]),
            actions=[ft.ElevatedButton("Salvar", on_click=salvar_evento)]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def criar_conteudo(titulo, role, extra_controls=None):
        return ft.View(
            controls=[
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
            if "/calendar" in page.route:
                page.views.append(
                    criar_conteudo(
                        titulo=f"Calendário {role.capitalize()}",
                        role=role,
                        extra_controls=[criar_calendario(role)]
                    )
                )
            else:
                page.views.append(
                    criar_conteudo(
                        titulo=f"Home {role.capitalize()}",
                        role=role
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

ft.app(target=main, view=ft.AppView.FLET_APP)
import flet as ft
import sqlite3
import bcrypt

# Configuração do banco de dados
def criar_tabela_usuarios():
    conn = sqlite3.connect('projeto_agua/src/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
        )
    ''')
    conn.commit()
    conn.close()

# Cria um usuário admin padrão
def criar_admin_padrao():
    conn = sqlite3.connect('projeto_agua/src/database.db')
    cursor = conn.cursor()
    senha_hash = bcrypt.hashpw("a".encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('INSERT INTO usuarios (username, email, senha_hash, role) VALUES (?, ?, ?, ?)',
                       ("admin", "admin@admin", senha_hash, "admin"))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Usuário já existe
    conn.close()

# Verifica credenciais
def verificar_login(username, senha):
    conn = sqlite3.connect('projeto_agua/src/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT senha_hash, role FROM usuarios WHERE username = ?', (username,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado and bcrypt.checkpw(senha.encode('utf-8'), resultado[0]):
        return resultado[1]  # Retorna o 'role'
    return None

# Interface Principal
def main(page: ft.Page):
    page.title = "Sistema de Autenticação"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def criar_nav_bar(role):
        """Cria a barra de navegação com base no papel do usuário"""
        return ft.AppBar(
            title=ft.Text("Projeto Água"),
            actions=[
                ft.IconButton(icon=ft.Icons.HOME, on_click=lambda _: page.go(f"/{role}/home")),
                ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: page.go(f"/{role}/calendar")),
                ft.IconButton(icon=ft.Icons.MESSAGE, on_click=lambda _: page.go(f"/{role}/messages")),
                ft.IconButton(icon=ft.Icons.LOGOUT, on_click=lambda _: page.go("/login")),
            ]
        )

    def criar_conteudo(titulo, role, extra_controls=None):
        """Layout base para todas as telas"""
        return ft.View(
            controls=[
                criar_nav_bar(role),
                ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD),
                *(extra_controls if extra_controls else []),
                # Adicione outros componentes comuns aqui
            ]
        )

    def rotear(route):
        page.views.clear()
        role = page.session.get("user_role")
        
        # Tela de Login
        if page.route == "/login":
            page.views.append(
                ft.View(
                    "/login",
                    [
                        ft.Text("Login", size=30, weight=ft.FontWeight.BOLD),
                        ft.TextField(label="Usuário", autofocus=True),
                        ft.TextField(label="Senha", password=True),
                        ft.ElevatedButton("Entrar", on_click=efetuar_login),
                        ft.Text("", color=ft.Colors.RED)
                    ]
                )
            )
        
        # Telas do Admin
        elif role == "admin":
            if "/admin/home" in page.route:
                page.views.append(criar_conteudo(
                    titulo="Home Admin",
                    role="admin",
                    extra_controls=[
                        ft.ElevatedButton("Criar Post", on_click=criar_post),
                        # ft.ElevatedButton("Gerenciar Usuários", on_click=gerenciar_usuarios)
                    ]
                ))
            elif "/admin/calendar" in page.route:
                page.views.append(criar_conteudo(
                    titulo="Calendário Admin",
                    role="admin",
                    extra_controls=[ft.Text("Calendário de postagens...")]
                ))
            elif "/admin/messages" in page.route:
                page.views.append(criar_conteudo(
                    titulo="Mensagens Admin",
                    role="admin",
                    extra_controls=[ft.Text("Caixa de entrada administrativa...")]
                ))
        
        # Telas do User
        elif role == "user":
            if "/user/home" in page.route:
                page.views.append(criar_conteudo(
                    titulo="Home User",
                    role="user",
                    extra_controls=[ft.Text("Conteúdo público atual...")]
                ))
            elif "/user/calendar" in page.route:
                page.views.append(criar_conteudo(
                    titulo="Calendário User",
                    role="user",
                    extra_controls=[ft.Text("Calendário de eventos...")]
                ))
            elif "/user/messages" in page.route:
                page.views.append(criar_conteudo(
                    titulo="Mensagens User",
                    role="user",
                    extra_controls=[ft.Text("Caixa de entrada do usuário...")]
                ))
        
        page.update()

    def efetuar_login(e):
        username = page.views[0].controls[1].value
        senha = page.views[0].controls[2].value
        role = verificar_login(username, senha)
        
        if role:
            page.session.set("user_role", role)
            page.go(f"/{role}/home")  # Redireciona para a home correspondente
        else:
            page.views[0].controls[-1].value = "Credenciais inválidas!"
            page.update()

    def criar_post(e):
        # Lógica para criar posts (exemplo)
        dialog = ft.AlertDialog(title=ft.Text("Post criado com sucesso!"))
        page.dialog = dialog
        dialog.open = True
        page.update()

    # Inicialização
    criar_tabela_usuarios()
    criar_admin_padrao()
    page.on_route_change = rotear
    page.go("/login")

ft.app(target=main, view=ft.AppView.FLET_APP)  # Para web; use `view=ft.AppView.FLET_APP` para desktop
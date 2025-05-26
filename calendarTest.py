import flet as ft
from datetime import date

# dados de exemplo
anotacoes = {
    "2025-05-25": "Aniversário",
    "2025-05-26": "Reunião importante",
}

def main(page: ft.Page):
    page.title = "Exemplo de Calendário em Flet"

    # Label para mostrar info da data
    info = ft.Text("Selecione uma data", size=16)

    # DatePicker nativo
    dp = ft.DatePicker(
        value=date.today(),
        on_change=lambda e: on_date_change(e, info),
    )

    page.add(dp, info)


def on_date_change(e, info: ft.Text):
    # formata para dd/mm/YYYY
    d = e.control.value.strftime("%d/%m/%Y")
    info.value = f"{d} — {anotacoes.get(d, 'Nenhuma anotação')}"
    e.control.page.update()


if __name__ == "__main__":
    ft.app(target=main)

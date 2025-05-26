import flet as ft
import time

def main(page: ft.Page):

    t1 = ft.Text("Txt A", size=20)
    t2 = ft.Text("Txt B", size=20)
    t3 = ft.Text("Txt C", size=20)

    first_name = ft.TextField()
    last_name = ft.TextField()
    # first_name.disabled = True
    # last_name.disabled = True
    page.add(first_name, last_name)

    def aumento(e):
        if t1.size == 20:
            t1.size *= 5
            t2.size *= 4
            t3.size *= 3
        else:
            t1.size=20
            t2.size=20
            t3.size=20

    page.add(
        ft.Row(controls=[
            t1,
            t2,
            t3,
            ft.TextField(label="Vai ao racha?"),
            ft.ElevatedButton(text="Aumento", on_click=aumento)
        ])
    )

    counter = ft.Text("0", size=50, data=0)
    t = ft.Text("Menssagem secreta que não aparece", size=60, color="pink")
    page.add(t)

    for i in range(10):
        t.value = f"Na 10° iteração um contador vai surgir! A iteração atual é a {i+1}°."
        if i >= 9:
            page.controls.pop(1)
        page.update()
        time.sleep(0.2)

    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    page.add(
        ft.SafeArea(
            ft.Container(
                counter,
                alignment=ft.alignment.center,
            ),
            expand=True,
        )
    )

ft.app(main)

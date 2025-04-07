from chromium_utils import extract_data as chrome_data
from firefox_utils import extract_passwords as firefox_pass
import flet as ft
import utils
import config
import os

if __name__ == "__main__":

    def main(page: ft.Page):
        page.title = "HBDPython"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        page.bgcolor = ft.Colors.BLACK
        log_output = ft.Column(auto_scroll=True)

        def switch_to_config(e=None):
            main_view.visible = False
            config_view.visible = True

            # Ajout des contrôles de sélection de fichiers
            page.add(result_picker, profil_picker)
            page.update()

        def switch_to_main(e=None):
            config_view.visible = False
            main_view.visible = True

            # Suppression des contrôles de sélection de fichiers
            page.remove(result_picker, profil_picker)
            page.update()

        def run_clicked(e):
            log_output.controls.append(
                ft.Text("▶️ Exécution en cours...", color=ft.Colors.GREEN_300)
            )
            utils.set_platform()
            firefox_pass()
            chrome_data()
            page.update()       

        # Text inputs
        result_folder_input = ft.TextField(
            label="📂 Dossier résultat, cliquez pour modifier",
            value=config.DEFAULT_RESULT_PATH,
            width=600,
            read_only=True,
            on_click=lambda _: result_picker.get_directory_path(),
            mouse_cursor=ft.MouseCursor.CLICK,
        )

        profil_path_input = ft.TextField(
            label="📂 Dossier du profil utilisateur (Automatique par défaut), cliquez pour modifier",
            width=800,
            read_only=True,
            on_click=lambda _: profil_picker.get_directory_path(),
            mouse_cursor=ft.MouseCursor.CLICK,
        )
        
        
        checkboxes = []
        for key, item in config.OPTIONS.items():
            checkbox = ft.Checkbox(
                label=item["name"],
                value=item.get("default", False),
                tooltip=item.get("description", ""),
                width=200
            )
            checkboxes.append(checkbox)


        def result_picker_folder(e: ft.FilePickerResultEvent):
            if e.path:
                result_folder_input.value = e.path
                # Créer le dossier s'il n'existe pas
                try:
                    if not os.path.exists(e.path):
                        os.makedirs(e.path)
                    result_folder_input.update()
                    config.DEFAULT_RESULT_PATH = e.path    
                except OSError as error:
                    result_folder_input.value = f"Erreur de création du dossier : {error}"
    
        def result_profil_folder(e: ft.FilePickerResultEvent):
            if e.path:
                profil_path_input.value = e.path
                profil_path_input.update()

        # File pickers
        result_picker = ft.FilePicker(
            on_result=result_picker_folder
        )

        profil_picker = ft.FilePicker(
            on_result=result_profil_folder
        )

        config_dialog = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        result_folder_input,
                    ],
                ),
                ft.Row(
                    controls=[
                        profil_path_input,
                    ],
                ),
                ft.Column(controls=checkboxes),
            ]
        )

        # Header avec icône et bouton config
        header = ft.Row(
            controls=[
                ft.Text("Hack Browser Data Python", size=20, weight="bold"),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS, tooltip="Configuration", on_click=switch_to_config
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Zone de logs
        log_container = ft.Container(
            content=log_output,
            height=200,
            width=400,
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=10,
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
        )

        # Contenu central
        content = ft.Row(
            controls=[
            ft.ElevatedButton("🚀 Run", on_click=run_clicked, width=200, height=50),
            log_container,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
            expand=True,
        )

        ### MAIN VIEW ###
        main_view = ft.Column(controls=[header, content], visible=True)

        ### CONFIG VIEW ###
        config_view = ft.Column(
            controls=[
                ft.Text("⚙️ Configuration", size=20, weight="bold"),
                config_dialog,
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "⬅️ Retour",
                            on_click=switch_to_main,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            visible=False,
        )

        # Ajout des vues à la page
        page.add(main_view, config_view)

    ft.app(target=main)

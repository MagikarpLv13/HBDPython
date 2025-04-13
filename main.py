from chromium_utils import extract_data as chrome_data
import flet as ft
import utils
import config
import os

if __name__ == "__main__":

    def main(page: ft.Page):
        utils.PAGE = page
        utils.PAGE.title = "HBDPython"
        utils.PAGE.theme_mode = ft.ThemeMode.DARK
        utils.PAGE.padding = 20
        utils.PAGE.scroll = ft.ScrollMode.AUTO
        utils.PAGE.bgcolor = ft.Colors.BLACK
        utils.PAGE.window.height = 600
        utils.PAGE.window.width = 1000
        utils.LOG = ft.ListView(
            expand=True,
            spacing=10,
            height=200,
            width=500,
            padding=10,            
        )
        

        def switch_to_config(e=None):
            main_view.visible = False
            config_view.visible = True

            # Ajout des contrôles de sélection de fichiers
            utils.PAGE.add(result_picker)
            utils.PAGE.update()

        def switch_to_main(e=None):
            config_view.visible = False
            main_view.visible = True

            # Suppression des contrôles de sélection de fichiers
            utils.PAGE.remove(result_picker)
            utils.PAGE.update()

        # Mise à jour de la visibilité du bouton après l'extraction
        def run_clicked(e):
            # Cacher le bouton de résultats pendant l'extraction
            view_results_button.visible = False
            # Empêcher le clic sur le bouton pendant l'extraction
            header.controls[2].disabled = True            
            utils.add_to_log("▶️ Exécution en cours...", style="info")
            utils.set_platform()
            chrome_data()
            utils.add_to_log("✅ Extraction terminée !", style="success")
            # Afficher le bouton de résultats après l'extraction
            view_results_button.visible = True
            # Rendre le bouton de configuration cliquable à nouveau
            header.controls[2].disabled = False
            utils.PAGE.update()      

        # Text inputs
        result_folder_input = ft.TextField(
            label="📂 Dossier résultat, cliquez pour modifier",
            value=config.DEFAULT_RESULT_PATH,
            width=600,
            read_only=True,
            on_click=lambda _: result_picker.get_directory_path(),
            mouse_cursor=ft.MouseCursor.CLICK,
        )

        # Met à jour la valeur de l'option dans le fichier de configuration
        def checkbox_changed(e):
            config.OPTIONS[e.control.key]["active"] = e.control.value

        checkboxes = []
        for key, item in config.OPTIONS.items():
            checkbox = ft.Checkbox(
                key=key,
                label=item["name"],
                value=item.get("default", False),
                tooltip=item.get("description", ""),
                width=200,
                on_change=checkbox_changed,
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

        # File pickers
        result_picker = ft.FilePicker(
            on_result=result_picker_folder
        )

        config_dialog = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        result_folder_input,
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
            content=utils.LOG,
            height=200,
            width=600,
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
        
        # Bouton Résultats centré
        view_results_button = ft.Container(
            content=ft.ElevatedButton(
            "📂 Voir les résultats",
            on_click=lambda _: os.startfile(config.DEFAULT_RESULT_PATH),
            visible=True,
            width=200,
            height=50,
            ),
            alignment=ft.alignment.center,
            visible=False,
        )

        ### MAIN VIEW ###
        main_view = ft.Column(controls=[header, content], visible=True)
        main_view.controls.append(view_results_button)

        ### CONFIG VIEW ###
        config_view = ft.Column(
            controls=[
                ft.Text("⚙️ Configuration", size=20, weight="bold"),
                config_dialog,
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "🔙 Retour",
                            on_click=switch_to_main,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            visible=False,
        )

        # Ajout des vues à la page
        utils.PAGE.add(main_view, config_view)

    ft.app(target=main)

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib
import subprocess
import os
import threading

class ExtrairAudioApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.extrairaudio",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.janela = Gtk.ApplicationWindow(application=app)
        self.janela.set_title("Media Audio Extractor | Converter/Extrair Áudio")
        self.janela.set_default_size(650, 370)  # Ajuste a altura para acomodar o rodapé
        self.janela.set_resizable(False)
        self.janela.set_border_width(20)
        self.janela.set_position(Gtk.WindowPosition.CENTER)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.janela.add(main_box)

        # Seção de Configuração
        config_frame = Gtk.Frame(label="Selecionar Arquivo de Vídeo/Áudio")
        config_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        config_frame.add(config_box)
        main_box.pack_start(config_frame, False, False, 0)

        # Arquivo de Vídeo/Áudio
        file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.file_chooser = Gtk.FileChooserButton.new("Selecione o arquivo", Gtk.FileChooserAction.OPEN)
        self.adicionar_filtros(self.file_chooser)
        self.file_chooser.connect("file-set", self.on_file_selected)

        self.entry_file_path = Gtk.Entry()
        self.entry_file_path.set_editable(False)
        self.entry_file_path.set_hexpand(True)

        file_box.pack_start(self.file_chooser, True, True, 0)
        file_box.pack_start(self.entry_file_path, True, True, 0)
        config_box.pack_start(file_box, False, False, 0)

        # Saída
        output_frame = Gtk.Frame(label="Arquivo de Saída:")
        output_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        output_frame.add(output_box)

        output_info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.entry_nome_saida = Gtk.Entry()
        self.entry_nome_saida.set_placeholder_text("arquivo-audio")
        self.entry_nome_saida.set_text("arquivo-audio")
        self.entry_nome_saida.set_hexpand(True)
        output_info_box.pack_start(self.entry_nome_saida, True, True, 0)

        lbl_tipo = Gtk.Label(label="Tipo:")
        output_info_box.pack_start(lbl_tipo, False, False, 0)

        self.format_combo = Gtk.ComboBoxText()
        self.format_combo.append("mp3", "MP3")
        self.format_combo.append("wav", "WAV")
        self.format_combo.append("ogg", "OGG")
        self.format_combo.append("aac", "AAC")
        self.format_combo.set_active(0)
        output_info_box.pack_start(self.format_combo, False, False, 0)

        output_box.pack_start(output_info_box, False, False, 0)
        main_box.pack_start(output_frame, False, False, 0)

        # Seletor de pasta de saída
        pasta_frame = Gtk.Frame(label="Selecione a Pasta de Destino")
        pasta_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        pasta_frame.add(pasta_box)

        self.folder_chooser_saida = Gtk.FileChooserButton.new("Selecione a pasta", Gtk.FileChooserAction.SELECT_FOLDER)
        pasta_box.pack_start(self.folder_chooser_saida, True, True, 0)
        main_box.pack_start(pasta_frame, False, False, 0)

        # Botões
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.btn_converter = Gtk.Button(label="Converter/Extrair Áudio")
        self.btn_converter.connect("clicked", self.on_converter)
        self.btn_cancelar = Gtk.Button(label="Fechar")
        self.btn_cancelar.connect("clicked", self.on_fechar)
        button_box.pack_start(self.btn_converter, True, True, 0)
        button_box.pack_start(self.btn_cancelar, True, True, 0)
        main_box.pack_start(button_box, False, False, 0)

        # Status
        self.lbl_status = Gtk.Label(label="Status: Aguardando")
        self.lbl_status.set_halign(Gtk.Align.START)
        main_box.pack_start(self.lbl_status, False, False, 0)

        # Rótulo para exibir o PID do processo
        self.lbl_pid = Gtk.Label(label="PID: Aguardando")
        self.lbl_pid.set_halign(Gtk.Align.START)
        main_box.pack_start(self.lbl_pid, False, False, 0)

        # Footer
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        lbl_footer = Gtk.Label(label="Donate PayPal: Sergio ReOli (sergioreoli@hotmail.com)")
        lbl_footer.set_halign(Gtk.Align.START)
        footer_box.pack_start(lbl_footer, False, False, 0)
        main_box.pack_end(footer_box, False, False, 0)

        self.janela.show_all()

    def adicionar_filtros(self, file_chooser):
        formatos = [
            ("Arquivos MP4", "*.mp4"),
            ("Arquivos MKV", "*.mkv"),
            ("Arquivos AVI", "*.avi"),
            ("Arquivos MOV", "*.mov"),
            ("Arquivos MP3", "*.mp3"),
            ("Arquivos WAV", "*.wav"),
            ("Arquivos OGG", "*.ogg"),
            ("Arquivos AAC", "*.aac")
        ]

        for nome, padrao in formatos:
            file_filter = Gtk.FileFilter()
            file_filter.set_name(nome)
            file_filter.add_pattern(padrao)
            file_chooser.add_filter(file_filter)

    def on_file_selected(self, widget):
        arquivo = self.file_chooser.get_filename()
        if arquivo:
            self.entry_file_path.set_text(arquivo)

    def on_fechar(self, button):
        self.quit()

    def on_converter(self, button):
        input_path = self.file_chooser.get_filename()
        output_name = self.entry_nome_saida.get_text().strip()
        output_folder = self.folder_chooser_saida.get_filename()
        output_format = self.format_combo.get_active_id()

        if not input_path or not output_name or not output_folder or not output_format:
            self.mostrar_erro("Preencha todos os campos corretamente!")
            return

        output_path = os.path.join(output_folder, f"{output_name}.{output_format}")

        if os.path.exists(output_path):
            resposta = self.confirmar_sobrescrever(output_path)
            if not resposta:
                self.lbl_status.set_text("Status: Cancelado pelo usuário")
                return

        self.lbl_status.set_text("Status: Convertendo/Extraindo...")
        self.btn_converter.set_sensitive(False)

        thread = threading.Thread(target=self.executar_ffmpeg, args=(input_path, output_path))
        thread.start()

    def executar_ffmpeg(self, input_path, output_path):
        try:
            comando = ['ffmpeg', '-y', '-i', input_path, output_path]

            processo = subprocess.Popen(
                comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            GLib.idle_add(self.lbl_pid.set_text, f"PID: {processo.pid}")

            stdout, stderr = processo.communicate()

            if processo.returncode == 0:
                GLib.idle_add(self.lbl_status.set_text,
                              f"Status: Arquivo convertido/extraído para: {output_path}")
                GLib.idle_add(self.mostrar_info, "Concluído", "Conversão/Extração concluída com sucesso!")
            else:
                GLib.idle_add(self.lbl_status.set_text, "Status: Erro na conversão/extração")
                GLib.idle_add(self.mostrar_erro, f"Erro na conversão/extração:\n{stderr}")

        except Exception as e:
            GLib.idle_add(self.lbl_status.set_text, "Status: Erro")
            GLib.idle_add(self.mostrar_erro, str(e))
        finally:
            GLib.idle_add(self.btn_converter.set_sensitive, True)

    def confirmar_sobrescrever(self, arquivo):
        dialog = Gtk.MessageDialog(
            transient_for=self.janela,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Arquivo já existe"
        )
        dialog.format_secondary_text(
            f"O arquivo '{os.path.basename(arquivo)}' já existe na pasta de destino.\n"
            "Deseja sobrescrevê-lo?"
        )
        resposta = dialog.run()
        dialog.destroy()
        return resposta == Gtk.ResponseType.YES

    def mostrar_info(self, titulo, mensagem):
        dialog = Gtk.MessageDialog(
            transient_for=self.janela,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=titulo
        )
        dialog.format_secondary_text(mensagem)
        dialog.run()
        dialog.destroy()

    def mostrar_erro(self, mensagem):
        dialog = Gtk.MessageDialog(
            transient_for=self.janela,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Erro"
        )
        dialog.format_secondary_text(mensagem)
        dialog.run()
        dialog.destroy()

app = ExtrairAudioApp()
app.run(None)

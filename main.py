import sys
import os
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QLabel, QLineEdit, QMessageBox, QDialog, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QHBoxLayout
)
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt, QSettings

CONFIG_FILE = "config.json"

def load_config():
    default_config = {
        "included_extensions": ["py", "ts", "js", "cs", "gd", "html", "css"],
        "ignored_patterns": ["node_modules", "dist", "venv", ".git", "__pycache__"],
        "language_mapping": {
            "Python": ["py"],
            "TypeScript": ["ts", "tsx"],
            "JavaScript": ["js", "jsx"],
            "C#": ["cs"],
            "Godot (GDScript)": ["gd"],
            "HTML": ["html"],
            "CSS": ["css"]
        }
    }
    config_path = Path(CONFIG_FILE)
    if config_path.exists():
        with config_path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    else:
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config

class GPTCodeExporter(QWidget):

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.setWindowTitle("Code Exporter")
        self.setMinimumSize(800, 600)

        self.config = load_config()
        self.settings = QSettings("CodeExporter", "GPTExporter")
        self.current_folder = None

        self.layout = QVBoxLayout()

        self.label = QLabel("Extensions à inclure (séparées par des virgules, ex: py,ts,cs):")
        self.layout.addWidget(self.label)

        self.extension_input = QLineEdit()
        self.layout.addWidget(self.extension_input)

        self.ignore_label = QLabel("Dossiers/fichiers à ignorer (ex: node_modules,dist,venv):")
        self.layout.addWidget(self.ignore_label)

        self.ignore_input = QLineEdit()
        self.layout.addWidget(self.ignore_input)

        self.restore_settings()

        self.extension_input.textChanged.connect(self.update_preview_file_list)
        self.ignore_input.textChanged.connect(self.update_preview_file_list)

        self.lang_button = QPushButton("Choisir les langages à inclure")
        self.lang_button.clicked.connect(self.open_language_selector)
        self.layout.addWidget(self.lang_button)

        self.select_button = QPushButton("Charger un dossier")
        self.select_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_button)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher un fichier...")
        self.search_bar.textChanged.connect(self.filter_tree_items)
        self.layout.addWidget(self.search_bar)

        self.preview_label = QLabel("Fichiers qui seront extraits :")
        self.layout.addWidget(self.preview_label)

        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderHidden(True)
        self.layout.addWidget(self.preview_tree)

        self.button_bar = QHBoxLayout()
        self.check_all_button = QPushButton("Tout cocher")
        self.check_all_button.clicked.connect(lambda: self.set_all_items_checked(True))
        self.uncheck_all_button = QPushButton("Tout décocher")
        self.uncheck_all_button.clicked.connect(lambda: self.set_all_items_checked(False))
        self.button_bar.addWidget(self.check_all_button)
        self.button_bar.addWidget(self.uncheck_all_button)
        self.layout.addLayout(self.button_bar)

        self.extract_button = QPushButton("Extraire le code")
        self.extract_button.clicked.connect(self.extract_code)
        self.layout.addWidget(self.extract_button)

        self.output_text = QTextEdit()
        self.layout.addWidget(self.output_text)

        self.save_button = QPushButton("Sauvegarder dans un fichier")
        self.save_button.clicked.connect(self.save_to_file)
        self.layout.addWidget(self.save_button)

        self.copy_button = QPushButton("Copier dans le presse-papiers")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.layout.addWidget(self.copy_button)

        self.setWindowTitle("📦 Code Exporter")
        self.preview_label.setText("🧾 Fichiers qui seront extraits :")
        self.check_all_button.setText("✅ Tout cocher")
        self.uncheck_all_button.setText("❌ Tout décocher")
        self.extract_button.setText("🚀 Extraire le code")
        self.save_button.setText("💾 Sauvegarder dans un fichier")
        self.copy_button.setText("📋 Copier dans le presse-papiers")
        self.select_button.setText("📂 Charger un dossier")
        self.lang_button.setText("🧠 Choisir les langages à inclure")
        self.search_bar.setPlaceholderText("🔍 Rechercher un fichier...")

        self.setLayout(self.layout)

    def restore_settings(self):
        ext = self.settings.value("included_extensions")
        ignore = self.settings.value("ignored_patterns")
        if ext:
            self.extension_input.setText(ext)
        else:
            self.extension_input.setText(",".join(self.config["included_extensions"]))
        if ignore:
            self.ignore_input.setText(ignore)
        else:
            self.ignore_input.setText(",".join(self.config["ignored_patterns"]))

    def open_language_selector(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Choisir les langages à inclure")
        layout = QVBoxLayout()
        checkboxes = []

        current_exts = set(self.extension_input.text().split(","))
        for lang, exts in self.config["language_mapping"].items():
            checkbox = QCheckBox(f"{lang} ({', '.join(exts)})")
            checkbox.setChecked(any(ext in current_exts for ext in exts))
            checkboxes.append((checkbox, exts))
            layout.addWidget(checkbox)

        def apply_selection():
            selected_exts = set()
            for checkbox, exts in checkboxes:
                if checkbox.isChecked():
                    selected_exts.update(exts)
            self.extension_input.setText(",".join(sorted(selected_exts)))
            dialog.accept()

        apply_button = QPushButton("Valider")
        apply_button.clicked.connect(apply_selection)
        layout.addWidget(apply_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Choisir un dossier", os.getcwd())
        if not folder_path:
            return
        self.current_folder = Path(folder_path)
        gitignore_path = self.current_folder / ".gitignore"
        if gitignore_path.exists():
            with gitignore_path.open("r", encoding="utf-8", errors="ignore") as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
                current_ignores = set(self.ignore_input.text().split(","))
                current_ignores.update(lines)
                self.ignore_input.setText(",".join(sorted(current_ignores)))

        self.update_preview_file_list()

    def update_preview_file_list(self):
        if not self.current_folder:
            return

        self.preview_tree.clear()
        self.settings.setValue("included_extensions", self.extension_input.text())
        self.settings.setValue("ignored_patterns", self.ignore_input.text())

        extensions = set(ext.strip().lower() for ext in self.extension_input.text().split(",") if ext.strip())
        ignore_patterns = set(p.strip().lower() for p in self.ignore_input.text().split(",") if p.strip())

        files = []
        for path in self.current_folder.rglob("*"):
            if not path.is_file():
                continue
            relative_path = path.relative_to(self.current_folder).as_posix()
            if any(pattern in relative_path.lower() for pattern in ignore_patterns):
                continue
            if path.suffix[1:].lower() in extensions:
                files.append(relative_path)

        self.preview_label.setText(f"Fichiers à extraire ({len(files)} fichier(s))")

        for file_path in sorted(files):
            item = QTreeWidgetItem([file_path])
            item.setCheckState(0, Qt.Checked)
            self.preview_tree.addTopLevelItem(item)

    def set_all_items_checked(self, checked: bool):
        for i in range(self.preview_tree.topLevelItemCount()):
            item = self.preview_tree.topLevelItem(i)
            if not item.isHidden():
                item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)

    def filter_tree_items(self, text):
        for i in range(self.preview_tree.topLevelItemCount()):
            item = self.preview_tree.topLevelItem(i)
            item.setHidden(text.lower() not in item.text(0).lower())

    def extract_code(self):
        if not self.current_folder:
            QMessageBox.warning(self, "Erreur", "Aucun dossier n'a été chargé.")
            return

        output = []
        for i in range(self.preview_tree.topLevelItemCount()):
            item = self.preview_tree.topLevelItem(i)
            if item.checkState(0) != Qt.Checked:
                continue
            file_path = self.current_folder / item.text(0)
            if file_path.exists() and file_path.is_file():
                try:
                    code = file_path.read_text(encoding="utf-8", errors="ignore")
                    ext = file_path.suffix[1:]
                    block = f"// {item.text(0)}\n```{ext}\n{code.strip()}\n```"
                    output.append(block)
                except Exception as e:
                    print(f"Erreur de lecture pour {file_path}: {e}")

        result = "\n\n".join(output)
        self.output_text.setPlainText(result)

    def save_to_file(self):
        if not self.output_text.toPlainText().strip():
            QMessageBox.warning(self, "Erreur", "Rien à sauvegarder.")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder le fichier", "code_for_gpt.txt", "Text Files (*.txt)")
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(self.output_text.toPlainText())
                QMessageBox.information(self, "Succès", "Fichier sauvegardé avec succès.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Échec de la sauvegarde : {e}")

    def copy_to_clipboard(self):
        text = self.output_text.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        line_count = text.count("\n") + 1 if text.strip() else 0
        QMessageBox.information(
            self,
            "📋 Copié",
            f"Le code a été copié dans le presse-papiers.\n\n📄 {line_count} ligne(s) copiée(s)."
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.is_dir():
                self.current_folder = path
                gitignore_path = path / ".gitignore"
                if gitignore_path.exists():
                    with gitignore_path.open("r", encoding="utf-8", errors="ignore") as f:
                        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
                        current_ignores = set(self.ignore_input.text().split(","))
                        current_ignores.update(lines)
                        self.ignore_input.setText(",".join(sorted(current_ignores)))
                self.update_preview_file_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPTCodeExporter()
    window.show()
    sys.exit(app.exec_())

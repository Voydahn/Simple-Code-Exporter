# 📦 GPT Code Exporter

A PyQt5-based desktop application that helps you extract source code from a selected folder while allowing filtering by file extension, exclusion of ignored folders (like `.git`, `node_modules`, etc.), and dynamic preview of selected files. You can copy the extracted code to the clipboard or save it into a single text file.

---

## ✨ Features

- ✅ Include or exclude file extensions dynamically
- 🔍 Live file preview with a search bar
- 🧠 Language-based extension selection
- 📂 Load folder with optional `.gitignore` support
- 📝 Tree view with check/uncheck toggles
- 🚀 Code extraction with syntax-tagged code blocks
- 💾 Save the output to a `.txt` file
- 📋 Copy to clipboard with line count notification
- 🖱️ Drag and drop folder support

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PyQt5

### Installation

```bash
pip install pyqt5
```

### Running the App

```bash
python main.py
```

---

## 🗂️ Project Structure

```
project_root/
├── main.py           # Main application file (PyQt5 GUI)
├── config.json       # Default configuration for extensions and ignore patterns
└── code_for_gpt.txt  # Output file (optional)
```

---

## ⚙️ Configuration

On first run, a `config.json` file is created. It includes:
- File extensions grouped by language
- Default ignored folders (e.g., `.git`, `node_modules`, `venv`, etc.)

This can be modified manually or through the app interface.

---

## ⚠️ Disclaimer

This is an unfinished application. It is provided **as-is**, primarily intended for portfolio demonstration purposes.

This project is currently a work in progress and is shared in its current state. It may not yet be production-ready.

---

## 📄 License

This project is shared for **learning and demonstration purposes only**.


import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class BearCoreStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("BearCore Studio V0.2")
        self.root.geometry("1200x760")
        self.bearcore = None
        self.running = False
        self.logs = []

        self.build_ui()
        self.log("Studio käynnistetty.")
        self.refresh_modules()
        self.refresh_git()

    def build_ui(self):
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="BearCore Studio V0.2",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left")

        self.status = tk.StringVar(value="● Offline")
        ttk.Label(header, textvariable=self.status).pack(side="right", padx=10)

        self.start_btn = ttk.Button(
            header, text="Käynnistä BearCore", command=self.start
        )
        self.start_btn.pack(side="right")

        self.stop_btn = ttk.Button(
            header, text="Pysäytä", command=self.stop, state="disabled"
        )
        self.stop_btn.pack(side="right", padx=5)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.chat_tab = ttk.Frame(self.tabs)
        self.memory_tab = ttk.Frame(self.tabs)
        self.tools_tab = ttk.Frame(self.tabs)
        self.modules_tab = ttk.Frame(self.tabs)
        self.tests_tab = ttk.Frame(self.tabs)
        self.git_tab = ttk.Frame(self.tabs)
        self.log_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.chat_tab, text="Chat")
        self.tabs.add(self.memory_tab, text="Muisti")
        self.tabs.add(self.tools_tab, text="Työkalut")
        self.tabs.add(self.modules_tab, text="Moduulit")
        self.tabs.add(self.tests_tab, text="Testit")
        self.tabs.add(self.git_tab, text="GitHub")
        self.tabs.add(self.log_tab, text="Loki")

        self.build_chat()
        self.build_memory()
        self.build_tools()
        self.build_modules()
        self.build_tests()
        self.build_git()
        self.build_log()

    def build_chat(self):
        self.chat = tk.Text(self.chat_tab, state="disabled", wrap="word")
        self.chat.pack(fill="both", expand=True, padx=8, pady=8)

        row = ttk.Frame(self.chat_tab)
        row.pack(fill="x", padx=8, pady=(0, 8))

        self.input = ttk.Entry(row)
        self.input.pack(side="left", fill="x", expand=True)
        self.input.bind("<Return>", lambda _: self.send())

        ttk.Button(row, text="Lähetä", command=self.send).pack(
            side="left", padx=5
        )

        ttk.Label(
            self.chat_tab,
            text="/module nimi   /test   /git viesti   /memory"
        ).pack(anchor="w", padx=10, pady=(0, 8))

    def build_memory(self):
        row = ttk.Frame(self.memory_tab)
        row.pack(fill="x", padx=8, pady=8)

        ttk.Button(row, text="Päivitä", command=self.refresh_memory).pack(side="left")
        ttk.Button(
            row, text="Tärkeys", command=self.change_importance
        ).pack(side="left", padx=5)
        ttk.Button(
            row, text="Poista", command=self.delete_memory
        ).pack(side="left")

        cols = ("importance", "category", "source", "text")
        self.memory = ttk.Treeview(
            self.memory_tab, columns=cols, show="headings"
        )
        for c, title, width in [
            ("importance", "Tärkeys", 100),
            ("category", "Kategoria", 110),
            ("source", "Lähde", 80),
            ("text", "Muisto", 700),
        ]:
            self.memory.heading(c, text=title)
            self.memory.column(c, width=width)
        self.memory.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def build_tools(self):
        row = ttk.Frame(self.tools_tab)
        row.pack(fill="x", padx=8, pady=8)
        ttk.Button(row, text="Päivitä", command=self.refresh_tools).pack(side="left")

        self.tools = ttk.Treeview(
            self.tools_tab, columns=("name",), show="headings"
        )
        self.tools.heading("name", text="Työkalu")
        self.tools.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def build_modules(self):
        row = ttk.Frame(self.modules_tab)
        row.pack(fill="x", padx=8, pady=8)

        ttk.Button(row, text="Päivitä", command=self.refresh_modules).pack(side="left")
        ttk.Button(row, text="Luo moduuli", command=self.create_module).pack(
            side="left", padx=5
        )
        ttk.Button(row, text="Avaa kansio", command=self.open_modules).pack(
            side="left"
        )

        self.modules = ttk.Treeview(
            self.modules_tab,
            columns=("name", "path", "status"),
            show="headings"
        )
        self.modules.heading("name", text="Moduuli")
        self.modules.heading("path", text="Polku")
        self.modules.heading("status", text="Tila")
        self.modules.column("name", width=220)
        self.modules.column("path", width=650)
        self.modules.column("status", width=130)
        self.modules.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def build_tests(self):
        ttk.Button(
            self.tests_tab, text="Aja pytest", command=self.run_tests
        ).pack(anchor="w", padx=8, pady=8)

        self.test_output = tk.Text(
            self.tests_tab, state="disabled", wrap="word"
        )
        self.test_output.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def build_git(self):
        row = ttk.Frame(self.git_tab)
        row.pack(fill="x", padx=8, pady=8)

        ttk.Button(row, text="Status", command=self.refresh_git).pack(side="left")
        ttk.Button(
            row, text="Checkpoint + Push", command=self.git_checkpoint
        ).pack(side="left", padx=5)

        self.git_output = tk.Text(
            self.git_tab, state="disabled", wrap="word"
        )
        self.git_output.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def build_log(self):
        self.log_output = tk.Text(
            self.log_tab, state="disabled", wrap="word"
        )
        self.log_output.pack(fill="both", expand=True, padx=8, pady=8)

    def start(self):
        if self.running:
            return
        try:
            from core.engine import BearCore
            self.bearcore = BearCore()
            self.running = True
            self.status.set("● Online")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.log("BearCore käynnistetty.")
            self.chat_add("Studio", "BearCore on käynnissä.")
            self.refresh_memory()
            self.refresh_tools()
        except Exception as exc:
            self.error("BearCore käynnistysvirhe", exc)

    def stop(self):
        self.bearcore = None
        self.running = False
        self.status.set("● Offline")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("BearCore pysäytetty.")

    def send(self):
        text = self.input.get().strip()
        if not text:
            return
        self.input.delete(0, "end")
        self.chat_add("Sinä", text)

        if self.command(text):
            return

        if not self.running:
            self.chat_add("Studio", "Käynnistä BearCore ensin.")
            return

        threading.Thread(
            target=self.process,
            args=(text,),
            daemon=True
        ).start()

    def command(self, text):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "/test":
            self.run_tests()
            self.chat_add("Studio", "Testit käynnistetty.")
            return True

        if cmd == "/module":
            self.create_module(parts[1] if len(parts) > 1 else None)
            return True

        if cmd == "/git":
            self.git_checkpoint(parts[1] if len(parts) > 1 else None)
            return True

        if cmd == "/memory":
            self.tabs.select(self.memory_tab)
            self.refresh_memory()
            return True

        return False

    def process(self, text):
        try:
            response = self.bearcore.process(text)
            self.root.after(0, lambda: self.chat_add("BearCore", response))
            self.root.after(0, self.refresh_memory)
        except Exception as exc:
            self.root.after(0, lambda: self.error("Vastausvirhe", exc))

    def refresh_memory(self):
        if not self.running:
            return

        for item in self.memory.get_children():
            self.memory.delete(item)

        try:
            for i, m in enumerate(self.bearcore.memory_manager.get_all()):
                self.memory.insert(
                    "", "end", iid=str(i),
                    values=(
                        m.get("importance", "normal"),
                        m.get("category", "unknown"),
                        m.get("source", ""),
                        m.get("text", "")
                    )
                )
        except Exception as exc:
            self.log("Muistin lukuvirhe: " + str(exc))

    def change_importance(self):
        selection = self.memory.selection()
        if not selection or not self.running:
            return

        index = int(selection[0])
        memories = self.bearcore.memory_manager.get_all()
        if index >= len(memories):
            return

        current = memories[index].get("importance", "normal")
        choice = simpledialog.askstring(
            "Muiston tärkeys",
            "low / normal / important / permanent",
            initialvalue=current
        )

        if choice not in ("low", "normal", "important", "permanent"):
            return

        memories[index]["importance"] = choice
        self.refresh_memory()
        self.log("Muiston tärkeys muutettu: " + choice)

    def delete_memory(self):
        selection = self.memory.selection()
        if not selection or not self.running:
            return

        index = int(selection[0])
        memories = self.bearcore.memory_manager.get_all()
        if index >= len(memories):
            return

        if not messagebox.askyesno("Poista muisto", "Poistetaanko valittu muisto?"):
            return

        del self.bearcore.memory_manager.memories[index]
        self.refresh_memory()
        self.log("Muisto poistettu.")

    def refresh_tools(self):
        for item in self.tools.get_children():
            self.tools.delete(item)

        if not self.running:
            return

        try:
            for name in self.bearcore.tool_manager.get_available_tools():
                self.tools.insert("", "end", values=(name,))
        except Exception as exc:
            self.log("Työkalujen lukuvirhe: " + str(exc))

    def refresh_modules(self):
        for item in self.modules.get_children():
            self.modules.delete(item)

        folder = PROJECT_ROOT / "modules"
        if not folder.exists():
            return

        for child in sorted(folder.iterdir()):
            if not child.is_dir() or child.name == "__pycache__":
                continue

            status = (
                "Python-moduuli"
                if (child / "__init__.py").exists()
                else "Kansio"
            )

            self.modules.insert(
                "", "end",
                values=(
                    child.name,
                    str(child.relative_to(PROJECT_ROOT)),
                    status
                )
            )

    def create_module(self, requested=None):
        name = requested or simpledialog.askstring(
            "Luo moduuli", "Moduulin nimi:"
        )
        if not name:
            return

        name = name.strip().lower().replace(" ", "_")

        if not name.isidentifier():
            messagebox.showerror(
                "Virhe", "Moduulin nimi ei kelpaa Python-moduuliksi."
            )
            return

        folder = PROJECT_ROOT / "modules" / name

        if folder.exists():
            messagebox.showwarning(
                "Moduuli löytyy jo",
                "Tämä moduuli on jo olemassa."
            )
            return

        folder.mkdir(parents=True)
        (folder / "__init__.py").write_text(
            '"""BearCore module."""\n',
            encoding="utf-8"
        )

        class_name = "".join(
            part.capitalize() for part in name.split("_")
        )

        code = (
            '"""BearCore module."""\n\n\n'
            'class ' + class_name + ':\n'
            '    """Uuden BearCore-moduulin pohja."""\n\n'
            '    def __init__(self):\n'
            '        self.name = "' + name + '"\n\n'
            '    def status(self):\n'
            '        return {\n'
            '            "module": self.name,\n'
            '            "status": "ready",\n'
            '        }\n'
        )

        (folder / (name + ".py")).write_text(
            code, encoding="utf-8"
        )

        self.refresh_modules()
        self.log("Moduuli luotu: " + name)
        self.chat_add("Studio", "Moduulin '" + name + "' pohja luotu.")

    def open_modules(self):
        try:
            subprocess.Popen(
                ["explorer.exe", str(PROJECT_ROOT / "modules")]
            )
        except Exception as exc:
            self.error("Kansion avaus epäonnistui", exc)

    def run_tests(self):
        def worker():
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest"],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                output = (result.stdout + "\n" + result.stderr).strip()
                self.root.after(
                    0,
                    lambda: self.set_text(
                        self.test_output,
                        output or "Ei testitulostetta."
                    )
                )
                self.root.after(
                    0,
                    lambda: self.log(
                        "Testit valmis, exit code "
                        + str(result.returncode)
                    )
                )
            except Exception as exc:
                self.root.after(
                    0,
                    lambda: self.error("Testien ajo epäonnistui", exc)
                )

        threading.Thread(target=worker, daemon=True).start()

    def refresh_git(self):
        try:
            result = subprocess.run(
                ["git", "status", "--short", "--branch"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )
            self.set_text(
                self.git_output,
                result.stdout.strip() or "Git: ei muutoksia."
            )
        except Exception as exc:
            self.set_text(
                self.git_output,
                "Git-status epäonnistui:\n" + str(exc)
            )

    def git_checkpoint(self, message=None):
        message = message or simpledialog.askstring(
            "GitHub checkpoint",
            "Commit-viesti:",
            initialvalue="BearCore Studio checkpoint"
        )
        if not message:
            return

        def worker():
            try:
                outputs = []
                commands = [
                    ["git", "add", "."],
                    ["git", "commit", "-m", message],
                    ["git", "push"]
                ]

                for command in commands:
                    result = subprocess.run(
                        command,
                        cwd=PROJECT_ROOT,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    outputs.append(
                        "$ " + " ".join(command) + "\n"
                        + result.stdout + result.stderr
                    )
                    if result.returncode != 0 and command[1] != "commit":
                        raise RuntimeError(outputs[-1])

                final = "\n\n".join(outputs)
                self.root.after(
                    0,
                    lambda: self.set_text(self.git_output, final)
                )
                self.root.after(
                    0,
                    lambda: self.log("GitHub checkpoint valmis.")
                )
            except Exception as exc:
                self.root.after(
                    0,
                    lambda: self.error(
                        "GitHub checkpoint epäonnistui", exc
                    )
                )

        threading.Thread(target=worker, daemon=True).start()

    def chat_add(self, who, text):
        self.chat.config(state="normal")
        self.chat.insert("end", who + ": " + str(text) + "\n\n")
        self.chat.see("end")
        self.chat.config(state="disabled")

    def set_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def log(self, text):
        self.logs.append(text)
        if hasattr(self, "log_output"):
            self.set_text(self.log_output, "\n".join(self.logs))

    def error(self, title, exc):
        self.log(title + ": " + str(exc))
        messagebox.showerror(title, str(exc))


def launch():
    root = tk.Tk()
    BearCoreStudio(root)
    root.mainloop()


if __name__ == "__main__":
    launch()

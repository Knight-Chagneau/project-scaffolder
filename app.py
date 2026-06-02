#!/usr/bin/env python3
"""
Project Scaffolder - Création automatique de structure de projets clients
Portable : fonctionne sans installation ni droits admin (Windows & Linux)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Pillow optionnel — utilisé uniquement pour afficher le logo PNG
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ── Chemins portables ──────────────────────────────────────────────────────────

def get_app_dir():
    """Retourne le répertoire de l'exécutable (ou du script)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


CONFIG_PATH = get_app_dir() / "config.json"


# ── Gestion de la config ───────────────────────────────────────────────────────

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"templates": [{"id": "default", "name": "Nouveau Template", "items": []}]}


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ── Couleurs / style ───────────────────────────────────────────────────────────

BG        = "#1e1e2e"
BG2       = "#2a2a3e"
BG3       = "#313145"
ACCENT    = "#7c6af7"
ACCENT2   = "#a89df5"
SUCCESS   = "#4caf78"
DANGER    = "#e05c5c"
TEXT      = "#e0e0f0"
TEXT_DIM  = "#888aaa"
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_H1   = ("Segoe UI", 14, "bold")
FONT_H2   = ("Segoe UI", 11, "bold")
FONT_MONO = ("Courier New", 9)


# ── Widget helpers ─────────────────────────────────────────────────────────────

def styled_button(parent, text, command, color=ACCENT, fg=TEXT, **kw):
    btn = tk.Button(parent, text=text, command=command,
                    bg=color, fg=fg, activebackground=ACCENT2, activeforeground=TEXT,
                    relief="flat", bd=0, padx=12, pady=6,
                    font=FONT_MAIN, cursor="hand2", **kw)
    return btn


def styled_entry(parent, **kw):
    e = tk.Entry(parent, bg=BG3, fg=TEXT, insertbackground=TEXT,
                 relief="flat", bd=0, highlightthickness=1,
                 highlightcolor=ACCENT, highlightbackground=BG3,
                 font=FONT_MAIN, **kw)
    return e


def section_label(parent, text):
    return tk.Label(parent, text=text, bg=BG, fg=ACCENT2, font=FONT_H2, anchor="w")


# ── Fenêtre principale ─────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Scaffolder")
        self.configure(bg=BG)
        self.minsize(860, 580)
        self.resizable(True, True)

        # Centre la fenêtre
        self.update_idletasks()
        w, h = 960, 640
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.config_data   = load_config()
        self.current_tmpl  = tk.StringVar()
        self.dest_path     = tk.StringVar(value=str(Path.home()))
        self.project_name  = tk.StringVar()
        self.check_vars    = {}   # path -> BooleanVar

        self._build_ui()
        self._load_template_list()
        set_window_icon(self)


    # ── Construction de l'UI ───────────────────────────────────────────────────

    def _build_ui(self):
        # Barre du haut
        top = tk.Frame(self, bg=BG2, pady=10, padx=16)
        top.pack(fill="x")
        tk.Label(top, text="⬡  Project Scaffolder", bg=BG2, fg=TEXT,
                 font=FONT_H1).pack(side="left")
        tk.Label(top, text="Création de structure de project !!!!",
                 bg=BG2, fg=TEXT_DIM, font=FONT_MAIN).pack(side="left", padx=16)
        styled_button(top, "⚙  Configuration", self._open_config,
                      color=BG3).pack(side="right")
        styled_button(top, "ℹ  À propos", self._open_about,
                      color=BG3).pack(side="right", padx=(0, 6))

        # Corps principal
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Colonne gauche : paramètres + liste
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        self._build_params(left)
        self._build_checklist(left)

        # Colonne droite : actions
        right = tk.Frame(body, bg=BG, width=200)
        right.pack(side="right", fill="y", padx=(16, 0))
        right.pack_propagate(False)
        self._build_actions(right)


    def _build_params(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", pady=(0, 12))

        section_label(frame, "Paramètres du projet").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        # Nom du projet
        tk.Label(frame, text="Nom du projet :", bg=BG, fg=TEXT,
                 font=FONT_MAIN).grid(row=1, column=0, sticky="w", padx=(0, 8))
        e = styled_entry(frame, textvariable=self.project_name, width=30)
        e.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        # Template
        tk.Label(frame, text="Template :", bg=BG, fg=TEXT,
                 font=FONT_MAIN).grid(row=1, column=2, sticky="w", padx=(8, 8))
        self.tmpl_combo = ttk.Combobox(frame, textvariable=self.current_tmpl,
                                       state="readonly", width=22, font=FONT_MAIN)
        self.tmpl_combo.grid(row=1, column=3, sticky="ew")
        self.tmpl_combo.bind("<<ComboboxSelected>>", lambda _: self._refresh_checklist())

        # Destination
        tk.Label(frame, text="Destination :", bg=BG, fg=TEXT,
                 font=FONT_MAIN).grid(row=2, column=0, sticky="w", pady=(8, 0))
        e2 = styled_entry(frame, textvariable=self.dest_path, width=50)
        e2.grid(row=2, column=1, columnspan=3, sticky="ew", pady=(8, 0))
        styled_button(frame, "📂 Parcourir", self._browse_dest,
                      color=BG3).grid(row=2, column=4, padx=(8, 0), pady=(8, 0))

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        # Style ttk
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox", fieldbackground=BG3, background=BG3,
                        foreground=TEXT, arrowcolor=ACCENT2)


    def _build_checklist(self, parent):
        section_label(parent, "Éléments à créer").pack(anchor="w", pady=(0, 6))

        # Toolbar de sélection rapide
        tbar = tk.Frame(parent, bg=BG)
        tbar.pack(fill="x", pady=(0, 4))
        styled_button(tbar, "Tout sélectionner",  lambda: self._select_all(True),
                      color=BG3, fg=TEXT_DIM).pack(side="left", padx=(0, 4))
        styled_button(tbar, "Tout désélectionner", lambda: self._select_all(False),
                      color=BG3, fg=TEXT_DIM).pack(side="left")

        # Zone scrollable
        container = tk.Frame(parent, bg=BG3, bd=0, highlightthickness=1,
                             highlightbackground=BG3)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=BG3, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.check_frame = tk.Frame(canvas, bg=BG3)
        self.check_window = canvas.create_window((0, 0), window=self.check_frame,
                                                  anchor="nw")

        self.check_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self.check_window, width=e.width))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self.canvas = canvas


    def _build_actions(self, parent):
        tk.Label(parent, text="Actions", bg=BG, fg=ACCENT2,
                 font=FONT_H2).pack(anchor="w", pady=(0, 12))

        styled_button(parent, "✦  Créer la structure",
                      self._create_structure, color=ACCENT).pack(fill="x", pady=(0, 8))
        styled_button(parent, "⟳  Aperçu arborescence",
                      self._preview, color=BG3).pack(fill="x", pady=(0, 8))

        tk.Frame(parent, bg=BG3, height=1).pack(fill="x", pady=8)

        tk.Label(parent, text="Raccourcis", bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))
        styled_button(parent, "📋  Ouvrir destination",
                      self._open_dest, color=BG3, fg=TEXT_DIM).pack(fill="x", pady=(0, 4))

        # Zone de log
        tk.Frame(parent, bg=BG3, height=1).pack(fill="x", pady=8)
        tk.Label(parent, text="Journal", bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))

        log_frame = tk.Frame(parent, bg=BG3)
        log_frame.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_frame, bg=BG3, fg=TEXT_DIM, font=FONT_MONO,
                                state="disabled", relief="flat", bd=0,
                                wrap="word", height=10)
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)

    # ── Données ───────────────────────────────────────────────────────────────

    def _get_template(self, name=None):
        n = name or self.current_tmpl.get()
        for t in self.config_data["templates"]:
            if t["name"] == n:
                return t
        return None

    def _load_template_list(self):
        names = [t["name"] for t in self.config_data["templates"]]
        self.tmpl_combo["values"] = names
        if names:
            self.current_tmpl.set(names[0])
            self._refresh_checklist()


    def _refresh_checklist(self):
        for w in self.check_frame.winfo_children():
            w.destroy()
        self.check_vars.clear()

        tmpl = self._get_template()
        if not tmpl:
            return

        items = sorted(tmpl["items"], key=lambda x: (x["type"] != "folder", x["path"]))
        current_group = None

        for item in items:
            depth  = item["path"].count("/")
            is_sub = depth > 0
            parent_path = "/".join(item["path"].split("/")[:-1]) if is_sub else None

            # Séparateur de groupe
            group = item["path"].split("/")[0]
            if group != current_group and item["type"] == "folder" and depth == 0:
                current_group = group
                tk.Frame(self.check_frame, bg=BG3, height=1).pack(
                    fill="x", padx=8, pady=2)

            var = tk.BooleanVar(value=item.get("default", True))
            self.check_vars[item["path"]] = var

            row = tk.Frame(self.check_frame, bg=BG3)
            row.pack(fill="x", padx=4, pady=1)

            indent = depth * 20
            if indent:
                tk.Label(row, width=indent // 8, bg=BG3).pack(side="left")

            icon = "📁" if item["type"] == "folder" else "📄"
            cb = tk.Checkbutton(row, variable=var, bg=BG3, fg=TEXT,
                                activebackground=BG3, activeforeground=TEXT,
                                selectcolor=ACCENT, relief="flat",
                                font=FONT_MAIN, anchor="w",
                                text=f" {icon}  {item['path']}")
            cb.pack(side="left", fill="x", expand=True)


    def _select_all(self, value: bool):
        for var in self.check_vars.values():
            var.set(value)

    def _browse_dest(self):
        path = filedialog.askdirectory(initialdir=self.dest_path.get(),
                                       title="Choisir le dossier de destination")
        if path:
            self.dest_path.set(path)

    def _open_dest(self):
        path = self.dest_path.get()
        if os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')
        else:
            messagebox.showwarning("Introuvable", f"Le dossier n'existe pas :\n{path}")

    # ── Création ─────────────────────────────────────────────────────────────

    def _create_structure(self):
        name = self.project_name.get().strip()
        dest = self.dest_path.get().strip()

        if not name:
            messagebox.showwarning("Nom manquant", "Saisis un nom de projet.")
            return
        if not dest or not os.path.isdir(dest):
            messagebox.showwarning("Destination invalide",
                                   "Choisis un dossier de destination valide.")
            return

        selected = [p for p, v in self.check_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("Rien de sélectionné",
                                   "Sélectionne au moins un élément à créer.")
            return

        root = Path(dest) / name
        if root.exists():
            if not messagebox.askyesno("Dossier existant",
                f"Le dossier « {name} » existe déjà.\nContinuer quand même ?"):
                return

        tmpl  = self._get_template()
        items = {i["path"]: i for i in tmpl["items"]}
        created, skipped = [], []

        try:
            root.mkdir(parents=True, exist_ok=True)
            self._log(f"📁  {root}", "ok")

            for path_str in selected:
                item    = items[path_str]
                target  = root / path_str

                if item["type"] == "folder":
                    target.mkdir(parents=True, exist_ok=True)
                    created.append(f"📁 {path_str}")
                    self._log(f"  📁  {path_str}", "ok")
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if not target.exists():
                        content = item.get("content", "")
                        target.write_text(content, encoding="utf-8")
                        created.append(f"📄 {path_str}")
                        self._log(f"  📄  {path_str}", "ok")
                    else:
                        skipped.append(path_str)
                        self._log(f"  ⚠   {path_str} (existant, ignoré)", "warn")

            msg = f"Structure créée dans :\n{root}\n\n"
            msg += f"✓  {len(created)} élément(s) créé(s)"
            if skipped:
                msg += f"\n⚠  {len(skipped)} fichier(s) ignoré(s) (déjà présents)"
            messagebox.showinfo("Terminé", msg)

        except PermissionError as e:
            messagebox.showerror("Erreur de permission", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


    # ── Aperçu ────────────────────────────────────────────────────────────────

    def _preview(self):
        name = self.project_name.get().strip() or "<NomDuProjet>"
        selected = [p for p, v in self.check_vars.items() if v.get()]
        if not selected:
            messagebox.showinfo("Aperçu", "Aucun élément sélectionné.")
            return

        lines = [f"📁 {self.dest_path.get()}/", f"  └─ 📁 {name}/"]
        tmpl  = self._get_template()
        items = {i["path"]: i for i in tmpl["items"]}

        for p in sorted(selected):
            depth  = p.count("/")
            indent = "     " + "   " * depth + "└─ "
            icon   = "📁" if items[p]["type"] == "folder" else "📄"
            lines.append(f"{indent}{icon} {p.split('/')[-1]}")

        win = tk.Toplevel(self, bg=BG)
        win.title("Aperçu de l'arborescence")
        win.geometry("520x420")
        win.configure(bg=BG)

        tk.Label(win, text="Aperçu arborescence", bg=BG, fg=TEXT,
                 font=FONT_H2).pack(padx=16, pady=(12, 6), anchor="w")

        txt = tk.Text(win, bg=BG3, fg=TEXT, font=FONT_MONO, relief="flat",
                      bd=0, padx=10, pady=10, wrap="none")
        txt.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        txt.insert("1.0", "\n".join(lines))
        txt.configure(state="disabled")

    # ── Log ───────────────────────────────────────────────────────────────────

    def _log(self, msg, level="info"):
        colors = {"ok": SUCCESS, "warn": "#f5a623", "info": TEXT_DIM}
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


    # ── Fenêtre de configuration ──────────────────────────────────────────────

    def _open_config(self):
        ConfigWindow(self)

    # ── Fenêtre À propos ──────────────────────────────────────────────────────

    def _open_about(self):
        AboutWindow(self)


# ══════════════════════════════════════════════════════════════════════════════
# Fenêtre de configuration
# ══════════════════════════════════════════════════════════════════════════════

class ConfigWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.master_app  = master
        self.title("Configuration des templates")
        self.geometry("820x560")
        self.resizable(True, True)
        self.grab_set()

        self.config_data = master.config_data
        self.cur_tmpl    = tk.StringVar()
        self.sel_item    = None   # index dans la liste

        self._build_ui()
        self._load_templates()

    def _build_ui(self):
        top = tk.Frame(self, bg=BG2, pady=8, padx=14)
        top.pack(fill="x")
        tk.Label(top, text="⚙  Configuration des templates",
                 bg=BG2, fg=TEXT, font=FONT_H2).pack(side="left")

        panes = tk.Frame(self, bg=BG)
        panes.pack(fill="both", expand=True, padx=14, pady=10)

        # ── Panneau gauche : liste templates ──
        left = tk.Frame(panes, bg=BG, width=200)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(left, text="Templates", bg=BG, fg=ACCENT2,
                 font=FONT_BOLD).pack(anchor="w", pady=(0, 6))

        self.tmpl_list = tk.Listbox(left, bg=BG2, fg=TEXT, font=FONT_MAIN,
                                    selectbackground=ACCENT, selectforeground=TEXT,
                                    relief="flat", bd=0, activestyle="none",
                                    highlightthickness=0)
        self.tmpl_list.pack(fill="both", expand=True)
        self.tmpl_list.bind("<<ListboxSelect>>", lambda _: self._on_tmpl_select())

        btns = tk.Frame(left, bg=BG)
        btns.pack(fill="x", pady=(6, 0))
        styled_button(btns, "+ Ajouter", self._add_template,
                      color=ACCENT).pack(side="left", padx=(0, 4))
        styled_button(btns, "🗑 Suppr.", self._del_template,
                      color=DANGER).pack(side="left")

        # ── Panneau droite : éléments du template ──
        right = tk.Frame(panes, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Nom du template
        name_row = tk.Frame(right, bg=BG)
        name_row.pack(fill="x", pady=(0, 10))
        tk.Label(name_row, text="Nom du template :", bg=BG, fg=TEXT,
                 font=FONT_MAIN).pack(side="left")
        self.tmpl_name_var = tk.StringVar()
        e = styled_entry(name_row, textvariable=self.tmpl_name_var, width=28)
        e.pack(side="left", padx=8)
        styled_button(name_row, "Renommer", self._rename_template,
                      color=BG3).pack(side="left")

        tk.Label(right, text="Éléments", bg=BG, fg=ACCENT2,
                 font=FONT_BOLD).pack(anchor="w", pady=(0, 4))

        # Liste des éléments
        list_frame = tk.Frame(right, bg=BG3)
        list_frame.pack(fill="both", expand=True)

        self.items_list = tk.Listbox(list_frame, bg=BG3, fg=TEXT, font=FONT_MONO,
                                     selectbackground=ACCENT, selectforeground=TEXT,
                                     relief="flat", bd=0, activestyle="none",
                                     highlightthickness=0)
        sb = ttk.Scrollbar(list_frame, orient="vertical",
                           command=self.items_list.yview)
        self.items_list.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.items_list.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        self.items_list.bind("<<ListboxSelect>>", lambda _: self._on_item_select())


        # Formulaire d'édition d'élément
        form = tk.LabelFrame(right, text=" Éditer l'élément ", bg=BG, fg=ACCENT2,
                             font=FONT_MAIN, bd=1, relief="groove",
                             highlightbackground=BG3)
        form.pack(fill="x", pady=(8, 0))

        # Ligne 1 : type + path
        r1 = tk.Frame(form, bg=BG)
        r1.pack(fill="x", padx=8, pady=(6, 4))
        tk.Label(r1, text="Type :", bg=BG, fg=TEXT, font=FONT_MAIN).pack(side="left")
        self.item_type = tk.StringVar(value="folder")
        for val, lbl in [("folder", "📁 Dossier"), ("file", "📄 Fichier")]:
            tk.Radiobutton(r1, text=lbl, variable=self.item_type, value=val,
                           bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                           font=FONT_MAIN).pack(side="left", padx=(8, 0))

        r2 = tk.Frame(form, bg=BG)
        r2.pack(fill="x", padx=8, pady=4)
        tk.Label(r2, text="Chemin :", bg=BG, fg=TEXT, font=FONT_MAIN).pack(side="left")
        self.item_path = tk.StringVar()
        styled_entry(r2, textvariable=self.item_path, width=40).pack(
            side="left", padx=8, fill="x", expand=True)

        # Par défaut
        r3 = tk.Frame(form, bg=BG)
        r3.pack(fill="x", padx=8, pady=4)
        self.item_default = tk.BooleanVar(value=True)
        tk.Checkbutton(r3, text="Coché par défaut", variable=self.item_default,
                       bg=BG, fg=TEXT, selectcolor=ACCENT, activebackground=BG,
                       font=FONT_MAIN).pack(side="left")

        # Contenu fichier
        r4 = tk.Frame(form, bg=BG)
        r4.pack(fill="x", padx=8, pady=(4, 6))
        tk.Label(r4, text="Contenu (fichier) :", bg=BG, fg=TEXT_DIM,
                 font=FONT_MAIN).pack(anchor="w")
        self.item_content = tk.Text(r4, bg=BG3, fg=TEXT, font=FONT_MONO,
                                    relief="flat", bd=0, height=4, wrap="word",
                                    insertbackground=TEXT)
        self.item_content.pack(fill="x", pady=(4, 0))

        # Boutons
        brow = tk.Frame(form, bg=BG)
        brow.pack(fill="x", padx=8, pady=(0, 8))
        styled_button(brow, "💾  Enregistrer", self._save_item,
                      color=ACCENT).pack(side="left", padx=(0, 6))
        styled_button(brow, "+  Nouvel élément", self._new_item,
                      color=BG3).pack(side="left", padx=(0, 6))
        styled_button(brow, "🗑  Supprimer", self._del_item,
                      color=DANGER).pack(side="left")

        # Bas : bouton fermer
        bot = tk.Frame(self, bg=BG)
        bot.pack(fill="x", padx=14, pady=(0, 10))
        styled_button(bot, "✓  Fermer & sauvegarder", self._close_save,
                      color=SUCCESS).pack(side="right")


    # ── Gestion templates ─────────────────────────────────────────────────────

    def _load_templates(self):
        self.tmpl_list.delete(0, "end")
        for t in self.config_data["templates"]:
            self.tmpl_list.insert("end", t["name"])
        if self.config_data["templates"]:
            self.tmpl_list.select_set(0)
            self._on_tmpl_select()

    def _on_tmpl_select(self):
        sel = self.tmpl_list.curselection()
        if not sel:
            return
        tmpl = self.config_data["templates"][sel[0]]
        self.tmpl_name_var.set(tmpl["name"])
        self._load_items(tmpl)

    def _add_template(self):
        name = simpledialog.askstring("Nouveau template", "Nom du template :",
                                      parent=self)
        if not name:
            return
        new = {"id": name.lower().replace(" ", "_"),
               "name": name, "items": []}
        self.config_data["templates"].append(new)
        self._load_templates()
        self.tmpl_list.select_set("end")
        self._on_tmpl_select()

    def _del_template(self):
        sel = self.tmpl_list.curselection()
        if not sel:
            return
        if len(self.config_data["templates"]) == 1:
            messagebox.showwarning("Impossible", "Il faut garder au moins un template.")
            return
        if messagebox.askyesno("Confirmer", "Supprimer ce template ?"):
            del self.config_data["templates"][sel[0]]
            self._load_templates()

    def _rename_template(self):
        sel = self.tmpl_list.curselection()
        if not sel:
            return
        new_name = self.tmpl_name_var.get().strip()
        if not new_name:
            return
        self.config_data["templates"][sel[0]]["name"] = new_name
        self._load_templates()

    # ── Gestion éléments ──────────────────────────────────────────────────────

    def _get_cur_tmpl(self):
        sel = self.tmpl_list.curselection()
        if not sel:
            return None
        return self.config_data["templates"][sel[0]]

    def _load_items(self, tmpl):
        self.items_list.delete(0, "end")
        for item in tmpl["items"]:
            icon = "📁" if item["type"] == "folder" else "📄"
            flag = "✓" if item.get("default") else " "
            self.items_list.insert("end", f"[{flag}] {icon}  {item['path']}")
        self._clear_form()

    def _on_item_select(self):
        sel = self.items_list.curselection()
        tmpl = self._get_cur_tmpl()
        if not sel or not tmpl:
            return
        self.sel_item = sel[0]
        item = tmpl["items"][sel[0]]
        self.item_type.set(item["type"])
        self.item_path.set(item["path"])
        self.item_default.set(item.get("default", True))
        self.item_content.delete("1.0", "end")
        self.item_content.insert("1.0", item.get("content", ""))

    def _clear_form(self):
        self.sel_item = None
        self.item_type.set("folder")
        self.item_path.set("")
        self.item_default.set(True)
        self.item_content.delete("1.0", "end")

    def _new_item(self):
        self.items_list.selection_clear(0, "end")
        self._clear_form()

    def _save_item(self):
        tmpl = self._get_cur_tmpl()
        if not tmpl:
            messagebox.showwarning("Aucun template", "Sélectionne un template d'abord.")
            return
        path = self.item_path.get().strip().replace("\\", "/")
        if not path:
            messagebox.showwarning("Chemin vide", "Saisis un chemin.")
            return

        item = {
            "type":    self.item_type.get(),
            "path":    path,
            "default": self.item_default.get(),
        }
        if item["type"] == "file":
            item["content"] = self.item_content.get("1.0", "end-1c")

        if self.sel_item is not None:
            tmpl["items"][self.sel_item] = item
        else:
            # Vérifier doublon
            if any(i["path"] == path for i in tmpl["items"]):
                messagebox.showwarning("Doublon", f"« {path} » existe déjà.")
                return
            tmpl["items"].append(item)

        self._load_items(tmpl)

    def _del_item(self):
        tmpl = self._get_cur_tmpl()
        if not tmpl or self.sel_item is None:
            return
        if messagebox.askyesno("Confirmer", "Supprimer cet élément ?"):
            del tmpl["items"][self.sel_item]
            self._load_items(tmpl)

    # ── Fermer ────────────────────────────────────────────────────────────────

    def _close_save(self):
        save_config(self.config_data)
        self.master_app._load_template_list()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# Fenêtre À propos
# ══════════════════════════════════════════════════════════════════════════════

APP_NAME        = "Project Scaffolder"
APP_VERSION     = "1.0.0"
APP_AUTHOR      = "Thomas 'Knight' Chagneau"
APP_DESCRIPTION = (
    "Project Scaffolder est un outil portable de création automatique de "
    "structures de projets clients.\n\n"
    "Il permet de définir des templates personnalisés (dossiers et fichiers "
    "avec contenus pré-remplis), puis de générer en un clic l'arborescence "
    "complète d'un nouveau projet, sans jamais avoir à tout recréer manuellement.\n\n"
    "Conçu pour fonctionner sans installation et sans droit administrateur, "
    "aussi bien sous Windows que sous Linux."
)
APP_LICENSE     = "MIT License — Logiciel libre et open source"
APP_YEAR        = "2026"


def _draw_logo(canvas, cx, cy, size=38):
    """Dessine un logo vectoriel simple dans un Canvas tkinter."""
    s = size
    # Hexagone de fond
    pts = []
    import math
    for i in range(6):
        angle = math.radians(60 * i - 30)
        pts += [cx + s * math.cos(angle), cy + s * math.sin(angle)]
    canvas.create_polygon(pts, fill=ACCENT, outline=ACCENT2, width=2)
    # Lettre P stylisée
    canvas.create_text(cx, cy, text="PS", fill=TEXT,
                       font=("Segoe UI", int(s * 0.55), "bold"))


# Chemin du logo PNG
LOGO_PATH = get_app_dir() / "logo.png"
LOGO_SIZE  = (84, 84)   # taille d'affichage dans la fenêtre À propos
ICON_SIZE  = (32, 32)   # taille pour l'icône de fenêtre


def load_logo_image(size=LOGO_SIZE):
    """
    Charge logo.png et retourne un ImageTk.PhotoImage redimensionné.
    Retourne None si Pillow n'est pas disponible ou si le fichier est absent.
    """
    if not PIL_AVAILABLE or not LOGO_PATH.exists():
        return None
    try:
        img = Image.open(LOGO_PATH).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def set_window_icon(window):
    """
    Applique logo.png comme icône de la fenêtre (barre de titre + taskbar).
    Silencieux si le fichier est absent ou Pillow manquant.
    """
    photo = load_logo_image(size=ICON_SIZE)
    if photo:
        window._icon_ref = photo   # évite le garbage collection
        try:
            window.iconphoto(True, photo)
        except Exception:
            pass


class AboutWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.title("À propos")
        self.resizable(False, False)
        self.grab_set()

        # Centre par rapport à la fenêtre parente
        self.update_idletasks()
        w, h = 480, 620
        px = master.winfo_x() + (master.winfo_width()  - w) // 2
        py = master.winfo_y() + (master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{px}+{py}")

        self._build_ui()

    def _build_ui(self):
        # ── En-tête avec logo ──
        header = tk.Frame(self, bg=BG2, pady=20)
        header.pack(fill="x")

        # Logo : PNG si disponible, sinon vectoriel de secours
        logo_photo = load_logo_image(size=LOGO_SIZE)
        if logo_photo:
            logo_lbl = tk.Label(header, image=logo_photo, bg=BG2)
            logo_lbl.image = logo_photo   # garde la référence
            logo_lbl.pack()
        else:
            # Fallback vectoriel
            import math
            logo_canvas = tk.Canvas(header, width=84, height=84,
                                    bg=BG2, highlightthickness=0)
            logo_canvas.pack()
            cx, cy, s = 42, 42, 38
            pts = []
            for i in range(6):
                angle = math.radians(60 * i - 30)
                pts += [cx + s * math.cos(angle), cy + s * math.sin(angle)]
            logo_canvas.create_polygon(pts, fill=ACCENT, outline=ACCENT2, width=2)
            logo_canvas.create_text(cx, cy, text="PS", fill=TEXT,
                                    font=("Segoe UI", int(s * 0.55), "bold"))

        tk.Label(header, text=APP_NAME, bg=BG2, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(pady=(8, 2))
        tk.Label(header, text=f"version {APP_VERSION}", bg=BG2, fg=TEXT_DIM,
                 font=("Segoe UI", 9)).pack()

        # ── Corps ──
        body = tk.Frame(self, bg=BG, padx=24)
        body.pack(fill="both", expand=True, pady=14)

        # Description
        tk.Label(body, text="Description", bg=BG, fg=ACCENT2,
                 font=FONT_BOLD, anchor="w").pack(fill="x", pady=(0, 4))

        desc_frame = tk.Frame(body, bg=BG3)
        desc_frame.pack(fill="both", expand=True)
        desc = tk.Text(desc_frame, bg=BG3, fg=TEXT, font=("Segoe UI", 9),
                       relief="flat", bd=0, wrap="word", height=6,
                       padx=10, pady=8, state="normal",
                       cursor="arrow", highlightthickness=0)
        desc.insert("1.0", APP_DESCRIPTION)
        desc.configure(state="disabled")
        desc.pack(fill="both", expand=True)

        # Séparateur
        tk.Frame(body, bg=BG3, height=1).pack(fill="x", pady=12)

        # Grille infos
        info_frame = tk.Frame(body, bg=BG)
        info_frame.pack(fill="x")

        def info_row(row, label, value, value_color=TEXT):
            tk.Label(info_frame, text=label, bg=BG, fg=TEXT_DIM,
                     font=("Segoe UI", 9), anchor="w", width=12).grid(
                         row=row, column=0, sticky="w", pady=2)
            tk.Label(info_frame, text=value, bg=BG, fg=value_color,
                     font=("Segoe UI", 9, "bold"), anchor="w").grid(
                         row=row, column=1, sticky="w", pady=2, padx=(8, 0))

        author_display = APP_AUTHOR if APP_AUTHOR.strip() else "— (non renseigné)"
        info_row(0, "Auteur :",   author_display, ACCENT2)
        info_row(1, "Licence :",  APP_LICENSE,    SUCCESS)
        info_row(2, "Copyright :", f"© {APP_YEAR} {APP_AUTHOR or 'Auteur'} — Open Source", TEXT_DIM)

        # ── Pied ──
        foot = tk.Frame(self, bg=BG2, pady=10)
        foot.pack(fill="x", side="bottom")
        styled_button(foot, "Fermer", self.destroy, color=BG3).pack()


# ── Point d'entrée ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()

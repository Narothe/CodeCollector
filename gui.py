"""Main window: choose a project folder and generate the export."""

import customtkinter as ctk
from tkinter import filedialog, messagebox

from config import FONT
from exporter import analyze_project, collect_files
from result_window import ResultWindow

MUTED_TEXT = ("gray35", "gray70")


def run():
    ctk.set_appearance_mode("System")  # follow the OS light/dark setting
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Project Code Exporter")
    app.geometry("640x300")
    app.resizable(False, False)

    path_var = ctk.StringVar()  # selected project folder
    status_var = ctk.StringVar(value="Ready")

    # ---- Actions ----

    def browse():
        """Lets the user pick the project folder."""
        folder = filedialog.askdirectory()

        if folder:
            path_var.set(folder)

    def confirm_large_project(files_count, directories):
        """Asks whether to continue with a very large project."""
        return messagebox.askyesno(
            "Large Project",
            f"The selected project contains more than {files_count:,} files\n"
            f"in at least {directories:,} directories.\n\n"
            "Exporting such a large directory may take a long time.\n\n"
            "Do you want to continue?"
        )

    def generate():
        """Collects the project files and opens the result window."""
        folder = path_var.get().strip()

        # Validate the input before touching the file system.
        if not folder:
            messagebox.showwarning("Warning", "Select a project folder.")
            return

        files_count, directories, limit_exceeded = analyze_project(folder)

        if limit_exceeded and not confirm_large_project(files_count, directories):
            return

        # Show progress while collecting.
        status_var.set("Generating...")
        generate_btn.configure(state="disabled")
        progress.pack(fill="x", padx=30, pady=(0, 6))
        progress.start()
        app.update_idletasks()

        try:
            files = list(collect_files(folder))
        except Exception as error:
            status_var.set("Export failed.")
            messagebox.showerror("Error", str(error))
            return
        finally:
            # Always restore the UI, whether collecting succeeded or not.
            progress.stop()
            progress.pack_forget()
            generate_btn.configure(state="normal")

        status_var.set(f"Done ✓ {len(files):,} files collected")
        ResultWindow(app, folder, files, status_var)

    # ---- Layout ----

    card = ctk.CTkFrame(app, corner_radius=14)
    card.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        card, text="Project Code Exporter", font=(FONT, 24, "bold")
    ).pack(pady=(18, 0))

    ctk.CTkLabel(
        card,
        text="Collect a project's source code into a single text file",
        font=(FONT, 13),
        text_color=MUTED_TEXT,
    ).pack(pady=(0, 14))

    # Folder row: entry + Browse button.
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=30)

    ctk.CTkEntry(
        row,
        textvariable=path_var,
        placeholder_text="Project folder...",
        height=38,
        corner_radius=10,
    ).pack(side="left", fill="x", expand=True, padx=(0, 10))

    ctk.CTkButton(
        row, text="Browse", width=100, height=38, corner_radius=10, command=browse
    ).pack(side="right")

    generate_btn = ctk.CTkButton(
        card,
        text="Generate",
        width=220,
        height=42,
        corner_radius=10,
        font=(FONT, 15, "bold"),
        command=generate,
    )
    generate_btn.pack(pady=18)

    # Only packed while generating (see generate()).
    progress = ctk.CTkProgressBar(card, mode="indeterminate")

    ctk.CTkLabel(
        card, textvariable=status_var, font=(FONT, 12), text_color=MUTED_TEXT
    ).pack(pady=(0, 10))

    app.mainloop()

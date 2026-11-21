"""The window shown after export: preview, save location, Save / Copy all / Close."""

from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from config import CODE_FONT, FONT
from exporter import default_output_path, files_to_text, save_text
from highlight import fill_preview

MUTED_TEXT = ("gray35", "gray70")
SUCCESS_TEXT = ("#1a7f37", "#4ac26b")


class ResultWindow(ctk.CTkToplevel):
    """Shows the collected code and lets the user save it or copy it."""

    def __init__(self, app, folder, files, status_var):
        super().__init__(app)

        self.app = app
        self.status_var = status_var
        self.text = files_to_text(files)  # full text used by Save and Copy
        self.files = files

        self.path_var = ctk.StringVar(value=str(default_output_path(folder)))
        self.result_var = ctk.StringVar(value="")

        self.title("Export ready")
        self.geometry("820x640")
        self.minsize(600, 460)
        self.transient(app)  # keep above the main window
        self.after(100, self.focus)

        self._build_header()
        self._build_preview()
        self._build_save_row()
        self._build_buttons()

    # ---- UI construction ----

    def _build_header(self):
        ctk.CTkLabel(
            self, text="Export ready", font=(FONT, 20, "bold"), anchor="w"
        ).pack(fill="x", padx=20, pady=(18, 0))

        ctk.CTkLabel(
            self,
            text=(
                f"{len(self.files):,} files collected ({len(self.text):,} characters). "
                "Save it to a file or copy everything."
            ),
            font=(FONT, 13),
            text_color=MUTED_TEXT,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(2, 10))

    def _build_preview(self):
        box = ctk.CTkTextbox(
            self, font=(CODE_FONT, 12), corner_radius=10, wrap="none"
        )
        box.pack(fill="both", expand=True, padx=20)

        fill_preview(box, self.files)
        box.configure(state="disabled")  # read-only (selecting and Ctrl+C still work)

    def _build_save_row(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(12, 0))

        ctk.CTkLabel(row, text="Save to:", font=(FONT, 13)).pack(
            side="left", padx=(0, 8)
        )

        ctk.CTkButton(
            row, text="Change...", width=90, height=32, command=self.change_location
        ).pack(side="right", padx=(8, 0))

        ctk.CTkEntry(
            row, textvariable=self.path_var, height=32, corner_radius=8
        ).pack(side="left", fill="x", expand=True)

        # Confirmation line ("Saved: ..." / "Copied ...") shown under the row.
        ctk.CTkLabel(
            self,
            textvariable=self.result_var,
            font=(FONT, 12),
            anchor="w",
            text_color=SUCCESS_TEXT,
        ).pack(fill="x", padx=20, pady=(8, 0))

    def _build_buttons(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(8, 18))

        ctk.CTkButton(
            row, text="Save file", width=130, height=36, command=self.save
        ).pack(side="left")

        ctk.CTkButton(
            row, text="Copy all", width=130, height=36, command=self.copy_all
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            row,
            text="Close",
            width=100,
            height=36,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self.destroy,
        ).pack(side="right")

    # ---- Actions ----

    def change_location(self):
        """Lets the user pick the output file with the system 'Save as' dialog."""
        current = Path(self.path_var.get())

        chosen = filedialog.asksaveasfilename(
            parent=self,
            title="Choose where to save",
            initialdir=str(current.parent),
            initialfile=current.name,
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
        )

        if chosen:
            self.path_var.set(str(Path(chosen)))

    def save(self):
        """Writes the full text to the path currently shown in the entry."""
        target = self.path_var.get().strip()

        if not target:
            messagebox.showwarning("Warning", "Choose where to save.", parent=self)
            return

        try:
            output = save_text(target, self.text)
        except OSError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return

        self.result_var.set(f"Saved: {output}")
        self.status_var.set(f"Saved ✓ ({output.name})")

    def copy_all(self):
        """Copies the full text (without colors) to the clipboard."""
        self.app.clipboard_clear()
        self.app.clipboard_append(self.text)
        self.app.update()  # keeps the clipboard content alive after the window closes

        self.result_var.set("Copied everything to the clipboard ✓")

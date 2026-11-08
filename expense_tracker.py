"""
Expense Tracker - a minimal Tkinter front-end application.

Real-world problem: people lose track of where their money goes.
This app lets the user add expenses, see them in a table, delete them,
and view the running total plus a per-category summary.

Data is saved automatically to expenses.json next to this file.
Run:  python expense_tracker.py
"""

import json
import os
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.json")
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Education", "Other"]

# Minimal colour palette
BG = "#f5f6f8"
CARD = "#ffffff"
ACCENT = "#2f6fed"
TEXT = "#222222"
MUTED = "#6b7280"


class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("720x560")
        self.minsize(640, 500)
        self.configure(bg=BG)

        self.expenses = self.load_data()

        self.setup_style()
        self.build_header()
        self.build_form()
        self.build_table()
        self.build_summary()
        self.refresh()

    # ---------- data ----------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                messagebox.showwarning("Data", "Could not read saved data. Starting fresh.")
        return []

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, indent=2)
        except OSError as err:
            messagebox.showerror("Save error", f"Could not save data:\n{err}")

    # ---------- styling ----------
    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("TEntry", padding=5)
        style.configure("TCombobox", padding=5)
        style.configure("Accent.TButton", background=ACCENT, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=(14, 6), borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#1f56c4")])
        style.configure("Plain.TButton", font=("Segoe UI", 10), padding=(14, 6))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10),
                        background=CARD, fieldbackground=CARD, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background="#eceef2", foreground=TEXT)
        style.map("Treeview", background=[("selected", "#dbe6fd")],
                  foreground=[("selected", TEXT)])

    # ---------- layout ----------
    def build_header(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=20, pady=(18, 6))
        tk.Label(header, text="Expense Tracker", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        self.total_label = tk.Label(header, text="", bg=BG, fg=ACCENT,
                                    font=("Segoe UI", 16, "bold"))
        self.total_label.pack(side="right")

    def build_form(self):
        card = ttk.Frame(self, style="Card.TFrame", padding=14)
        card.pack(fill="x", padx=20, pady=6)

        ttk.Label(card, text="Description").grid(row=0, column=0, sticky="w")
        ttk.Label(card, text="Amount (₹)").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(card, text="Category").grid(row=0, column=2, sticky="w", padx=(10, 0))

        self.desc_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.cat_var = tk.StringVar(value=CATEGORIES[0])

        desc_entry = ttk.Entry(card, textvariable=self.desc_var, width=26)
        desc_entry.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Entry(card, textvariable=self.amount_var, width=12).grid(
            row=1, column=1, padx=(10, 0), pady=(2, 0))
        ttk.Combobox(card, textvariable=self.cat_var, values=CATEGORIES,
                     state="readonly", width=14).grid(row=1, column=2, padx=(10, 0), pady=(2, 0))
        ttk.Button(card, text="Add", style="Accent.TButton",
                   command=self.add_expense).grid(row=1, column=3, padx=(14, 0), pady=(2, 0))

        card.columnconfigure(0, weight=1)
        desc_entry.focus()
        self.bind("<Return>", lambda e: self.add_expense())

    def build_table(self):
        card = ttk.Frame(self, style="Card.TFrame", padding=10)
        card.pack(fill="both", expand=True, padx=20, pady=6)

        columns = ("date", "description", "category", "amount")
        self.tree = ttk.Treeview(card, columns=columns, show="headings", height=8)
        for col, text, width, anchor in [
            ("date", "Date", 100, "w"),
            ("description", "Description", 260, "w"),
            ("category", "Category", 110, "w"),
            ("amount", "Amount (₹)", 100, "e"),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)

        scroll = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        actions = tk.Frame(self, bg=BG)
        actions.pack(fill="x", padx=20)
        ttk.Button(actions, text="Delete selected", style="Plain.TButton",
                   command=self.delete_selected).pack(side="left")
        ttk.Button(actions, text="Clear all", style="Plain.TButton",
                   command=self.clear_all).pack(side="left", padx=8)

    def build_summary(self):
        self.summary_label = tk.Label(self, text="", bg=BG, fg=MUTED,
                                      font=("Segoe UI", 10), justify="left", anchor="w")
        self.summary_label.pack(fill="x", padx=20, pady=(8, 16))

    # ---------- actions ----------
    def add_expense(self):
        desc = self.desc_var.get().strip()
        amount_text = self.amount_var.get().strip()

        if not desc:
            messagebox.showwarning("Missing info", "Please enter a description.")
            return
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid amount", "Enter a positive number for the amount.")
            return

        self.expenses.append({
            "date": date.today().isoformat(),
            "description": desc,
            "category": self.cat_var.get(),
            "amount": round(amount, 2),
        })
        self.save_data()
        self.desc_var.set("")
        self.amount_var.set("")
        self.refresh()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Select a row first.")
            return
        # Delete from the end so earlier indexes stay valid
        for idx in sorted((int(i) for i in selected), reverse=True):
            del self.expenses[idx]
        self.save_data()
        self.refresh()

    def clear_all(self):
        if self.expenses and messagebox.askyesno("Clear all", "Delete every expense?"):
            self.expenses.clear()
            self.save_data()
            self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, e in enumerate(self.expenses):
            self.tree.insert("", "end", iid=str(i),
                             values=(e["date"], e["description"], e["category"],
                                     f"{e['amount']:.2f}"))

        total = sum(e["amount"] for e in self.expenses)
        self.total_label.config(text=f"Total: ₹{total:,.2f}")

        by_cat = {}
        for e in self.expenses:
            by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]
        if by_cat:
            parts = [f"{c}: ₹{v:,.2f}" for c, v in sorted(by_cat.items(), key=lambda x: -x[1])]
            self.summary_label.config(text="By category  |  " + "   ".join(parts))
        else:
            self.summary_label.config(text="No expenses yet. Add your first one above.")


if __name__ == "__main__":
    ExpenseTracker().mainloop()
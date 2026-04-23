import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import csv
from datetime import datetime
from collections import defaultdict
import random

DATA_FILE = "transactions.json"

CATEGORIES = {
    "income": ["Salary", "Freelance", "Investment", "Gift", "Other Income"],
    "expense": ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]
}

PALETTE = {
    "bg":        "#0F1117",
    "card":      "#1A1D27",
    "border":    "#2A2D3E",
    "accent":    "#6C63FF",
    "accent2":   "#FF6584",
    "green":     "#43D9AD",
    "yellow":    "#FFD166",
    "text":      "#E8E8F0",
    "subtext":   "#8888AA",
    "entry_bg":  "#22253A",
}

# ── helpers ──────────────────────────────────────────────────────────────────

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(transactions):
    with open(DATA_FILE, "w") as f:
        json.dump(transactions, f, indent=2)

def fmt_money(amount):
    return f"₹{amount:,.2f}"

# ── main app ─────────────────────────────────────────────────────────────────

class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Budget Tracker")
        self.geometry("1100x720")
        self.minsize(900, 620)
        self.configure(bg=PALETTE["bg"])
        self.resizable(True, True)

        self.transactions = load_data()
        self.filter_type = tk.StringVar(value="All")
        self.filter_category = tk.StringVar(value="All")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh_table())

        self._apply_styles()
        self._build_ui()
        self.refresh_all()

    # ── styles ────────────────────────────────────────────────────────────

    def _apply_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure("TFrame", background=PALETTE["bg"])
        s.configure("Card.TFrame", background=PALETTE["card"])

        s.configure("Treeview",
                    background=PALETTE["card"],
                    foreground=PALETTE["text"],
                    fieldbackground=PALETTE["card"],
                    rowheight=34,
                    borderwidth=0,
                    font=("Courier New", 11))
        s.configure("Treeview.Heading",
                    background=PALETTE["border"],
                    foreground=PALETTE["subtext"],
                    font=("Courier New", 10, "bold"),
                    relief="flat",
                    borderwidth=0)
        s.map("Treeview",
              background=[("selected", PALETTE["accent"])],
              foreground=[("selected", "#ffffff")])

        s.configure("Accent.TButton",
                    background=PALETTE["accent"],
                    foreground="#ffffff",
                    font=("Courier New", 11, "bold"),
                    borderwidth=0,
                    relief="flat",
                    padding=(16, 8))
        s.map("Accent.TButton",
              background=[("active", "#8580ff")])

        s.configure("Danger.TButton",
                    background=PALETTE["accent2"],
                    foreground="#ffffff",
                    font=("Courier New", 11, "bold"),
                    borderwidth=0,
                    relief="flat",
                    padding=(16, 8))
        s.map("Danger.TButton",
              background=[("active", "#ff8fa3")])

        s.configure("Flat.TButton",
                    background=PALETTE["border"],
                    foreground=PALETTE["text"],
                    font=("Courier New", 10),
                    borderwidth=0,
                    relief="flat",
                    padding=(10, 6))
        s.map("Flat.TButton",
              background=[("active", PALETTE["entry_bg"])])

        s.configure("TCombobox",
                    fieldbackground=PALETTE["entry_bg"],
                    background=PALETTE["border"],
                    foreground=PALETTE["text"],
                    selectbackground=PALETTE["accent"],
                    selectforeground="#fff",
                    arrowcolor=PALETTE["subtext"],
                    borderwidth=0)

        s.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])
        s.configure("Card.TLabel", background=PALETTE["card"], foreground=PALETTE["text"])
        s.configure("Sub.TLabel", background=PALETTE["card"], foreground=PALETTE["subtext"],
                    font=("Courier New", 9))
        s.configure("Big.TLabel", background=PALETTE["card"], foreground=PALETTE["text"],
                    font=("Courier New", 20, "bold"))
        s.configure("Title.TLabel", background=PALETTE["bg"], foreground=PALETTE["text"],
                    font=("Courier New", 18, "bold"))

    # ── UI build ─────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── header ──
        hdr = tk.Frame(self, bg=PALETTE["bg"], pady=10)
        hdr.pack(fill="x", padx=24)

        tk.Label(hdr, text="◈ BUDGET TRACKER", bg=PALETTE["bg"],
                 fg=PALETTE["accent"], font=("Courier New", 20, "bold")).pack(side="left")

        tk.Label(hdr, text=datetime.now().strftime("%B %Y"),
                 bg=PALETTE["bg"], fg=PALETTE["subtext"],
                 font=("Courier New", 11)).pack(side="left", padx=16)

        ttk.Button(hdr, text="⬆ Export CSV", style="Flat.TButton",
                   command=self.export_csv).pack(side="right", padx=4)
        ttk.Button(hdr, text="⬇ Import CSV", style="Flat.TButton",
                   command=self.import_csv).pack(side="right", padx=4)

        # ── summary cards ──
        cards_frame = tk.Frame(self, bg=PALETTE["bg"])
        cards_frame.pack(fill="x", padx=24, pady=(0, 14))

        self.card_balance  = self._summary_card(cards_frame, "NET BALANCE", "₹0.00",  PALETTE["accent"])
        self.card_income   = self._summary_card(cards_frame, "INCOME",      "₹0.00",  PALETTE["green"])
        self.card_expense  = self._summary_card(cards_frame, "EXPENSES",    "₹0.00",  PALETTE["accent2"])
        self.card_count    = self._summary_card(cards_frame, "TRANSACTIONS","0",       PALETTE["yellow"])

        # ── body ──
        body = tk.Frame(self, bg=PALETTE["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_right_panel(body)

    def _summary_card(self, parent, label, value, color):
        card = tk.Frame(parent, bg=PALETTE["card"], padx=20, pady=14)
        card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # color bar
        tk.Frame(card, bg=color, width=3).pack(side="left", fill="y", padx=(0, 12))

        inner = tk.Frame(card, bg=PALETTE["card"])
        inner.pack(side="left")

        tk.Label(inner, text=label, bg=PALETTE["card"], fg=PALETTE["subtext"],
                 font=("Courier New", 8, "bold")).pack(anchor="w")
        val_lbl = tk.Label(inner, text=value, bg=PALETTE["card"],
                           fg=color, font=("Courier New", 18, "bold"))
        val_lbl.pack(anchor="w")
        return val_lbl

    def _build_left_panel(self, parent):
        left = tk.Frame(parent, bg=PALETTE["card"], padx=18, pady=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left, text="ADD TRANSACTION", bg=PALETTE["card"],
                 fg=PALETTE["accent"], font=("Courier New", 11, "bold")).pack(anchor="w", pady=(0, 14))

        def lbl(text):
            tk.Label(left, text=text, bg=PALETTE["card"], fg=PALETTE["subtext"],
                     font=("Courier New", 9)).pack(anchor="w", pady=(8, 2))

        lbl("TYPE")
        self.type_var = tk.StringVar(value="expense")
        type_frame = tk.Frame(left, bg=PALETTE["card"])
        type_frame.pack(fill="x")
        for val, label, color in [("expense", "Expense", PALETTE["accent2"]),
                                   ("income",  "Income",  PALETTE["green"])]:
            tk.Radiobutton(type_frame, text=label, variable=self.type_var, value=val,
                           bg=PALETTE["card"], fg=color, selectcolor=PALETTE["entry_bg"],
                           activebackground=PALETTE["card"], activeforeground=color,
                           font=("Courier New", 10, "bold"),
                           command=self._update_categories).pack(side="left", padx=(0, 10))

        lbl("CATEGORY")
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(left, textvariable=self.cat_var, state="readonly", width=22)
        self.cat_combo.pack(fill="x")
        self._update_categories()

        lbl("AMOUNT (₹)")
        self.amount_entry = tk.Entry(left, bg=PALETTE["entry_bg"], fg=PALETTE["text"],
                                     insertbackground=PALETTE["text"],
                                     font=("Courier New", 12), relief="flat",
                                     highlightthickness=1, highlightcolor=PALETTE["accent"],
                                     highlightbackground=PALETTE["border"])
        self.amount_entry.pack(fill="x", ipady=6)

        lbl("DESCRIPTION")
        self.desc_entry = tk.Entry(left, bg=PALETTE["entry_bg"], fg=PALETTE["text"],
                                   insertbackground=PALETTE["text"],
                                   font=("Courier New", 11), relief="flat",
                                   highlightthickness=1, highlightcolor=PALETTE["accent"],
                                   highlightbackground=PALETTE["border"])
        self.desc_entry.pack(fill="x", ipady=6)

        lbl("DATE  (YYYY-MM-DD)")
        self.date_entry = tk.Entry(left, bg=PALETTE["entry_bg"], fg=PALETTE["text"],
                                   insertbackground=PALETTE["text"],
                                   font=("Courier New", 11), relief="flat",
                                   highlightthickness=1, highlightcolor=PALETTE["accent"],
                                   highlightbackground=PALETTE["border"])
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(fill="x", ipady=6)

        tk.Frame(left, bg=PALETTE["border"], height=1).pack(fill="x", pady=16)

        ttk.Button(left, text="＋  ADD TRANSACTION", style="Accent.TButton",
                   command=self.add_transaction).pack(fill="x")

        tk.Frame(left, bg=PALETTE["card"], height=8).pack()

        ttk.Button(left, text="✕  DELETE SELECTED", style="Danger.TButton",
                   command=self.delete_transaction).pack(fill="x")

        tk.Frame(left, bg=PALETTE["card"], height=8).pack()

        ttk.Button(left, text="✎  EDIT SELECTED", style="Flat.TButton",
                   command=self.edit_transaction).pack(fill="x")

    def _build_right_panel(self, parent):
        right = tk.Frame(parent, bg=PALETTE["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # filter bar
        fbar = tk.Frame(right, bg=PALETTE["card"], padx=12, pady=10)
        fbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        tk.Label(fbar, text="FILTER:", bg=PALETTE["card"], fg=PALETTE["subtext"],
                 font=("Courier New", 9)).pack(side="left", padx=(0, 8))

        for val in ["All", "income", "expense"]:
            color = (PALETTE["green"] if val == "income" else
                     PALETTE["accent2"] if val == "expense" else PALETTE["subtext"])
            tk.Radiobutton(fbar, text=val.upper(), variable=self.filter_type, value=val,
                           bg=PALETTE["card"], fg=color, selectcolor=PALETTE["entry_bg"],
                           activebackground=PALETTE["card"], activeforeground=color,
                           font=("Courier New", 9, "bold"),
                           command=self.refresh_table).pack(side="left", padx=4)

        tk.Label(fbar, text="  CATEGORY:", bg=PALETTE["card"], fg=PALETTE["subtext"],
                 font=("Courier New", 9)).pack(side="left", padx=(12, 4))
        all_cats = ["All"] + CATEGORIES["income"] + CATEGORIES["expense"]
        cat_cb = ttk.Combobox(fbar, textvariable=self.filter_category,
                              values=all_cats, state="readonly", width=14,
                              font=("Courier New", 9))
        cat_cb.pack(side="left")
        cat_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        tk.Label(fbar, text="  SEARCH:", bg=PALETTE["card"], fg=PALETTE["subtext"],
                 font=("Courier New", 9)).pack(side="left", padx=(12, 4))
        tk.Entry(fbar, textvariable=self.search_var,
                 bg=PALETTE["entry_bg"], fg=PALETTE["text"],
                 insertbackground=PALETTE["text"],
                 font=("Courier New", 9), relief="flat", width=18).pack(side="left")

        # treeview
        tree_frame = tk.Frame(right, bg=PALETTE["card"])
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        cols = ("date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        for col, heading, width, anchor in [
            ("date",        "DATE",        100, "center"),
            ("type",        "TYPE",         80, "center"),
            ("category",    "CATEGORY",    130, "w"),
            ("description", "DESCRIPTION", 250, "w"),
            ("amount",      "AMOUNT",      110, "e"),
        ]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.tag_configure("income",  foreground=PALETTE["green"])
        self.tree.tag_configure("expense", foreground=PALETTE["accent2"])
        self.tree.tag_configure("odd",     background="#1E2133")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        # mini bar chart
        chart_frame = tk.Frame(right, bg=PALETTE["card"], padx=14, pady=10)
        chart_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        tk.Label(chart_frame, text="CATEGORY BREAKDOWN  (expenses)",
                 bg=PALETTE["card"], fg=PALETTE["subtext"],
                 font=("Courier New", 8, "bold")).pack(anchor="w")
        self.chart_canvas = tk.Canvas(chart_frame, bg=PALETTE["card"],
                                      height=70, highlightthickness=0)
        self.chart_canvas.pack(fill="x", pady=(6, 0))

    # ── category update ───────────────────────────────────────────────────

    def _update_categories(self):
        cats = CATEGORIES[self.type_var.get()]
        self.cat_combo["values"] = cats
        self.cat_var.set(cats[0])

    # ── CRUD ──────────────────────────────────────────────────────────────

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a positive number.")
            return

        desc = self.desc_entry.get().strip() or "—"
        date_str = self.date_entry.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Use format YYYY-MM-DD.")
            return

        txn = {
            "id": int(datetime.now().timestamp() * 1000),
            "type": self.type_var.get(),
            "category": self.cat_var.get(),
            "description": desc,
            "amount": round(amount, 2),
            "date": date_str,
        }
        self.transactions.append(txn)
        save_data(self.transactions)
        self.amount_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.refresh_all()

    def delete_transaction(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a transaction to delete.")
            return
        txn_id = int(self.tree.item(sel[0])["tags"][0])
        if not messagebox.askyesno("Delete", "Delete this transaction?"):
            return
        self.transactions = [t for t in self.transactions if t["id"] != txn_id]
        save_data(self.transactions)
        self.refresh_all()

    def edit_transaction(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Select a transaction to edit.")
            return
        txn_id = int(self.tree.item(sel[0])["tags"][0])
        txn = next((t for t in self.transactions if t["id"] == txn_id), None)
        if not txn:
            return

        new_desc = simpledialog.askstring("Edit Description", "New description:",
                                          initialvalue=txn["description"])
        if new_desc is None:
            return
        new_amount = simpledialog.askfloat("Edit Amount", "New amount:",
                                           initialvalue=txn["amount"], minvalue=0.01)
        if new_amount is None:
            return

        txn["description"] = new_desc.strip() or "—"
        txn["amount"] = round(new_amount, 2)
        save_data(self.transactions)
        self.refresh_all()

    # ── refresh ───────────────────────────────────────────────────────────

    def refresh_all(self):
        self.refresh_table()
        self.refresh_summary()
        self.refresh_chart()

    def _filtered(self):
        ft   = self.filter_type.get()
        fcat = self.filter_category.get()
        q    = self.search_var.get().lower()
        result = []
        for t in self.transactions:
            if ft  != "All" and t["type"]     != ft:   continue
            if fcat != "All" and t["category"] != fcat: continue
            if q and q not in t["description"].lower() \
                  and q not in t["category"].lower():   continue
            result.append(t)
        return sorted(result, key=lambda x: x["date"], reverse=True)

    def refresh_table(self, *_):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, t in enumerate(self._filtered()):
            sign = "+" if t["type"] == "income" else "-"
            tags = (str(t["id"]), t["type"])
            if i % 2 == 1:
                tags = tags + ("odd",)
            self.tree.insert("", "end", tags=tags, values=(
                t["date"],
                t["type"].upper(),
                t["category"],
                t["description"],
                f"{sign}{fmt_money(t['amount'])}",
            ))

    def refresh_summary(self):
        income  = sum(t["amount"] for t in self.transactions if t["type"] == "income")
        expense = sum(t["amount"] for t in self.transactions if t["type"] == "expense")
        balance = income - expense
        color   = PALETTE["green"] if balance >= 0 else PALETTE["accent2"]

        self.card_balance.config(text=fmt_money(balance), fg=color)
        self.card_income.config(text=fmt_money(income))
        self.card_expense.config(text=fmt_money(expense))
        self.card_count.config(text=str(len(self.transactions)))

    def refresh_chart(self):
        c = self.chart_canvas
        c.delete("all")
        c.update_idletasks()
        W = c.winfo_width() or 600
        H = 60

        totals = defaultdict(float)
        for t in self.transactions:
            if t["type"] == "expense":
                totals[t["category"]] += t["amount"]
        if not totals:
            c.create_text(W//2, H//2, text="No expense data yet",
                          fill=PALETTE["subtext"], font=("Courier New", 9))
            return

        max_val = max(totals.values())
        bar_colors = [PALETTE["accent"], PALETTE["accent2"], PALETTE["green"],
                      PALETTE["yellow"], "#A78BFA", "#38BDF8", "#FB923C"]
        items = sorted(totals.items(), key=lambda x: -x[1])[:7]
        bw = (W - 20) / len(items)

        for i, (cat, val) in enumerate(items):
            bh = max(4, int((val / max_val) * (H - 20)))
            x0 = 10 + i * bw + 4
            x1 = x0 + bw - 8
            y0 = H - bh
            y1 = H - 2
            color = bar_colors[i % len(bar_colors)]
            c.create_rectangle(x0, y0, x1, y1, fill=color, outline="", width=0)
            c.create_text((x0+x1)/2, H - bh - 8,
                          text=cat[:6], fill=PALETTE["subtext"],
                          font=("Courier New", 7), anchor="s")

    # ── export / import ───────────────────────────────────────────────────

    def export_csv(self):
        from tkinter.filedialog import asksaveasfilename
        path = asksaveasfilename(defaultextension=".csv",
                                 filetypes=[("CSV files", "*.csv")],
                                 initialfile="transactions.csv")
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id","date","type","category","description","amount"])
            writer.writeheader()
            writer.writerows(self.transactions)
        messagebox.showinfo("Export", f"Exported {len(self.transactions)} records to:\n{path}")

    def import_csv(self):
        from tkinter.filedialog import askopenfilename
        path = askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        imported = 0
        existing_ids = {t["id"] for t in self.transactions}
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    txn = {
                        "id": int(row["id"]),
                        "date": row["date"],
                        "type": row["type"],
                        "category": row["category"],
                        "description": row["description"],
                        "amount": float(row["amount"]),
                    }
                    if txn["id"] not in existing_ids:
                        self.transactions.append(txn)
                        existing_ids.add(txn["id"])
                        imported += 1
                except Exception:
                    continue
        save_data(self.transactions)
        self.refresh_all()
        messagebox.showinfo("Import", f"Imported {imported} new transactions.")


if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()

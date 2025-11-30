from tkinter import ttk


class StatusBar(ttk.Frame):
    """
    Bottom bar: status message + clock.
    """

    def __init__(self, master):
        super().__init__(master, style="Top.TFrame")

        self.lbl_status = ttk.Label(
            self,
            text="Ready.",
            anchor="w",
            style="Top.TLabel",
        )
        self.lbl_status.pack(side="left", padx=10, pady=5)

        self.lbl_clock = ttk.Label(
            self,
            text="--:--:--",
            anchor="e",
            style="Top.TLabel",
        )
        self.lbl_clock.pack(side="right", padx=10, pady=5)

    def set_message(self, msg: str):
        self.lbl_status.config(text=msg)

    def set_clock(self, text: str):
        self.lbl_clock.config(text=text)

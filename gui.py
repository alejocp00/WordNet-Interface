from enum import Enum
import tkinter as tk


class GUI:
    def __init__(self):
        # Instance the state of the program
        self.state = CheckButtonState.IDLE

        # Create the buttons dictionary
        self.buttons_dic = {}

        # Instance the size of the window
        self.width = 600
        self.height = 400

        # Instance entries size
        self.entry_high = 30
        self.entry_width = self.width / 2
        self.min_separation = 10

        # Create the root window
        self.root = tk.Tk()
        self.root.title("WordNet")
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(0, 0)

        # Create the entries frame
        self.entries_frame = tk.Frame(self.root)

        # Create the two entries. Font size is 18
        self.entry_1 = tk.Entry(self.entries_frame, font=("Arial", 12))
        self.entry_2 = tk.Entry(self.entries_frame, font=("Arial", 12))

        # Create the entries info text
        self.entry_info_1 = tk.Label(self.entries_frame, text="Word 1")
        self.entry_info_2 = tk.Label(self.entries_frame, text="Word 2")

        # Create the check buttons frame
        self.check_buttons_frame = tk.Frame(self.root)

        # Create the twelve check buttons (Assertion, Hyperonym,Entailment,Similarity,Meronym/Holonym,Semantic Relation,Verbs Lexical Relation, Atributte, Antonym, SA, Participe, Pertenece)
        self.buttons_dic[self.state.ASSERTION] = tk.Checkbutton(
            self.check_buttons_frame, text="Assertion"
        )
        self.buttons_dic[self.state.HYPERONYM] = tk.Checkbutton(
            self.check_buttons_frame, text="Hyperonym"
        )
        self.buttons_dic[self.state.ENTAILMENT] = tk.Checkbutton(
            self.check_buttons_frame, text="Entailment"
        )
        self.buttons_dic[self.state.SIMILARITY] = tk.Checkbutton(
            self.check_buttons_frame, text="Similarity"
        )
        self.buttons_dic[self.state.MERONYM_HOLONYM] = tk.Checkbutton(
            self.check_buttons_frame, text="Meronym/Holonym"
        )
        self.buttons_dic[self.state.SEMANTIC_RELATION] = tk.Checkbutton(
            self.check_buttons_frame, text="Semantic Relation"
        )
        self.buttons_dic[self.state.VERBS_LEXICAL_RELATION] = tk.Checkbutton(
            self.check_buttons_frame, text="Verbs Lexical Relation"
        )
        self.buttons_dic[self.state.ATRIBUTTE] = tk.Checkbutton(
            self.check_buttons_frame, text="Atributte"
        )
        self.buttons_dic[self.state.ANTONYM] = tk.Checkbutton(
            self.check_buttons_frame, text="Antonym"
        )
        self.buttons_dic[self.state.SA] = tk.Checkbutton(
            self.check_buttons_frame, text="SA"
        )
        self.buttons_dic[self.state.PARTICIPE] = tk.Checkbutton(
            self.check_buttons_frame, text="Participe"
        )
        self.buttons_dic[self.state.PERTENECE] = tk.Checkbutton(
            self.check_buttons_frame, text="Pertenece"
        )

        # Create the two buttons (Search, Clear)
        self.button_search = tk.Button(self.entries_frame, text="Search")
        self.button_clear = tk.Button(self.entries_frame, text="Clear")

        # Create the result text
        self.result_text = tk.Text(self.root)

        # Update the state of the program
        self.place()

    def run(self):
        self.root.mainloop()

    def place(self):
        """This function will place the widgets in the window.
        The widgets will be placed in the following order:
            1st and 4th quadrant: Result text
            2nd quadrant: Entries and buttons
            3rd quadrant: Check buttons and buttons

        The entries zone will be divided in two parts:
            1st and 4th quadrant: Buttons
            2nd and 3rd quadrant: Entries

        The check buttons will be placed in a grid inside their zone.

        All placing process will take in count the size of the window for the calcs.
        """

        # Placing the entries frame.
        self.entries_frame.place(
            x=0,
            y=0,
            width=self.width / 2,
            height=self.height / 2,
        )

        # Placing the entries.
        self.entry_1.place(
            x=5,
            y=0,
            width=self.entry_width - self.min_separation,
            height=self.entry_high,
        )

        # Placing the entries info text.
        self.entry_info_1.place(
            x=0,
            y=self.entry_1.winfo_y() + self.entry_high,
            width=self.entry_width - self.min_separation,
            height=self.entry_high,
        )

        self.entry_2.place(
            x=5,
            y=80 + self.min_separation,
            width=self.entry_width - self.min_separation,
            height=self.entry_high,
        )

        self.entry_info_2.place(
            x=0,
            y=80 + self.min_separation + self.entry_high,
            width=self.entry_width - self.min_separation,
            height=self.entry_high,
        )

        # Placing the buttons.
        self.button_search.place(
            x=5,
            y=self.height / 2 - self.entry_high,
            width=self.width / 4 - self.min_separation,
            height=self.entry_high,
        )

        self.button_clear.place(
            x=5 + self.width / 4,
            y=self.height / 2 - self.entry_high,
            width=self.width / 4 - self.min_separation,
            height=self.entry_high,
        )

        # Placing the check buttons frame.
        self.check_buttons_frame.place(
            x=0,
            y=self.height / 2,
            width=self.width / 2,
            height=self.height / 2,
        )

        # Placing the check buttons.
        for i in range(12):
            self.buttons_dic[CheckButtonState(i + 1)].grid(
                row=i // 2,
                column=i % 2,
                sticky="w",
            )

        # Placing the result text.
        self.result_text.place(
            x=self.width / 2,
            y=0,
            width=self.width / 2,
            height=self.height,
        )


class CheckButtonState(Enum):
    """This class will be used to identify the state of the program."""

    IDLE = 0
    ASSERTION = 1
    HYPERONYM = 2
    ENTAILMENT = 3
    SIMILARITY = 4
    MERONYM_HOLONYM = 5
    SEMANTIC_RELATION = 6
    VERBS_LEXICAL_RELATION = 7
    ATRIBUTTE = 8
    ANTONYM = 9
    SA = 10
    PARTICIPE = 11
    PERTENECE = 12


GUI().run()

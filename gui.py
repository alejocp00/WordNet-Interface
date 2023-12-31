from enum import Enum
import tkinter as tk
from prolog_api import Consulter, Operator


class GUI:
    def __init__(self):
        # Instance the state of the program
        self.state = Operator.IDLE

        # Create the buttons dictionaries
        self.check_buttons_dic = {}
        self.check_buttons_state = {}

        # Create the consulter
        self.consulter = Consulter()

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
        self.root.state("zoomed")

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

        self.poblate_check_buttons_state()
        self.create_check_buttons()

        # Create the two buttons (Search, Clear)
        self.button_search = tk.Button(
            self.entries_frame, text="Search", command=self.search_behavior
        )
        self.button_clear = tk.Button(
            self.entries_frame, text="Clear", command=self.clear_behavior
        )

        # Create the result text
        self.result_text = tk.Text(self.root)
        self.result_text.config(state=tk.DISABLED)

        # Update the state of the program
        self.place()

        # Bind the resize event
        self.root.bind("<Configure>", self.resize_result_text)

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
        for i in range(11):
            self.check_buttons_dic[Operator(i + 1)].grid(
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

    # Resize the result text
    def resize_result_text(self, event):
        """This function will resize the result text when the window is resized."""

        # Delay the resize event 1s
        self.root.after(500, self.resize_result_text_aux)

    def resize_result_text_aux(self):
        """This function will resize the result text when the window is resized."""

        # Get the new size of the window
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        # Resize the result text
        self.result_text.place(
            x=self.width / 2,
            y=0,
            width=width,
            height=height,
        )

    def create_check_buttons(self):
        """Create the twelve check buttons (Assertion, Hypernym,Entailment,Similarity,Meronym/Holonym,Semantic Relation,Verbs Lexical Relation, Attribute, Antonym, SA, Participe, Pertenece)"""
        for i in range(11):
            c_enum = Operator(i + 1)
            self.check_buttons_dic[c_enum] = tk.Checkbutton(
                self.check_buttons_frame,
                text=c_enum,
                variable=self.check_buttons_state[c_enum],
                command=lambda c=c_enum: self.check_box_behavior(c),
            )

    def poblate_check_buttons_state(self):
        """This function will poblate the check buttons dictionary with the state of the program."""
        for i in range(11):
            self.check_buttons_state[Operator(i + 1)] = tk.IntVar()

    def check_box_behavior(self, selected):
        """This will be the behavior of the check buttons."""

        # Deactivate the other check buttons
        self.only_one_active(selected)

        # Set state to IDLE if no check button is selected
        for value in self.check_buttons_state.values():
            if value.get() == 0:
                self.state = Operator.IDLE
            else:
                # Update the state of the program
                self.state = selected
                break

        # Update the text of the entries
        self.select_text()

    def only_one_active(self, selected):
        """This function will make sure that only one check button is active at the same time."""

        for key in self.check_buttons_state.keys():
            if key is not selected:
                self.check_buttons_state[key].set(0)

    def select_text(self):
        """This function will select the text of the two entries info text."""
        if self.state == Operator.IDLE:
            self.entry_info_1.config(text="Word 1")
            self.entry_info_2.config(text="Word 2")
        elif self.state == Operator.ASSERTION:
            self.entry_info_1.config(text="All kind of words.")
            self.entry_info_2.config(text="Not be used")
        elif self.state == Operator.HYPERNYM:
            self.entry_info_1.config(text="Noun or verb")
            self.entry_info_2.config(text="Noun or verb")
        elif self.state == Operator.ENTAILMENT:
            self.entry_info_1.config(text="Verb")
            self.entry_info_2.config(text="Verb")
        elif self.state == Operator.SIMILARITY:
            self.entry_info_1.config(text="All kind of words.")
            self.entry_info_2.config(text="All kind of words.")
        elif self.state == Operator.MERONYM_HOLONYM:
            self.entry_info_1.config(text="Noun")
            self.entry_info_2.config(text="Noun")
        elif self.state == Operator.CAUSED:
            self.entry_info_1.config(text="Verb")
            self.entry_info_2.config(text="Verb")
        elif self.state == Operator.ATTRIBUTE:
            self.entry_info_1.config(text="Noun")
            self.entry_info_2.config(text="Adjective")
        elif self.state == Operator.ANTONYM:
            self.entry_info_1.config(text="All kind of words.")
            self.entry_info_2.config(text="All kind of words.")
        elif self.state == Operator.SA:
            self.entry_info_1.config(text="Verb")
            self.entry_info_2.config(text="Verb or adjective")
        elif self.state == Operator.PARTICIPLE:
            self.entry_info_1.config(text="Adjective")
            self.entry_info_2.config(text="Verb")
        elif self.state == Operator.PERTAINS:
            self.entry_info_1.config(text="Adjective or adverb")
            self.entry_info_2.config(text="Adjective if 1st is adverb. Otherwise both.")

    def show_result(self, result: str):
        """This method will update the Text widget with the given result"""

        # Enable the text widget
        self.result_text.config(state=tk.NORMAL)

        # Delete the current text
        self.result_text.delete("1.0", tk.END)

        # Insert the new text
        self.result_text.insert(tk.END, result)

        # Disable the text widget
        self.result_text.config(state=tk.DISABLED)

    def search_behavior(self):
        """This function will be attached to the search button."""

        # Get the text of the entries
        word_1 = self.entry_1.get()
        word_2 = self.entry_2.get()

        # Get the state of the program
        state = self.state

        self.consulter.receive_query(state, word_1, word_2)
        self.consulter.process_query()

        self.show_result(self.consulter.result_string)

    def clear_behavior(self):
        """This function will be attached to the clear button."""

        # Delete the text of the entries
        self.entry_1.delete(0, tk.END)
        self.entry_2.delete(0, tk.END)

        # Set the state of the program to IDLE
        self.state = Operator.IDLE

        # Deactivate the check buttons
        for value in self.check_buttons_state.values():
            value.set(0)

        # Delete the text of the result text
        self.show_result("")

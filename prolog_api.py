from pyswip import Prolog
from gui import CheckButtonState
import os


class Consulter:
    def __init__(self):
        # Create the prolog object.
        self.prolog = Prolog()

        # Consult the prolog files.
        self.load_consults()

    def load_consults(self):
        """Load every prolog file in prolog_files."""

        for file in os.listdir("prolog_files"):
            if file.endswith(".pl"):
                self.prolog.consult("prolog_files/" + file)

    def receive_query(self, operator: CheckButtonState, word_1: str, word_2: str):
        """Receive two words and the operator to apply, and set the query"""

        self.operator = operator
        self.word_1 = WordInfo(word_1)
        self.word_2 = WordInfo(word_2)

    def process_query(self):
        """Perform the operation in the query"""

        self.result_string = "Processing..."

        if self.operator == CheckButtonState.ASSERTION:
            self.result_string = self.assertion()

    def assertion(self):
        """Search all possible meanings of the word 1"""

        # Get all the word info through the s predicate.
        s_result = self.make_consult(
            f"s(SynsetID, WordNumber,'{self.word_1.word}', WordType, WordSense, TagCount)"
        )

        if s_result == []:
            return self.not_fount(self.word_1.word)

        # Fill the word info with the results.
        for result in s_result:
            self.word_1.synset_id_list.append(result["SynsetID"])
            self.word_1.word_number_list.append(result["WordNumber"])
            self.word_1.word_sense_list.append(result["WordSense"])
            self.word_1.word_type_list.append(
                self.translate_word_type(result["WordType"])
            )
            self.word_1.tag_count_list.append(result["TagCount"])

        # Get all the word info through the g predicate.
        for synset_id in self.word_1.synset_id_list:
            g_result = self.make_consult(f"g({synset_id}, Gloss)")
            self.word_1.gloss_list.append(g_result[0]["Gloss"])

        # Create the result string.
        result_string = ""
        for i in range(len(self.word_1.synset_id_list)):
            result_string += f"{self.word_1.word}:\n  ({self.word_1.word_type_list[i]}):\n    {self.word_1.gloss_list[i]}\n"

        return result_string

    def make_consult(self, query: str) -> list:
        """Make a consult to the prolog file."""
        return list(self.prolog.query(query))

    def translate_word_type(self, word_type: str) -> str:
        """Translate the word type to a more readable format."""
        if word_type == "n":
            return "noun"
        elif word_type == "v":
            return "verb"
        elif word_type == "a" or word_type == "s":
            return "adjective"
        elif word_type == "r":
            return "adverb"
        else:
            return "unknown"

    def not_found(self, word):
        return f"The word {word} was not found in the database."


class WordInfo:
    """Class that contains the information of a word."""

    def __init__(self, word: str):
        self.word = word
        self.synset_id_list = []
        self.word_type_list = []
        self.word_number_list = []
        self.word_sense_list = []
        self.gloss_list = []
        self.tag_count_list = []

    def __str__(self):
        return self.word

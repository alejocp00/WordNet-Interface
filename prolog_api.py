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

        # Check for the Assertion operator.
        if self.operator == CheckButtonState.ASSERTION:
            self.result_string = self.assertion()

        # Check for the Similarity operator.
        elif self.operator == CheckButtonState.SIMILARITY:
            if self.word_2.word == "" and self.word_1.word != "":
                self.result_string = self.similarity_1_to_all(1)
            elif self.word_1.word == "" and self.word_2.word != "":
                self.result_string = self.similarity_1_to_all(2)
            else:
                self.result_string = self.similarity_1_to_2()

        # Check for the Antonym operator.
        elif self.operator == CheckButtonState.ANTONYM:
            if self.word_2.word == "" and self.word_1.word != "":
                self.result_string = self.antonym_1_to_all(1)
            elif self.word_1.word == "" and self.word_2.word != "":
                self.result_string = self.antonym_1_to_all(2)
            else:
                self.result_string = self.antonym_1_to_2()

        # Check for the Hypernym operator.
        elif self.operator == CheckButtonState.HYPERNYM:
            if self.word_2.word == "" and self.word_1.word != "":
                self.result_string = self.hypernym_of()
            elif self.word_1.word == "" and self.word_2.word != "":
                self.result_string = self.inverse_hypernym()
            else:
                self.result_string = self.is_hypernym()

        # Check for the Entailment operator.
        elif self.operator == CheckButtonState.ENTAILMENT:
            if self.word_2.word == "" and self.word_1.word != "":
                self.result_string = self.entailment_of()
            elif self.word_1.word == "" and self.word_2.word != "":
                self.result_string = self.inverse_entailment()
            else:
                self.result_string = self.is_entailment()

        # Check for meronym holonym
        elif self.operator == CheckButtonState.MERONYM_HOLONYM:
            operations = ["mm", "ms", "mp"]
            if self.word_2.word == "" and self.word_1.word != "":
                for operation in operations:
                    self.result_string += self.mer_hol("Meronym", operation)
            elif self.word_1.word == "" and self.word_2.word != "":
                for operation in operations:
                    self.result_string += self.mer_hol("Holonym", operation)
            else:
                self.result_string = self.is_meronym()

        # Check for the Caused operator.
        elif self.operator == CheckButtonState.CAUSED:
            self.result_string = self.caused()

        # Check for the Attribute operator.
        elif self.operator == CheckButtonState.ATTRIBUTE:
            if self.word_2.word == "" and self.word_1.word != "":
                self.result_string = self.attribute_of(1)
            elif self.word_1.word == "" and self.word_2.word != "":
                self.result_string = self.attribute_of(2)
            else:
                self.result_string = self.is_attribute()

        # Check for the Adicional information operator.
        elif self.operator == CheckButtonState.SA:
            self.result_string = self.sa()

    def assertion(self):
        """Search all possible meanings of the word 1"""

        # Get the principal data of the word 1
        self.fill_word_info(1)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)

        # Get all the word info through the g predicate.
        for synset_id in self.word_1.synset_id_list:
            g_result = self.make_consult(f"g({synset_id}, Gloss)")
            self.word_1.gloss_list.append(g_result[0]["Gloss"])

        # Create the result string.
        result_string = ""
        for i in range(len(self.word_1.synset_id_list)):
            result_string += f"{self.word_1.word}:\n  ({self.word_1.word_type_list[i]}):\n    {self.word_1.gloss_list[i]}\n"

        return result_string

    def caused(self):
        """Use the cs predicate to search for the cause of the word 1"""

        # Get the principal data of the word 1
        self.fill_word_info(1)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)

        # Get all the cause of the word
        cause_synset_list = []
        for synset_id in self.word_1.synset_id_list:
            cause_result = self.make_consult(f"cs({synset_id}, CauseID)")
            cause_synset_list.append(cause_result)

        # Get all the words in the synset
        cause_words_list = []
        gloss_list = []
        for cause_synset in cause_synset_list:
            for cause_word in cause_synset:
                cause_words_list.append(self.get_all_words(cause_word["CauseID"]))
                gloss_list.append(
                    self.make_consult(f"g({cause_word['CauseID']}, Gloss)")[0]["Gloss"]
                )

        # Create the result string.
        result_string = f"Cause words of {self.word_1.word}:\n\n"
        for i in range(len(cause_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in cause_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if result_string == f"Cause words of {self.word_1.word}:\n\n":
            return "No cause words were found."

        return result_string

    def sa(self):
        """Use the sa predicate to search for words that adds adicional information to the word 1."""

        # sa/4 receive the word synset id and word number, and return the synset id and word number of the words that adds adicional information.

        # Get the principal data of the word 1
        self.fill_word_info(1)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)

        # Get all the words that adds adicional information to the word 1.
        sa_synset_list = []
        for i in range(len(self.word_1.synset_id_list)):
            sa_result = self.make_consult(
                f"sa({self.word_1.synset_id_list[i]}, {self.word_1.word_number_list[i]}, SynsetID, WordNumber)"
            )
            sa_synset_list.append(sa_result)

        # Get all the words in the synset
        sa_words_list = []
        gloss_list = []
        for sa_synset in sa_synset_list:
            for sa_word in sa_synset:
                sa_words_list.append(self.get_all_words(sa_word["SynsetID"]))
                gloss_list.append(
                    self.make_consult(f"g({sa_word['SynsetID']}, Gloss)")[0]["Gloss"]
                )

        # Create the result string.
        result_string = (
            f"Words that adds adicional information to {self.word_1.word}:\n\n"
        )
        for i in range(len(sa_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in sa_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if (
            result_string
            == f"Words that adds adicional information to {self.word_1.word}:\n\n"
        ):
            return "No words that adds adicional information were found."

        return result_string

    # region Similarity

    def similarity_1_to_all(self, word_indicator: int = 1):
        """Search all possible meanings of the word 1 and 2"""

        # Get the principal data of the word 1 and 2
        self.fill_word_info(word_indicator)

        temp_word = self.word_1 if word_indicator == 1 else self.word_2

        if not temp_word.exist:
            return self.not_found(temp_word.word)

        # Get all the similar of the word
        similar_synset_list = []
        for synset_id in temp_word.synset_id_list:
            similar_result = self.make_consult(f"sim({synset_id}, SimilarID)")
            similar_synset_list.append(similar_result)

        # Get all the words in the synset
        similar_words_list = []
        gloss_list = []
        for similar_synset in similar_synset_list:
            for similar_word in similar_synset:
                similar_words_list.append(self.get_all_words(similar_word["SimilarID"]))
                gloss_list.append(
                    self.make_consult(f"g({similar_word['SimilarID']}, Gloss)")[0][
                        "Gloss"
                    ]
                )

        # Create the result string.
        result_string = f"Similar words with {temp_word.word}:\n\n"
        for i in range(len(similar_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in similar_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if result_string == "":
            return "No similar words were found."

        return result_string

    def similarity_1_to_2(self):
        """Search if the two given words are similar"""

        # Fill words info
        self.fill_word_info(1)
        self.fill_word_info(2)

        # Check if the words exist
        if not self.word_1.exist:
            return self.not_found(self.word_1.word)
        if not self.word_2.exist:
            return self.not_found(self.word_2.word)

        # Get all the similar of the word 1
        similar_synset_list = []
        for synset_id in self.word_1.synset_id_list:
            similar_result = self.make_consult(f"sim({synset_id}, SimilarID)")
            similar_synset_list.append(similar_result)

        # Get all the words in the synset
        similar_words_list = []
        gloss_list = []
        for similar_synset in similar_synset_list:
            for similar_word in similar_synset:
                similar_words_list.append(self.get_all_words(similar_word["SimilarID"]))
                gloss_list.append(
                    self.make_consult(f"g({similar_word['SimilarID']}, Gloss)")[0][
                        "Gloss"
                    ]
                )

        # Check if the word 2 is in the similar words list
        for i in range(len(similar_words_list)):
            if self.word_2.word in similar_words_list[i]:
                return f"{self.word_1.word} and {self.word_2.word} are similar.\n\n{gloss_list[i]}:\n\t{self.word_2.word}"

        return f"{self.word_1.word} and {self.word_2.word} are not similar."

    # endregion

    # region Antonym

    def antonym_1_to_all(self, word_indicator: int = 1):
        """Search all possible meanings of the word 1 and 2"""

        # Get the principal data of the word 1 and 2
        self.fill_word_info(word_indicator)

        temp_word = self.word_1 if word_indicator == 1 else self.word_2

        if not temp_word.exist:
            return self.not_found(temp_word.word)

        # Get all the antonyms of the word
        antonym_synset_list = []
        for i in range(len(temp_word.synset_id_list)):
            antonym_result = self.make_consult(
                f"ant({temp_word.synset_id_list[i]},{temp_word.word_number_list[i]}, SynsetID, WordNumber)"
            )
            antonym_synset_list.append(antonym_result)

        # Get the words indexing with the word number. This will consult s/6 with the synset id and the word number.
        antonym_words_list = []
        for antonym_synset in antonym_synset_list:
            for antonym_word in antonym_synset:
                antonym_words_list.append(
                    self.make_consult(
                        f"s({antonym_word['SynsetID']}, {antonym_word['WordNumber']}, Word, _, _, _)"
                    )[0]["Word"]
                )

        # Get the gloss of the antonym synset.
        gloss_list = []
        for antonym_synset in antonym_synset_list:
            for antonym_word in antonym_synset:
                gloss_list.append(
                    self.make_consult(f"g({antonym_word['SynsetID']}, Gloss)")[0][
                        "Gloss"
                    ]
                )

        # Create the result string.
        result_string = f"Antonym words with {temp_word.word}:\n\n"
        for i in range(len(antonym_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            result_string += f"\t{antonym_words_list[i]}"
            result_string += "\n\n"

        if result_string == "":
            return "No antonym words were found."

        return result_string

    # Todo: Implement this method.
    def antonym_1_to_2(self):
        pass

    # endregion

    # region Hypernym

    def hypernym_of(self):
        """Search all possible meanings of the word 1"""

        # Get the principal data of the word 1
        self.fill_word_info(1)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)

        # Get all the hypernym of the word
        hypernym_synset_list = []
        for synset_id in self.word_1.synset_id_list:
            hypernym_result = self.make_consult(f"hyp({synset_id}, HypernymID)")
            hypernym_synset_list.append(hypernym_result)

        # Get all the words in the synset
        hypernym_words_list = []
        gloss_list = []
        for hypernym_synset in hypernym_synset_list:
            for hypernym_word in hypernym_synset:
                hypernym_words_list.append(
                    self.get_all_words(hypernym_word["HypernymID"])
                )
                gloss_list.append(
                    self.make_consult(f"g({hypernym_word['HypernymID']}, Gloss)")[0][
                        "Gloss"
                    ]
                )

        # Create the result string.
        result_string = f"Hypernym words of {self.word_1.word}:\n\n"
        for i in range(len(hypernym_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in hypernym_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if result_string == f"Hypernym words of {self.word_1.word}:\n\n":
            return "No hypernym words were found."

        return result_string

    def inverse_hypernym(self):
        """Search for all the words that the word 2 is hypernym of"""

        # Get the principal data of the word 2
        self.fill_word_info(2)

        if not self.word_2.exist:
            return self.not_found(self.word_2.word)

        # Get all the inverse hypernym of the word
        inverse_hypernym_synset_list = []
        for synset_id in self.word_2.synset_id_list:
            inverse_hypernym_result = self.make_consult(f"hyp(SynsetID, {synset_id})")
            inverse_hypernym_synset_list.append(inverse_hypernym_result)

        # Get all the words in the synset
        inverse_hypernym_words_list = []
        gloss_list = []
        for inverse_hypernym_synset in inverse_hypernym_synset_list:
            for inverse_hypernym_word in inverse_hypernym_synset:
                inverse_hypernym_words_list.append(
                    self.get_all_words(inverse_hypernym_word["SynsetID"])
                )
                gloss_list.append(
                    self.make_consult(f"g({inverse_hypernym_word['SynsetID']}, Gloss)")[
                        0
                    ]["Gloss"]
                )

        # Create the result string.
        result_string = f"Inverse hypernym words of {self.word_2.word}:\n\n"
        for i in range(len(inverse_hypernym_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in inverse_hypernym_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if result_string == f"Inverse hypernym words of {self.word_2.word}:\n\n":
            return "No inverse hypernym words were found."

        return result_string

    def is_hypernym(self):
        """Search if the word 2 is hypernym of the word 1"""

        # Get the principal data of the word 1 and 2
        self.fill_word_info(1)
        self.fill_word_info(2)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)
        if not self.word_2.exist:
            return self.not_found(self.word_2.word)

        # Get all the hypernym of the word 1
        hypernym_synset_list = []
        for synset_id in self.word_1.synset_id_list:
            hypernym_result = self.make_consult(f"hyp({synset_id}, HypernymID)")
            hypernym_synset_list.append(hypernym_result)

        # Get all the words in the synset
        hypernym_words_list = []
        gloss_list = []
        for hypernym_synset in hypernym_synset_list:
            for hypernym_word in hypernym_synset:
                hypernym_words_list.append(
                    self.get_all_words(hypernym_word["HypernymID"])
                )
                gloss_list.append(
                    self.make_consult(f"g({hypernym_word['HypernymID']}, Gloss)")[0][
                        "Gloss"
                    ]
                )

        # Check if the word 2 is in the hypernym words list
        for i in range(len(hypernym_words_list)):
            if self.word_2.word in hypernym_words_list[i]:
                return f"{self.word_2.word} is hypernym of {self.word_1.word}.\n\n{gloss_list[i]}:\n\t{self.word_1.word}"

        return f"{self.word_2.word} is not hypernym of {self.word_1.word}."

    # endregion

    # region Entailment

    def entailment_of(self):
        """Search all possible meanings of the word 1"""

        # Get the principal data of the word 1
        self.fill_word_info(1)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)

        # Get all the entailment of the word
        entailment_synset_list = []
        for synset_id in self.word_1.synset_id_list:
            entailment_result = self.make_consult(f"ent({synset_id}, EntailmentID)")
            entailment_synset_list.append(entailment_result)

        # Get all the words in the synset
        entailment_words_list = []
        gloss_list = []
        for entailment_synset in entailment_synset_list:
            for entailment_word in entailment_synset:
                entailment_words_list.append(
                    self.get_all_words(entailment_word["EntailmentID"])
                )
                gloss_list.append(
                    self.make_consult(f"g({entailment_word['EntailmentID']}, Gloss)")[
                        0
                    ]["Gloss"]
                )

        # Create the result string.
        result_string = f"Entailment words of {self.word_1.word}:\n\n"
        for i in range(len(entailment_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in entailment_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if result_string == f"Entailment words of {self.word_1.word}:\n\n":
            return "No entailment words were found."

        return result_string

    def inverse_entailment(self):
        """Search for all the words that the word 2 is entailment of"""

        # Get the principal data of the word 2
        self.fill_word_info(2)

        if not self.word_2.exist:
            return self.not_found(self.word_2.word)

        # Get all the inverse entailment of the word
        inverse_entailment_synset_list = []
        for synset_id in self.word_2.synset_id_list:
            inverse_entailment_result = self.make_consult(f"ent(SynsetID, {synset_id})")
            inverse_entailment_synset_list.append(inverse_entailment_result)

        # Get all the words in the synset
        inverse_entailment_words_list = []
        gloss_list = []
        for inverse_entailment_synset in inverse_entailment_synset_list:
            for inverse_entailment_word in inverse_entailment_synset:
                inverse_entailment_words_list.append(
                    self.get_all_words(inverse_entailment_word["SynsetID"])
                )
                gloss_list.append(
                    self.make_consult(
                        f"g({inverse_entailment_word['SynsetID']}, Gloss)"
                    )[0]["Gloss"]
                )

        # Create the result string.
        result_string = f"Inverse entailment words of {self.word_2.word}:\n\n"
        for i in range(len(inverse_entailment_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in inverse_entailment_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if result_string == f"Inverse entailment words of {self.word_2.word}:\n\n":
            return "No inverse entailment words were found."

        return result_string

    def is_entailment(self):
        """Search if the word 2 is entailment of the word 1"""

        # Get the principal data of the word 1 and 2
        self.fill_word_info(1)
        self.fill_word_info(2)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)
        if not self.word_2.exist:
            return self.not_found(self.word_2.word)

        # Get all the entailment of the word 1
        entailment_synset_list = []
        for synset_id in self.word_1.synset_id_list:
            entailment_result = self.make_consult(f"ent({synset_id}, EntailmentID)")
            entailment_synset_list.append(entailment_result)

        # Get all the words in the synset
        entailment_words_list = []
        gloss_list = []
        for entailment_synset in entailment_synset_list:
            for entailment_word in entailment_synset:
                entailment_words_list.append(
                    self.get_all_words(entailment_word["EntailmentID"])
                )
                gloss_list.append(
                    self.make_consult(f"g({entailment_word['EntailmentID']}, Gloss)")[
                        0
                    ]["Gloss"]
                )

        # Check if the word 2 is in the entailment words list
        for i in range(len(entailment_words_list)):
            if self.word_2.word in entailment_words_list[i]:
                return f"{self.word_2.word} is entailment of {self.word_1.word}.\n\n{gloss_list[i]}:\n\t{self.word_1.word}"

        return f"{self.word_2.word} is not entailment of {self.word_1.word}"

    # endregion

    # region Meronym Holonym

    def mer_hol(self, function: str, operator: str):
        """Make the consult to the prolog file with the operator. The operator can be mm, ms or mp."""

        if function == "Meronym":
            # Get the principal data of the word 1
            self.fill_word_info(1)

            if not self.word_1.exist:
                return self.not_found(self.word_1.word)
        elif function == "Holonym":
            # Get the principal data of the word 2
            self.fill_word_info(2)

            if not self.word_2.exist:
                return self.not_found(self.word_2.word)

        operation = (
            "member"
            if operator == "mm"
            else "substance"
            if operator == "ms"
            else "part"
        )

        # Get all the meronym of the word
        consult_synset_list = []
        for synset_id in self.word_1.synset_id_list:
            consult_result = self.make_consult(f"{operator}({synset_id}, Consult_ID)")
            consult_synset_list.append(consult_result)

        # Get all the words in the synset
        operation_words_list = []
        gloss_list = []
        for operation_synset in consult_synset_list:
            for operation_word in operation_synset:
                operation_words_list.append(
                    self.get_all_words(operation_word["Consult_ID"])
                )
                gloss_list.append(
                    self.make_consult(f"g({operation_word['Consult_ID']}, Gloss)")[0][
                        "Gloss"
                    ]
                )

        # Create the result string.
        result_string = f"{function}-{operation} words of {self.word_1.word}:\n\n"
        for i in range(len(operation_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in operation_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if result_string == f"{function}-{operation} words of {self.word_1.word}:\n\n":
            return f"No {function}-{operation} words were found."

        return result_string

    # Todo: Implement this method.
    def is_meronym(self):
        pass

    # endregion

    # region Attribute

    def attribute_of(self, word_indicator: int = 1):
        """Search all possible meanings of the word 1 and 2"""

        # Get the principal data of the word 1 and 2
        self.fill_word_info(word_indicator)

        temp_word = self.word_1 if word_indicator == 1 else self.word_2

        if not temp_word.exist:
            return self.not_found(temp_word.word)

        # Get all the attribute of the word
        attribute_synset_list = []
        for synset_id in temp_word.synset_id_list:
            attribute_result = self.make_consult(f"at({synset_id}, AttributeID)")
            attribute_synset_list.append(attribute_result)

        # Get all the words in the synset
        attribute_words_list = []
        gloss_list = []
        for attribute_synset in attribute_synset_list:
            for attribute_word in attribute_synset:
                attribute_words_list.append(
                    self.get_all_words(attribute_word["AttributeID"])
                )
                gloss_list.append(
                    self.make_consult(f"g({attribute_word['AttributeID']}, Gloss)")[0][
                        "Gloss"
                    ]
                )

        # Create the result string.
        result_string = f"Attribute words of {temp_word.word}:\n\n"
        for i in range(len(attribute_words_list)):
            result_string += f"{gloss_list[i]}:\n "
            for word in attribute_words_list[i]:
                result_string += f"\t{word}"
            result_string += "\n\n"

        if result_string == f"Attribute words of {temp_word.word}:\n\n":
            return "No attribute words were found."

        return result_string

    def is_attribute(self):
        """Search if the word 2 is attribute of the word 1"""

        # Get the principal data of the word 1 and 2
        self.fill_word_info(1)
        self.fill_word_info(2)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)
        if not self.word_2.exist:
            return self.not_found(self.word_2.word)

        # Call at predicate with the word 1 and 2 for every synset id.
        for synset_id_1 in self.word_1.synset_id_list:
            for synset_id_2 in self.word_2.synset_id_list:
                at_result = self.make_consult(f"at({synset_id_1}, {synset_id_2})")
                if at_result != []:
                    return f"{self.word_2.word} is attribute of {self.word_1.word}."
        return f"{self.word_2.word} is not attribute of {self.word_1.word}"

    # endregion

    def fill_word_info(self, word_selector: int):
        temp_word = self.word_1 if word_selector == 1 else self.word_2

        # Get all the word info through the s predicate.
        s_result = self.make_consult(
            f"s(SynsetID, WordNumber,'{temp_word.word}', WordType, WordSense, TagCount)"
        )

        # Check if the word exists.
        temp_word.exist = s_result != []

        # Fill the word info with the results.
        for result in s_result:
            temp_word.synset_id_list.append(result["SynsetID"])
            temp_word.word_number_list.append(result["WordNumber"])
            temp_word.word_sense_list.append(result["WordSense"])
            temp_word.word_type_list.append(
                self.translate_word_type(result["WordType"])
            )
            temp_word.tag_count_list.append(result["TagCount"])

    def get_all_words(self, S_ID: str):
        """Get all the words in a synset"""

        words_in_synset = []

        search_result = self.make_consult(f"s({S_ID}, _, Word, _, _, _)")

        for result in search_result:
            words_in_synset.append(result["Word"])

        return words_in_synset

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
        self.exist = False

    def __str__(self):
        return self.word

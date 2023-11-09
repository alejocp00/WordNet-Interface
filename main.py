from pyswip import Prolog

prolog = Prolog()
prolog.consult("prolog_files/wn_s.pl")
prolog.consult("prolog_files/wn_g.pl")


def make_consult(query: str) -> list:
    return list(prolog.query(query))


def translate_word_type(word_type: str) -> str:
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

answer = make_consult("s(S_ID,W_N,table,W_T,W_S,T_C)")

print("The word table has this synsets:")
for element in answer:
    s_id = element["S_ID"]
    w_number = element["W_N"]
    w_type = element["W_T"]
    w_sensibility = element["W_S"]
    t_ccount = element["T_C"]
    translated_w_type = translate_word_type(w_type)

    gloss = make_consult("g(" + str(s_id) + ",G)")[0]["G"]

    print(f"\t{translated_w_type}:")
    print(f"\t\t {gloss}")

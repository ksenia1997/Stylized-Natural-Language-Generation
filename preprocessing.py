import random
import re
import string

import en_core_web_sm
import spacy
from spacy.tokenizer import Tokenizer

from params import *
from utils.csv import *
from utils.json import *


def personas_description(line):
    your_persona = re.findall(r"your persona:(.*)", line)
    partner_persona = re.findall(r"partner's persona:(.*)", line)
    if your_persona:
        return True, your_persona[0], ""
    elif partner_persona:
        return True, "", partner_persona[0]
    else:
        return False, "", ""


def prepare_both_Persona_chat(filename, pair_count):
    print("Prepare Persona chat with both descriptions")
    with open(filename) as fp:
        # arr_len_utter1 = []
        # arr_len_utter2 = []
        # arr_len_y_descr = []
        # arr_len_p_descr = []
        # a_y, a_p = 0, 0
        # a_u1, a_u2 = 0, 0
        your_persona_description = []
        partner_persona_description = []
        counter = 0

        delimiter_context_dialogue = " CC "
        delimiter = " # "
        delimiter_start = " SS "
        delimiter_sep = " SEP "
        delimiter_end = " EE "

        person1, person2 = [], []
        add_description = True
        dialog_counter = 0
        train_data, valid_data, test_data = [], [], []

        for line in fp:
            counter += 1
            is_description, y, p = personas_description(line)
            if is_description:
                add_description = True
                if y != "":
                    your_persona_description.append(y)
                if p != "":
                    partner_persona_description.append(p)
            else:
                if add_description:
                    dialog_counter += 1
                    add_description = False
                    # for yp in your_persona_description:
                    #     arr_len_y_descr.append(len(yp.split()))
                    #     a_y += len(yp.split())
                    # for pp in partner_persona_description:
                    #     arr_len_p_descr.append(len(pp.split()))
                    #     a_p += len(pp.split())
                    context = ""
                    data = []
                    for i in range(len(person1)):
                        data.append(partner_persona_desc_str + delimiter_context_dialogue + delimiter_start + context)
                        data.append(person1[i])
                        context += person1[i] + delimiter
                        data.append(your_persona_desc_str + delimiter_context_dialogue + delimiter_start + context)
                        data.append(person2[i])
                        context += person2[i] + delimiter
                    your_persona_desc_str = delimiter.join(your_persona_description)
                    partner_persona_desc_str = delimiter.join(partner_persona_description)
                    person1, person2 = [], []
                    your_persona_description = []
                    partner_persona_description = []
                    if counter % 5 == 0:
                        valid_data += data
                    elif counter % 9 == 0:
                        test_data += data
                    else:
                        train_data += data
            sentences = line.split("\t")
            if len(sentences) > 1:
                utterance1 = re.findall(r"\d+ (.*)", sentences[0])[0]
                utterance2 = sentences[1]
                person1.append(utterance1)
                person2.append(utterance2)
                # arr_len_utter1.append(len(utterance1.split()))
                # arr_len_utter2.append(len(utterance2.split()))
                # a_u1 += len(utterance1.split())
                # a_u2 += len(utterance2.split())
    return train_data, valid_data, test_data


def prepare_Twitter_data(filename):
    print("Reading Twitter data")
    train_data = []
    valid_data = []
    test_data = []
    counter = 0
    with open(filename) as fp:
        for line in fp:
            train_data.append(line)
            if counter % 10 == 0:
                valid_data.append(line)
            if counter % 20 == 0:
                test_data.append(line)
            counter += 1

    return train_data, valid_data, test_data


def prepare_Persona_chat(filename, context_pair_count):
    print("Reading Persona chat")
    train_data = []
    test_data = []
    valid_data = []
    context_pair_counter = 0
    dialogue_counter = 1
    delimiter_context_dialogue = " CC "
    delimiter = " # "
    delimiter_start = " SS "
    delimiter_sep = " SEP "
    delimiter_end = " EE "

    your_persona_description = ""
    add_to_test_data = False
    add_to_valid_data = False

    arr_len_description = []
    arr_len_question = []
    arr_len_answer = []

    append_description = False

    with open(filename) as fp:
        question_line = ""
        for line in fp:
            data = []
            if line == '\n':
                question_line = ""
                dialogue_counter += 1
                if dialogue_counter % 5 == 0:
                    add_to_valid_data = True
                else:
                    add_to_valid_data = False
                    if random.randint(0, 100) < 5:
                        add_to_test_data = True
                        test_data.append("\n")
                        test_data.append("\n")
                    else:
                        add_to_test_data = False
            your_persona = re.findall(r"(your persona:.*\\n)", line)
            if WITH_DESCRIPTION and len(your_persona) > 0:
                append_description = True
                your_persona = re.sub(r"\\n", '', your_persona[0]).split("your persona: ")
                your_persona_description = delimiter.join(your_persona[1:])
                your_persona_description = JOIN_TOKEN.join(tokenize(your_persona_description, nlp)[1])
                arr_len_description.append(len(your_persona_description.split()))
                #   persona # persona # persona # persona <context delimiter>
                question_line += your_persona_description + delimiter_context_dialogue
            line = re.sub(r"(your persona:.*\\n)", ' ', line)
            line = ' '.join(line.split())
            question = re.findall(r"text:(.*)labels:", line)
            answer = re.findall(r"labels:(.*)episode_done:", line)
            if len(answer) == 0:
                answer = re.findall(r"labels:(.*)question:", line)
            if len(answer) and len(question):
                question = JOIN_TOKEN.join(tokenize(question[0], nlp)[1])
                answer = JOIN_TOKEN.join(tokenize(answer[0], nlp)[1])
                question = question.replace('_ _ SILENCE _ _', '#S#')
                answer = answer.replace('_ _ SILENCE _ _', '#S#')
                arr_len_question.append(len(question.split()))
                arr_len_answer.append(len(answer.split()))

                if append_description:
                    append_description = False
                    data.append(question_line)
                    data.append(question)
                    question_line += delimiter_start
                if context_pair_counter < context_pair_count or context_pair_count == 0:
                    question_line += question + delimiter
                    context_pair_counter += 1
                else:
                    question_line = your_persona_description + delimiter_context_dialogue + delimiter_sep + question
                    context_pair_counter = 0

                data.append(question_line)
                data.append(answer)
                if add_to_valid_data:
                    valid_data += data
                elif add_to_test_data:
                    test_data.append(question)
                    test_data.append(answer)
                else:
                    train_data += data
                question_line = question_line + answer + delimiter
    return train_data, valid_data, test_data


def tokenize(text: string, t):
    tokens = [tok for tok in t.tokenizer(text) if not tok.text.isspace()]
    text_tokens = [tok.text for tok in tokens]
    return tokens, text_tokens


def create_custom_tokenizer(nlp):
    print("Creating custom tokenizer")
    custom_prefixes = [r'[0-9]+', r'\~', r'\–', r'\—', r'\$']
    custom_infixes = [r'[!&:,()]', r'\.', r'\-', r'\–', r'\—', r'\$']
    custom_suffixes = [r'\.', r'\–', r'\—', r'\$']
    default_prefixes = list(nlp.Defaults.prefixes) + custom_prefixes
    default_prefixes.remove(r'US\$')
    default_prefixes.remove(r'C\$')
    default_prefixes.remove(r'A\$')

    all_prefixes_re = spacy.util.compile_prefix_regex(tuple(default_prefixes))
    infix_re = spacy.util.compile_infix_regex(tuple(list(nlp.Defaults.infixes) + custom_infixes))
    suffix_re = spacy.util.compile_suffix_regex(tuple(list(nlp.Defaults.suffixes) + custom_suffixes))

    rules = dict(nlp.Defaults.tokenizer_exceptions)
    # remove "a." to "z." rules so "a." gets tokenized as a|.
    for c in range(ord("a"), ord("z") + 1):
        if f"{chr(c)}." in rules:
            rules.pop(f"{chr(c)}.")

    return Tokenizer(nlp.vocab, rules,
                     prefix_search=all_prefixes_re.search,
                     infix_finditer=infix_re.finditer, suffix_search=suffix_re.search,
                     token_match=None)


nlp = en_core_web_sm.load()
nlp.tokenizer = create_custom_tokenizer(nlp)


def prepare_data():
    print("Prepare data")
    if DATA_TYPE == "PERSONA":
        filename_train = DATA_PATH + 'persona_train.csv'
        filename_valid = DATA_PATH + 'persona_valid.csv'
        filename_test = DATA_PATH + 'persona_test.csv'
        train_data, valid_data, test_data = prepare_Persona_chat((DATA_PATH + 'persona_chat.txt'), CONTEXT_PAIR_COUNT)
    elif DATA_TYPE == "TWITTER":
        filename_train = DATA_PATH + 'twitter_train.csv'
        filename_valid = DATA_PATH + 'twitter_valid.csv'
        filename_test = DATA_PATH + 'twitter_test.csv'
        train_data, valid_data, test_data = prepare_Twitter_data(DATA_PATH + 'twitter_chat.txt')
    elif DATA_TYPE == "PERSONA_BOTH":
        filename_train = DATA_PATH + 'train.csv'
        filename_valid = DATA_PATH + 'valid.csv'
        filename_test = DATA_PATH + 'test.csv'
        train_data, valid_data, test_data = prepare_both_Persona_chat(DATA_PATH + 'persona_chat_both.txt', 0)

    print("train data: ", len(train_data) / 2)
    print("valid data: ", len(valid_data) / 2)
    print("test data: ", len(test_data) / 2)

    process_data_to_json(DATA_PATH + "train.json", train_data)
    process_data_to_json(DATA_PATH + "valid.json", valid_data)
    process_data_to_json(DATA_PATH + "test.json", test_data)

    save_to_csv(filename_train, train_data)
    save_to_csv(filename_valid, valid_data)
    save_to_csv(filename_test, test_data)

    process_data_to_bin(DATA_PATH+"train", train_data)
    process_data_to_bin(DATA_PATH+"valid", valid_data)
    process_data_to_bin(DATA_PATH+"test", test_data)

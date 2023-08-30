import re
from collections import defaultdict
from typing import DefaultDict

import PyPDF2

nouns_dictT = DefaultDict[str, set[tuple[int, bool]]]


def extract_word_from_header(word: str) -> str:
    """
    handles the case HEADER2(Text|text)
    """
    match = re.match(r"\w*\d(\w*)", word)
    if match:
        return match.group(1)

    return ""


def process_page(page: PyPDF2.PageObject, page_num: int, res_dict: nouns_dictT):
    """
    Args:
        page: page to evaluate
        page_num: the number of the page we're currently on
        res_dict: DefaultDict(list) where the findings are added to
    """
    text = page.extract_text()

    words = text.split(" ")
    for i, word in enumerate(words):

        original_word = word

        # clean \n and other things that might dangle there
        word = word.strip()

        # ignore:
        #  empty words,
        #  words that are fully upper case (like roman numerals)
        #  words that are fully lower case
        if not word or word.isupper() or word.islower():
            continue

        # check if word is interesting at all
        if not word[0].isupper():
            if len(word) == 1:
                continue

            # case of something like '(Antonio'
            if word[1].isalpha() and word[1].isupper():
                word = word[1:]
            else:
                continue

        # we can encounter a structure like:
        # HEADER2(Text|text) where header of the page, page number
        #  and start of the actual text are entangled into one word
        if word[0].isupper() and word[1].isupper():
            word = extract_word_from_header(word)
            # if we didn't catch our scheme: continue
            if not word:
                continue

        # check if it is the potential start of a sentence
        potential_sentence_start = False
        if "." in words[i-1]:
            potential_sentence_start = True

        # check if there is some punctuation at the end
        word_before = word
        if not word[-1].isalpha():
            word = word[:-1]

        res_dict[word].add((page_num, potential_sentence_start))


def make_nice_output(data: nouns_dictT,
                     write_result_to="",
                     todo_marker="TODO",
                     page_num_seperator=", ",
                     noun_separator="\n") -> str:
    """
    sort alphabetically and pages ascending and format the output

    Args:
        data: the dict to format
        write_result_to: optional path to a file for the result
        todo_marker: label to sign that a page needs to be checked (default: 'TODO')
        page_num_seperator: seperator between the page numbers (default: ', ')
        noun_separator: seperator between the nouns (default: '\n')

    Returns:
        The formatted string

    example output:
    Chris: 42 (TODO), 69
    Pi: 1, 4, 6
    """
    sorted_nouns = sorted(data.items())

    result = ""
    for noun, occurrences in sorted_nouns:
        occurrences_sorted = sorted(list(occurrences))
        occ_str = page_num_seperator.join(
            f"{page} {f'{todo_marker}' if maybe_sentence else ''}" for page, maybe_sentence in occurrences_sorted
        )

        result += f"{noun}: {occ_str}{noun_separator}"


    if write_result_to:
        with open(write_result_to, "w") as f:
            f.write(result)

        print(f"Result saved under: {write_result_to}")

    return result


def read_and_extract(document_path, write_result_to="", report_to_console=True) -> nouns_dictT:
    """
    Read a pdf, search for Nouns
    Save result to a file or/and report to console

    Args:
        document_path: path to the document to check
        write_result_to: optional path to a file for the result
        report_to_console: True to print to console, False will execute silent

    Returns:
        The dict containing all nouns mapped to the pages they occur on
    """
    # each name mapped to the page-numbers it occurs on
    # each page is only interesting once, so we use a set()
    # the tuple contains the page and if this detection might just be the start of a sentence
    nouns_dict: nouns_dictT = defaultdict(set)

    with open(document_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pages = pdf_reader.pages[11:30]

        # iterate over pages and event their content
        for i, page in enumerate(pages, 1):
            process_page(page, i, nouns_dict)

    res_text = make_nice_output(nouns_dict, write_result_to=write_result_to)

    if report_to_console:
        from pprint import pprint
        legend_str = "\nLegend:\nName: {(page_number, if occurrence should be validated), ...}\n"
        print(legend_str)
        pprint(nouns_dict)
        print(legend_str)

    return nouns_dict


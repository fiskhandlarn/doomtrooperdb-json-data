#!/usr/bin/env python

import argparse
import json
import jsonschema
import os
import sys

CARDS_DIR="cards"
SCHEMA_DIR="schema"
TRANS_DIR="translations"

formatting_errors = 0
validation_errors = 0

unique_card_codes = {}

def check_dir_access(path):
    if not os.path.isdir(path):
        sys.exit("%s is not a valid path" % path)
    elif os.access(path, os.R_OK):
        return
    else:
        sys.exit("%s is not a readable directory")

def check_file_access(path):
    if not os.path.isfile(path):
        sys.exit("%s does not exist" % path)
    elif os.access(path, os.R_OK):
        return
    else:
        sys.exit("%s is not a readable file")

def check_json_schema(args, data, path):
    global validation_errors
    try:
        jsonschema.Draft4Validator.check_schema(data)
        return True
    except jsonschema.exceptions.SchemaError as e:
        verbose_print(args, "%s: Schema file is not valid Draft 4 JSON schema.\n" % path, 0)
        validation_errors += 1
        print(e)
        return False

def custom_card_check(args, card, expansion_code, locale=None):
    "Performs more in-depth sanity checks than jsonschema validator is capable of. Assumes that the basic schema validation has already completed successfully."
    if locale:
        pass #no checks by the moment
    else:
        if card["expansion_code"] != expansion_code:
            raise jsonschema.ValidationError("Expansion code '%s' of the card '%s' doesn't match the expansion code '%s' of the file it appears in." % (card["expansion_code"], card["code"], expansion_code))
        if card["code"] in unique_card_codes:
            raise jsonschema.ValidationError("Card code '%s' of the card '%s' has been used by '%s'." % (card["code"], card["name"], unique_card_codes[card["code"]]["name"]))

def custom_cards_check(args, expansions_data, locale=None):
    if cards["expansion_code"] not in [c["code"] for c in expansions_data]:
        raise jsonschema.ValidationError("Expansion code '%s' doesn't match any valid expansion code." % (cards["expansion_code"]))

def format_json(json_data):
    formatted_data = json.dumps(json_data, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
    formatted_data += "\n"
    return formatted_data

def load_json_file(args, path):
    global formatting_errors
    global validation_errors
    try:
        with open(path, "rb") as data_file:
            bin_data = data_file.read()
        raw_data = bin_data.decode("utf-8")
        json_data = json.loads(raw_data)
    except ValueError as e:
        verbose_print(args, "%s: File is not valid JSON.\n" % path, 0)
        validation_errors += 1
        print(e)
        return None

    verbose_print(args, "%s: Checking JSON formatting...\n" % path, 1)
    formatted_raw_data = format_json(json_data)

    if formatted_raw_data != raw_data:
        verbose_print(args, "%s: File is not correctly formatted JSON.\n" % path, 0)
        formatting_errors += 1
        if args.fix_formatting and len(formatted_raw_data) > 0:
            verbose_print(args, "%s: Fixing JSON formatting...\n" % path, 0)
            try:
                with open(path, "wb") as json_file:
                    bin_formatted_data = formatted_raw_data.encode("utf-8")
                    json_file.write(bin_formatted_data)
            except IOError as e:
                verbose_print(args, "%s: Cannot open file to write.\n" % path, 0)
                print(e)
    return json_data

def load_expansions(args, locale=None):
    verbose_print(args, "Loading expansion index file...\n", 1)
    expansions_base_path = locale and os.path.join(args.trans_path, locale) or args.base_path
    expansions_path = os.path.join(expansions_base_path, "expansions.json")
    expansions_data = load_json_file(args, expansions_path)

    if not validate_expansions(args, expansions_data, locale):
        return None

    return expansions_data

def load_cards_index(args, expansions_data, locale=None):
    verbose_print(args, "Loading cards index file...\n", 1)
    cardss_base_path = locale and os.path.join(args.trans_path, locale) or args.base_path
    cardss_path = os.path.join(cardss_base_path, "cardss.json")

    # if not validate_cardss(args, cardss_data, expansions_data, locale):
    #     return None

    for e in expansions_data:
        cards_filename = "{}.json".format(e["code"])
        cardss_dir = locale and os.path.join(args.trans_path, locale, CARDS_DIR) or args.cards_path
        cards_path = os.path.join(cardss_dir, cards_filename)
        check_file_access(cards_path)

    return cardss_data

def parse_commandline():
    argparser = argparse.ArgumentParser(description="Validate JSON in the netrunner cards repository.")
    argparser.add_argument("-f", "--fix_formatting", default=False, action="store_true", help="write suggested formatting changes to files")
    argparser.add_argument("-v", "--verbose", default=0, action="count", help="verbose mode")
    argparser.add_argument("-b", "--base_path", default=os.getcwd(), help="root directory of JSON repo (default: current directory)")
    argparser.add_argument("-p", "--cards_path", default=None, help=("cards directory of JSON repo (default: BASE_PATH/%s/)" % CARDS_DIR))
    argparser.add_argument("-c", "--schema_path", default=None, help=("schema directory of JSON repo (default: BASE_PATH/%s/" % SCHEMA_DIR))
    argparser.add_argument("-t", "--trans_path", default=None, help=("translations directory of JSON repo (default: BASE_PATH/%s/)" % TRANS_DIR))
    args = argparser.parse_args()

    # Set all the necessary paths and check if they exist
    if getattr(args, "schema_path", None) is None:
        setattr(args, "schema_path", os.path.join(args.base_path,SCHEMA_DIR))
    if getattr(args, "cards_path", None) is None:
        setattr(args, "cards_path", os.path.join(args.base_path,CARDS_DIR))
    if getattr(args, "trans_path", None) is None:
        setattr(args, "trans_path", os.path.join(args.base_path,TRANS_DIR))
    check_dir_access(args.base_path)
    check_dir_access(args.schema_path)
    check_dir_access(args.cards_path)

    return args

def validate_card(args, card, card_schema, expansion_code, locale=None):
    global validation_errors

    try:
        verbose_print(args, "Validating card %s... " % (locale and ("%s-%s" % (card["code"], locale)) or card["name"]), 2)
        jsonschema.validate(card, card_schema)
        custom_card_check(args, card, expansion_code, locale)
        unique_card_codes[card["code"]] = card
        verbose_print(args, "OK\n", 2)
    except jsonschema.ValidationError as e:
        verbose_print(args, "ERROR\n",2)
        verbose_print(args, "Validation error in card: (expansion code: '%s' card code: '%s' name: '%s')\n" % (expansion_code, card.get("code"), card.get("name")), 0)
        validation_errors += 1
        print(e)

def validate_cards(args, expansions_data, locale=None):
    global validation_errors

    card_schema_path = os.path.join(args.schema_path, locale and "card_schema_trans.json" or "card_schema.json")

    CARD_SCHEMA = load_json_file(args, card_schema_path)
    if not CARD_SCHEMA:
        return
    if not check_json_schema(args, CARD_SCHEMA, card_schema_path):
        return

    for e in expansions_data:
        verbose_print(args, "Validating cards from %s...\n" % (locale and "%s-%s" % (e["code"], locale) or e["name"]), 1)

        cards_base_path = locale and os.path.join(args.trans_path, locale, CARDS_DIR) or args.cards_path
        cards_path = os.path.join(cards_base_path, "{}.json".format(e["code"]))
        cards_data = load_json_file(args, cards_path)
        if not cards_data:
            continue

        for card in cards_data:
            validate_card(args, card, CARD_SCHEMA, e["code"], locale)

def validate_expansions(args, expansions_data, locale=None):
    global validation_errors

    verbose_print(args, "Validating expansion index file...\n", 1)
    expansion_schema_path = os.path.join(args.schema_path, locale and "expansion_schema_trans.json" or "expansion_schema.json")
    EXPANSION_SCHEMA = load_json_file(args, expansion_schema_path)
    if not isinstance(expansions_data, list):
        verbose_print(args, "Insides of expansion index file are not a list!\n", 0)
        return False
    if not EXPANSION_SCHEMA:
        return False
    if not check_json_schema(args, EXPANSION_SCHEMA, expansion_schema_path):
        return False

    retval = True
    for c in expansions_data:
        try:
            verbose_print(args, "Validating expansion %s... " % c.get("name"), 2)
            jsonschema.validate(c, EXPANSION_SCHEMA)
            verbose_print(args, "OK\n", 2)
        except jsonschema.ValidationError as e:
            verbose_print(args, "ERROR\n",2)
            verbose_print(args, "Validation error in expansion: (code: '%s' name: '%s')\n" % (c.get("code"), c.get("name")), 0)
            validation_errors += 1
            print(e)
            retval = False

    return retval

def validate_locales(args, en_expansions):
    verbose_print(args, "Validating I18N files...\n", 1)
    if os.path.exists(args.trans_path):
        check_dir_access(args.trans_path)
        for locale in [l for l in os.listdir(args.trans_path) if os.path.isdir(os.path.join(args.trans_path, l))]:
            verbose_print(args, "Validating I18N files for locale '%s'...\n" % locale, 1)

            expansions = load_expansions(args, locale)

            if expansions:
                validate_cards(args, expansions, locale)
            else:
                verbose_print(args, "Couldn't open expansions file correctly, skipping card validation...\n", 0)


def verbose_print(args, text, minimum_verbosity=0):
    if args.verbose >= minimum_verbosity:
        sys.stdout.write(text)

def main():
    # Initialize global counters for encountered validation errors
    global formatting_errors
    global validation_errors
    formatting_errors = 0
    validation_errors = 0

    args = parse_commandline()

    expansions = load_expansions(args)

    if expansions:
        validate_cards(args, expansions)
        validate_locales(args, expansions)
    else:
        verbose_print(args, "Couldn't open expansionss file correctly, skipping card validation...\n", 0)

    sys.stdout.write("Found %s formatting and %s validation errors\n" % (formatting_errors, validation_errors))
    if formatting_errors == 0 and validation_errors == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

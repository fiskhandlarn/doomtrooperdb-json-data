DoomtrooperDB cards JSON data [![Build status](https://travis-ci.org/Alsciende/thronesdb-json-data.svg?branch=master)](https://travis-ci.org/Alsciende/thronesdb-json-data)
=========

The goal of this repository is to store [DoomtrooperDB](https://doomtrooperdb.org) card data in a format that can be easily updated by multiple people and their changes reviewed.

## Validating and formatting JSON

Using python >=2.6, type in command line:

```
./validate.py --verbose --fix_formatting
```

The above script requires python package `jsonschema` which can be installed using `pip` via `pip install -U jsonschema`.

You can also just try to follow the style existing files use when editing entries. They are all formatted and checked using the script above.

## Description of properties in schemas

Required properties are in **bold**.

#### Expansion schema

* **code** - identifier of the expansion. One single lowercase word. Examples: `"base"`, `"inq"`, `"wz"`.
* **name** - properly formatted name of the expansion. Examples: `"Base Set"`, `"Inquisition"`, `"Warzone"`.
* **size** - number of cards in the expansion.

#### Card schema

* claim - Plots only
* **code** - 5 digit card identifier. Consists of two zero-padded numbers: first two digits are the expansion position, last three are position of the card within the expansion (printed on the card).
* cost - Play cost of the card. Relevant for all cards except agendas and titles. May be `null` - this value is used when the card has a special, possibly variable, cost.
* **deck_limit**
* **faction_code**
* flavor
* illustrator
* income - Plots only
* initiative - Plots only
* is_intrigue - Characters only
* **is_loyal**
* is_military - Characters only
* is_power - Characters only
* **is_unique**
* **name**
* octgn_id
* **expansion_code**
* **position**
* **quantity**
* reserve - Plots only
* strength - Characters only
* text
* traits
* **type_code** - Type of the card. Possible values: `"agenda"`, `"attachment"`, `"character"`, `"event"`, `"location"`, `"plot"`, `"title"`

## JSON text editing tips

Full description of (very simple) JSON format can be found [here](http://www.json.org/), below there are a few tips most relevant to editing this repository.

#### Non-ASCII symbols

When symbols outside the regular [ASCII range](https://en.wikipedia.org/wiki/ASCII#ASCII_printable_code_chart) are needed, UTF-8 symbols come in play. These need to be escaped using `\u<4 letter hexcode>`.

To get the 4-letter hexcode of a UTF-8 symbol (or look up what a particular hexcode represents), you can use a UTF-8 converter, such as [this online tool](http://www.ltg.ed.ac.uk/~richard/utf-8.cgi).

#### Quotes and breaking text into multiple lines

To have text spanning multiple lines, use `\n` to separate them. To have quotes as part of the text, use `\"`.  For example, `"flavor": "\"Winter is Coming.\"\n-Cardinal Durand"` results in following flavor text:

> *"The Darkness is upon Us, Have Faith."*
> *-Cardinal Durand*

#### Translations

To merge new changes in default language in all locales, run the CoffeeScript script `update_locales`.

Pre-requisites:
 * `node` and `npm` installed
 * `npm -g install coffee-script`

Usage: `coffee update_locales.coffee`

#!/usr/bin/env python

import argparse
import json
import logging
import gzip


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="Path to Wikidata JSON dump.")
    parser.add_argument("--output", required=True,
                        help="Path to output JSON file.")
    parser.add_argument("--language", required=True,
                        help="Language to extract.")
    return vars(parser.parse_args())


def main(arguments):
    _init_logging()
    extract_hierarchy(
        arguments["input"], arguments["output"], arguments["language"])


def _init_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S")


def extract_hierarchy(
        source_file: str, output_file: str, language: str) -> None:
    with open(output_file, "w", encoding="utf-8") as stream:
        for content in _iterate_wikidata(source_file):
            result = _wikidata_to_entity(content, language)
            if result is None:
                continue
            json.dump(result, stream, ensure_ascii=False)
            stream.write("\n")


def _iterate_wikidata(input_file: str):
    with open_file(input_file) as stream:
        # Skip first line '['
        next(stream)
        for line in stream:
            if line.startswith(']'):
                break
            line = line.rstrip()
            if line.endswith(","):
                line = line[:-1]
            yield json.loads(line)


def open_file(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    else:
        return open(path, "r", encoding="utf-8")


def _wikidata_to_entity(wikidata, language: str):
    result = {
        "@id": wikidata["id"],
    }
    data_available = False
    label = _collect_strings(wikidata.get("labels", None), language)
    if label is not None and len(label) > 0:
        result["label"] = label
        data_available = True
    aliases = _collect_strings(wikidata.get("aliases", None), language)
    if aliases is not None and len(aliases) > 0:
        result["aliases"] = aliases
        data_available = True
    return result if data_available else None


def _collect_strings(values, language: str):
    if values is None:
        return None
    values_in_language = values.get(language, [])
    # For example labels are single values while aliases are arrays.
    if not isinstance(values_in_language, list):
        values_in_language = [values_in_language]
    return [
        item["value"]
        for item in values_in_language
        if item["language"] == language
    ]


if __name__ == "__main__":
    main(_parse_arguments())

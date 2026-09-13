#This is the Python script utilized to pull the NAEP Math and Reading composite scores for 4th, 8th, and 12th grade and their respective subgrooups.

import csv
import logging
import time
import requests

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("naep_pull.log"), logging.StreamHandler()],
)

URL = "https://www.nationsreportcard.gov/Dataservice/GetAdhocData.aspx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

NAEP_YEARS = [2009, 2011, 2013, 2015, 2017, 2019, 2022, 2024]

# Exact Composite Subscale Mapping
SUBJECT_CONFIG = {
    "mathematics": {
        "4": "MRPCM",
        "8": "MRPCM",
    },
    "reading": {
        "4": "RRPCM",
        "8": "RRPCM",
    },
}

# Subgroups mapped to exact API documentation variables
SUBGROUPS = {
    "All": {"variable": "TOTAL", "subvariable": "TOTAL"},
    "Black": {"variable": "SDRACE", "subvariable": "2"},
    "White": {"variable": "SDRACE", "subvariable": "1"},
    "Hispanic": {"variable": "SDRACE", "subvariable": "3"},
    "Economically Disadvantaged": {"variable": "SLUNCH3", "subvariable": "1"},
    "English Language Learners": {"variable": "LEP", "subvariable": "1"},
    "SPED": {"variable": "IEP", "subvariable": "1"},
}

# StatTypes per Documentation
STAT_TYPES = {"Mean": "MN:MN", "Median": "PC:P5"}

# National + States Jurisdictions List
JURISDICTIONS = [
    "NT",
    "NP",
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]


def fetch_naep_score(
    year, state, subject, grade, subscale, var_name, subvar_name, stattype
):
    """Executes a single API query against NAEP GetAdhocData endpoint."""
    params = {
        "type": "data",
        "subject": subject,
        "grade": str(grade),
        "subscale": subscale,
        "variable": var_name,
        "jurisdiction": state,
        "stattype": stattype,
        "year": str(year),
    }

    if var_name != "TOTAL":
        params["subvariable"] = subvar_name

    try:
        res = requests.get(URL, params=params, headers=HEADERS, timeout=12)
        if res.status_code == 200:
            payload = res.json()
            if "result" in payload and len(payload["result"]) > 0:
                val = payload["result"][0].get("value", "N/A")
                try:
                    return f"{float(val):.2f}"
                except (ValueError, TypeError):
                    return "N/A"
        return "N/A"
    except Exception as err:
        logging.error(
            f"Error querying {state} {year} {subject} G{grade} ({var_name}={subvar_name}): {err}"
        )
        return "ERROR"


def main():
    logging.info("Starting NAEP Multi-Year Data Extraction with Updated Variables...")

    for year in NAEP_YEARS:
        filename = f"naep_summary_{year}.csv"
        logging.info(f"--- Extracting Year: {year} -> Output File: {filename} ---")

        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Year", "State", "Subject", "Grade", "Subgroup", "Mean", "Median"]
            )

            for subject, grade_dict in SUBJECT_CONFIG.items():
                for grade, subscale in grade_dict.items():
                    for subgroup_label, sub_info in SUBGROUPS.items():
                        var_name = sub_info["variable"]
                        subvar_name = sub_info["subvariable"]

                        for state in JURISDICTIONS:
                            mean_score = fetch_naep_score(
                                year,
                                state,
                                subject,
                                grade,
                                subscale,
                                var_name,
                                subvar_name,
                                STAT_TYPES["Mean"],
                            )
                            time.sleep(0.05)

                            median_score = fetch_naep_score(
                                year,
                                state,
                                subject,
                                grade,
                                subscale,
                                var_name,
                                subvar_name,
                                STAT_TYPES["Median"],
                            )
                            time.sleep(0.05)

                            writer.writerow(
                                [
                                    year,
                                    state,
                                    subject.capitalize(),
                                    grade,
                                    subgroup_label,
                                    mean_score,
                                    median_score,
                                ]
                            )

                        logging.info(
                            f"Completed: Year {year} | {subject.capitalize()} Grade {grade} | Subgroup: {subgroup_label}"
                        )

    logging.info("All NAEP Data Pulls Completed Successfully.")


if __name__ == "__main__":
    main()

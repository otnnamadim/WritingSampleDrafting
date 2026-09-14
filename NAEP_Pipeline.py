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

NAEP_YEARS = [2013, 2015, 2017, 2019, 2022, 2024]

# Subjects and Composite Subscales
SUBJECT_CONFIG = {
    "mathematics": {"4": "MRPCM", "8": "MRPCM"},
    "reading": {"4": "RRPCM", "8": "RRPCM"},
}

# Variable and categoryindex Mapping
SUBGROUPS = {
    "All": {"variable": "TOTAL", "categoryindex": None},
    "White": {"variable": "SRACE10", "categoryindex": "1"},  # Dynamically routed to SDRACE for 2009
    "Black": {"variable": "SRACE10", "categoryindex": "2"},  # Dynamically routed to SDRACE for 2009
    "Hispanic": {"variable": "SRACE10", "categoryindex": "3"},  # Dynamically routed to SDRACE for 2009
    "Economically Disadvantaged": {"variable": "SLUNCH3", "categoryindex": "1"},
    "English Language Learners": {"variable": "LEP", "categoryindex": "1"},
    "SPED": {"variable": "IEP", "categoryindex": "1"},
}

STAT_TYPES = {"Mean": "MN:MN", "Median": "PC:P5", "Count": "N:N"}

# National + State Level Jurisdictions
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
    year, state, subject, grade, subscale, var_name, category_idx, stattype
):
    """Executes single query against GetAdhocData.aspx using categoryindex."""
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

    # Pass categoryindex for non-TOTAL subcategories
    if var_name != "TOTAL" and category_idx:
        params["categoryindex"] = str(category_idx)

    try:
        res = requests.get(URL, params=params, headers=HEADERS, timeout=12)
        if res.status_code == 200:
            payload = res.json()
            results = payload.get("result", [])

            if len(results) > 0:
                val = results[0].get("value", "N/A")
                try:
                    if stattype == "N:N":
                        return str(int(float(val)))
                    return f"{float(val):.2f}"
                except (ValueError, TypeError):
                    return "N/A"
        return "N/A"
    except Exception as err:
        logging.error(
            f"Error querying {state} {year} {subject} G{grade} ({var_name}={category_idx}): {err}"
        )
        return "ERROR"


def main():
    logging.info(
        "Starting NAEP Panel Data Extraction (Mean, Median, Sample Size)..."
    )

    for year in NAEP_YEARS:
        filename = f"naep_summary_{year}.csv"
        logging.info(f"--- Extracting Year: {year} -> Output File: {filename} ---")

        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Year",
                    "State",
                    "Subject",
                    "Grade",
                    "Subgroup",
                    "Mean",
                    "Median",
                    "Sample_Size",
                ]
            )

            for subject, grade_dict in SUBJECT_CONFIG.items():
                for grade, subscale in grade_dict.items():
                    for subgroup_label, sub_info in SUBGROUPS.items():
                        category_idx = sub_info["categoryindex"]

                        # Dynamic variable swap for pre-2011 race standards
                        if subgroup_label in ["White", "Black", "Hispanic"]:
                            v_name = "SDRACE" if year == 2009 else "SRACE10"
                        else:
                            v_name = sub_info["variable"]

                        for state in JURISDICTIONS:
                            mean_score = fetch_naep_score(
                                year,
                                state,
                                subject,
                                grade,
                                subscale,
                                v_name,
                                category_idx,
                                STAT_TYPES["Mean"],
                            )
                            time.sleep(0.02)

                            median_score = fetch_naep_score(
                                year,
                                state,
                                subject,
                                grade,
                                subscale,
                                v_name,
                                category_idx,
                                STAT_TYPES["Median"],
                            )
                            time.sleep(0.02)

                            sample_size = fetch_naep_score(
                                year,
                                state,
                                subject,
                                grade,
                                subscale,
                                v_name,
                                category_idx,
                                STAT_TYPES["Count"],
                            )
                            time.sleep(0.02)

                            writer.writerow(
                                [
                                    year,
                                    state,
                                    subject.capitalize(),
                                    grade,
                                    subgroup_label,
                                    mean_score,
                                    median_score,
                                    sample_size,
                                ]
                            )

                        logging.info(
                            f"Completed: Year {year} | {subject.capitalize()} Grade {grade} | Subgroup: {subgroup_label}"
                        )

    logging.info("NAEP Panel Data Extraction Completed Successfully.")


if __name__ == "__main__":
    main()

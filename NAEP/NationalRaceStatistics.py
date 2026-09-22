# The purpose of this program is to pull the National statistics for each racial demographic for both NAEP Math and Reading at the 4th and 8th Grade level.

import csv
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("naep_pull.log"),
        logging.StreamHandler(),
    ],
)

# Setup session with automated retries and connection resilience
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False,
)
session.mount("https://", HTTPAdapter(max_retries=retries))

# NAEP API Configuration
URL = "https://www.nationsreportcard.gov/Dataservice/GetAdhocData.aspx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}

# ============================================================
# Assessment Years
# ============================================================

NAEP_YEARS = [
    2009, 2011, 2013, 2015, 2017, 2019, 2022, 2024
]

# ============================================================
# Subjects and Composite Subscales
# ============================================================

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

# ============================================================
# Race / Ethnicity Configuration
# ============================================================

SUBGROUPS = {
    "All": {
        "variable": "TOTAL",
        "categoryindex": None,
    },

    "White": {
        "variable": "SDRACE",
        "categoryindex": "1",
    },

    "Black": {
        "variable": "SDRACE",
        "categoryindex": "2",
    },

    "Hispanic": {
        "variable": "SDRACE",
        "categoryindex": "3",
    },

    "Asian": {
        "variable": "SDRACE",
        "categoryindex": "4",
    },

    "American Indian or Alaskan Native": {
        "variable": "SDRACE",
        "categoryindex": "5",
    },

    "Hawaiian": {
        "variable": "SDRACE",
        "categoryindex": "6",
    },

    "Multiracial": {
        "variable": "SDRACE",
        "categoryindex": "7",
    },
}

# ============================================================
# Statistic and Jurisdiction Configuration
# ============================================================

STAT_TYPES = {
    "Mean": "MN:MN",
    "25th Percentile": "PC:P2",
    "50th Percentile": "PC:P5",
    "75th Percentile": "PC:P7",
    "Standard Deviation": "SD:SD",
    "Discrete achievement level – At Basic": "ALD:BA",
    "Discrete achievement level – At Proficient": "ALD:PR",
    "Discrete achievement level – At Advanced": "ALD:AD",
    "Cumulative achievement level  - Below Basic": "ALC:BB",
    "Cumulative achievement level  - At or above Basic": "ALC:AB",
    "Cumulative achievement level  - At or above Proficient": "ALC:AP",
    "Cumulative achievement level  - At Advanced": "ALC:AD"
}

# NT = National Public + Private combined
JURISDICTIONS = [
    "NT"
]


# ============================================================
# NAEP API Query Function
# ============================================================

def fetch_naep_score(
        year,
        jurisdiction,
        subject,
        grade,
        subscale,
        variable,
        category_idx,
        stattype,
):
    """
    Execute a single query against the NAEP API using the persistent HTTP session.
    """

    params = {
        "type": "data",
        "subject": subject,
        "grade": str(grade),
        "subscale": subscale,
        "variable": variable,
        "jurisdiction": jurisdiction,
        "stattype": stattype,
        "year": str(year),
    }

    if variable != "TOTAL" and category_idx is not None:
        params["categoryindex"] = str(category_idx)

    try:
        response = session.get(
            URL,
            params=params,
            headers=HEADERS,
            timeout=12,
        )

        if response.status_code == 200:
            try:
                payload = response.json()
            except requests.exceptions.JSONDecodeError:
                logging.warning(
                    f"Response returned non-JSON/HTML for query: {params}"
                )
                return "N/A"

            results = payload.get("result", [])

            if len(results) > 0:
                value = results[0].get("value", "N/A")
                try:
                    return f"{float(value):.2f}"
                except (ValueError, TypeError):
                    return "N/A"

        logging.warning(
            f"No valid result (HTTP {response.status_code}): "
            f"{jurisdiction} | {year} | {subject} | Grade {grade} | {variable} | Category {category_idx}"
        )

        return "N/A"

    except Exception as err:
        logging.error(
            f"Error querying {jurisdiction} | {year} | {subject} | "
            f"Grade {grade} | {variable} | Category {category_idx}: {err}"
        )
        return "ERROR"


# ============================================================
# Main Extraction
# ============================================================

def main():
    output_filename = "National_Statistics_Achievement_Levels.csv"

    logging.info(
        f"Starting NAEP National Data Extraction -> Output File: {output_filename}"
    )

    with open(
            output_filename,
            mode="w",
            newline="",
            encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        # Output Columns
        writer.writerow(
            [
                "Year",
                "Jurisdiction",
                "Subject",
                "Grade",
                "Subgroup",
                "Mean",
                "25th Percentile",
                "50th Percentile",
                "75th Percentile",
                "Standard Deviation",
                "Discrete achievement level – At Basic",
                "Discrete achievement level – At Proficient",
                "Discrete achievement level – At Advanced",
                "Cumulative achievement level  - Below Basic",
                "Cumulative achievement level  - At or above Basic",
                "Cumulative achievement level  - At or above Proficient",
                "Cumulative achievement level  - At Advanced"
            ]
        )

        for year in NAEP_YEARS:
            logging.info(f"Processing Year: {year}")

            for subject, grade_dict in SUBJECT_CONFIG.items():
                for grade, subscale in grade_dict.items():
                    for subgroup_label, sub_info in SUBGROUPS.items():

                        variable_name = sub_info["variable"]
                        category_idx = sub_info["categoryindex"]

                        if (
                                year == 2015
                                and subgroup_label in ["White", "Black", "Hispanic"]
                        ):
                            variable_name = "SDRACE"

                        for jurisdiction in JURISDICTIONS:
                            mean_score = fetch_naep_score(
                                year=year,
                                jurisdiction=jurisdiction,
                                subject=subject,
                                grade=grade,
                                subscale=subscale,
                                variable=variable_name,
                                category_idx=category_idx,
                                stattype=STAT_TYPES["Mean"],
                            )

                            p25_score = fetch_naep_score(
                                year=year,
                                jurisdiction=jurisdiction,
                                subject=subject,
                                grade=grade,
                                subscale=subscale,
                                variable=variable_name,
                                category_idx=category_idx,
                                stattype=STAT_TYPES["25th Percentile"],
                            )

                            p50_score = fetch_naep_score(
                                year=year,
                                jurisdiction=jurisdiction,
                                subject=subject,
                                grade=grade,
                                subscale=subscale,
                                variable=variable_name,
                                category_idx=category_idx,
                                stattype=STAT_TYPES["50th Percentile"],
                            )

                            p75_score = fetch_naep_score(
                                year=year,
                                jurisdiction=jurisdiction,
                                subject=subject,
                                grade=grade,
                                subscale=subscale,
                                variable=variable_name,
                                category_idx=category_idx,
                                stattype=STAT_TYPES["75th Percentile"],
                            )

                            sd_score = fetch_naep_score(
                                year=year,
                                jurisdiction=jurisdiction,
                                subject=subject,
                                grade=grade,
                                subscale=subscale,
                                variable=variable_name,
                                category_idx=category_idx,
                                stattype=STAT_TYPES["Standard Deviation"],
                            )

                            cum_below_basic = fetch_naep_score(
                                year=year,
                                jurisdiction=jurisdiction,
                                subject=subject,
                                grade=grade,
                                subscale=subscale,
                                variable=variable_name,
                                category_idx=category_idx,
                                stattype=STAT_TYPES["Cumulative achievement level  - Below Basic"],
                            )

                            disc_at_basic = fetch_naep_score(
                                year=year,
                                jurisdiction=jurisdiction,
                                subject=subject,
                                grade=grade,
                                subscale=subscale,
                                variable=variable_name,
                                category_idx=category_idx,
                                stattype=STAT_TYPES["Discrete achievement level – At Basic"],
                            )

                        cum_above_basic = fetch_naep_score(
                            year=year,
                            jurisdiction=jurisdiction,
                            subject=subject,
                            grade=grade,
                            subscale=subscale,
                            variable=variable_name,
                            category_idx=category_idx,
                            stattype=STAT_TYPES["Cumulative achievement level  - At or above Basic"],
                        )

                        disc_proficient = fetch_naep_score(
                            year=year,
                            jurisdiction=jurisdiction,
                            subject=subject,
                            grade=grade,
                            subscale=subscale,
                            variable=variable_name,
                            category_idx=category_idx,
                            stattype=STAT_TYPES["Discrete achievement level – At Proficient"],
                        )

                        cum_proficient = fetch_naep_score(
                            year=year,
                            jurisdiction=jurisdiction,
                            subject=subject,
                            grade=grade,
                            subscale=subscale,
                            variable=variable_name,
                            category_idx=category_idx,
                            stattype=STAT_TYPES["Cumulative achievement level  - At or above Proficient"],
                        )

                        disc_advanced = fetch_naep_score(
                            year=year,
                            jurisdiction=jurisdiction,
                            subject=subject,
                            grade=grade,
                            subscale=subscale,
                            variable=variable_name,
                            category_idx=category_idx,
                            stattype=STAT_TYPES["Discrete achievement level – At Advanced"],
                        )

                        cum_advanced = fetch_naep_score(
                            year=year,
                            jurisdiction=jurisdiction,
                            subject=subject,
                            grade=grade,
                            subscale=subscale,
                            variable=variable_name,
                            category_idx=category_idx,
                            stattype=STAT_TYPES["Cumulative achievement level  - At Advanced"],
                        )

                        # Write row containing all requested metrics
                        writer.writerow(
                            [
                                year,
                                jurisdiction,
                                subject.capitalize(),
                                grade,
                                subgroup_label,
                                mean_score,
                                p25_score,
                                p50_score,
                                p75_score,
                                sd_score,
                                cum_below_basic,
                                disc_at_basic,
                                cum_above_basic,
                                disc_proficient,
                                cum_proficient,
                                disc_advanced,
                                cum_advanced,
                            ]
                        )

                        logging.info(
                            f"Completed: {year} | {jurisdiction} | "
                            f"{subject.capitalize()} | Grade {grade} | "
                            f"{subgroup_label} | Mean={mean_score}, P50={p50_score}, SD={sd_score}, BLBC={cum_below_basic}, ATBC={disc_at_basic}, ABVBC={cum_above_basic}, PF={disc_proficient}, ABVPF={cum_proficient}, ADV={disc_advanced}, ADVABV={cum_advanced}",
                        )

                        time.sleep(0.05)


logging.info("NAEP National Data Extraction Completed Successfully.")

if __name__ == "__main__":
    main()

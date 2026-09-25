import csv
import logging
import time
import requests


# ============================================================
# Setup Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("naep_pull_econ_disadv.log"),
        logging.StreamHandler(),
    ],
)


# ============================================================
# NAEP API Configuration
# ============================================================

URL = "https://www.nationsreportcard.gov/Dataservice/GetAdhocData.aspx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


# ============================================================
# Assessment Years
# ============================================================

NAEP_YEARS = [
    2009,
    2011,
    2013,
    2015,
    2017,
    2019,
    2022,
    2024,
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
# Economically Disadvantaged Definitions
#
# ECONDIS:
#   1 = Eligible (Economically Disadvantaged)
#   2 = Not eligible (Not Economically Disadvantaged)
#   3 = Information not available
#
# Category 3 is intentionally excluded from the analysis.
# ============================================================

SUBGROUPS = {
    "Economically Disadvantaged": {
        "variable": "ECONDIS",
        "categoryindex": "1",
    },
    "Not Economically Disadvantaged": {
        "variable": "ECONDIS",
        "categoryindex": "2",
    },
}


# ============================================================
# Statistics and Jurisdiction
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

JURISDICTIONS = [
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
    Execute a single query against the NAEP API.
    Returns the reported mean score.
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
        response = requests.get(
            URL,
            params=params,
            headers=HEADERS,
            timeout=12,
        )

        if response.status_code == 200:

            payload = response.json()
            results = payload.get("result", [])

            if len(results) > 0:

                value = results[0].get("value", "N/A")

                try:
                    return f"{float(value):.2f}"

                except (ValueError, TypeError):
                    return "N/A"

        logging.warning(
            f"No valid result: "
            f"{jurisdiction} | {year} | {subject} | Grade {grade} | "
            f"{variable} | Category {category_idx}"
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

    output_filename = "naep_national_averages_EconDisadv_by_State_2009_2024.csv"

    logging.info(
        f"Starting NAEP National Data Extraction -> "
        f"Output File: {output_filename}"
    )

    with open(
        output_filename,
        mode="w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
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
        ])

        for year in NAEP_YEARS:

            logging.info(f"Processing Year: {year}")

            for subject, grade_dict in SUBJECT_CONFIG.items():

                for grade, subscale in grade_dict.items():

                    for subgroup_label, subgroup_config in SUBGROUPS.items():

                        variable_name = subgroup_config["variable"]
                        category_idx = subgroup_config["categoryindex"]

                        for jurisdiction in JURISDICTIONS:
                            mean_score = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES["Mean"],
                            )

                            p25_score = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES["25th Percentile"],
                            )

                            p50_score = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES["50th Percentile"],
                            )

                            p75_score = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES["75th Percentile"],
                            )

                            sd_score = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES["Standard Deviation"],
                            )

                            cum_below_basic = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES[
                                    "Cumulative achievement level  - Below Basic"
                                ],
                            )

                            disc_at_basic = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES[
                                    "Discrete achievement level – At Basic"
                                ],
                            )

                            cum_above_basic = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES[
                                    "Cumulative achievement level  - At or above Basic"
                                ],
                            )

                            disc_proficient = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES[
                                    "Discrete achievement level – At Proficient"
                                ],
                            )

                            cum_proficient = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES[
                                    "Cumulative achievement level  - At or above Proficient"
                                ],
                            )

                            disc_advanced = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES[
                                    "Discrete achievement level – At Advanced"
                                ],
                            )

                            cum_advanced = fetch_naep_score(
                                year,
                                jurisdiction,
                                subject,
                                grade,
                                subscale,
                                variable_name,
                                category_idx,
                                STAT_TYPES[
                                    "Cumulative achievement level  - At Advanced"
                                ],
                            )

                            writer.writerow([
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
                            ])

                            logging.info(
                                f"Completed: {year} | {jurisdiction} | "
                                f"{subject.capitalize()} | Grade {grade} | "
                                f"{subgroup_label} | "
                                f"ECONDIS Category {category_idx} | "
                                f"Mean = {mean_score}"
                            )

                            time.sleep(0.05)

    logging.info(
        "NAEP National Data Extraction Completed Successfully."
    )


# ============================================================
# Run Script
# ============================================================

if __name__ == "__main__":
    main()

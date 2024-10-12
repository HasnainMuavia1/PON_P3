# # genomic_conversion.py
# import requests
# import pandas as pd
# import re
# import time
#
#
# def fetch_cdna_info(genomics_id):
#     """Fetch cDNA to gene information for a given transcript from the API."""
#     base_url = "https://mtb.bioinf.med.uni-goettingen.de/CCS/v1/GenomicToGene/hg38/"
#     full_url = f'{base_url}{genomics_id}'
#
#     try:
#         response = requests.get(full_url)  # Perform a GET request to the API
#         if response.status_code == 200:  # Check if the request was successful
#             output_data = response.json()  # Parse the JSON output
#             return output_data
#         else:
#             print(f"HTTP Error {response.status_code}: {response.text}")
#             return None
#     except requests.exceptions.RequestException as e:
#         print(f"Request error: {e}")
#         return None
#
#
# def extract_np_reference(variant_p):
#     """Extract the NP reference protein ID with version from the 'variant_p' string."""
#     if variant_p:
#         match = re.search(r'(NP_\d+\.\d+)', variant_p)  # Regex to find NP reference IDs with version
#         if match:
#             return match.group(0)  # Return the matched NP reference ID with version
#         else:
#             print(f"No NP reference found in variant_p: {variant_p}")
#             return None
#     else:
#         print("variant_p is None or empty.")
#         return None
#
#
# def convert_genomics_to_variations(genomics):
#     """Convert a list of genomic variation to protein variations."""
#     all_results = []  # List to store results
#
#     for genomic_input in genomics:
#         output = fetch_cdna_info(genomic_input)  # Fetch and parse the cDNA to gene info
#
#         if output:
#             # Check if output has expected structure
#             if isinstance(output, list) and len(output) > 0:
#                 try:
#                     data = output[0].get('data', None)
#
#                     # Check if data is None before accessing its keys
#                     if data is not None:
#                         variant_p = data.get('variant')  # Get the Variant P data
#                         result = {"Input_Genomic_variation": genomic_input,
#                                   "refseq_ids": extract_np_reference(variant_p),
#                                   "variation_ids": data.get('variant_exchange')}
#                         all_results.append(result)
#
#                     else:
#                         print(f"No data found for genomic variation {genomic_input}. Output: {output}")
#                         result = {"Input_Genomic_variation": genomic_input,
#                                   "refseq_ids": None,
#                                   "variation_ids": None}
#                         all_results.append(result)
#
#                 except (KeyError, IndexError) as e:
#                     print(f"Error parsing output for genomic variation {genomic_input}: {e}")
#             else:
#                 print(f"Unexpected output format for genomic variation {genomic_input}: {output}")
#         else:
#             print(f"No output for transcript {genomic_input}.")
#
#         time.sleep(1)  # Optional: Add a delay to avoid overwhelming the server
#
#     return all_results


import pandas as pd
import requests
import re
import time


def fetch_cdna_info(genomics_ids):
    """Fetch cDNA to gene information for a list of genomic variations in one request."""
    base_url = "https://mtb.bioinf.med.uni-goettingen.de/CCS/v1/GenomicToGene/hg38/"

    # Join the genomic IDs into a single string, comma-separated
    combined_ids = ','.join(genomics_ids)
    full_url = f'{base_url}{combined_ids}'

    try:
        response = requests.get(full_url)  # Perform a GET request to the API
        if response.status_code == 200:  # Check if the request was successful
            output_data = response.json()  # Parse the JSON output
            return output_data
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def extract_np_reference(variant_p):
    """Extract the NP reference protein ID with version from the 'variant_p' string."""
    if variant_p:
        match = re.search(r'(NP_\d+\.\d+)', variant_p)  # Regex to find NP reference IDs with version
        if match:
            return match.group(0)  # Return the matched NP reference ID with version
    return None


def convert_genomics_to_variations(genomics_data):
    """Convert a list of genomic variations to protein variations."""
    all_results = []  # List to store all results

    chunk_size = 100  # Adjust as necessary based on API limits or server behavior
    for i in range(0, len(genomics_data), chunk_size):
        genomics_chunk = genomics_data[i:i + chunk_size]
        output = fetch_cdna_info(genomics_chunk)  # Fetch and parse the cDNA to gene info

        if output:
            # Check if output has the expected structure
            if isinstance(output, list) and len(output) > 0:
                for idx, entry in enumerate(output):
                    genomic_input = genomics_chunk[idx] if idx < len(genomics_chunk) else None
                    data = entry.get('data', None)

                    if data is not None:
                        variant_p = data.get('variant')  # Get the Variant P data
                        result = {
                            "genomic_variation": genomic_input,
                            "refseq_ids": extract_np_reference(variant_p),
                            "variation_ids": data.get('variant_exchange')
                        }
                    else:
                        # If data is missing, append with None values
                        result = {
                            "genomic_variation": genomic_input,
                            "refseq_ids": None,
                            "variation_ids": None
                        }
                    all_results.append(result)
            else:
                # If output structure is unexpected, append genomic input with None values
                for genomic_input in genomics_chunk:
                    result = {
                        "genomic_variation": genomic_input,
                        "refseq_ids": None,
                        "variation_ids": None
                    }
                    all_results.append(result)
        else:
            # If no output for the chunk, append genomic inputs with None values
            for genomic_input in genomics_chunk:
                result = {
                    "genomic_variation": genomic_input,
                    "refseq_ids": None,
                    "variation_ids": None
                }
                all_results.append(result)

        time.sleep(1)  # Optional: Add a delay to avoid overwhelming the server
    print("Genomic",all_results)
    return all_results

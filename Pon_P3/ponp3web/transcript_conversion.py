import requests
import pandas as pd
import re
import time


def fetch_cdna_info(transcripts):
    """Fetch cDNA to gene information for a list of transcripts in one request."""
    base_url = "https://mtb.bioinf.med.uni-goettingen.de/CCS/v1/cdnaToGene/hg38/"

    # Join transcripts into a single string with commas separating them
    combined_transcripts = ','.join(transcripts)
    full_url = f'{base_url}{combined_transcripts}'

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
        else:
            print(f"No NP reference found in variant_p: {variant_p}")
            return None
    else:
        print("variant_p is None or empty.")
        return None


def convert_transcripts_to_variations(transcripts):
    """Convert a list of transcripts to protein variations."""
    all_results = []  # List to store results

    # Process transcripts in chunks
    chunk_size = 100  # Adjust based on API limits
    for i in range(0, len(transcripts), chunk_size):
        transcript_chunk = transcripts[i:i + chunk_size]  # Create a chunk of transcripts
        output = fetch_cdna_info(transcript_chunk)  # Fetch and parse the cDNA to gene info

        if output:
            # Check if output has expected structure
            if isinstance(output, list) and len(output) > 0:
                for j, entry in enumerate(output):
                    transcript_input = transcript_chunk[j]  # Match the input with the corresponding output
                    data = entry.get('data', None)

                    if data is not None:  # Check if data is None before accessing its keys
                        variant_p = data.get('variant_p')  # Get the Variant P data
                        result = {
                            "transcript_variation": transcript_input,
                            "refseq_ids": extract_np_reference(variant_p),
                            "variation_ids": data.get('variant_exchange')
                        }
                        all_results.append(result)
                    else:
                        print(f"No data found for transcript {transcript_input}. Output: {entry}")
                        result = {
                            "transcript_variation": transcript_input,
                            "refseq_ids": None,
                            "variation_ids": None
                        }
                        all_results.append(result)

            else:
                print(f"Unexpected output format for chunk starting with transcript {transcript_chunk[0]}: {output}")
                for transcript_input in transcript_chunk:
                    result = {
                        "transcript_variation": transcript_input,
                        "refseq_ids": None,
                        "variation_ids": None
                    }
                    all_results.append(result)
        else:
            print(f"No output for chunk starting with transcript {transcript_chunk[0]}.")

        time.sleep(1)  # Optional: Add a delay to avoid overwhelming the server

    return all_results
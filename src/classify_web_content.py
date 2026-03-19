"""
Utilities for classifying crawled website content using a local LLM.

This module consumes serialized webpage data produced by
`collect_web_content.py` and determines whether a website provides
a general-purpose, generative AI chatbot service.

The output format and inference assumptions are intentionally stable
to support reproducible experiments.
"""

# useful libraries
import json
import time
import pathlib
from datetime import datetime

from ollama import chat
from pydantic import BaseModel


# =============================================================================
# Configuration
# =============================================================================
EXPERIMENT_ROOT = pathlib.Path.cwd()
DEFAULT_AVAILABLE_MODELS = {
    "1": "deepseek-r1:latest",
    "2": "qwen3:8B",
    "3": "llama3:latest",
}


# =============================================================================
# Data Models
# =============================================================================


class ClassificationResponse(BaseModel):
    verdict: str
    reason: str


def get_prompt_template():
    prompt_template = """"I need to classify a website based on its primary function. The following is partial information extracted from the website.
{weblog_data}
My Question: Does this website (i.e. the domain name given in above URL) provide a general-purpose, generative AI chat service for answering a wide variety of questions?
Please check if it meets these criteria:
Functions like ChatGPT, Grok, meta.ai, or Gemini: It can understand and answer a broad range of general knowledge questions (e.g., "Explain photosynthesis," "Help me solve this algebra problem," "Write an essay outline"), or it serves as frontend chat interface for accessing such LLMs.
General Purpose: It is not a simple customer service bot limited to one topic (like tracking an order or answering questions about a single product).
Please answer with 'Yes' or 'No' and provide a brief explanation of what the website is, based on the provided info.
the format of your answer should only contain a JSON formatted response as {{'verdict': answer, 'reason':reason}}
"""
    return prompt_template


# =============================================================================
# Core Classification Logic
# =============================================================================


def extract_url_from_log(weblog_data: str):
    """
    Extract the source URL from serialized crawl output.

    IMPORTANT:
        This logic assumes the format produced by collect_web_content.py.

    Args:
        weblog_data (str): Serialized crawl output.

    Returns:
        str: Extracted URL.
    """
    return weblog_data.split("metadata")[0].strip().lstrip("URL:").strip()


def classify_single_weblog(weblog_data, llm_model):
    """
    Classify a single crawled website.

    Args:
        weblog_data (str): Serialized webpage content.
        llm_model (str): Ollama model identifier.

    Returns:
        Dict[str, Any]: Classification verdict with metadata.
    """
    start_t = time.time()
    prompt_template = get_prompt_template()
    prepared_prompt = prompt_template.format(weblog_data=weblog_data)

    response = chat(
        model=llm_model,
        messages=[
            {
                "role": "user",
                "content": prepared_prompt,
            },
        ],
        format=ClassificationResponse.model_json_schema(),
    )
    verdict = ClassificationResponse.model_validate_json(response["message"]["content"])
    verdict = verdict.model_dump()

    duration = time.time() - start_t
    verdict["URL"] = extract_url_from_log(weblog_data)
    verdict["LLM_model"] = llm_model
    verdict["inference_duration"] = duration
    return verdict


# =============================================================================
# Batch Processing
# =============================================================================


def classify_list_of_logs(input_dir, output_dir, llm_model):
    """
    Classify all crawl logs in a directory.

    Args:
        input_dir (str): Directory containing crawl JSON files.
        output_dir (str): Directory to write verdict files.
        llm_model (str): Ollama model identifier.
    """

    log_directory_path = EXPERIMENT_ROOT / input_dir
    verdict_directory_path = EXPERIMENT_ROOT / output_dir
    verdict_directory_path.mkdir(parents=True, exist_ok=True)
    # Check if the path is a valid directory
    log_dict = {"llm_model": llm_model, "verdicts": []}

    if not log_directory_path.is_dir():
        raise NotADirectoryError(f"Invalid input directory: {log_directory_path}")

    else:
        # --- 2. Loop Through All Items in the Directory ---
        for item_path in log_directory_path.iterdir():
            if item_path.is_file() and item_path.suffix == ".json":
                with open(item_path) as website_file:
                    weblog_data = json.load(website_file)
                    # classify it

                    verdict = classify_single_weblog(weblog_data, llm_model)
                    log_dict["verdicts"].append(verdict)
                    print(f"[OK] Classified: {verdict['URL']}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = (
            verdict_directory_path / f"{llm_model.replace(':', '_')}_{timestamp}.json"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(log_dict, f, indent=4)
        print(f"[INFO] Saved classification results → {output_file}")


if __name__ == "__main__":
    """
    Interactive command-line interface.
    """
    choice = input(
        "Select operation:\n"
        "0 - Classify a single crawl log\n"
        "1 - Classify all LLM website samples\n"
        "2 - Classify all non-LLM website samples\n"
        "3 - Run full LLM vs non-LLM classification\n"
        "> "
    ).strip()
    # llm_model = "qwen3:8B"  # "qwen3:14B" "deepseek-r1" "qwen3:8B"  # "llama3",  # orders of magnitude slow

    if choice == "0":
        file_to_test = input("Enter crawl log path: ").strip()
        model_to_use = input(f"Choose model {DEFAULT_AVAILABLE_MODELS}: ").strip()

        weblog_data = json.load(open(file_to_test, "r", encoding="utf-8"))
        verdict = classify_single_weblog(
            log_data=weblog_data, llm_model=DEFAULT_AVAILABLE_MODELS[model_to_use]
        )
        print(json.dumps(verdict, indent=4))

    elif choice == "1":  # classify llm smples
        model_to_use = input(f"Choose model {DEFAULT_AVAILABLE_MODELS}: ").strip()
        classify_list_of_logs(
            "experiement_data/collected_website_data/LLM_website_data",
            "experiement_data/llm_verdict/LLM_data_classified",
            DEFAULT_AVAILABLE_MODELS[model_to_use],
        )
    elif choice == "2":  # classify non llm smples
        model_to_use = input("choose model {DEFAULT_AVAILABLE_MODELS}: ").strip()
        classify_list_of_logs(
            "experiement_data/collected_website_data/non_LLM_website_data",
            "experiement_data/llm_verdict/non_LLM_data_classified",
            DEFAULT_AVAILABLE_MODELS[model_to_use],
        )
    elif choice == "3":
        for datagroup in [
            ("LLM_website_data", "LLM_data_classified"),
            ("non_LLM_website_data", "non_LLM_data_classified"),
        ]:  # llm vs non llm
            for aimodel in ["deepseek-r1:latest", "qwen3:8B", "llama3:latest"]:
                classify_list_of_logs(
                    "experiement_data/collected_website_data/" + datagroup[0],
                    "experiement_data/llm_verdict/" + datagroup[1],
                    aimodel,
                )
    else:
        print("[INFO] No valid option selected. Exiting.")

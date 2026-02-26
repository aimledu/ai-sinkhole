# Website Classification Pipeline for AI-Sinkhole

This project introduces AI-Sinkhole, a method for the discovery, classification, and blocking of emerging LLM chatbot services during proctored exams.

It is an experimental, research-oriented pipeline intended for **research, experimentation, and benchmarking**, not for production crawling or commercial deployment.

---

## 📄 Corresponding Publication

The corresponding paper is available at:

> Author1, A., Author2, B., & Author3, C. (Year). _Fighting AI with AI: AI-Agent Augmented DNS Blocking of LLM Services during Student Evaluations_. Journal/Conference Name.  
> DOI: https://doi.org/xxxxx

```bibtex
@article{author2024paper,
  title={Fighting AI with AI: AI-Agent Augmented DNS Blocking of LLM Services during Student Evaluations},
  author={Author1, A. and Author2, B. and Author3, C.},
  journal={Journal/Conference Name},
  year={2024},
  doi={xxxxx}
}
```

--

## Overview

<img src="artefacts/AI-sinkhole_icon_0.png" align="left" width="25%">

### 🗒️ This repository contains the following:

1.  **Scripts to facilitate DNS query exportring for AI based classification**
2.  **Scripts to facilitate enabling/disabling of AI-service blocking on Pi-hole**
3.  **Pipeline scripts for Web Content Collection and LLM-Based website Classification**

<br clear="left"/>

### 1. DNS query exportring for AI based classification

A script for exporting DNS query logs is below, procedures are discussed in installation section. The script will export **all** domains successfully queried by clients.

- **export_dns.sh**

### 2. enabling/disabling of AI-service blocking on Pi-hole

Scripts for enabling/disabling are the following, procedures are discussed in installation section.

- **blocking_timer.sh**
- **enable.sh**
- **disable.sh**

### 3. extraction and classification Pipeline

The pipeline has two clearly separated stages:

(scripts and corresponding datasets available in /src folder).

1. **Web Content Collection**
   - Crawl publicly accessible websites
   - Extract metadata and readable content
   - Normalize results into a stable, text-based format

2. **LLM-Based Classification**
   - Prompt a local LLM to reason about a website’s primary function
   - Decide whether it provides a _general-purpose generative AI chat service_
   - Produce structured JSON verdicts with reasoning and timing metadata

The separation between collection and classification enables offline analysis and reproducible experiments.

---

---

## Design goals

- **Stable data contracts**  
  The crawler emits a serialized text format that the classifier depends on.

- **Local-first inference**  
  All classification is performed using local LLMs via Ollama.

- **Reproducibility over performance**  
  Sequential execution, explicit prompts, and timestamped outputs are used intentionally.

- **Research-first design**  
  This code prioritizes clarity and auditability over robustness or scale.

---

## Stage 1: Website Content Collection

### Script

collect_web_content.py

### Functionality

- Crawls a webpage using `crawl4ai`
- Filters out scripts and styles
- Extracts:
  - URL
  - Page metadata
  - Markdown-formatted page content
- Serializes everything into a **single string**
- Saves results as timestamped JSON files

### Output Format (Important)

Each crawl result is saved as a JSON file containing **one string**, for example:

**This format must remain stable**  
The classifier relies on this exact structure to extract the URL and context.

### Usage

Run the script interactively:

python collect_web_content.py

Options:

- `0` – Crawl a single URL
- `1` – Crawl a predefined list of non-LLM websites
- `2` – Crawl a predefined list of LLM-related websites

URL lists are stored in:

/dataset/

---

## Stage 2: Website Classification

### Script

classify_web_content.py

### Functionality

- Loads crawl logs produced by `collect_web_content.py`
- Prompts a local LLM with extracted website data
- Determines whether the website provides:
  - A **general-purpose**
  - **Generative AI chatbot**
  - Comparable to ChatGPT, Gemini, Grok, etc.
- Produces structured verdicts with reasoning and inference duration

### Classification Criteria

A website is classified as an LLM chatbot only if it:

- Can answer a wide range of general knowledge questions
- Is not limited to a single product, service, or support task
- Acts as a general conversational interface or frontend for an LLM

---

## Supported LLMs

Classification is performed using **Ollama**.

Default configured models:

- `deepseek-r1:latest`
- `qwen3:8B`
- `llama3:latest`

Models can be extended or replaced directly in `classify_web_content.py`.

---

## Running the Full Pipeline

1. **Collect website data**
   python collect_web_content.py

2. **Classify collected data**
   python classify_web_content.py

3. **Run full LLM vs non-LLM classification**

- Choose option `3` in the classifier CLI

---

## Assumptions & Limitations

- Websites are publicly accessible and allow automated crawling
- Crawling is sequential and rate-limited
- Classification quality depends on:
- Prompt wording
- LLM capability
- Extracted website content
- No retries, concurrency, or advanced fault tolerance
- Not suitable for large-scale or commercial crawling

---

## Intended Use Cases

- Research experiments
- Dataset construction
- Prompt engineering studies
- LLM reasoning evaluation
- AI service landscape analysis

---

## Non-Goals

- Production-grade crawling
- High-throughput scraping
- Legal or compliance guarantees
- Perfect classification accuracy

---

## License & Usage Notes

This code is provided **as is** for **experimental and research purposes**.

Please:

- Crawl responsibly
- Review and adapt the code before any external or production use

---

---

# Installation

To install Pihole follow the manual avaiable at : https://docs.pi-hole.net/docker/. You can also install it as follows:

## **Quick Start**

Using [Docker-compose](https://docs.docker.com/compose/install/):

1. Copy the below docker compose example and update as needed:

```yml
# More info at https://github.com/pi-hole/docker-pi-hole/ and https://docs.pi-hole.net/
services:
  pihole:
    container_name: pihole
    image: pihole/pihole:latest
    ports:
      # DNS Ports
      - "53:53/tcp"
      - "53:53/udp"
      # Default HTTP Port
      - "80:80/tcp"
      # Default HTTPs Port. FTL will generate a self-signed certificate
      - "443:443/tcp"
      # Uncomment the line below if you are using Pi-hole as your DHCP server
      #- "67:67/udp"
      # Uncomment the line below if you are using Pi-hole as your NTP server
      #- "123:123/udp"
    environment:
      # Set the appropriate timezone for your location (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), e.g:
      TZ: "America/New_York"
      # Set a password to access the web interface. Not setting one will result in a random password being assigned
      FTLCONF_webserver_api_password: "correct horse battery staple"
      # If using Docker's default `bridge` network setting the dns listening mode should be set to 'ALL'
      FTLCONF_dns_listeningMode: "ALL"
    # Volumes store your data between container upgrades
    volumes:
      # For persisting Pi-hole's databases and common configuration file
      - "./etc-pihole:/etc/pihole"
      # Uncomment the below if you have custom dnsmasq config files that you want to persist. Not needed for most starting fresh with Pi-hole v6. If you're upgrading from v5 you and have used this directory before, you should keep it enabled for the first v6 container start to allow for a complete migration. It can be removed afterwards. Needs environment variable FTLCONF_misc_etc_dnsmasq_d: 'true'
      #- './etc-dnsmasq.d:/etc/dnsmasq.d'
    cap_add:
      # See https://github.com/pi-hole/docker-pi-hole#note-on-capabilities
      # Required if you are using Pi-hole as your DHCP server, else not needed
      - NET_ADMIN
      # Required if you are using Pi-hole as your NTP client to be able to set the host's system time
      - SYS_TIME
      # Optional, if Pi-hole should get some more processing time
      - SYS_NICE
    restart: unless-stopped
```

2. Run `docker compose up -d` to build and start pi-hole (Syntax may be `docker-compose` on older systems).

> [!NOTE]
> Volumes are recommended for persisting data across container re-creations for updating images.

## **Loading Blocklists**

To load the blocklist you must first add the list's URL in the **Group Management > Adlists** section of the web interface. To do this, enter **https://raw.githubusercontent.com/aimledu/ai-sinkhole/refs/heads/main/blocklist/ai_services.txt** in the \* _Address_ _ field, and enter **ai-sinkhole** in the _ _Comment_ \* field. Adding the proper comment tag is essential for using our enabling/disabling scripts. After the previous steps have been completed, run **pihole -g** in the terminal or click **"Update"** in the **Tools > Update Gravity** section to finish loading the blocklist.

## **Enabling/Disabling Blocklists**

Blocklists can be enabled/disabled directly in the Pi-hole web UI by locating the blocklist and toggling the enable/disable option.
Alternatively, our scripts can be used to enable/disable individual blocklists for specified time ranges directly from the host machine.

### **Enabling/Disabling Blocklists with Scripts**

#### **blocking_timer.sh**

To use this script, run the script **blocking_timer.sh** on the host machine. You will be prompted to tell the script what to do. If you want to disable the blocklist, enter **0**. If you want to enable the blocklist, enter **1**. You will then be asked to enter the duration. Be sure to specify the time unit (e.g. If you want 15 seconds, enter **15s**. If you want 15 minutes, enter **15m**. If you want 15 hours, enter **15h**.) After your specified duration is over, the blocklist will revert to its original state.

#### **enable.sh**

To use this script, run the script **enable.sh** on the host machine. This will enable the wordlist indefinitely.

#### **disable.sh**

To use this script, run the script **disable.sh** on the host machine. This will disable the wordlist indefinitely.

### **Exporting Pihole Database with Scripts**

#### **export_dns.sh**

To use this script, run the script **export_dns.sh** on the host machine. This will export the logs to a CSV file "*pihole_dns_logs.csv*" that will contain **all** domains that were successfully reached by clients.

# Future Extensions (Ideas welcome)

- Classification confidence calibration
- Automated end to end system with human in the loop:
  - a daemon service for automated candidate URLs extraction from news and social media platforms
  - a daemon service for automated DNS request log ingestion for identifying historical use of AI services
  - automated evaluation metrics
- Experiment tracking
- Ensemble classification across multiple LLMs

---

## If you find this repository helpful, you can cite the following accompanying paper:

## 📄 Corresponding Publication

> Author1, A., Author2, B., & Author3, C. (Year). _Fighting AI with AI: AI-Agent Augmented DNS Blocking of LLM Services during Student Evaluations_. Journal/Conference Name.  
> DOI: https://doi.org/xxxxx

```bibtex
@article{author2024paper,
  title={Fighting AI with AI: AI-Agent Augmented DNS Blocking of LLM Services during Student Evaluations},
  author={Author1, A. and Author2, B. and Author3, C.},
  journal={Journal/Conference Name},
  year={2024},
  doi={xxxxx}
}
```

--

# Open Deep Research

Welcome to this open replication of [OpenAI's Deep Research](https://openai.com/index/introducing-deep-research/)! This agent attempts to replicate OpenAI's model and achieve similar performance on research tasks.

Read more about this implementation's goal and methods in our [blog post](https://huggingface.co/blog/open-deep-research).


This agent achieves **55% pass@1** on the GAIA validation set, compared to **67%** for the original Deep Research.

## Setup

To get started, follow the steps below:

### Clone the repository

```bash
git clone https://github.com/huggingface/smolagents.git
cd smolagents/examples/open_deep_research
```

### Install dependencies

Run the following command to install the required dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Set up environment variables

The agent uses the `GoogleSearchTool` for web search, which requires an environment variable with the corresponding API key, based on the selected provider:
- `SERPAPI_API_KEY` for SerpApi: [Sign up here to get a key](https://serpapi.com/users/sign_up)
- `SERPER_API_KEY` for Serper: [Sign up here to get a key](https://serper.dev/signup)

Depending on the model you want to use, you may need to set environment variables.
For example, to use the default `gpt-4o-mini` model, you need to set the `OPENAI_API_KEY` environment variable.
[Sign up here to get a key](https://platform.openai.com/signup).


## Usage

Then you're good to go! Run the research agent script, as in:

### Using OpenAI or other standard providers
```bash
python cli/research-agent-cli.py --model "gpt-4o-mini" "2+2?"
```

### Using a local OpenAI-compatible endpoint
```bash
python cli/research-agent-cli.py --model "openai/qwen3:32b" --api-base "http://127.0.0.1:11434/v1" --api-key "dummy" "2+2?"
```

### CLI Options
- `--model`: Model name
- `--api-base`: Base URL for custom API endpoints (e.g., local LLM servers)
- `--api-key`: API key for authentication

## GAIA Evaluation

To run evaluation on the GAIA benchmark dataset, use the evaluation CLI:

### Using OpenAI or other standard providers
```bash
python cli/gaia-eval-cli.py --model "gpt-4o" --run-name "my-evaluation" --concurrency 8
```

### Using a local OpenAI-compatible endpoint
```bash
python cli/gaia-eval-cli.py --model "openai/qwen3:32b" --api-base "http://127.0.0.1:11434/v1" --api-key "dummy" --run-name "local-evaluation" --concurrency 4
```

### GAIA CLI Options
- `--model`: Model name
- `--api-base`: Base URL for custom API endpoints (e.g., local LLM servers)  
- `--api-key`: API key for authentication
- `--run-name`: Name for this evaluation run (required)
- `--concurrency`: Number of parallel tasks (default: 8)
- `--set-to-run`: Dataset split to evaluate ("validation" or "test", default: "validation")
- `--use-raw-dataset`: Use the raw GAIA dataset instead of the annotated version
- `--use-open-models`: Use open models (legacy option)

## Full reproducibility of results

The data used in our submissions to GAIA was augmented in this way:
 -  For each single-page .pdf or .xls file, it was opened in a file reader (MacOS Sonoma Numbers or Preview), and a ".png" screenshot was taken and added to the folder.
- Then for any file used in a question, the file loading system checks if there is a ".png" extension version of the file, and loads it instead of the original if it exists.

This process was done manually but could be automatized.

After processing, the annotated was uploaded to a [new dataset](https://huggingface.co/datasets/smolagents/GAIA-annotated). You need to request access (granted instantly).
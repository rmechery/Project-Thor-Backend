import os
import json
import argparse
import requests
from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import (
    LLMContextPrecisionWithReference,
    LLMContextRecall,
    ContextEntityRecall,
    NoiseSensitivity,
    ResponseRelevancy,
    Faithfulness,
    FactualCorrectness,
    SemanticSimilarity,
    RougeScore,
    AspectCritic,
)
from datasets import Dataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import nltk

nltk.data.path.append('/Users/ryanmechery/Documents/CS320 Local/ThorWebScraper/.venv')

# Load environment variables
load_dotenv()

# Initialize LLM and embeddings
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

# Define API endpoint
api_url = 'http://localhost:3000/api/single-chat/'

def main(input_file, output_dir):
    # Load experimental data
    input_path = os.path.join('./testing_data', input_file)
    with open(input_path, 'r') as file:
        experiments = json.load(file)

    # Initialize data storage
    data = {
        "user_input": [],
        "reference": [],
        "response": [],
        "retrieved_contexts": [],
        "section": [],
        "pdf_url": [],
    }

    # Process experiments
    for experiment in experiments:
        question = experiment['question']
        ground_truth = experiment['ground_truth']
        section = experiment['section']
        pdf_url = experiment['pdf_url']
        payload = {'prompt': question}

        # Simulate API response (replace with actual API call)
        response = requests.post(api_url, json=payload)
        response_data = response.json()

        # Extract required fields
        model_answer = response_data.get('response', 'Response not generated.')
        retrieved_contexts = response_data.get('contexts', [])

        # Append to data structure
        data["user_input"].append(question)
        data["reference"].append(ground_truth)
        data["response"].append(model_answer)
        data["section"].append(section)
        data["pdf_url"].append(pdf_url)
        data["retrieved_contexts"].append(retrieved_contexts)

    # Convert data to Dataset
    dataset = Dataset.from_dict(data)

    # Evaluate the dataset
    metrics = [
        LLMContextPrecisionWithReference(llm=evaluator_llm),
        LLMContextRecall(llm=evaluator_llm),
        ContextEntityRecall(llm=evaluator_llm),
        NoiseSensitivity(llm=evaluator_llm),
        ResponseRelevancy(llm=evaluator_llm),
        Faithfulness(llm=evaluator_llm),
        FactualCorrectness(llm=evaluator_llm),
        SemanticSimilarity(embeddings=evaluator_embeddings),
        RougeScore(),
        AspectCritic(
            name="conciseness",
            definition="Is the response concise and free from unnecessary information?",
            llm=evaluator_llm
        ),
        AspectCritic(
            name="error_handling",
            definition="Does the chatbot appropriately handle errors or acknowledge when it lacks information?",
            llm=evaluator_llm
        ),
        AspectCritic(
            name="originality",
            definition="Is the response original and not overly reliant on verbatim excerpts from the retrieved context?",
            llm=evaluator_llm
        )
    ]
    result = evaluate(dataset=dataset, metrics=metrics)
    df = result.to_pandas()

    # Add custom fields to the DataFrame
    df['section'] = data['section']
    df['pdf_url'] = data['pdf_url']

    # Ensure output directory exists
    output_path = os.path.join('./testing_data', output_dir)
    os.makedirs(output_path, exist_ok=True)

    # Save results
    df.to_csv(os.path.join(output_path, 'output.csv'), index=False)
    df.to_json(os.path.join(output_path, 'output.json'), orient='records', lines=True)

    print(f"Results saved to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate experimental data and save results.')
    parser.add_argument('input_file', type=str, help='Input JSON filename located in ./testing_data/')
    parser.add_argument('output_dir', type=str, help='Output directory name under ./testing_data/')

    args = parser.parse_args()
    main(args.input_file, args.output_dir)

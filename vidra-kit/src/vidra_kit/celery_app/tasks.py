# from vidra_kit.celery_app import get_celery_app
from loguru import logger
import time
import random
from celery import shared_task

# --- Simple Task Example ---


@shared_task
def add(x, y):
    """Adds two numbers and logs the result."""

    # Loguru automatically includes task_id and task_name in the output
    logger.info("Starting arithmetic task: {} + {}", x, y)

    result = x + y

    # Example of a contextual log for successful completion
    logger.info("Arithmetic task completed successfully. Result: {}", result)
    return result


# --- Binding Task Example (for retries/state) ---


@shared_task(
    bind=True, max_retries=3, default_retry_delay=5
)  # Retry up to 3 times, waiting 5s
def fetch_external_data(self, url):
    """Simulates fetching data from an unreliable external API with retries."""

    # The 'self' argument is available because bind=True
    attempt = self.request.retries + 1
    logger.info(
        "Attempting to fetch URL: {} (Attempt {}/{})...",
        url,
        attempt,
        self.max_retries + 1,
    )

    try:
        # Simulate network failure 75% of the time on first two attempts
        if attempt <= 2 and random.random() < 0.75:
            raise ConnectionError("Simulated API connection failure.")

        # Simulate success
        time.sleep(1)
        logger.info("Data successfully fetched from {}", url)
        return {"status": "success", "data_size": 1024}

    except ConnectionError as e:
        # Log the exception, which automatically includes the traceback
        logger.exception("Connection error during fetch. Retrying...")

        # Raise retry to trigger the delay and next attempt
        raise self.retry(exc=e)

    except Exception as e:
        # Log unexpected errors
        logger.error("A critical, non-retryable error occurred.")
        return {"status": "failed", "error": str(e)}


# --- Chaining Task Example (Using a chord to aggregate results) ---


@shared_task
def process_data_chunk(chunk_id, data_list):
    """Processes a small chunk of data and returns a result."""
    # Simulate processing time
    time.sleep(random.uniform(0.1, 0.5))
    result = sum(data_list)
    logger.debug("Processed chunk {}: sum={}", chunk_id, result)
    return result


@shared_task
def aggregate_results(results):
    """Aggregates the results from all processed chunks."""
    final_sum = sum(results)
    logger.info("All chunks processed. Final aggregated sum: {}", final_sum)
    return final_sum


# Example of how to call the chain (usually done from an external application)
def start_processing_workflow():
    data = [10, 20, 30, 40, 50, 60]
    chunks = [data[i : i + 2] for i in range(0, len(data), 2)]

    # 1. Create a group of parallel tasks (the header)
    header = [process_data_chunk.s(i, chunk) for i, chunk in enumerate(chunks)]

    # 2. Define the callback task (the body)
    callback = aggregate_results.s()

    # 3. Combine them into a chord
    workflow = app.signature("celery.chord", args=[header, callback])

    logger.info("Starting chunk processing workflow (Chord).")
    # Execute the workflow and return the AsyncResult object
    return workflow.apply_async()


if __name__ == "__main__":
    # This block allows you to run tasks directly for testing outside the worker

    # Example 1: Simple task
    result_add = add.delay(10, 5)
    print(f"ADD Task ID: {result_add.id}")

    # Example 2: Retrying task
    # This will likely fail a couple of times then succeed, logging retry messages
    result_fetch = fetch_external_data.delay("http://example.com/api/v1")
    print(f"FETCH Task ID: {result_fetch.id}")

    # Example 3: Complex workflow
    result_workflow = start_processing_workflow()
    print(f"WORKFLOW Task ID: {result_workflow.id}")

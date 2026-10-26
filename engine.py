# engine.py
import asyncio
import logging
import httpx
from parsers import parse_html_quotes, parse_api_quotes


async def worker(
    worker_id: int,
    task_queue: asyncio.Queue,
    results_queue: asyncio.Queue,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3
):
    """
    Async worker consuming extraction tasks from task_queue.
    Enforces concurrency limits via semaphores and handles retries with linear backoff.
    """
    while True:
        task = await task_queue.get()
        if task is None:  # Sentinel signal to terminate worker
            task_queue.task_done()
            break

        async with semaphore:
            url = task["url"]
            task_type = task["task_type"]

            for attempt in range(1, max_retries + 1):
                try:
                    response = await client.get(url, headers=task.get("headers"), timeout=5.0)
                    response.raise_for_status()

                    # Route parsing based on task type
                    if task_type == "HTML":
                        records = parse_html_quotes(response.content)
                    elif task_type == "JSON":
                        records = parse_api_quotes(response.json())
                    else:
                        records = []

                    for record in records:
                        await results_queue.put(record)
                    break
                except Exception as e:
                    if attempt == max_retries:
                        logging.error(f"[Worker {worker_id}] Task {url} failed permanently: {e}")
                    else:
                        logging.warning(f"[Worker {worker_id}] Task {url} attempt {attempt} failed: {e}. Retrying...")
                    await asyncio.sleep(1.0 * attempt)

        task_queue.task_done()

import asyncio
import httpx
import logging
import argparse
from engine import worker
from sinks import SQLSink, CSVSink

logging.BasicConfig(levelname=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def run_pipeline(concurrency, db_path : str, csv_path : str):
    tasks_queue = asyncio.Queue 
    result_queue = asyncio.Queue 

    for page in range(1, 6):
        await tasks_queue.put({
            "url" : f"https://quotes.toscrape.com/page/{page}",
            "task_type" : "HTML",
            "headers" : {"User-Agent" : "Mozilla/5.0"}
        })

    semaphore = asyncio.semaphore(concurrency)
    db_sink = SQLSink(db_path)
    csv_sink = CSVSink(csv_path)

    async with httpx.AsyncClient as client : 
        workers = [asyncio.create_task(worker(i, tasks_queue, result_queue, client, semaphore)) for i in range(concurrency)]

    await tasks_queue.join()

    for _ in range(concurrency) : 
        await tasks_queue.put(None)

    await asyncio.gather(*workers)

    records = []

    while not result_queue.empty():
        records.append(await result_queue.get())
        result_queue.task_done()


    if db_path:
        SQLSink.write_batch(records)
    
    if csv_path:
        csv_sink.open()
        csv_sink.write_row(records)
        csv_sink.close()

    logging.info(f"Pipeline complete. Successfully wrote {len(batch)} records to {db_path}")

    
def main():

    parser = argparse.ArgumentParser(description="Async API & DOM Extraction Engine")

    parser.add_argument(" --concurrency", type=int, default=3, help="Number of concurrent workers")

    parser.add_argument(" --db", type=str, default="output.db", help="SQLite database path ")

    parser.add_argument(" --csv", type=str, default="output.csv", help="CSV output file path")

    args = parser.parse_args()

    asyncio.run(run_pipeline(args.concurrency, args.db, args.csv))

if __name__ == "__main__":
    main()

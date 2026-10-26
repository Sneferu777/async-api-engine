import asyncio
import httpx
import logging
import argparse
from engine import worker
from sinks import SQLSink, CSVSink
from config import config 

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def run_pipeline(concurrency, db_path : str, csv_path : str):
    tasks_queue = asyncio.Queue() 
    result_queue = asyncio.Queue() 

    for page in range(1, 6):
        await tasks_queue.put({
            "url" : config.BASE_URL.format(page=page),
            "task_type" : "HTML",
            "headers" : config.DEFAULT_HEADERS
        })

    semaphore = asyncio.Semaphore(concurrency)
    db_sink = SQLSink(db_path)
    csv_sink = CSVSink(csv_path, fieldnames=config.CSV_FIELDNAMES)

    if db_path:
        db_sink.init_schema()



    async with httpx.AsyncClient(follow_redirects=True) as client : 
        workers = [asyncio.create_task(worker(i, tasks_queue, result_queue, client, semaphore)) for i in range(concurrency)]

        await tasks_queue.join()

        for _ in range(concurrency) : 
            await tasks_queue.put(None)

        await asyncio.gather(*workers)

    records = []

    while not result_queue.empty():
        records.append(await result_queue.get())
        result_queue.task_done()


    if db_path and records:
        db_sink.write_batch(records)
    
    if csv_path and records:
        csv_sink.open()
        csv_sink.write_batch(records)
        csv_sink.close()

    logging.info(f"Pipeline complete. Successfully wrote {len(records)} records to {db_path}")

    
def main():

    parser = argparse.ArgumentParser(description="Async API & DOM Extraction Engine")

    parser.add_argument("--concurrency", type=int, default=config.DEFAULT_CONCURRENCY, help="Number of concurrent workers")

    parser.add_argument("--db", type=str, default=config.DEFAULT_DB_PATH, help="SQLite database path ")

    parser.add_argument("--csv", type=str, default=config.DEFAULT_CSV_PATH, help="CSV output file path")

    args = parser.parse_args()

    asyncio.run(run_pipeline(args.concurrency, args.db, args.csv))

if __name__ == "__main__":
    main()

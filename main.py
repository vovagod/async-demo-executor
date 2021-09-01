import asyncio
import time
import concurrent.futures
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["restdb"]
col = db["jobs"]


def tasks(s):
    start = time.time()
    time.sleep(s[1])
    print('TASK: {}, SLEEP_TIME: {}, DELAY: {:.2f}'.format(s[0], s[1], (time.time()-start)))
    if s[0] > 0:
        j = col.find_one({'task': s[0]})
        if j:
            query = {'task':j['task'], 'time':j['time']}
            newvalues = {"$set": { "task":j['task'], 'time':0}}
            col.update_one(query, newvalues)
    return (s[0], True)


async def survey():
    loop = asyncio.get_event_loop()
    while loop.is_running():
        try:
            output = []
            for j in col.find():
                if isinstance(j.get('task',), int):
                    output.append((j['task'], j['time']))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                poll_tasks = [loop.run_in_executor(executor, tasks, i) for i in output if i[1]]
                completed, pending = await asyncio.wait(poll_tasks)
            results = [t.result() for t in completed]
            
        except KeyboardInterrupt:
            pass
        
            
if __name__ == "__main__":

    print('Executor is running...')
    asyncio.run(survey())


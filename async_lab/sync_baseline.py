import httpx
import time


print("One call:")
start = time.perf_counter()
response = httpx.get("http://127.0.0.1:5001/nutrition/eggs")

#print(response.status_code)
#print(response.text)
print(time.perf_counter() - start)


print("Three calls:")
start = time.perf_counter()
response = httpx.get("http://127.0.0.1:5001/nutrition/rice")
response = httpx.get("http://127.0.0.1:5001/nutrition/beans")
response = httpx.get("http://127.0.0.1:5001/nutrition/chicken")

#print(response.status_code)
#print(response.text)
print(time.perf_counter() - start)

print("Five calls:")
start = time.perf_counter()
response = httpx.get("http://127.0.0.1:5001/nutrition/milk")
response = httpx.get("http://127.0.0.1:5001/nutrition/bread")
response = httpx.get("http://127.0.0.1:5001/nutrition/cheese")
response = httpx.get("http://127.0.0.1:5001/nutrition/apple")
response = httpx.get("http://127.0.0.1:5001/nutrition/banana")

#print(response.status_code)
#print(response.text)
print(time.perf_counter() - start)



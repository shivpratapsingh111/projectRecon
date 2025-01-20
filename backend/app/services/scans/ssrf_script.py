# import os
# import sys
# import subprocess
# from datetime import datetime

# def main():
#     url_file = sys.argv[1]
#     link = sys.argv[2]

#     open_redirect_results = "openRedirects.txt"
#     ssrf_results = "ssrfUrls.txt"

#     time_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     # For getting first 20 characters of `link`
#     first_20 = link[:20]
#     counter = 1
#     temp_file = "tempResults.txt"
#     try:
#         with open(url_file, "r") as url_results:
#             for line in url_results:
#                 line = line.strip()
#                 lc = f"{link}?no={counter}"
#                 # Prepare query and filter results
#                 qs = subprocess.run(
#                     ["qsreplace", "-a"],
#                     input=line.encode(),
#                     stdout=subprocess.PIPE
#                 ).stdout.decode()
#                 qs = subprocess.run(
#                     ["qsreplace", lc],
#                     input=qs.encode(),
#                     stdout=subprocess.PIPE
#                 ).stdout.decode()
#                 qs_lines = list(filter(None, qs.splitlines()))
#                 with open(ssrf_results, "a") as ssrf_file:
#                     ssrf_file.write("\n".join(qs_lines) + "\n")
#                 for qs_line in qs_lines:
#                     headers = subprocess.run(
#                         ["curl", "-I", "-L", qs_line, "-k"],
#                         stderr=subprocess.DEVNULL,
#                         stdout=subprocess.PIPE
#                     ).stdout.decode()
#                     location_header = next((line for line in headers.splitlines() if "location:" in line.lower()), None)
#                     if location_header:
#                         url = location_header.split(" ", 1)[1].strip()
#                         with open(temp_file, "a") as temp:
#                             temp.write(f"{qs_line} ---> {url}\n")
#                 counter += 1
#         # Filtering out proper Open Redirects
#         with open(temp_file, "r") as temp:
#             with open(open_redirect_results, "w") as open_redirects:
#                 for line in temp:
#                     if f"---> {first_20}" in line:
#                         open_redirects.write(line)
#         # Check if open redirects were found
#         if os.path.getsize(open_redirect_results) > 0:
#             count = sum(1 for _ in open(open_redirect_results))
#             print(f"\033[32mOpen redirects found: {count}\033[0m")
#         else:
#             os.remove(open_redirect_results)
#     except Exception as e:

#         print("Error in Ssrf script:", e)
#     # Go back to base directory
# if __name__ == "__main__":
#     main()

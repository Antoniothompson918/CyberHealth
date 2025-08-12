from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv("GA_EMAIL"), os.getenv("GA_PASSWORD"))

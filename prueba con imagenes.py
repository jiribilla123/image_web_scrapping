import os, time, requests
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from tqdm import tqdm

df = pd.read_excel("/Users/jaime/Downloads/Plantilla_Productos 03.06.2025.xlsx")
df["code"] = df["clave1 *"].astype(str)
pattern = r"^\d{4}-\d{4}$"
codes = df[df["code"].str.match(pattern, na=False)]["code"].tolist()
download_folder = "images"
os.makedirs(download_folder, exist_ok=True)
logs = []

options = Options()
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

for code in tqdm(codes, desc="Downloading images"): #I added this to calculate time
    filename = f"{code}.jpg"
    path = os.path.join(download_folder, filename)
    
    if os.path.exists(path):
        print(f"⏭️ Skipping {filename} (already exists)")
        logs.append({"code": code, "status": "skipped", "message": "File already exists"})
        continue

    url = f"https://www.motosyequipos.com/ProductosPorGrupoGeneral.aspx?parbus={code}#galleryCuadricula"
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    image_tag = soup.find("img", {"class": "fancybox-image"})

    if image_tag and image_tag.get("src"):
        img_url = image_tag["src"]
        r = requests.get(img_url)
        path = os.path.join(download_folder, f"{code}.jpg")
        with open(path, "wb") as f:
            f.write(r.content)
    logs.append({"code": code, "status": "downloaded", "message": "Image saved"})
else:
    logs.append({"code": code, "status": "failed", "message": "Image not found"})

log_df = pd.DataFrame(logs)
log_df.to_csv("/Users/jaime/Downloads/download_log.csv", index=False)
print("📄 Log saved to download_log.csv")
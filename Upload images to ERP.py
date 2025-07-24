import os
import time
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
EXCEL_FILE = 'path_to_codes.xlsx' 
IMAGE_FOLDER = "Folder were images were saved (see prevoius code)"
LOGIN_URL = "web.app"  #private
EMAIL = "user@email.com"  #private
PASSWORD = "********"  #private

# Create codes DB, some products
df = pd.read_excel(EXCEL_FILE)
df["clave1 *"] = df["clave1 *"].astype(str)
pattern = r"^\d{4}-\d{4}$"

codes = df[df["clave1 *"].str.match(pattern, na=False)]["clave1 *"].tolist() # To test, just create a manual list of 2 or three products

# Run headless only after testing
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

# Log in
driver.get(LOGIN_URL)
wait.until(EC.presence_of_element_located((By.ID, "input-email"))).send_keys(EMAIL)
driver.find_element(By.ID, "input-password").send_keys(PASSWORD)
ingresar_button = wait.until(EC.element_to_be_clickable(
    (By.ID, "button-login")
))
ingresar_button.click()

# Second "Ingresar button"
ingresar_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[.//text()='Ingresar']")
))
ingresar_button.click()

# Go to "Productos"
productos_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//span[text()='Productos']")
))
productos_button.click()
time.sleep(1)

# Uploading Loop
logs = [] # I didn't really use the logs file but its ok to keep it 

for code in tqdm(codes, desc="Uploading images", dynamic_ncols=True):
    try:
        img_path = os.path.join(IMAGE_FOLDER, f"{code}.jpg")
        if not os.path.exists(img_path):
            logs.append({"code": code, "status": "skipped", "message": "Image not found"}) #some products were deleted from supplier's website and might not have an image available
            continue

        # 1: Search the product
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Buscar')]")))
        search_box.click()
        search_box.send_keys(Keys.COMMAND + "a")
        search_box.send_keys(Keys.DELETE)
        search_box.send_keys(code)
        search_box.send_keys(Keys.ENTER)
        time.sleep(1) # probably avoidable

        # This turned to be unnecesary since the product is autmatically selected after searching
        """ 
        # 2: Click the first result
        table_rows = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="productListContainer"]/div/div[1]/div')
        ))
        if not table_rows:
            logs.append({"code": code, "status": "not found", "message": "No search results"})
            continue
        table_rows[0].click()
        time.sleep(1)
        """

        # 3: Click the Edit button
        edit_button = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '//*[@id="secundaryContainer"]/div[1]/header/div/div[2]/div/div/button[1]'
        )))
        driver.execute_script("arguments[0].style.border='2px solid red'", edit_button)
        edit_button.click()
        time.sleep(1)  # Probably avoidable

        # 4: Upload the image
        upload_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
        upload_input.send_keys(os.path.abspath(img_path))
        time.sleep(2)

        # 5: Click Save button
        save_button = wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "MuiButton-containedSuccess")
        ))
        save_button.click()
        time.sleep(1) # Probably avoidable

        logs.append({"code": code, "status": "uploaded", "message": "Image uploaded successfully"})

    except Exception as e:
        logs.append({"code": code, "status": "error", "message": str(e)})
        continue

# Quit and save logs
driver.quit()
pd.DataFrame(logs).to_csv("upload_log.csv", index=False)
print("✅ Upload complete. Log saved to upload_log.csv")

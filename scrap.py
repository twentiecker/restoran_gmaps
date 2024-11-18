from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import re
import json
from datetime import date


def transform_data(data):
    transformed_data = {}
    for day, records in data.items():
        day_data = {}
        for record in records:
            # Extract percentage
            percentage_match = re.search(r"\d+", record)
            time_match = re.search(r"\d{2}\.\d{2}", record)

            # Only proceed if both percentage and time are found
            if percentage_match and time_match:
                percentage = int(percentage_match.group())
                time = time_match.group()
                day_data[time] = percentage
        transformed_data[day] = day_data
    return transformed_data


start = time.time()

# setup Chrome options (opsional)
chrome_options = Options()
# chrome_options.add_argument(
#     "--headless"
# )  # Menjalankan di background, tanpa GUI (optional)

# setup ChromeDriver
service = Service(ChromeDriverManager().install())

# initiate driver with WebDriverManager dan service
driver = webdriver.Chrome(service=service, options=chrome_options)

# open google maps
driver.get("https://www.google.com/maps")
time.sleep(2)  # Tunggu sejenak hingga halaman termuat

# input keyword
search_box = driver.find_element(By.ID, "searchboxinput")
time.sleep(2)
search_box.send_keys("restoran jakarta")  # Ganti dengan kata kunci yang diinginkan
search_box.send_keys(Keys.RETURN)
time.sleep(5)  # Tunggu sejenak hingga hasil pencarian muncul

# element scroll
el_scroll = driver.find_elements(
    By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd"
)

# get height
el_height = el_scroll[1].size["height"]

is_scroll = True
while is_scroll:
    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollTop + 10", el_scroll[1]
    )
    time.sleep(0.5)  # adjust the sleep time for slower scrolling

    # end of list
    try:
        el_end_list = driver.find_element(By.CSS_SELECTOR, "span.HlvSq")
        print(el_end_list.text)
        is_scroll = False
    except:
        pass

# scroll to top
driver.execute_script("arguments[0].scrollTop = 0;", el_scroll[1])
time.sleep(3)

# cards
cards = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")

restaurants = {}
j = 0
for card in cards:
    if j == 2:
        driver.execute_script("arguments[0].scrollIntoView(true);", card)
        j = 0

    # click card
    card.click()
    time.sleep(15)

    # elemen data
    el_name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf.lfPIob")
    el_summaries = driver.find_element(By.CSS_SELECTOR, "div.fontBodyMedium.dmRWX")
    el_category = driver.find_element(By.CSS_SELECTOR, "button.DkEaL")
    el_details = driver.find_elements(
        By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"
    )
    el_busy_times = driver.find_elements(By.CSS_SELECTOR, "div.g2BVhd")

    print(100 * "=")

    # name
    print("nama_restoran:", el_name.text)

    # rating, reviews dan price
    summaries = {"rating": "N/A", "reviews": "N/A", "price": "N/A"}
    summary_keys = ["rating", "reviews", "price"]
    for i in range(len(el_summaries.text.split("\n"))):
        print(
            summary_keys[i] + ":",
            re.sub(r"[()·Rp+ ]", "", el_summaries.text.split("\n")[i]),
        )
        summaries[summary_keys[i]] = re.sub(
            r"[()·Rp+ ]", "", el_summaries.text.split("\n")[i]
        )

    # category
    print("category:", el_category.text)

    # address, website, phone
    details_dict = {
        "address": "N/A",
        "website": "N/A",
        "phone": "N/A",
    }
    website_regex = r"^(https?://)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}(/[-a-zA-Z0-9@:%_+.~#?&//=]*)?$"
    phone_regex = r"^(\(?\d{1,4}\)?)[\s\-]?\d{3,}$"
    for detail in el_details:
        if "Jl." in detail.text or "Jalan" in detail.text:
            details_dict["address"] = detail.text
        elif re.match(website_regex, detail.text):
            details_dict["website"] = detail.text
        elif re.match(phone_regex, detail.text):
            details_dict["phone"] = detail.text
        else:
            pass
    print(details_dict)

    # busy times
    busy_times_dict = {
        "sunday": [],
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
    }
    days = [
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ]
    i = 0
    for parent in el_busy_times:
        childs = parent.find_elements(By.CSS_SELECTOR, "div.dpoVLd")
        for child in childs:
            busy_times_dict[days[i]].append(child.get_attribute("aria-label"))
        i += 1

    print(100 * "=")

    busy_times = transform_data(busy_times_dict)

    # add data to restaurant
    restaurants[el_name.text] = {}
    restaurants[el_name.text].update(summaries)
    restaurants[el_name.text]["category"] = el_category.text
    restaurants[el_name.text].update(details_dict)
    restaurants[el_name.text]["busy_times"] = busy_times

    j += 1

# convert to json
restaurants_json = json.dumps(restaurants, indent=4)
print(restaurants_json)

# get date today
today = date.today()
formatted_today = today.strftime("%d-%m-%Y")

# write json file
with open(f"restaurants_{formatted_today}.json", "w") as json_file:
    json_file.write(restaurants_json)

print("Data telah disimpan dalam bentuk JSON!")

# elapsed time
end = time.time()
print("Elapsed time:", int(end - start))

# close driver
driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import math
from threading import Thread
from operator import itemgetter
from datetime import datetime
import os

# Sets up selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1420,1080')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-setuid-sandbox')

data_listed = []
missing_url = []

def write_csv(data_list):
    # Create the csv file
    file_name = "data" + datetime.now().strftime("%Y%m%d") + ".csv"
    f = open(file_name, 'w')
    writer = csv.writer(f, lineterminator='\n')

    data_list = sorted(data_list, key=itemgetter(0))

    # Write header row
    header_row = ["Account#","Principal","Owner","Bank Code","Interest","Address","Deductions","Total","City/State","Int.Date", \
    "Location","B","L","Q","L.Pay Date","Certificate","Date of Sale","Amount","Subsequents","Type","Status","Lien Holder", \
    "Paid_by_0","Paid_by_1","Paid_by_2","Paid_by_3","Paid_by_4","Paid_by_5","Paid_by_6","Paid_by_7","Paid_by_8","Paid_by_9","Paid_by_10","Paid_by_11","Paid_by_12","Paid_by_13","Paid_by_14","Paid_by_15","Paid_by_16","Paid_by_17","Paid_by_18","Paid_by_19","Paid_by_20","Paid_by_21","Paid_by_22","Paid_by_23","Paid_by_24","Paid_by_25","Paid_by_26","Paid_by_27", "Paid_by_28","Paid_by_29", \
    "description_0","description_1","description_2","description_3","description_4","description_5","description_6","description_7","description_8","description_9", \
    "year_0","year_1","year_2","year_3","year_4","year_5","year_6","year_7","year_8","year_9"]

    writer.writerow(header_row)

    # Write rows
    for data in data_list:
        writer.writerow(data)

    # Close the file
    f.close()

def get_data(page_source):
    soup = BeautifulSoup(page_source, "html.parser")

    rows = soup.find_all("div", {"class":"row"})
    list_data = []

    first_row_divs = rows[2].find_all("div")
    account = first_row_divs[1].text.strip()

    # Splitting blq code if possible
    blq = first_row_divs[3].text.strip().split(" / ")
    b_code = ""
    l_code =  ""
    q_code = ""
    if len(blq) > 0:
        b_code = blq[0].lstrip("0")
    if len(blq) > 1:
        l_code = blq[1].lstrip("0")
    if len(blq) > 2:
        q_code = blq[2].lstrip("0")

    principal = first_row_divs[5].text.strip()

    second_row_divs = rows[3].find_all("div")
    owner = second_row_divs[1].text.strip()
    bank_code = second_row_divs[3].text.strip().replace("N/A", "")
    interest = second_row_divs[5].text.strip()

    third_row_divs = rows[4].find_all("div")
    address = third_row_divs[1].text.strip()
    deductions = round(float(third_row_divs[3].text.strip()))
    total = third_row_divs[5].text.strip()

    fourth_row_divs = rows[5].find_all("div")
    city_state = fourth_row_divs[1].text.strip().replace("  ", " ")
    int_date = fourth_row_divs[3].text.strip()

    fifth_row_divs = rows[6].find_all("div")
    location = fifth_row_divs[1].text.strip()
    l_pay_date = fifth_row_divs[3].text.strip()

    # Getting the data from the table
    paid_bys = []
    table_rows = []
    table = soup.find("div", {"class": "col-md-7 col-sm-7 col-md-offset-1 col-sm-offset-1"}).find("table").find("tbody")
    if table:
        table_rows = soup.find("div", {"class": "col-md-7 col-sm-7 col-md-offset-1 col-sm-offset-1"}).find("table").find("tbody").find_all("tr")

    for i in range(30):
        if len(table_rows) > i:
            paid_by = table_rows[i].find_all("td")[9].text.strip()
            paid_bys.append(paid_by)

            continue

        paid_bys.append("")

    descriptions = []
    years = []
    for i in range(10):
        if len(table_rows) > i:
            description = table_rows[i].find_all("td")[3].text.strip()
            descriptions.append(description)

            year = table_rows[i].find_all("td")[0].text.strip()
            years.append(year)
            continue

        descriptions.append("")
        years.append("")

    certificate = ""
    date_of_sale = ""
    amount = ""
    subsequents = ""
    type_data = ""
    status = ""
    lien_holder = ""
    # Getting the addiotanal values
    if soup.find("tr", {"class": "bred"}):
        print("has certificates")
        add_data_rows = soup.find("div", {"class": "col-md-5 col-sm-5 col-md-offset-1 col-sm-offset-1"}).find("table").find("tbody").find("tr").find_all("td")
        certificate = add_data_rows[0].text.strip()
        date_of_sale = add_data_rows[1].text.strip()
        amount = add_data_rows[2].text.strip()
        subsequents = add_data_rows[3].text.strip()
        type_data = add_data_rows[4].text.strip()
        status = add_data_rows[5].text.strip()
        lien_holder = add_data_rows[6].text.strip()

    data_list = [account, principal, owner, bank_code, interest, address, deductions, total, city_state, int_date, location, b_code, l_code, q_code, l_pay_date,
                certificate, date_of_sale, amount, subsequents, type_data, status, lien_holder, *paid_bys, *descriptions, *years]
    return data_list

def get_urls(from_page, to_page):
    urls = []
    def_url = "https://taxes.ci.newark.nj.us"
    for i in range(from_page, to_page):
        url = "https://taxes.ci.newark.nj.us/ViewPay?accountNumber=1"+"{:05d}".format(i)
        urls.append(url)

    return urls

def get_page(f, t):
    # Define driver
    s = Service("./Chromedriver/chromedriver.exe")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    for url in get_urls(f, t):
        print(url)

        try:
            # Open the browser
            driver.get(url)

            # Get the data and store it
            data = get_data(driver.page_source)
            data_listed.append(data)

        except Exception as e:
            # Print out the error
            print("some error: " + str(e))
            print("Didn't get: " + url)
            missing_url.append(url)

    # Close the drive
    driver.close()
    driver.quit()

def get_from_to_accounts():
    # Define driver
    s = Service("./Chromedriver/chromedriver.exe")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    url = "https://taxes.ci.newark.nj.us/?page=1"

    # Setup driver
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    # Get first account
    first_account = soup.find("table", {"class", "table table-bordered"}).find_all("td")[0].text.strip()
    first_account_number = int(first_account[1:])

    # Resetup driver
    last_page = soup.find("div", {"class": "col-md-4 col-md-offset-1"}).find_all("a")[1]["href"].split("=")[1]
    driver.get("https://taxes.ci.newark.nj.us/?page="+last_page)
    soup_accounts = BeautifulSoup(driver.page_source, "html.parser")

    # Get last account
    last_account = soup_accounts.find("table", {"class", "table table-bordered"}).find_all("tr")[-1].find("td").text.strip()
    last_account_number = int(last_account[1:])

    return[first_account_number, last_account_number]


def main():
    # Deleting files from before
    root_files = os.listdir("/home/zikavaclav05/")
    for data_file in root_files:
        if "data" in data_file and not "city" in data_file:
            os.remove("/home/zikavaclav05/" + data_file)

    print("Aplication will get the data between the accounts you enter :)")
    # Get input data
    start_numbers = get_from_to_accounts()
    first_account = start_numbers[0]
    last_account = start_numbers[1]+1
#    last_account = 50
    speed = 1
    #first_account = int(input("First account number (Write only the real number, 100001==1, 102001=2001): "))
    #last_account = int(input("Last account number (Write only the real number, 155321==55321, 104551=4451): "))+1
    #speed = int(input("Speed/Threading - Enter 2-4 for slow pcs, 10 to 20 for fast pcs: "))

    number_of_accounts = int(last_account - first_account)

    # Timing the function
    start_time = time.time()

    # Threading
    max_threads = speed
    threads = []
    start_from = first_account / (number_of_accounts / max_threads)
    for i in range(0, max_threads):
        from_p = int(start_from * (number_of_accounts / max_threads))
        to_p =  int(start_from * (number_of_accounts / max_threads) + (number_of_accounts / max_threads))
        t = Thread(target=get_page, args=(from_p, to_p))
        t.start()
        threads.append(t)
        start_from += 1

    for t in threads:
        t.join()

    write_csv(data_listed)

    # Print out status
    print("Data has been saved to csv")
    print("It took: " + str(round((time.time() - start_time), 2)) + "seconds")
    if missing_url:
        print("These accounts do not exist or we could not get them: ")
    for missing in missing_url:
        print(missing)

if __name__ == "__main__":
    main()


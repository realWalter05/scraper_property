import requests, csv, os
from bs4 import BeautifulSoup
from time import perf_counter
from datetime import datetime

class Property():

    def __init__(self, page: str, city_code: str):
        self.soup = BeautifulSoup(page.content, "html.parser")
        self.soup_main_div = self.soup.find("div", {"class" : "col-md-8"})
        self.city_code = city_code

        # Cadastre data
        self.property_address = None
        self.block = None
        self.lot = None
        self.property_city = None
        self.property_country = None

        # Owner data
        self.owner_name = None
        self.owner_address = None
        self.owner_city_zip = None

        # Details
        self.type = None
        self.building_description = None
        self.year_constructed = None
        self.interior_space = None
        self.acreage = None

        # Taxes date
        self.taxes = None

        # Sales data
        self.sales = []

        if not self.check_found():
            return

        self.set_taxes()
        self.set_cadastre_data()
        self.set_owner_data()
        self.set_details_table_data()
        self.set_sales_data()


    def __repr__(self) -> str:
        return f"""
            Data about property https://www.njparcels.com/property/{self.property_city}/{self.block}/{self.lot} bellow :)
            {self.property_address}, {self.city_code}, {self.block}, {self.lot}, {self.property_country}, {self.taxes}
            {self.owner_name}, {self.owner_address}, {self.owner_city_zip}
            {self.type}, {self.building_description}, {self.year_constructed}, {self.interior_space}, {self.acreage}
            {self.sales}"""


    def check_found(self) -> bool:
        if (self.soup_main_div.find("h1").text == "Search NJ Records"):
            return False
        return True


    def set_cadastre_data(self):
        cadastre_div = self.soup_main_div.find("p", {"class" : "cadastre"})
        cadastre_text = cadastre_div.text

        if not cadastre_text:
            return

        self.property_address = cadastre_div.find("b").text
        self.block = cadastre_text.split("Block ")[1].split(",")[0]
        self.lot = cadastre_text.split("Lot ")[1].split(" ")[0]
        self.property_city = cadastre_text.split("in ")[1].split(",")[0]
        self.property_country = cadastre_text.split(",")[-1][:-1]


    def set_owner_data(self):
        owner_div = self.soup_main_div.find("div", {"class" : "col-sm-6"})

        self.owner_name = owner_div.find("span", {"itemprop" : "name"}).text if owner_div.find("span", {"itemprop" : "name"}) else ""
        self.owner_address = owner_div.find("span", {"itemprop" : "street-address"}).text if owner_div.find("span", {"itemprop" : "street-address"}) else ""
        self.owner_city_zip = f'{owner_div.find("span", {"itemprop" : "locality"}).text if owner_div.find("span", {"itemprop" : "locality"}) else "" }, \
                                {owner_div.find("span", {"itemprop" : "postal-code"}).text if owner_div.find("span", {"itemprop" : "postal-code"}) else "" }'


    def set_details_table_data(self):
        table = self.soup_main_div.find("table", {"class" : "table"})

        self.type = table.find("th", text = "Type").next_sibling.text if table.find("th", text = "Type") else ""
        self.building_description = table.find("th", text = "Building Description").next_sibling.text if table.find("th", text = "Building Description") else ""
        self.year_constructed = table.find("th", text = "Year Constructed").next_sibling.text if table.find("th", text = "Year Constructed") else ""
        self.interior_space = table.find("th", text = "Interior Space (ft2)").next_sibling.text if table.find("th", text = "Interior Space (ft2)") else ""
        self.acreage = table.find("th", text = "Acreage").next_sibling.text if table.find("th", text = "Acreage") else ""


    def set_taxes(self):
        anual_divs = self.soup_main_div.find("div", {"class" : "col-md-7"}).find_all("p")
        for anual_div in anual_divs:
            if "annually in taxes." in str(anual_div):
                self.taxes = anual_div.find("script").text.split('writeCurrency("')[1].split('");')[0]
                return


    def set_sales_data(self):
        sales_page = requests.get(f"http://www.njparcels.com/sales/{self.city_code}_{self.block}_{self.lot}")
        content = sales_page.text.replace("<br>", "</br>")
        soup = BeautifulSoup(str.encode(content), "html.parser")

        sales_tables = soup.find("table", {"class" : "table"})
        if not sales_tables:
            return

        table_trs = sales_tables.find_all("tr")
        for tr in table_trs:
            sale = {}
            tds = tr.find_all("td")
            if not tds:
                continue

            p = tds[0].find_all("p")
            buyer = p[0]
            sale["buyer"] = buyer.find("br").next_sibling

            seller = p[1]
            sale["seller"] = seller.find("br").next_sibling

            deed_date = tds[1]
            date = next(deed_date.children, None).text.replace("\n\t\t", "").split("-")
            sale["deed_date"] = f"{date[2]}.{date[1]}.{date[0]}"

            sale_price = tds[2]
            sale["sale_price"] = sale_price.find("script").text.split('writeCurrency("')[1].split("');")[0]
            self.sales.append(sale)


    def get_buyer_seller_csv_format(self) -> list:
        listed = []
        for sale in self.sales:
            listed.append(sale["buyer"])
            listed.append(sale["seller"])
            listed.append(sale["deed_date"])
            listed.append(sale["sale_price"])
        return listed


    def get_data_csv_format(self):
        return [self.property_address, self.block, self.lot, self.property_city, self.property_country, self.owner_name, self.owner_address, self.owner_city_zip,
                self.type, self.building_description, self.year_constructed, self.interior_space, self.acreage, self.taxes, *self.get_buyer_seller_csv_format()]


class CityProperty():


    def __init__(self, city_code : str):
        self.city_code = city_code
        self.most_property_sales = 0
        self.file_name = ""
        self.city_data = self.get_all_properties_by_city()
        self.properties = self.get_properties()


    def __repr__(self) -> str:
        return f"""
            Data about city with code_code {self.city_code} on page https://www.njparcels.com/property/{self.city_code} bellow :)
            Most property_sales: {self.most_property_sales}
            {self.city_data}
            """


    def get_property(self, block: str, lot: str) -> Property:
        base_url = "http://www.njparcels.com/property/"

        url = base_url + f"/{self.city_code}/{block}/{lot}"
        page = requests.get(url)
        return Property(page, city_code=self.city_code)


    def get_properties(self) -> list:
        listed_properties = []
        for property_data in self.city_data:
            for lot in property_data["lot"]:
                print(f"{self.city_code} - {property_data['block']} - {lot}")
                property = self.get_property(property_data["block"], lot)

                if len(property.sales) > self.most_property_sales:
                    self.most_property_sales = len(property.sales)

                listed_properties.append(property)

        return listed_properties


    def get_lots_by_block(self, block: str) -> list:
        base_url = "http://www.njparcels.com/property/"
        city_page = requests.get(f"{base_url}{self.city_code}/{block}")

        lots = []
        soup = BeautifulSoup(city_page.content, "html.parser")
        properties_table = soup.find("table")
        trs = properties_table.find_all("tr")
        for tr in trs:
            if not tr.find("td"):
                continue
            lots.append(tr.find("td").text.replace("\n", ""))

        return lots


    def get_all_properties_by_city(self) -> list:
        base_url = "http://www.njparcels.com/property/"
        city_page = requests.get(f"{base_url}{self.city_code}")

        properties = []
        soup = BeautifulSoup(city_page.content, "html.parser")
        properties_table = soup.find("table")
        if not properties_table:
            return []
        trs = properties_table.find_all("tr")
        for tr in trs:
            if not tr.find("td"):
                continue
            block = tr.find("td").text
            data = {
                "block" : block,
                "lot" : self.get_lots_by_block(block)
            }
            properties.append(data)
        return properties


    def write_csv(self):
        # Create the csv file
        file_name = f"city{self.city_code}_data" + datetime.now().strftime("%Y%m%d") + ".csv"
        self.file_name = file_name
        f = open("./scraper_property/" + file_name, 'w')
        writer = csv.writer(f, lineterminator='\n')

        # Write header row
        header_row = [
            "Property Address",
            "Block",
            "Lot",
            "Property City",
            "Property county",
            "Owner Name",
            "Owner address",
            "Owner City state zip",
            "Type",
            "Building Description",
            "Year Constructed",
            "Interior Space",
            "Acreage",
            "Taxes",]

        for i in range(0, self.most_property_sales * 4):
            header_row.append(f"Buyer{i}")
            header_row.append(f"Seller{i}")
            header_row.append(f"Deed date{i}")
            header_row.append(f"Sale price{i}")

        writer.writerow(header_row)

        # Write rows
        for property in self.properties:
            writer.writerow(property.get_data_csv_format())

        # Close the file
        f.close()


if __name__ == "__main__":
    start = perf_counter()
    requested = []

    if os.path.exists("requested_properties.txt"):
        with open("requested_properties.txt", "r") as f:
            for line in f.readlines():
                requested.append(line.replace("\n", ""))

        for requested_property in requested:
            city_properties = CityProperty(requested_property)
            city_properties.write_csv()
            print(city_properties)

        end = perf_counter()
        print(f"It took: {end - start} seconds :/")
        print(f"which is {(end - start) / 60} minutes :)")
        os.remove("requested_properties.txt")


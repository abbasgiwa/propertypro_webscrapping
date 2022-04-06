# importing regex, request_HTML and pandas
import requests, re
from requests_html import HTMLSession
import pandas as pd

session = HTMLSession()
# get location within lagos
r = session.get(f'https://www.propertypro.ng/property-for-rent/in/lagos')
lagos_location_text =r.html.find('ul.extra-listings')[2].text.split('\n\n\n')[0].split('|\n')

# iterate throug lagos_location_text  for locations and replace space with '-'
for loc in lagos_location_text:

    l = []
    #removing the space in the locations and adding "-"
    locate = loc.strip().lower().replace(" ", "-")

    print(locate)

    r = session.get(f'https://www.propertypro.ng/property-for-rent/in/lagos/{locate}')

    #getting the areas in the locations
    try:
        area_location_text = r.html.find("div.property-items-name")[0].find("ul.extra-listings")[2].text.split('\n\n\n')[0].split('|\n')
    except IndexError as e:
        area_location_text = [locate]
    for area in area_location_text:
        # strip the name of the area and convert " " to "-"
        area_locate = area.strip().lower().replace(" ", "-")

        # the link of the area
        r = session.get(f'https://www.propertypro.ng/property-for-rent/in/lagos/{locate}/{area_locate}')

#        getting the page of each area
        page = re.findall('\d+',r.html.find('div.property-sale-number >div.property-number-left >h3')[0].text.split('\n')[0])

         # the number pages to iterate through
        try:
            n_of_pages = int(int(page[-1]) / int(page[-2]))
        except ZeroDivisionError:
            n_of_pages = 0
        for page1 in range(n_of_pages):
            r = session.get(f'https://www.propertypro.ng/property-for-rent/in/lagos/{locate}/{area_locate}?page={page1}')

            # properties in an area
            properties = r.html.find('div.single-room-text')

            for i in range(len(properties)):
                d = {}

                # Extracting the neccesssry information about each apartment
                d["location"] = locate
                d["area"] = area_locate

                try:
                    d["pid"] = properties[i].find('div.single-room-text > h2')[0].text.split("\n")[0].split(":")[-1].strip()
                except (IndexError, TypeError, AttributeError):
                    d["pid"] = None
                try:
                    d["date"] = properties[i].find('div.single-room-text > h5')[0].text.split("\n")[0]
                except (IndexError, TypeError, AttributeError):
                    d["date"] = None
                try:
                    d["apartment_status"] = \
                    properties[i].find('div.single-room-text > div.furnished-btn > a')[0].text.split("\n")[0]
                except (IndexError, TypeError, AttributeError, ValueError) as e:
                    d["apartment_status"] = None

                try:
                    d["specific_location"] = properties[i].find('h4')[0].text.split('\n')[0]
                except (IndexError, TypeError, AttributeError):
                    d["location"] = None
                try:
                    d["features"] = properties[i].find('div.fur-areea')[0].text.split('\n')[0]
                except (AttributeError, IndexError) as e:
                    d["features"] = None
                try:
                    d["bed"] = int(re.findall("..bed", properties[i].find('div.fur-areea')[0].text)[0].strip()[0][0])
                except (IndexError, TypeError, AttributeError, ValueError) as e:
                    d["bed"] = 0
                try:
                    d["bath"] = int(re.findall("..bath", properties[i].find('div.fur-areea')[0].text)[0].strip()[0][0])
                except (IndexError, TypeError, AttributeError, ValueError) as e:
                    d["bath"] = 0
                try:
                    d["toilet"] = int(
                        re.findall("..Toilet", properties[i].find('div.fur-areea')[0].text)[0].strip()[0][0])
                except (IndexError, TypeError, AttributeError, ValueError) as e:
                    d["toilet"] = 0
                try:
                    d["description"] = properties[i].find('h3.listings-property-title2')[0].text.split('\n')[0]
                except (IndexError, TypeError, AttributeError) as e:
                    d["description"] = None

                try:
                    d["price"] = \
                    properties[i].find('h3.listings-price')[0].find('h3.listings-price')[0].text.replace("₦ ",
                                                                                                         "").replace(
                        ",", "").split("\n")[0]
                except (IndexError, TypeError, AttributeError) as e:
                    d["price"] = None
                l.append(d)
    # Instantiating Pandas DataFrame with list of dicts
    property_data = pd.DataFrame(l)

    # Saving each location DataFrame to csv file
    property_data.to_csv(f"Lagos_Properties_{locate}.csv", index=False)
    print('collected data for {} location'.format(locate))


# Adding all the CSV together
import os
import pandas as pd
cwd = os.path.abspath('')
files = os.listdir(cwd)
df = pd.DataFrame()
for file in files:
     if file.endswith('.csv'):
            df = df.append(pd.read_csv(file), ignore_index=True)

df.to_csv(f"Lagos_House_prices.csv")

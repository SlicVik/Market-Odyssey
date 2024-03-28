import json
import time

from kivy.atlas import CoreImage
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from urllib import request
from kivy.app import App
from kivy_garden.zbarcam import ZBarCam
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.button import MDRoundFlatIconButton
from kivymd.uix.list import MDList
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, Clock, ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
import firebase_admin
from firebase_admin import db, credentials
from kivyauth.google_auth import initialize_google, login_google, logout_google
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from collections import defaultdict

import sys
import os

import pprint
import urllib
from urllib.request import urlopen

import cv2
from kivymd.uix.snackbar import Snackbar
from pyzbar.pyzbar import decode
from pydub import AudioSegment
from pydub.playback import play

import requests
import webbrowser

maps_api_key = 'AIzaSyCwWnSI1iiQz2Y-oH5U93ch5nDetqkITm8'
places_api_key = 'AIzaSyA0zYRNWfqTgJNIoBpHb8YdpYEHQN5-VZc'

cred = firebase_admin.credentials.Certificate("fbcredentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://moddy-aa743-default-rtdb.firebaseio.com"})

barcodetxt = ""
data = ""
currentList = "testname"

example_json = {
    "products": [
        {
            "barcode_number": "886736874000",
            "barcode_formats": "UPC-A 886736874135, EAN-13 0886736874135",
            "mpn": "CE-XLR3200",
            "model": "XLR",
            "asin": "B01KUHG2G8",
            "title": "Bluetooth Speaker",
            "category": "Media > Books > Print Books",
            "manufacturer": "Xerox",
            "brand": "Xerox",
            "contributors": [
                {
                    "role": "author",
                    "name": "Blake, Quentin"
                },
                {
                    "role": "publisher",
                    "name": "Greenwillow Books"
                }
            ],
            "age_group": "adult",
            "ingredients": "Organic Tapioca Syrup, Organic Dried Cane Syrup, Natural Flavor.",
            "nutrition_facts": "Protein 0 G, Total lipid (fat) 0 G, Energy 300 KCAL, Sugars, total including NLEA 40 G.",
            "energy_efficiency_class": "A+ (A+++ to D)",
            "color": "blue",
            "gender": "female",
            "material": "cloth",
            "pattern": "checkered",
            "format": "DVD",
            "multipack": "8",
            "size": "7 US",
            "length": "45 in",
            "width": "30 in",
            "height": "22 in",
            "weight": "7 lb",
            "release_date": "2003-07-28",
            "description": "One of a kind, Nike Red Running Shoes that are great for walking, running and sports.",
            "features": [
                "Rugged construction",
                "Convenient carrying case",
                "5 year warranty"
            ],
            "images": [
                "https://images.barcodelookup.com/5219/52194594-1.jpg",
                "https://images.barcodelookup.com/5219/52194594-2.jpg",
                "https://images.barcodelookup.com/5219/52194594-3.jpg"
            ],
            "last_update": "2022-03-03 20:28:19",
            "stores": [
                {
                    "name": "Best Buy",
                    "country": "US",
                    "currency": "USD",
                    "currency_symbol": "$",
                    "price": "80.00",
                    "sale_price": "35.99",
                    "tax": [
                        {
                            "country": "US",
                            "region": "US",
                            "rate": "5.00",
                            "tax_ship": "no"
                        }
                    ],
                    "link": "https://www.newegg.com/product-link",
                    "item_group_id": "AB-4312",
                    "availability": "in stock",
                    "condition": "new",
                    "shipping": [
                        {
                            "country": "US",
                            "region": "US",
                            "service": "Standard",
                            "price": "8.49 USD"
                        }
                    ],
                    "last_update": "2021-05-19 09:07:42"
                }

            ],
            "reviews": [
                {
                    "name": "Josh Keller",
                    "rating": "5",
                    "title": "Love these shoes!",
                    "review": "A stylish and great fitting shoe for walking and running.",
                    "date": "2015-03-19 21:48:03"
                }
            ]
        }
    ]
}


class AddFromRecentsScreen(Screen):
    title = StringProperty("Select List")
    current_list_name = StringProperty("")
    current_item_title = StringProperty("")
    current_mode = StringProperty("")

    def on_enter(self):
        # Reference to the current user's "recent_search_list"
        user_recent_search_list_ref = db.reference('Google UIDs/' + glbUID + '/recent_search_list')

        # Get the recent searches data from Firebase
        recent_searches_data = user_recent_search_list_ref.get()

        # Reference to the MDList widget where recent searches will be displayed
        add_from_recents_screen_widget = self.ids.recent_search_list

        # Clear the existing list
        add_from_recents_screen_widget.clear_widgets()

        if recent_searches_data:
            # If there is recent searches data, iterate through it and display each entry
            for entry in recent_searches_data:
                # Extract the "products" field from each JSON entry
                products = entry.get("products", [{}])

                # Check if there is at least one product and its "asin" is not "deleted"
                if products and products[0].get("asin", "") != "deleted":
                    # Extract the "title" field from the first product
                    title = products[0].get("title", "")

                    # Create a OneLineListItem for each recent search entry with the "title" as text
                    list_item = OneLineListItem(text=title)
                    list_item.bind(
                        on_release=lambda instance, title=title: AddFromRecentsScreen.on_list_item_click(self,
                                                                                                         currentList,
                                                                                                         title))
                    add_from_recents_screen_widget.add_widget(list_item)

    def on_list_item_click(self, list_name, item_title):
        print("currentList = " + currentList)
        # Assuming you have the user's UID
        user_uid = glbUID  # Replace with the actual user's UID

        # Call retrieve_item_by_title with the provided list_name and item_title
        json_data = Main.retrieve_item_by_title("recent_search_list", item_title, "recent")

        destination_list_ref = db.reference('Google UIDs/' + user_uid + '/main_list/' + list_name)

        existing_data = destination_list_ref.get()
        print(existing_data)
        # If there is no existing data or it's not a list, initialize the list with the current JSON data
        if existing_data is None or not isinstance(existing_data, list):
            existing_data = [json_data]
        else:
            # Append the current JSON data to the existing list
            existing_data.append(json_data)

        destination_list_ref.set(existing_data)

        Snackbar(
            text='Item Added!',
            snackbar_x='10dp',
            snackbar_y='10dp',
            size_hint_x=(
                                Window.width - (dp(10) * 2)
                        ) / Window.width
        ).open()


class loginScreen(Screen):
    pass


class RecentSearchScreen(Screen):
    def on_enter(self):
        # Reference to the current user's "recent_search_list"
        user_recent_search_list_ref = db.reference('Google UIDs/' + glbUID + '/recent_search_list')

        # Get the recent searches data from Firebase
        recent_searches_data = user_recent_search_list_ref.get()

        # Reference to the MDList widget where recent searches will be displayed
        recent_search_list_widget = self.ids.recent_search_list

        # Clear the existing list
        recent_search_list_widget.clear_widgets()

        if recent_searches_data:
            # If there is recent searches data, iterate through it and display each entry
            for entry in recent_searches_data:
                # Extract the "products" field from each JSON entry
                products = entry.get("products", [{}])

                # Check if there is at least one product and its "asin" is not "deleted"
                if products and products[0].get("asin", "") != "deleted":
                    # Extract the "title" field from the first product
                    title = products[0].get("title", "")

                    # Create a OneLineListItem for each recent search entry with the "title" as text
                    list_item = OneLineListItem(text=title)
                    list_item.bind(
                        on_release=lambda instance, title=title: RecentSearchScreen.on_list_item_click(self, "recent",
                                                                                                       title))
                    recent_search_list_widget.add_widget(list_item)

    def on_list_item_click(self, list_name, item_title):
        # Assuming you have the user's UID
        user_uid = glbUID  # Replace with the actual user's UID

        if 'item_details_screen' in self.manager.screen_names:
            self.manager.remove_widget(self.manager.get_screen('item_details_screen'))

        # Create a new instance of the listItemsScreen
        item_details_screen = ItemDetailsScreen(name='item_details_screen',
                                                current_list_name=list_name,
                                                current_item_title=item_title,
                                                current_mode="recent")
        # Switch to the listItemsScreen
        self.manager.add_widget(item_details_screen)
        # Add the label to the item_details_screen's layout

        # Call retrieve_item_by_title with the provided list_name and item_title
        item_json = Main.retrieve_item_by_title(list_name, item_title, "recent")

        def get_all_key_value_pairs(data, prefix=''):
            all_pairs = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    all_pairs.update(get_all_key_value_pairs(value, prefix + key + '.'))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            all_pairs.update(get_all_key_value_pairs(item, prefix + key + f' {i}: '))
                        else:
                            all_pairs[prefix + key + f' {i}: '] = item
                else:
                    all_pairs[prefix + key] = value
                print(value)
            return all_pairs

        if item_json:
            try:
                # Get the product dictionary
                product = item_json.get("products", [{}])[0]
                flattened_product = get_all_key_value_pairs(product)

                # Create a BoxLayout to hold the list items vertically
                box_layout = MDList()

                # Function to recursively add items for nested data
                def add_items(data, level=0):
                    for key, value in data.items():
                        # Skip empty or non-string values
                        if not value or not isinstance(value, (str, int, float)):
                            continue

                        # Create a TwoLineListItem widget for the field
                        item = TwoLineListItem(text=key, secondary_text=str(value))
                        box_layout.add_widget(item)

                        # If the value is a dictionary, recursively add items
                        if isinstance(value, dict):
                            nested_list = MDList()
                            add_items(value, level + 1)
                            item.add_widget(nested_list)
                        # If the value is a list, recursively add items for each element
                        elif isinstance(value, list):
                            for item_data in value:
                                nested_list = MDList()
                                add_items(item_data, level + 1)
                                item.add_widget(nested_list)

                add_items(flattened_product)

                # Add the BoxLayout to the ListView
                item_details_screen.ids.key_value_pairs.add_widget(box_layout)

            except json.JSONDecodeError:
                # Handle the case where the JSON string is not valid
                print("Invalid JSON format:", item_json)
                return

        self.manager.current = 'item_details_screen'


class AddListScreen(Screen):
    def add_list(self):
        self.manager.current = 'add_list_screen'
        # Get the list name from the input field
        list_name = self.ids.list_name_input.text.strip()

        if list_name:
            # Reference to the current user's "main_list"
            user_main_list_ref = db.reference('Google UIDs/' + glbUID + '/main_list')

            # Add the list name to Firebase with an empty value
            user_main_list_ref.update({list_name: ""})

            # Clear the input field
            self.ids.list_name_input.text = ""

            Snackbar(
                text='List Added!',
                snackbar_x='100dp',
                snackbar_y='10dp',
                size_hint_x=(
                                    Window.width - (dp(10) * 2)
                            ) / Window.width
            ).open()

            # Optionally, you can navigate back to the main screen or perform other actions here
            # Example: app.root.current = "main_screen"
            self.manager.current = "main_screen"
        else:
            # Handle case where the input field is empty
            print("Please enter a list name")


class barcodeScreen(Screen):
    def on_enter(self):
        self.zbarcam = ZBarCam()
        self.add_widget(self.zbarcam)

        # Add an "Exit" button over the camera view
        exit_button = MDRoundFlatIconButton(text="Exit", pos_hint={"center_x": 0.5, "center_y": 0.1})
        exit_button.on_release = self.return_to_main_screen
        self.add_widget(exit_button)

        Clock.schedule_interval(self.read_qr_text, 1)

    def read_qr_text(self, *args):
        """Check if zbarcam.symbols is filled and stop scanning in such case"""
        global barcodetxt
        global data

        if len(self.zbarcam.symbols) > 0:  # when something is detected
            barcodetxt = str(self.zbarcam.symbols[0].data)  # text from QR
            Clock.unschedule(self.read_qr_text, 1)

            mod_path = os.path.dirname(sys.modules['kivy_garden.zbarcam'].__file__)
            zbar_kv_path = os.path.join(mod_path, 'zbarcam.kv')
            Builder.unload_file(zbar_kv_path)

            mod_path = os.path.dirname(sys.modules['kivy_garden.xcamera'].__file__)
            xcam_kv_path = os.path.join(mod_path, 'xcamera.kv')
            Builder.unload_file(xcam_kv_path)

            barcodetxt = barcodetxt[2:-1]

            api_key = "eyjwdwzjosa9b8g8vti1dvxb0ht2rs"
            url = ("https://api.barcodelookup.com/v3/products?barcode=" + barcodetxt + "&formatted=y&key=" + api_key)

            try:
                with request.urlopen(url) as url_response:
                    data = url_response.read().decode()
                    print(data)
                    data_json = json.loads(data)
                    print(data_json)
                    # Save the JSON data as a serialized JSON string
                    Main.save_json_to_recent_search_list(glbUID, data_json)

                    if data_json:
                        try:
                            # Convert the dictionary back to a formatted JSON string
                            formatted_json = json.dumps(data_json, indent=4)
                            print(formatted_json)
                            # Create a label widget to display the formatted JSON string with black font color
                            json_label = Label(text=formatted_json, font_size=16,
                                               color=(0, 0, 0, 1))  # Set font_size and color

                        except json.JSONDecodeError:
                            # Handle the case where the JSON string is not valid
                            print("Invalid JSON format:", data_json)
                            return

                    if 'item_details_screen' in self.manager.screen_names:
                        self.manager.remove_widget(self.manager.get_screen('item_details_screen'))

                    if 'item_details_screen' in self.manager.screen_names:
                        self.manager.remove_widget(self.manager.get_screen('item_details_screen'))

                    # Create a new instance of the listItemsScreen
                    item_details_screen = ItemDetailsScreen(name='item_details_screen')

                    # Switch to the listItemsScreen
                    self.manager.add_widget(item_details_screen)
                    # Add the label to the item_details_screen's layout
                    item_details_screen.ids.key_value_pairs.add_widget(json_label)
                    self.manager.current = 'item_details_screen'



            except Exception as e:
                print(f"Error while fetching data from the URL: {e}")

            # data_file = open("data.json", "w")
            # json.dump(data, data_file, indent=6)
            # self.manager.current = "barcode_results"
            # do something with the barcodeQRtext here

            return self

    def return_to_main_screen(self, *args):
        self.manager.current = 'main_screen'


class listItemsScreen(Screen):
    title = StringProperty()

    def remove_current_list(self):
        # Get a reference to the current user's main list
        user_main_list_ref = db.reference('Google UIDs/' + glbUID + '/main_list')

        # Get the name of the current list
        list_name = self.title

        if list_name:
            # Remove the current list from the Firebase database
            user_main_list_ref.child(list_name).delete()

            Snackbar(
                text='List Removed!',
                snackbar_x='10dp',
                snackbar_y='10dp',
                size_hint_x=(
                                    Window.width - (dp(10) * 2)
                            ) / Window.width
            ).open()

            # Optionally, you can navigate back to the main screen or perform other actions here
            # Example: app.root.current = "main_screen"
            self.manager.current = "main_screen"
        else:
            # Handle the case where the list name is not available
            print("No list name available to remove")

    def on_list_item_click(self, list_name,
                           item_title):  ## This function is called when a user clicks on an item within a list to view its details
        # Assuming you have the user's UID
        user_uid = glbUID  # Replace with the actual user's UID
        if 'item_details_screen' in self.manager.screen_names:
            self.manager.remove_widget(self.manager.get_screen('item_details_screen'))

        item_details_screen = ItemDetailsScreen(name='item_details_screen',
                                                current_list_name=list_name,
                                                current_item_title=item_title,
                                                current_mode="list")

        self.manager.add_widget(item_details_screen)

        # Call retrieve_item_by_title with the provided list_name and item_title
        item_json = Main.retrieve_item_by_title(list_name, item_title, "list")

        def get_all_key_value_pairs(data, prefix=''):
            all_pairs = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    all_pairs.update(get_all_key_value_pairs(value, prefix + key + '.'))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            all_pairs.update(get_all_key_value_pairs(item, prefix + key + f' {i}: '))
                        else:
                            all_pairs[prefix + key + f' {i}: '] = item
                else:
                    all_pairs[prefix + key] = value
                print(value)
            return all_pairs

        if item_json:
            try:
                # Get the product dictionary
                product = item_json.get("products", [{}])[0]
                flattened_product = get_all_key_value_pairs(product)

                # Create a BoxLayout to hold the list items vertically
                box_layout = MDList()

                # Function to recursively add items for nested data
                def add_items(data, level=0):
                    for key, value in data.items():
                        # Skip empty or non-string values
                        if not value or not isinstance(value, (str, int, float)):
                            continue

                        # Create a TwoLineListItem widget for the field
                        item = TwoLineListItem(text=key, secondary_text=str(value))
                        box_layout.add_widget(item)

                        # If the value is a dictionary, recursively add items
                        if isinstance(value, dict):
                            nested_list = MDList()
                            add_items(value, level + 1)
                            item.add_widget(nested_list)
                        # If the value is a list, recursively add items for each element
                        elif isinstance(value, list):
                            for item_data in value:
                                nested_list = MDList()
                                add_items(item_data, level + 1)
                                item.add_widget(nested_list)

                add_items(flattened_product)

                # Add the BoxLayout to the ListView
                item_details_screen.ids.key_value_pairs.add_widget(box_layout)

            except json.JSONDecodeError:
                # Handle the case where the JSON string is not valid
                print("Invalid JSON format:", item_json)
                return

        self.manager.current = 'item_details_screen'


class ItemDetailsScreen(Screen):
    title = StringProperty("Product Details")
    current_list_name = StringProperty("")
    current_item_title = StringProperty("")
    current_mode = StringProperty("")


# 1. Load user generated list
# Define class for storing an item
# Includes name of item and pairs of a retailer and the price at that retailer
# Chose index represents the index of the retailer-price pair to be routed to. Initialized to -1.
class Item:
    def __init__(self, name, retailer_price):
        self.name = name
        self.retailer_price = retailer_price
        self.chosen_index = -1

    def __str__(self):
        retailer_and_prices = [f"({retailer}, {price:.2f})" for retailer, price in self.retailer_price]
        return f"Item: {self.name}, Retailer-Price: {', '.join(retailer_and_prices)}, Chosen Index: {self.chosen_index}"


class directionsScreen(Screen):
    maps_route_url = ""

    def on_pre_enter(self):
        # get list items and locations
        global currentList
        name_location_price_data = self.get_list_items_locations(currentList)
        for item in name_location_price_data:
            print(item)
        item_list = self.parse_name_location_data(name_location_price_data)
        for item in item_list:
            print(item)

        priority = 0
        if priority == 0:
            # Price prioritized:
            # Set chosen_index to the index of the lowest price
            for item in item_list:
                lowest_price = float('inf')  # Initialize to positive infinity
                for index, (_, price) in enumerate(item.retailer_price):
                    if price < lowest_price:
                        lowest_price = price
                        item.chosen_index = index
        elif priority == 1:
            print("Distance priority selected, under development")
        else:
            print("Invalid priority, error")

        # For each item, chosen_index is now set to the index of the retailer-price pair of the chosen retailer
        # Access and print information about the items in the list, including the chosen index
        for item in item_list:
            print(item)

        # Create a dictionary to store items by retailer
        items_by_retailer = defaultdict(list)

        # Iterate through the items and determine which items are available at each retailer
        for item in item_list:
            chosen_index = item.chosen_index
            if chosen_index >= 0:
                chosen_retailer = item.retailer_price[chosen_index][0]
                items_by_retailer[chosen_retailer].append(item.name)
            else:
                # If chosen_index is -1, categorize the item as "Unavailable"
                items_by_retailer["Unavailable"].append(item.name)

        # Create a list of retailer-item pairs
        retailer_item_pairs = [(retailer, items) for retailer, items in items_by_retailer.items()]
        print("RETAILER ITEM PAIRS")
        print(retailer_item_pairs)

        items_location_list = self.ids.items_location_list
        items_location_list.clear_widgets()


        # Create a set to store unique chosen retailers
        chosen_retailers = set()

        # Iterate through the items and add chosen retailers to the set
        # Check is the retailer is a valid location before setting
        # If no valid location, chosen_index remains -1 meaning not available at physical location

        for item in item_list:
            for retailer, _ in item.retailer_price:
                if self.is_valid_location(retailer, places_api_key):
                    print("VALID")
                    chosen_index = item.chosen_index
                    if chosen_index >= 0:
                        chosen_retailer = item.retailer_price[chosen_index][0]
                        chosen_retailers.add(chosen_retailer)
                else:
                    item.chosen_index = -1

        for item in item_list:
            print(item)

                # Create UI elements for each retailer and associated Items
        # Create UI elements for each retailer and associated items
        retailer_list_layout = MDList()

        for item in item_list:
            if(item.chosen_index == -1):
                retailer_item = TwoLineListItem(text = item.name, secondary_text = "Unavailable")
            else:
                retailer_item = TwoLineListItem(text = item.name, secondary_text = item.retailer_price[item.chosen_index][0])


            retailer_list_layout.add_widget(retailer_item)

        # Add the "Unavailable" TwoLineListItem and associated items
        unavailable_items = items_by_retailer["Unavailable"]
        if unavailable_items:
            unavailable_item = TwoLineListItem(
                text="Unavailable:",  # Text for "Unavailable" items
                secondary_text="Items: " + ", ".join(unavailable_items),  # Include item names as secondary text
                size_hint_y=None,
                height=72,
                on_release=lambda x=unavailable_items: self.on_item_click(x),  # Add a callback function on item click
            )
            retailer_list_layout.add_widget(unavailable_item)

        # Add the retailer list layout to your main layout or wherever you want to display it
        self.ids.items_location_list.add_widget(retailer_list_layout)

        # Convert the set to a list of chosen retailers
        chosen_retailers_list = list(chosen_retailers)

        # Print the list of chosen retailers
        print("Chosen Retailers: " + ', '.join(chosen_retailers_list))

        # Generate UI elements to display which item is available at each location

        # 3. Calculate route
        # Get user's current location
        # This requires mobile device specific functionality
        # For testing purposes, use example origin address

        origin_address = 'Parking lot, 1510 N Westwood Ave, Toledo, OH 43607'

        # Get the address of first chosen retailer location nearest to the origin address
        # Next, get the address of the next choen retailer location nearest to the previous chosen retailer location
        # Repeat until all chosen retailer location addresses are found

        # Create a list to store the addresses of the nearest locations in order
        route_addresses = []

        # Initialize the current location to the origin address
        current_location = origin_address

        # Create a list to store the addresses of the nearest locations for the chosen retailers
        route_addresses = []

        # Initialize the starting location as the origin address
        current_location = origin_address

        # Iterate through the list of chosen retailers and determine the address of the nearest location for each retailer
        for retailer in chosen_retailers_list:
            # Use the Geocoding API to get the latitude and longitude for the current location
            geocoding_url = 'https://maps.googleapis.com/maps/api/geocode/json'
            geocoding_params = {
                'address': current_location,
                'key': maps_api_key,
            }

            # Make the Geocoding API request for the current location
            geocoding_response = requests.get(geocoding_url, params=geocoding_params)

            if geocoding_response.status_code == 200:
                geocoding_data = geocoding_response.json()
            if geocoding_data['status'] == 'OK':
                # Extract latitude and longitude for the current location
                location = geocoding_data['results'][0]['geometry']['location']
                location_lat = location['lat']
                location_lng = location['lng']

                # Use the current location coordinates to find the nearest retailer location
                places_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
                places_params = {
                    'location': f'{location_lat},{location_lng}',
                    'radius': 100000,  # Search radius in meters (adjust as needed)
                    'keyword': retailer,
                    'key': places_api_key,
                }

                # Make the Places API request
                places_response = requests.get(places_url, params=places_params)

                if places_response.status_code == 200:
                    places_data = places_response.json()
                    if places_data['status'] == 'OK' and places_data['results']:
                        nearest_retailer = places_data['results'][0]
                        name = nearest_retailer['name']
                        vicinity = nearest_retailer['vicinity']

                        # Add the retailer name and address as a pair to the route_addresses array
                        route_addresses.append((name, vicinity))

        # Print the list of addresses in order
        print("Route Addresses:")
        for address in route_addresses:
            print(address)

        # Define the origin, destination, and waypoints
        origin = origin_address
        destination = origin_address
        waypoints = []
        for _, address in route_addresses:
            waypoints.append(address)

        # Construct the URL for the Directions API request
        url = 'https://maps.googleapis.com/maps/api/directions/json'
        params = {
            'origin': origin,
            'destination': destination,
            'waypoints': '|'.join(waypoints),  # Separate waypoints with '|'
            'mode': 'driving',  # Specify the mode of transportation
            'optimizeWaypoints': 'true',  # Optionally optimize the route
            'key': maps_api_key,
        }

        # Make the API request
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            # if data['status'] == 'OK':
            # Parse and analyze the route information from the JSON response
            # You can access directions, distances, and durations.
            # routes = data['routes']
            # for route in routes:
            # Access information about each leg of the route
            # for leg in route['legs']:
            # print(f"Start Address: {leg['start_address']}")
            # print(f"End Address: {leg['end_address']}")
            # print("Directions:")
            # for step in leg['steps']:
            # print(step['html_instructions'])
            # print(f"Distance: {step['distance']['text']}")
            # print(f"Duration: {step['duration']['text']}")
            # print("---")
            # else:
            # print(f"Directions API request failed with status: {data['status']}")
        else:
            print(f"Directions API request failed with status code: {response.status_code}")

        self.maps_route_url = self.build_google_maps_url(origin_address, waypoints, origin_address)
        # webbrowser.open(maps_route_url)

    def go_to_google_maps(self):
        print("URL: " + self.maps_route_url)
        webbrowser.open(self.maps_route_url)

    def build_google_maps_url(self, origin, waypoints, destination):
        # Ensure that the origin, waypoints, and destination are properly encoded
        origin = origin.replace(" ", "+")
        destination = destination.replace(" ", "+")
        waypoints = [waypoint.replace(" ", "+") for waypoint in waypoints]

        # Join the origin, waypoints, and destination with pipe "|" characters
        waypoints_str = "|".join(waypoints)

        # Construct the URL
        url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints_str}&travelmode=driving"

        return url

    def is_valid_location(self, location_name, api_key):
        # Construct the API request URL to check if the location name is valid
        url = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?' \
              f'input={location_name}&inputtype=textquery&fields=name&key={api_key}'

        # Send the request to the Google Places API
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Check if there are any results
            if 'candidates' in data and len(data['candidates']) > 0:
                return True  # Location name is valid
        return False  # Location name is not valid or there was an error

    def get_list_items_locations(self, list_name):
        # Reference to the current user's main_list
        user_main_list_ref = db.reference('Google UIDs/' + glbUID + '/main_list')

        # Check if the specified list_name exists in the user's main_list
        if list_name in user_main_list_ref.get():
            # If the list exists, fetch its items
            list_items_ref = user_main_list_ref.child(list_name)
            items = list_items_ref.get()

            # Extract and return the data in the desired format
            name_location_data = []
            if isinstance(items, list):
                for item in items:
                    if "products" in item and isinstance(item["products"], list):
                        title = item["products"][0].get("title", "")
                        asin = item["products"][0].get("asin", "")

                        print("title: " + title)
                        location_price_pairs = []

                        for product_info in item["products"]:
                            locations = [store.get("name", "") for store in product_info.get("stores", [])]
                            print("locations: " + str(locations))
                            prices = [store.get("price", "") for store in product_info.get("stores", [])]
                            print("prices: " + str(prices))

                            location_price_pairs.extend(zip(locations, prices))

                        if title and location_price_pairs:
                            if asin != "deleted":
                                name_location_data.append((title, location_price_pairs))
                                print(f"Name: {title}, Location-Price Pairs: {location_price_pairs}")

            return name_location_data
        else:
            # If the list doesn't exist, return an empty list or handle the error as needed
            return []

    def parse_name_location_data(self, name_location_data):
        # Create a list to store Item objects
        item_objects = []

        for title, location_price_pairs in name_location_data:
            converted_pairs = []

            for location, price in location_price_pairs:
                try:
                    # Convert price to float, and handle any exceptions
                    price = float(price)
                    converted_pairs.append((location, price))
                except ValueError:
                    # Handle the case where price is not a valid float
                    print(f"Warning: Skipping invalid price '{price}' for item '{title}'")

            item = Item(title, converted_pairs)
            item_objects.append(item)

        return item_objects


class mainScreen(Screen):
    def on_enter(self):
        self.display_user_list_names()
        Clock.schedule_once(self.set_toolbar_font_name)
        Clock.schedule_once(self.set_toolbar_font_size)

    def set_toolbar_font_name(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Kiona-Regular.ttf"

    def set_toolbar_font_size(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '35sp'

    def display_user_list_names(self):
        user_lists = Main().get_user_list_names()  # Create a new instance of Main class to access the method

        # Reference the MDList widget
        user_lists_widget = self.ids.user_lists

        # Clear the current list
        user_lists_widget.clear_widgets()

        # Populate the MDList with the user's lists
        for list_name in user_lists:
            list_item = OneLineListItem(text=list_name,
                                        secondary_text="List Description")  # You can modify the secondary text as needed
            list_item.bind(on_release=lambda x, list_name=list_name: self.show_list_items(list_name))
            user_lists_widget.add_widget(list_item)

    def show_list_items(self, list_name):

        # Check if a listItemsScreen instance already exists and remove it if so
        if 'list_items_screen' in self.manager.screen_names:
            self.manager.remove_widget(self.manager.get_screen('list_items_screen'))

        # Create a new instance of the listItemsScreen
        list_items_screen = listItemsScreen(name='list_items_screen')
        list_items_screen.title = list_name  # Set the screen title to the selected list name
        global currentList
        currentList = list_name

        # Retrieve the list titles from the database based on the selected list name
        list_titles = Main().get_list_items(list_name)  # Use the updated get_list_items function

        # Reference the MDList widget in the listItemsScreen
        list_items_widget = list_items_screen.ids.list_items

        # Clear the existing list items
        list_items_widget.clear_widgets()

        if list_titles:
            # If the list of titles is not empty, populate the MDList with the titles
            for title in list_titles:
                list_item = OneLineListItem(text=title)
                list_item.bind(
                    on_release=lambda instance, title=title: listItemsScreen.on_list_item_click(self, list_name, title))
                list_items_widget.add_widget(list_item)

        # Switch to the listItemsScreen
        self.manager.add_widget(list_items_screen)
        self.manager.current = 'list_items_screen'

    def get_results(self):
        input_text = self.ids.product_name.text.replace(" ", "%20")
        print(input_text)
        global data

        api_key = "eyjwdwzjosa9b8g8vti1dvxb0ht2rs"
        url = f"https://api.barcodelookup.com/v3/products?search={input_text}&formatted=y&key={api_key}"

        try:
            with request.urlopen(url) as url_response:
                data = url_response.read().decode()
                # Parse the JSON response
                data_json = json.loads(data)

                if data_json and 'products' in data_json:
                    products = data_json['products']
                    for product in products:
                        # Save each product individually to Firebase
                        Main.save_json_to_recent_search_list(glbUID, {'products': [product]})
                        print("Saved product:", product)

        except Exception as e:
            print(f"Error while fetching data from the URL: {e}")

        # app = App.get_running_app()
        self.manager.current = "recent_search_screen"

        return self


class settings(Screen):
    def on_enter(self):
        self.ids.namelbl.text = "My Name: " + gblname
        self.ids.maillbl.text = "My Email: " + gblemail

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self.setToolbarFont)
        Clock.schedule_once(self.setToolbarFontSize)

    def logout(self):
        logout_google(self.after_logout)

    def after_logout(self):
        self.manager.current = "login_screen"

    def setToolbarFont(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Kiona-Regular.ttf"

    def setToolbarFontSize(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '35sp'


class SlideshowScreen(Screen):
    def on_enter(self):
        pass

class Main(MDApp):

    def build(self):
        client_id = open("client_id.txt")
        client_secret = open("client_secret.txt")
        initialize_google(self.after_login, self.error_listener, client_id.read(), client_secret.read())
        Builder.load_file("my.kv")
        sm = ScreenManager()
        sm.add_widget(loginScreen(name='login_screen'))
        sm.add_widget(mainScreen(name='main_screen'))
        sm.add_widget(settings(name='settings'))
        sm.add_widget(barcodeScreen(name='barcode_screen'))
        sm.add_widget(AddListScreen(name='add_list_screen'))
        sm.add_widget(RecentSearchScreen(name='recent_search_screen'))
        sm.add_widget(ItemDetailsScreen(name='item_details_screen'))
        sm.add_widget(directionsScreen(name='directions_screen'))
        sm.add_widget(AddFromRecentsScreen(name='add_from_recent_search_screen'))
        sm.add_widget(SlideshowScreen(name='slideshow_screen'))

        return sm

    def on_start(self):
        pass

    def movetosetting(self):
        self.root.current = "settings"

    def movetomain(self):
        self.root.current = "main_screen"

    def move_to_recent_search(self):
        self.root.current = "recent_search_screen"

    def move_to_add_from_recent_search(self):
        self.root.current = "add_from_recent_search_screen"

    def movetolistitemsscreen(self):
        self.root.current = "item_details_screen"

    def move_to_directions_screen(self):
        self.root.current = "directions_screen"

    def error_listener(self):
        pass

    def login(self):
        login_google()

    def after_login(self, name, email, photo_uri):
        user_ref = db.reference('Google UIDs')  # Reference to the "Google UIDs" node in the database
        user_uid = None

        # Check if the Google account is already in the database
        existing_users = user_ref.get()

        if existing_users is not None:
            for uid, user_data in existing_users.items():
                if user_data.get('email') == email:
                    user_uid = uid
                    break

        if user_uid is None:
            # User not found in the database, create a new entry
            new_user_ref = user_ref.push()  # Create a new node with a unique key
            user_uid = new_user_ref.key
            new_user_ref.set({
                'name': name,
                'email': email,
                'photo_uri': photo_uri,
                'main_list': {
                    'Example List': [example_json]  # Add the "Example List" with example_json data
                },
                'recent_search_list': [example_json]  # Add the "Example List" with example_json data

            })

        # Set the user's Google UID
        global glbUID
        glbUID = user_uid

        # Set the global variables
        global gblname
        gblname = name

        global gblemail
        gblemail = email

        global gblephoto_uri
        gblephoto_uri = photo_uri

        self.root.current = "main_screen"

    def get_user_list_names(self):
        # Reference to the current user's "main_list"
        user_main_list_ref = db.reference('Google UIDs/' + glbUID + '/main_list')

        # Get the keys (list names) under the "main_list" node
        list_names = user_main_list_ref.get()

        if list_names:
            return list(list_names.keys())
        else:
            return []  # Return an empty list if there are no keys (list names)

    def get_list_items(self, list_name):
        # get the title of every product saved under a list name
        # Reference to the current user's main_list
        user_main_list_ref = db.reference('Google UIDs/' + glbUID + '/main_list')

        # Check if the specified list_name exists in the user's main_list
        if list_name in user_main_list_ref.get():
            # If the list exists, fetch its items
            list_items_ref = user_main_list_ref.child(list_name)
            items = list_items_ref.get()

            # Extract and return the titles for each JSON item
            titles = []
            if isinstance(items, list):
                for item in items:
                    # Check if "products" is a list with at least one item and if that item has a "title"
                    if "products" in item and isinstance(item["products"], list) and len(item["products"]) > 0:
                        title = item["products"][0].get("title", "")
                        asin = item["products"][0].get("asin", "")
                        if asin != "deleted":
                            titles.append(title)
                            print(title)
            return titles
        else:
            # If the list doesn't exist, return an empty list or handle the error as needed
            return []

    def save_json_to_recent_search_list(user_uid, json_data):
        # Reference to the current user's "recent_search_list"
        user_recent_search_list_ref = db.reference('Google UIDs/' + user_uid + '/recent_search_list')

        # Get the existing data from the recent_search_list
        existing_data = user_recent_search_list_ref.get()

        # If there is no existing data or it's not a list, initialize the list with the current JSON data
        if existing_data is None or not isinstance(existing_data, list):
            existing_data = [json_data]
        else:
            # Append the current JSON data to the existing list
            existing_data.append(json_data)

        user_recent_search_list_ref.set(existing_data)

    def retrieve_item_by_title(list_name, item_title, mode):
        # Assuming you have already initialized Firebase Admin with your database URL
        print(item_title)
        print(list_name)
        # Construct the reference path based on the current user and list_name
        user_uid = glbUID  # Replace with the actual user's UID

        if mode == "list":
            ref_path = f'Google UIDs/{user_uid}/main_list/{list_name}'
        elif mode == "recent":
            ref_path = f'Google UIDs/{user_uid}/recent_search_list'

        # Create a reference to the specified location in the database
        ref = db.reference(ref_path)
        i = 0
        while True:
            sub_ref_path = f'{ref_path}/{i}'
            sub_ref = db.reference(sub_ref_path)
            item_data = sub_ref.get()
            title_path = f'{sub_ref_path}/{"products"}/{0}/{"title"}'
            title_ref = db.reference(title_path)
            title = title_ref.get()
            print(title)
            if item_data is None:
                break  # Exit the loop if there's no more data

            # Check if the "title" field in the JSON data matches the desired title
            if title == item_title:
                print(item_data)
                return item_data
                break  # Exit the loop if the title matches

            i += 1

    def remove_item_from_list(self, list_name, item_title, mode):
        # Construct the reference path based on the current user and list_name
        user_uid = glbUID  # Replace with the actual user's UID

        if mode == "list":
            ref_path = f'Google UIDs/{user_uid}/main_list/{list_name}'
        elif mode == "recent":
            ref_path = f'Google UIDs/{user_uid}/recent_search_list'

        # Create a reference to the specified location in the database
        ref = db.reference(ref_path)
        i = 0
        while True:
            sub_ref_path = f'{ref_path}/{i}'
            sub_ref = db.reference(sub_ref_path)
            item_data = sub_ref.get()
            title_path = f'{sub_ref_path}/{"products"}/{0}/{"title"}'
            title_ref = db.reference(title_path)
            title = title_ref.get()
            print(title)
            if item_data is None:
                break  # Exit the loop if there's no more data

            # Check if the "title" field in the JSON data matches the desired title
            if title == item_title:
                product_path = f'{sub_ref_path}/{"products"}'
                product_ref = db.reference(product_path)
                product_ref.set({"0": {"asin": "deleted"}})
                break  # Exit the loop if the title matches

            i += 1

        Snackbar(
            text='Item Removed!',
            snackbar_x='10dp',
            snackbar_y='10dp',
            size_hint_x=(
                                Window.width - (dp(10) * 2)
                        ) / Window.width
        ).open()

        self.root.current = "main_screen"

    def add_item_to_list(json_data, list_name):
        user_recent_search_list_ref = db.reference('Google UIDs/' + glbUID + '/main_list/' + list_name)

        # Get the existing data from the recent_search_list
        existing_data = user_recent_search_list_ref.get()

        # If there is no existing data or it's not a list, initialize the list with the current JSON data
        if existing_data is None or not isinstance(existing_data, list):
            existing_data = [json_data]
        else:
            # Append the current JSON data to the existing list
            existing_data.append(json_data)

        user_recent_search_list_ref.set(existing_data)


if __name__ == "__main__":
    Main().run()

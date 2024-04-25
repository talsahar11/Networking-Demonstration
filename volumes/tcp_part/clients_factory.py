import random

# List of all the first names we generate the random clients names from
first_names = ["Jonny", "Yehuda", "Yehudit", "Yoram", "Yohai", "Shuli", "Shmulik", "Dorimon", "Ahuva", "Tikva",
               "Najira", "Ehud", "Benny", "Alma", "Yehoyahin", "Metushelah", "Dror", "Dorit", "Hen", "Hanania", "Gal",
               "Liron", "Liran", "Liroy", "Matan", "Yael", "Yahli", "Niv", "Nir", "Nirit", "Irit", "Iris", "Zohar",
               "Ofer", "Tamir", "Ovadia", "Dor", "Shimon", "Liam", "Emma","Emma", "Liam", "Olivia", "Noah", "Ava",
               "Ethan", "Sophia", "Mason", "Isabella", "Logan", "Mia", "Lucas", "Charlotte", "Jackson", "Amelia",
               "Aiden", "Harper", "Elijah", "Abigail", "Caden", "Emily", "Grayson", "Ella", "Michael", "Avery",
               "Caleb", "Madison", "Benjamin", "Scarlett", "Jacob", "Victoria", "Levi", "Aria", "Luke", "Chloe",
               "Alexander", "Grace", "Owen", "Hannah", "Daniel", "Natalie", "Jack", "Lily", "William", "Addison",
               "Ryan", "Evelyn", "Jayden", "Brooklyn", "Gabriel", "Zoe", "Nicholas", "Audrey", "Isaac", "Savannah",
               "Anthony", "Anna", "Joseph", "Aaliyah", "David", "Ellie", "Ezra", "Stella", "Adam", "Bella", "Wyatt",
               "Makayla", "Christopher", "Maya", "Isabelle", "Violet", "Sebastian", "Claire", "Samuel", "Lucy", "Henry",
               "Lila", "Julian", "Layla", "Cameron", "Peyton", "Jaxon", "Sofia", "Leah", "Alexa", "Zachary", "Aubrey",
               "Ian", "Mila", "Enrika", "Henery", "Josh", "George"]

# List of all the last names we generate the random clients name from
last_names = ["Gold", "Silver", "Bronze", "Zilberg", "Goldman", "Silverman", "Bronzman", "Galili", "Sahar", "Nahshun",
              "Cohen", "Levi", "Mizrahi", "Zilberman", "Emanuel", "Shmuelovich", "Shushan", "Thzvi", "Bokra", "Ohana",
              "Abrams", "Adler", "Bach", "Baum", "Becker", "Berkowitz", "Blum", "Cohen", "Davidson", "Eisenberg",
              "Epstein", "Feinberg", "Feldman", "Finkelstein", "Fishman", "Friedman", "Geller", "Gershon", "Glick",
              "Goldberg", "Goldman", "Goldstein", "Gordon", "Greenberg", "Gross", "Gurevich", "Hoffman", "Horowitz",
              "Isaacson", "Jacobson", "Kaplan", "Katz", "Klein", "Kramer", "Krause", "Kleinman", "Levine", "Levy",
              "Lieberman", "Mandel", "Marcus", "Meyer", "Miller", "Moses", "Nathan", "Neumann", "Newman", "Orlov",
              "Oren", "Ostrovsky", "Perelman", "Pollack", "Rabinowitz", "Rappaport", "Rosen", "Rosenberg", "Roth",
              "Rubin", "Sandler", "Schwartz", "Shapiro", "Shein", "Sherman", "Shulman", "Silver", "Silverman", "Simon",
              "Sokoloff", "Solomon", "Spector", "Stein", "Steinberg", "Steiner", "Stern", "Stolowitz", "Taub",
              "Teitelbaum", "Weinberg", "Weiner", "Weinstein", "Wexler", "Wolfe", "Yakobson", "Yudin", "Zeldin",
              "Zimmerman"]

# List of all the phone prefixes we generate the random clients phone numbers from
phone_prefix = ["050", "052", "053", "054", "055"]

# List of all the cities we generate the random city from
cities = ["Rishon Le Zion", "Raanana", "Petah Tikva", "Jerusalem", "Mazkeret Batya", "Lehavot Ha Bashan", "Herzelia",
          "Bat Yam", "Ashkelon", "Beer Sheva", "Modiin", "Tiberias", "Yeruham", "Ariel", "Rosh Ha-Ayin", "Eilat",
          "Haifa", "Kfar Saba", "Hod Ha-Sharon", "Nes Tziona", "Rehovot", "Tel Aviv"]

# Sizes of the lists
first_names_len = len(first_names)
last_names_len = len(last_names)
phone_prefix_len = len(phone_prefix)
cities_len = len(cities)


# Client class - represent a client as it being stored in the database
class Client:
    def __init__(self, first_name, last_name, cid, phone_number, age, city):
        self.cid = cid
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.age = age
        self.city = city

    def __repr__(self):
        return f"Client(first_name={self.first_name}, last_name={self.last_name}, cid={self.cid}," \
               f" phone_number={self.phone_number}, age={self.age}, city={self.city})"


def scan_client():
    cid = int(input("Enter the client's ID:"))
    first_name = input("Enter the client's first name:")
    last_name = input("Enter the client's last name:")
    phone_number = input("Enter the client's phone number:")
    age = int(input("Enter the client's age:"))
    city = input("Enter the client's city:")
    client = Client(first_name, last_name, cid, phone_number, age, city)
    return client


def update_client(client):
    while True:
        option = input("Select the field to update: \n 1 - ID \n 2 - First name \n 3 - Last name \n 4 - Phone number"
                       "\n 5 - Age \n 6 - City \n\n To save the changes and proceed, enter 's'")
        if option == '1':
            cid = int(input("Enter the new ID:"))
            client.cid = cid
        elif option == '2':
            first_name = input("Enter the new first name:")
            client.first_name = first_name
        elif option == '3':
            last_name = input("Enter the new last name:")
            client.last_name = last_name
        elif option == '4':
            phone_number = input("Enter the new phone number:")
            client.phone_number = phone_number
        elif option == '5':
            age = int(input("Enter the new age:"))
            client.age = age
        elif option == '6':
            city = input("Enter the new city:")
            client.city = city
        elif option == 's':
            break
        else:
            print("Unsupported option, please try again.")
    return client


# Struct a client instance from a data returned from the mysql server
def struct_client_from_data(client_data):
    values = values_list = list(client_data.values())
    client = Client(values[1], values[2], values[3], values[4], values[5], values[6])
    return client


# Generate random client
def generate_client():
    first_name = first_names[random.randint(0, first_names_len - 1)]
    last_name = last_names[random.randint(0, last_names_len - 1)]
    city = cities[random.randint(0, cities_len - 1)]
    cid = random.randint(100000000, 999999999)
    phone_number = f'{phone_prefix[random.randint(0, phone_prefix_len - 1)]}-{str(random.randint(1000000, 9999999))}'
    age = random.randint(19, 80)
    client = Client(first_name, last_name, cid, phone_number, age, city)
    return client


# Generate a specified number of random clients
def generate_clients(number_of_clients):
    clients = list()
    for i in range(number_of_clients):
        clients.append(generate_client())
    return clients

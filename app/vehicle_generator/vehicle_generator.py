import csv
import datetime as dt
import random
import sys
from typing import List, Callable, Tuple
from uuid import uuid4

from app.data_plates_generator.prefix_getter import PrefixGetter
from app.models.model import Crud

# TODO: Add functions to export generated data directly to database
class VehicleGenerator:
    @staticmethod
    def gen_numbers() -> Tuple[List[int],List[int]]:
        gen_nums: List[int] = [random.randint(0, 9) for _ in range(4)]
        cs_nums: List[int] = [num * (5 - index) for index, num in enumerate(gen_nums)]

        return gen_nums, cs_nums

    @staticmethod
    def car_plate() -> str:
        """
        Generate passenger vehicle number plate

        Checksum:
        where A=1 and Z=26,
        Each individual number is then multiplied
        by 6 fixed numbers (9, 4, 5, 4, 3, 2)

        These are added up, then divided by 19.
        19 letters used
        (A, Z, Y, X, U, T, S, R, P, M, L, K, J, H, G, E, D, C, B)
        with "A" corresponding to a remainder of 0,
        "Z" corresponding to 1, "Y" corresponding to 2 and so on
        """

        prefix: str = PrefixGetter.get_cars_plate_prefix()
        exception = "SKY"

        if prefix == exception: #TODO find solution for this edge case
            pass

        gen_nums, cs_nums = VehicleGenerator.gen_numbers()

        number_associate_second_letter = (ord(prefix[1].lower()) - 96) * 9
        number_associate_third_letter = (ord(prefix[2].lower()) - 96) * 4
        compute = number_associate_second_letter + number_associate_third_letter + sum(cs_nums)
        number = ''.join(str(num) for num in gen_nums)

        # TODO: Handle Value Error
        suffix = VehicleGenerator.get_suffix(compute)
        compete = prefix + number + suffix

        return compete

    @staticmethod
    def goods_plate() -> str:
        # Generates number plate for a commercial vehicle

        gen_nums, cs_nums = VehicleGenerator.gen_numbers()
        prefix = PrefixGetter.get_good_plate_prefix()

        if len(prefix) == 2:
            cs_alp2 = (ord(prefix[0].lower()) - 96) * 9
            cs_alp3 = (ord(prefix[1].lower()) - 96) * 4

        else:
            cs_alp2 = (ord(prefix[1].lower()) - 96) * 9
            cs_alp3 = (ord(prefix[2].lower()) - 96) * 4

        compute = cs_alp2 + cs_alp3 + sum(cs_nums)
        number = ''.join(str(num) for num in gen_nums)

        # TODO: Handle Value Error
        suffix = VehicleGenerator.get_suffix(compute)
        compete = prefix + number + suffix

        return compete


    @staticmethod
    def get_suffix(num) -> str:
        compute_dict = {
            0  : 'A',
            1  : 'Z',
            2  : 'Y',
            3  : 'X',
            4  : 'U',
            5  : 'T',
            6  : 'S',
            7  : 'R',
            8  : 'P',
            9  : 'M',
            10 : 'L',
            11 : 'K',
            12 : 'J',
            13 : 'H',
            14 : 'G',
            15 : 'E',
            16 : 'D',
            17 : 'C',
            18 : 'B'
        }

        if num % 19 in compute_dict:
            return compute_dict[num % 19]
        else:
            raise ValueError("Error generating suffix please enter a valid number")


    @staticmethod
    def generate_expiry_date():
        # Generate random date ranging between today and next year today.'

        random_days = random.randrange(0, 365)
        random_date = dt.timedelta(days=random_days)

        return dt.datetime.today().date() + random_date


    @staticmethod
    def final_plate_generator(number, typeof=None) -> List[str]:
        # function responsible for generating a numberplate
        # param 1: number -> amount of plates to be generated
        # param 2: optional -> takes car or goods as input to generate corresponding type of plate
        # else autopicks

        generate_type = None
        cars: List[str] = []

        if not typeof:
            plate_generators: List[Callable] = [VehicleGenerator.car_plate, VehicleGenerator.goods_plate]
            random_int: int = random.randint(0, len(plate_generators) - 1)
            generate_type = plate_generators[random_int]

        elif typeof == "cars":
            generate_type = VehicleGenerator.car_plate

        else:
            generate_type = VehicleGenerator.goods_plate

        for _ in range(number):
            new_license_plate: str = generate_type()
            cars.append(new_license_plate)

        return cars


    @staticmethod
    def csv_writer(entries, typeof=None):
        """
        write a list of random generated vehicle number and road-tax expiry date
        to a CSV file with filename as "roadtax.csv"

        args:
            refer to generate(number, typeof = None) for more info
        """

        with open('../store/roadtax.csv', 'w+', newline='') as f:
            fieldnames = ['VehicleID', 'CarPlate', 'ExpiryDate']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            items = VehicleGenerator.final_plate_generator(entries, typeof)
            writer.writeheader()
            for item in items:
                writer.writerow(
                    {'VehicleID': f"{uuid4()}", 'CarPlate': f"{item}", 'ExpiryDate': f"{VehicleGenerator.generate_expiry_date()}"})


    @staticmethod
    def database_upload(entries, typeof=None):
        """
        write a list of random generated vehicle number and road-tax expiry date
        to a Sqlite3 database with filename as "roadtax_date.db" according to
        model.py

        args:
            refer to generate(number, typeof = None) for more info
        """
        c = Crud
        items = VehicleGenerator.final_plate_generator(entries, typeof)

        for item in items:
            c.create_vehicle(uuid4(), item, VehicleGenerator.generate_expiry_date())

    @staticmethod
    def main():
        """
        running as a script.
            --> no arg provided, auto generate 100 random vehicle numbers
            --> number of vehicle number provided, generate number with random
                type
            --> number of vehicle and type provided, generate number with that
                named type. refer to generate function for typeof keywords
        """

        if len(sys.argv) == 2:
            VehicleGenerator.final_plate_generator(int(sys.argv[1]))
            input(
                f"{sys.argv[1]} random vehicle generated. Press any key to continue..")
        elif len(sys.argv) > 2:
            VehicleGenerator.final_plate_generator(int(sys.argv[1]), sys.argv[2])
            input(
                f"{sys.argv[1]} random vehicle generated. Press any key to continue..")
        else:
            VehicleGenerator.final_plate_generator(100)
            VehicleGenerator.csv_writer(100) # Create csv file while generating values
            # Create Entries in Database(road-tax_date) table('vehicle') With the help of model class
            VehicleGenerator.database_upload(100)
            input(f"{100} random vehicle generated. Press any key to continue..")


if __name__ == '__main__':
    VehicleGenerator.main()

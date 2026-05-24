from datetime import timedelta
from peewee import Model, SqliteDatabase, CharField, DateField, BooleanField, IntegrityError
import datetime as dt

db = SqliteDatabase('../store/roadtax_date.db')


class Vehicle(Model):
    vehicle_id = CharField(primary_key=True)
    vehicle_no = CharField(null=False)
    expiry_date = DateField(null=False)
    is_informed = BooleanField(default=False)
    is_inspected = BooleanField(default=False)
    is_renewed = BooleanField(default=False)

    class Meta:
        database = db


def date_parse(date_input):

    if isinstance(date_input, dt.date):
        return date_input

    if isinstance(date_input, str):

        formats = [
            "%d-%m-%Y",
            "%Y-%m-%d"
        ]

        for fmt in formats:
            try:
                return dt.datetime.strptime(
                    date_input,
                    fmt
                ).date()

            except ValueError:
                continue

    raise ValueError(
        "Date cannot be Parsed. Please provide a valid date."
    )


class Crud:

    @classmethod
    def create_vehicle(cls, vehicle_id, vehicle_no, expiry_date) -> str:
        # creates a new vehicle entry in db when called.

        db.create_tables([Vehicle], safe=True)
        try:
            parsed_date = expiry_date

        except ValueError:
            manual_date_input = input("Enter date manually: ")
            parsed_date = date_parse(manual_date_input)

        try:
            Vehicle.create(
                vehicle_id=vehicle_id,
                vehicle_no=vehicle_no,
                expiry_date=parsed_date
            )
            return "New record created"

        except IntegrityError:
            Vehicle.update(expiry_date=parsed_date).where(Vehicle.vehicle_id == vehicle_id).execute()
            return "Attempting to make change to existing vehicle."


    @classmethod
    def sort_all(cls):
        # sorts all the entries according to expiry_dates

        return list(
            Vehicle.select(
                Vehicle.vehicle_id,
                Vehicle.vehicle_no,
                Vehicle.expiry_date
            ).order_by(Vehicle.expiry_date).tuples()
        )


    @classmethod
    def sort_within(cls, start_date, end_date):

        query = (
            Vehicle.select().where(
                (Vehicle.expiry_date >= start_date) & (Vehicle.expiry_date <= end_date)
            ).order_by(
                Vehicle.expiry_date
            )
        ).tuples()

        return list(query)


    @classmethod
    def update_checks(cls, data: Vehicle):
        if not data:
            return None

        Vehicle.update(
            is_informed = data.is_informed,
            is_inspected = data.is_inspected,
            is_renewed = data.is_renewed,
            expiry_date = data.expiry_date + timedelta(days=183)
        ).where(Vehicle.vehicle_id == data.vehicle_id).execute()

        if data.is_renewed and data.is_informed and data.is_inspected:
            return f"{data.vehicle_no} renewed, expiry date updated to 6 months from now."

        return f"{data.vehicle_no} updated"

    @classmethod
    def delete(cls, vehicle_id) -> str | None:
        if not vehicle_id:
            return None

        del_entry = Vehicle.delete().where(Vehicle.vehicle_id == vehicle_id).execute()
        return f"Vehicle with id {vehicle_id} deleted successfully."

db.connect()
c = Crud
print(c.sort_all())
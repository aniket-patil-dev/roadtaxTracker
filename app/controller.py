from models.model import Crud

c = Crud()

def add_new(vehicle_id, vehicle_no, expiry):
    add_item = c.create_vehicle(vehicle_id, vehicle_no, expiry)
    return add_item


def sort_all():
    sorted_list = c.sort_all()
    return list(sorted_list)


def sort_show_vehicle():
    sorted_list = c.sort_all()
    list_vehicle = []
    for row in sorted_list:
        list_vehicle.append(row[0])
    return list_vehicle


def show_within(day_arg):
    sorted_list = c.sort_within(day_arg)
    return sorted_list


def update_checks(vehicle, expiry, inform, inspect, renew):
    update_item = c.update_checks(vehicle, expiry, inform, inspect, renew)
    return update_item


def delete_item(vehicle):
    del_it = c.delete_item(vehicle)
    return del_it

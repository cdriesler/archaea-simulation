import sys
import os
import getopt
import subprocess
from archaea.geometry.point3d import Point3d

from specklepy.api.client import Account, SpeckleClient
from specklepy.api import operations
from specklepy.api.credentials import get_default_account
from specklepy.transports.server import ServerTransport
from specklepy.objects.geometry import Mesh, Base

from archaea_simulation.simulation_objects.domain import Domain
from archaea_simulation.utils.path import get_cfd_export_path
from archaea_simulation.simulation_objects.courtyard_building import CourtyardBuilding


def cfd_stl_export(argv):
    # Default values
    arg_name = "test"
    arg_exec = False
    arg_domain_width = 50.0
    arg_domain_depth = 100.0
    arg_domain_height = 50.0
    arg_number_of_storeys = 1
    arg_number_of_rooms = 3
    arg_courtyard_width = 10.0
    arg_room_width = 4.0
    arg_room_depth = 4.0
    arg_room_height = 3.0
    arg_room_wall_thickness = 0.1
    arg_room_window_existence = 1
    arg_room_window_width = 0.6
    arg_room_window_height = 1.2
    arg_room_door_existence = 1
    arg_room_door_width = 0.8
    arg_room_door_height = 2.0

    arg_help = "{0}\n\n" \
               "Welcome to stl exporter program for cfd calculations! \n" \
               "Use below flags to generate stl.\n" \
               " -n\t--name                        <name>                    default: test\n" \
               " -x\t--exec                        <exec>                    default: 0\n" \
               " -dw\t--domain-width               <domain_width>            default: 100.0\n" \
               " -dd\t--domain-depth               <domain_depth>            default: 50.0\n" \
               " -dh\t--domain-height              <domain_height>           default: 50.0\n" \
               " -nos\t--number-of-storeys         <number_of_storeys>        default: 1\n" \
               " -nor\t--number-of-rooms           <number_of_rooms>          default: 3\n" \
               " -cw\t--courtyard-width            <courtyard_width>         default: 10.0\n" \
               " -rw\t--room-width                 <room_width>              default: 4.0\n" \
               " -rd\t--room-depth                 <room_depth>              default: 4.0\n" \
               " -rh\t--room-height                <room_height>             default: 3.0\n" \
               " -rwt\t--room-wall-thickness       <room_wall_thickness>      default: 0.1\n" \
               " -rwe\t--room-window-existence     <room_window_existence>    default: 1\n" \
               " -rww\t--room-window-width         <room_window_width>        default: 0.6\n" \
               " -rwh\t--room-window-height        <room_window_height>       default: 1.2\n" \
               " -rde\t--room-door-existence       <room_door_existence>      default: 1\n" \
               " -rdw\t--room-door-width           <room_door_width>          default: 0.8\n" \
               " -rdh\t--room-door-height          <room_door_height>         default: 2.0\n".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "hxn:hdw:dd:dh:nos:nor:cw:rw:rd:rh:rwt:rwe:rww:rwh:rde:rdw:rdh:",
                                   ["help",
                                    "exec",
                                    "name=",
                                    "domain-width=",
                                    "domain-depth=",
                                    "domain-height=",
                                    "number-of-storeys=",
                                    "number-of-rooms=",
                                    "courtyard-width=",
                                    "room-width=",
                                    "room-depth=",
                                    "room-height=",
                                    "room-wall-thickness=",
                                    "room-window-existence=",
                                    "room-wall-width=",
                                    "room-wall-height=",
                                    "room-door-existence=",
                                    "room-door-width=",
                                    "room-door-height="])
    except ValueError:
        print(arg_help)
        sys.exit(2)

    # if user does not provide any argument, print help message
    if len(opts) == 0:
        print(arg_help)  # print the help message
        print("NOTE: Stl generated with default parameters because no argument provided.\n")

    # Find the upcoming flag and set it to it's value
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-n", "--name"):
            arg_name = arg
        elif opt in ("-x", "--exec"):
            arg_exec = True
        elif opt in ("-dw", "--domain-width"):
            arg_domain_width = arg
        elif opt in ("-dd", "--domain-depth"):
            arg_domain_depth = arg
        elif opt in ("-dh", "--domain-height"):
            arg_domain_height = arg
        elif opt in ("-nos", "--number-of-storeys"):
            arg_number_of_storeys = arg
        elif opt in ("-nor", "--number-of-rooms"):
            arg_number_of_rooms = arg
        elif opt in ("-cw", "--courtyard-width"):
            arg_courtyard_width = arg
        elif opt in ("-rw", "--room-width"):
            arg_room_width = arg
        elif opt in ("-rd", "--room-depth"):
            arg_room_depth = arg
        elif opt in ("-rh", "--room-height"):
            arg_room_height = arg
        elif opt in ("-rwt", "--room-wall-thickness"):
            arg_room_wall_thickness = arg
        elif opt in ("-rwe", "--room-window-existence"):
            arg_room_window_existence = arg
        elif opt in ("-rww", "--room-window-width"):
            arg_room_window_width = arg
        elif opt in ("-rwh", "--room-window-height"):
            arg_room_window_height = arg
        elif opt in ("-dwe", "--door-window-existence"):
            arg_room_door_existence = arg
        elif opt in ("-dww", "--door-window-width"):
            arg_room_door_width = arg
        elif opt in ("-dwh", "--door-window-height"):
            arg_room_door_height = arg

    courtyard_building = CourtyardBuilding(
        Point3d.origin(),
        int(arg_number_of_storeys),
        int(arg_number_of_rooms),
        float(arg_courtyard_width),
        float(arg_room_width),
        float(arg_room_depth),
        float(arg_room_height),
        float(arg_room_wall_thickness),
        bool(arg_room_window_existence),
        float(arg_room_window_width),
        float(arg_room_window_height),
        bool(arg_room_door_existence),
        float(arg_room_door_width),
        float(arg_room_door_height)
    )

    # create and authenticate a client
    token_path = os.path.join(os.path.expanduser('~'), '.speckle', 'token')
    host_path = os.path.join(os.path.expanduser('~'), '.speckle', 'host')
    token_file = open(token_path, "r")
    host_file = open(host_path, "r")
    token = token_file.read().replace('\n', '')
    host = host_file.read().replace('\n', '')
    client = SpeckleClient(host=host)
    account = Account.from_token(token, host)
    client.authenticate_with_account(account)


    results = client.stream.search("Archaea Tests")
    if not results:
        new_stream_id = client.stream.create(name="Archaea Tests")

    results = client.stream.search("Archaea Tests")
    stream = results[0]

    transport = ServerTransport(client=client, stream_id=stream.id)

    branches = client.branch.list(stream.id)
    is_openfoam_branch_exist = any(branch.name == "OpenFOAM" for branch in branches)

    if not is_openfoam_branch_exist:
        branch_id = client.branch.create(stream.id, "OpenFOAM", "Created by Archaea.")

    branch = client.branch.get(stream.id, "OpenFOAM")

    domain = Domain(Point3d.origin(),
                    float(arg_domain_width),       # x
                    float(arg_domain_depth),       # y
                    float(arg_domain_height)       # z
                    )

    for zone in courtyard_building.zones:
        domain.add_zone(zone)

    base = Base()
    mesh = Mesh()
    mesh.units = 'm'
    archaea_mesh = domain.export_all_to_single_mesh()
    mesh.vertices = [item for sublist in archaea_mesh.vertices for item in sublist]
    mesh.faces = [item for sublist in archaea_mesh.polygons for item in [len(sublist)] + sublist]
    base.data = [mesh]

    obj_id = operations.send(base, [transport])

    # now create a commit on that branch with your updated data!
    commit_id = client.commit.create(
        stream.id,
        obj_id,
        branch.name,
        message="Sent from Archaea.",
    )

    archaea_folder = get_cfd_export_path()
    if not os.path.exists(archaea_folder):
        os.makedirs(archaea_folder)

    case_folder = os.path.join(archaea_folder, arg_name)
    domain.create_case(case_folder)

    if arg_exec:
        cmd = os.path.join(case_folder, './Allrun')
        pipefile = open('output', 'w')
        retcode = subprocess.call(cmd, shell=True, stdout=pipefile)
        pipefile.close()
        os.remove('output')


if __name__ == "__main__":
    cfd_stl_export(sys.argv)

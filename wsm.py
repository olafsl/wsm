#!/usr/bin/python3
import datetime
import sys, os
import subprocess
import yaml
from collections import namedtuple, OrderedDict
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

config_location = os.path.expanduser("~/.config/wsm/wsmrc")

with open(config_location, "r") as configuration:
    config = yaml.load(configuration, Loader=yaml.FullLoader)

def main():
    try:
        os.mkdir(config["tmp_folder"])
    except:
        pass
    try:
        os.mkdir(config["command_folder"])
    except:
        pass

    handler = CommandHandler()
    observer = Observer()
    observer.schedule(handler, config["command_folder"])
    observer.start()
    while True:
        sleep(0.1)
        handler.unlock(tick=True)
        handler.reload_active_workspace()
        handler.displaygen()

class CommandHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        super().__init__()
        self.locked_groups = []
        self.display = ""
        self.groups = []
        self.monitors = {}
        monitors = command("bspc query -M --names").strip().split("\n")
        for monitor in monitors:
            self.monitors[monitor] = []
            workspaces = command("bspc query -D -m " + monitor + " --names").strip().split("\n")
            command("bspc desktop -f " + workspaces[0])
            self.groups.append(Group())
            self.activegroup = self.groups[-1]
            self.activegroup.workspaces = [workspace for workspace in workspaces]
        try:
            command("rm {}*".format(config["command_folder"]))
        except:
            pass
        self.displaygen()

    def activemonitor(self):
        return command("bspc query -m focused -M --names").strip()

    def reload_active_workspace(self):
        current_ws = command("bspc query -d focused -D --names").strip()
        if self.activegroup.active != current_ws:
            try:
                self.activegroup = [x for x in self.groups if current_ws in x.workspaces][0]
                self.activegroup.active = self.activegroup.workspaces[self.activegroup.workspaces.index(current_ws)]
            except:
                self.activegroup = self.groups[0]
                self.activegroup.active = self.active.group.workspaces[0]

    def on_created(self, event):
        command = event.src_path[len(config["command_folder"]):]
        if command == "create":
            self.create()
        elif command == "create_group":
            self.create_group()
        elif command == "delete":
            self.delete()
        elif command == "focus_left":
            self.focus(-1)
        elif command == "focus_right":
            self.focus(1)
        elif command == "focus_group_left":
            self.focus_group(-1)
        elif command == "focus_group_right":
            self.focus_group(1)
        elif command == "move_left":
            self.move(-1)
        elif command == "move_right":
            self.move(1)
        elif command == "move_group_left":
            self.movegroup(-1)
        elif command == "move_group_right":
            self.movegroup(1)
        elif command == "change_group_left":
            self.change_group(-1)
        elif command == "change_group_right":
            self.change_group(1)
        elif command == "group_colour":
            self.activegroup.changetype()
        elif command == "lock":
            self.lock()
        elif command == "manual_unlock":
            self.man_unlock()
        elif command == "hard_unlock":
            self.man_unlock(full=True)
        elif command == "save":
            self.save_state()
        else:
            pass
        os.remove(config["command_folder"] + command)
        self.unlock()
        self.displaygen()

    def create(self, name=None):
        names = config["workspace_names"].copy()
        if name==None:
            for group in self.groups:
                for ws in group.workspaces:
                    try:
                        names.remove(ws)
                    except:
                        pass
            for group in self.locked_groups:
                for ws in group.workspaces:
                    try:
                        names.remove(ws)
                    except:
                        pass
            name = names[0]
        command("bspc monitor -a " + name)
        command("bspc desktop -f " + name)
        self.activegroup.workspaces.append(name)
        self.activegroup.active = self.activegroup.workspaces[-1]

    def create_group(self, colour=config["defaultfg"]):
        if not self.activegroup:
            newgroup = Group(colour)
            self.groups.append(newgroup)
            self.activegroup = newgroup
        else:
            if len(self.activegroup.workspaces) == 1:
                return
            newgroup = Group(colour)
            self.groups.append(newgroup)
            ws = self.activegroup.active
            self.activegroup.workspaces.remove(ws)
            self.activegroup.active = self.activegroup.workspaces[0]
            self.activegroup = newgroup
            self.activegroup.workspaces.append(ws)
            self.activegroup.active = ws
        self.monitors[self.activemonitor()].append(newgroup)

    def delete(self):
        windows = command("bspc query -d focused -N").strip().split("\n")
        for window in windows:
            command("bspc node {} -c".format(window))

        if len(self.activegroup.workspaces) == 1:
            if len(self.monitors[self.activemonitor()]) == 1: 
                return
            self.groups.remove(self.activegroup)
            self.activegroup = self.groups[0]
        ws = command("bspc query -d focused -D --names").strip()
        try:
            self.activegroup.workspaces.remove(ws)
        except:
            pass
        command("bspc desktop -r")
        self.focus(-1)

    def focus(self, change):
        if self.activegroup.active in self.activegroup.workspaces:
            index = self.activegroup.workspaces.index(self.activegroup.active)
            self.activegroup.active = self.activegroup.workspaces[(index+change)%len(self.activegroup.workspaces)]
            command("bspc desktop -f {}".format(self.activegroup.active))
        else:
            self.activegroup.active = self.activegroup.workspaces[0]
            command("bspc desktop -f {}".format(self.activegroup.active))

    def focus_group(self, change):
        try:
            index = self.groups.index(self.activegroup)
            self.activegroup = self.groups[(index+change)%len(self.groups)]
        except:
            try:
                self.activegroup = self.groups[0]
            except:
                pass
        if self.activegroup.active == None:
            self.activegroup.active = self.activegroup.workspaces[0]
        command("bspc desktop -f {}".format(self.activegroup.active))

    def move(self, diff):
        window_id = command("bspc query -n focused -N").strip()
        index = self.activegroup.workspaces.index(self.activegroup.active)
        command("bspc node -d " + str(self.activegroup.workspaces[(index+diff)%len(self.activegroup.workspaces)]))
        self.focus(diff)
        command("bspc node -f " + window_id)

    def movegroup(self, diff):
        window_id = command("bspc query -n focused -N").strip()
        index = self.groups.index(self.activegroup)
        target = self.groups[(index+diff)%len(self.groups)]
        command("bspc node -d " + str(target.active))
        self.focus_group(diff)
        command("bspc node -f " + window_id)
        
    def change_group(self, diff):
        ws = self.activegroup.active
        index = self.groups.index(self.activegroup)
        if len(self.activegroup.workspaces) == 1:
            self.groups.remove(self.activegroup)
        else:
            self.activegroup.workspaces.remove(ws)
            self.activegroup.active = self.activegroup.workspaces[0]
        self.activegroup = self.groups[(index+diff)%len(self.groups)]
        self.activegroup.workspaces.append(ws)
        self.activegroup.active = ws
        
    def displaygen(self):
        string = ""
        for group in self.locked_groups:
            if group.lock_counter == -1:
                for ws in group.workspaces:
                    string += colour(RGB("282828"), RGB("928374").change_hue(-0.7), " " + str(ws) + " ")
                string += "  "
        string += "    "
        for group in self.groups:
            if len(group.workspaces) == 0:
                self.groups.remove(group)
                break
            if group == self.activegroup:
                groupcolour = group.colour
                backcol = groupcolour.change_hue(-0.7)
            elif group in self.monitors[self.activemonitor().strip()]:
                groupcolour = group.colour.change_hue(-0.8)
                backcol = groupcolour.change_hue(-0.7)
            else:
                groupcolour = group.colour.change_hue(-0.8)
                backcol = RGB("1d2021")
            for ws in group.workspaces:
                urgency = command("bspc query -d .urgent -D --names")
                if urgency.strip() == str(ws):
                    col = RGB("fb241d")
                    backcol = col.change_hue(-0.8)
                else:
                    col = groupcolour
                if group.active == ws:
                    string += colour(col, backcol, " " + str(ws) + " ")
                else:
                    string += colour(col.change_hue(-0.8), backcol.change_hue(-0.7), " " + str(ws) + " ")
            string += "  "
        string += "    "
        for group in self.locked_groups:
            if group.lock_counter > 0:
                for ws in group.workspaces:
                    string += colour(RGB("282828"), RGB("928374").change_hue(-0.7), " " + str(ws) + " ")
                string += "  "
        self.display = string
        logfile = open(config["tmp_folder"] + "output", "a+")
        logfile.write(string + "\n")
        logfile.close()
        print(self.display, flush=True)

    def lock(self, time=-1):
        if len(self.groups)==1:
            self.create()
            self.create_group()
            self.focus_group(1)
        gp = self.activegroup
        gp.lock_counter = int(time)
        self.focus_group(1) 
        self.locked_groups.append(gp)
        self.groups.remove(gp)

    def unlock(self, tick=False):
        for lock_group in self.locked_groups:
            if lock_group.lock_counter == -1:
                pass
            elif lock_group.lock_counter > 0:
                if tick:
                    lock_group.lock_counter = lock_group.lock_counter - 1
            else:
                lock_group.lock_counter = 0
            if lock_group.lock_counter == 0:
                self.groups.append(lock_group)
                self.locked_groups.remove(lock_group)

    def man_unlock(self, full=False):
        for lock_group in self.locked_groups:
            if full or lock_group.lock_counter == -1:
                lock_group.lock_counter = 0
        self.unlock()

class Group():

    def __init__(self, colour=config["defaultfg"]):
        self.colour = RGB(colour)
        self.active = None
        self.lock_counter = 0
        self.workspaces = []

    def changetype(self):
        typefile = open(config["command_folder"] + "group_colour", "r")
        colour = typefile.read()
        try:
            self.colour = RGB(colour)
        except:
            pass
        typefile.close()

    def __str__(self):
        string = ""
        for ws in self.workspaces:
            string += " "
            if ws == self.active:
                string += str(ws) + "*"
            else:
                string += str(ws) + "-"
        return string

def colour(fg, bg, message):
    return "%{F#" + str(fg) + "}%{B#" + str(bg) + "}"  + message + "%{F- B-}"

def space(num):
    return "%{O" + str(num) + "}"

def font(num, message):
    return "%{T" + str(num) + "}" + message + "%{T-}"

def command(string):
    return (subprocess.run(string, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout).decode(encoding='UTF-8', errors='strict')

class RGB():
    def __init__(self, input_colour):
        self.red = int(input_colour[0:2], 16)
        self.green = int(input_colour[2:4], 16)
        self.blue = int(input_colour[4:], 16)
        self.colour = [self.red, self.green, self.blue]

    def change_hue(self, diff):
        new_colour = []
        for colour in self.colour:
            if diff > 0:
                colourdiff = 0xff - colour
                new_colour.append(colour + colourdiff * diff)
            if diff < 0:
                new_colour.append(colour * (- diff))
        listr = [str(hex(round(col)))[2:] for col in new_colour]
        new = RGB("".join(listr))
        return new
        
    def __str__(self):
        return '{:02X}{:02X}{:02X}'.format(self.red,self.green,self.blue)

if __name__ == "__main__":
    main()

Workspace Manager
===

**wsm** is the extremely uninspiring name for my **w**ork**s**pace **m**anager. This is built for my own system, which is quite specific. However, with some adaptation, it should not be too hard to change it to also fit other window managers. Feel free to use it for whatever you like, if you can find a good use for it.


Features
========

- Managing workspaces, switching between different workspaces, creating new workspaces, and removing them.
- Managing workspace groups, creating/removing them and moving between them.
- Moving windows from one workspace to another workspace, or another workspace group.
- Locking workspaces away, for either an undefined time or a pre-defined time. Obviously it also allows you to unlock all groups.
- Colouring the groups. If you do not use polybar, but have another way to display the workspaces, it should be pretty trivial to also incorporate this.
- Saving/Loading the current state. When I have a bunch of windows open, and I need to restart my window manager, I do not want to lose my entire setup. It should be putting everything in it's place again automatically, this is a little sketchy sometimes though.
- Maybe something else I either forgot, or implemented after writing this.

I will add more explanation about what it actually adds as features later. For now, if you want to know more, let me know.


Set-up
======

Okay, so I'm using bspwm as my window manager, combined with sxhkd. I use polybar on top of that, to make my status bar. 
The display of this application is made to suit that, it writes the output in a `/tmp/wsm/output`, where Polybar can read it out with a simple `tail -F` command. 

I have also supplied wsmex, which is the executable file in my `/usr/bin/`. It is not very exciting, it's just an easy method of sending commands to the wsm-instance. This is usually activated by a key-combination in my sxhkd.
The configuration of wsm are, again, not extremely imaginative, in `~/.config/wsm/wsmrc`. I provided a usable example,`wsmrc_example`. It is in yaml-format, and it requires:
- `defaultfg`, the default foreground colour of the displayed workspace. It automatically derives other shades from this colour.
- `command_folder`, a sensible location would be `/tmp/wsm/command/`
- `tmp_folder`, in a similar way I'd suggest `/tmp/wsm/`
- `workspace_names`. This is a list of letters, icons, or whatever you want, which it will use to name new workspaces. I use greek letters for this, but you can choose anything you like.



Do take note that you have to make sure the folders, and the configuration file, exist. I do this by including a couple of lines in my bspwmrc, since I always load the prior to starting this application.
I would like to have it auto-generate a config file when none is present, and check everything nicely, with sensible errors. However, time is limited, and it has a low priority for me, so I don't know if i'll ever come to it. 

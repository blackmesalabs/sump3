#!/usr/bin/python
###############################################################################
# Copyright (C) Kevin M. Hubbard 2024 BlackMesaLabs
# sump3.py borrows heavily from sump2.py and inherits its open-source license.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# https://www.ibm.com/docs/en/siffs/2.0.3?topic=python-installing-packages-offline-mode
# c:\python37\Scripts\pip.exe download pygame-gui
# c:\python37\Scripts\pip.exe install *.whl          
#
# WARNING : Latest pygame-gui breaks things. Force install of older version
#   pip install --force-reinstall -v "pygame-gui==0.6.12"
#
# 2023.03.14 : Beginning
# 2023.03.24 : DONE Memory leak on scrolling
# 2023.04.04 : DONE replace ana_values and dig_values with just values.
# 2023.04.06 : DONE channel store to file and retrieve.
# 2023.04.18 : TODO split-capture idea
# 2023.04.19 : TODO new RLE idea. 8+27+1 data+time+valid
# 2023.05.30 : Path cleanup on sourcing files. CWD vs UUT.
# 2023.07.10 : sump_script_remote feature added. save_view added trigger attrbs
# 2023.07.10 : fixed issue with cmd_assign_var assign ALL sigs, not just selected.
# 2023.07.12 : save_pic added
# 2023.08.04 : 2D array of Hub+Pod RLE working
# 2023.08.09 : Added create_group, end_group. Changed member_of from str to obj
# 2023.11.09 : Improved error handling on missing PyGame, missing Hardware.
# 2023.11.09 : Improved log creation to support multiple instances and crashing.
# 2023.11.10 : Added support for core view ROM.
# 2023.11.13 : Added fault handling to display_text_stats()
# 2023.11.15 : Added apply_attribute command to bd_shell
# 2023.11.27 : trigger core,miso,mosi latency work.
# 2023.11.28 : Added view roms from PZA loads.
# 2023.11.29 : Mouse action improvements. Pinch to zoom, etc.
# 2023.11.30 : Fixed apply_attribute. Support non-nibble RLE data widths.
# 2023.12.01 : Added save_vcd().
# 2023.12.04 : Added search_forward and search_backward.
# 2023.12.05 : Added time_snap and time_lock.
# 2023.12.06 : Added view_obj to support views being used multiple times.
# 2023.12.07 : Added VCD hierarchy
# 2023.12.08 : cmd_insert_signal() now supports moving signals around
# 2023.12.13 : Added VCD cursor cropping.
# 2023.12.20 : Added save_list() List dumping.
# 2023.12.21 : Fixed a bunch of save_view() bugs. Specifying view_name now optional.
# 2024.01.02 : Added list_csv_format option for save_list().
# 2024.01.02 : Added support for save_vcd() to only save selected signals.
# 2024.01.03 : Fixed view rom -triggerable issue with hub+pod naming.
# 2024.01.04 : Fixed issued with rle_mask and hidden attributes and toggle controls.
# 2024.01.04 : Fixed broken proc_acq_adj() offset issue.
# 2024.01.10 : pod_user_ctrl added.
# 2024.01.11 : Finished user_ctrl arbitration.
# 2024.01.12 : View highlighting added.
# 2024.01.15 : Added convert_object_id_to_tool_tip()
# 2024.01.16 : Added copy_signal() for copying existing signal to a blank new window.
# 2024.01.17 : Fixed PZA load issue with stored hard paths
# 2024.01.24 : Working on signal drag copying to new window
# 2024.01.27 : Added view drag to window.
# 2024.01.28 : Added cmd_rename_signal().
# 2024.01.30 : Fixed KeyError crash in generate_pod_user_ctrl_list()
# 2024.01.30 : Added download_rle_ondemand() which seems to work as expected
# 2024.02.01 : Fixed load_pza. Added defer_gui_update to speed up importing View ROMs
# 2024.02.06 : Fixed user_ctrl problems. Removed bulk_mask
# 2024.02.07 : Fixed cmd_remove_view() not removing view from view_applied_list
# 2024.02.09 : save_vcd() and load_vcd() improvements.
# 2024.02.16 : Improve measurement text field. Fixed panning issue with ADC samples.
# 2024.02.22 : Read and report View ROM sizes. Added GTKwave support w hierachy
# 2024.02.23 : Fixed multiple VCD export bugs with hierarchy, rips and gtkw file.
# 2024.02.27 : Fixed save_vcd() crashing due to RLE masked signals with no samples
# 2024.02.28 : Fixed acquire loop never stopping after trigger.
# 2024.02.29 : Fixed RLE time wrap issue on zero activity pre-trigger in rle_time_cull()
# 2024.03.01 : Added some attribute shortcuts for smaller ROM sizes.
# 2024.03.04 : Added vertical signal scrolling
# 2024.03.05 : Fixed issue with text zoom/pan indicator on really long captures
# 2024.03.06 : Added clone_signal(). Fixed bug of cursor delta stuck when signal selected
# 2024.03.07 : Replaced clone_signal() with cut_signal() as more intuitive.
# 2024.03.15 : Fixed save_view() missing view name. Fixed cursor grab also selecting signal.
# 2024.03.19 : Fixed rd_core_view_rom() to not loop past length of ROM if end not found.
# 2024.03.22 : More PyGame bar updates on RLE downloads.
# 2024.03.26 : Fixed cmd_save_view() to include "end_group" for nested groups.
# 2024.03.28 : Fixed identify_invalid_signals() incorrectly culling digital_rle signals.
# 2024.04.08 : Don't error on missing RAM files.
# 2024.04.08 : Improved hex rendering in create_drawing_lines()
# 2024.04.08 : Added WASD cursor keys for the VideoGamer generation.
# 2024.05.02 : Added apply_view_all and remove_view_all.
# 2024.05.03 : Auto select a window when #Display is pressed.
# 2024.08.16 : AES-256 Authentication and E2E Encryption added.
# 2024.10.29 : Try/Except for invalid -source
# 2024.10.29 : Working on user_write and user_read commands
# 2024.10.30 : Deprecated user_stim. Added user_bus 
# 2024.10.31 : Add no_view_rom_list for when there is no view rom. Make a generic one.
# 2024.11.04 : Handle pod_name_en == 0.
# 2024.11.04 : Added call to cmd_add_view_ontap inside cmd_load_uut()
# 2024.11.05 : Added norom_view_dwords, bytes, bits feature.
# 2024.11.05 : Added merge_view_rom_no_view_rom() 
# 2024.11.06 : Added view rom support for bd_shell cmds and comma separated attribs
# 2024.11.19 : New expand_view_rom_generates() 
# 2024.11.19 : Working on mouse_event_single_click_waveform()
# 2024.11.27 : Fixed View ROM .* generate instance issues
# 2024.11.27 : Removed all fnmatch.filter wildcard searches. Doesn't work with [3:0] in names.
# 2024.11.27 : set_trig now toggles trigger attribute rather than set it
# 2024.11.27 : Added quiet to proc_cmd to greatly speed up applying views
# 2024.12.05 : cur_val_list improvements. mouse_event_single_click_waveform() improvements.
# 2024.12.06 : viewrom_debugger() added. Don't crash on bad View ROMs, just ignore them.
# 2024.12.09 : Added start_match() for fnmatch.filter replacement.
# 2024.12.09 : F9, create_bit_group added.
# 2024.12.10 : Performance improvements to create_signal (defer_updates). ApplyAll
# 2024.12.10 : Performance improvements on signal_attribute_inheritance()
# 2024.12.12 : cmd_create_signal() assign type="analog" if source=="analog_ls"
# 2024.12.12 : Fixed select_window() border shadow issue with VNC.
# 2024.12.12 : On load_pza, set self.sump_connected = False;
# 2024.12.16 : Added sig attribute maskable for RLE masking.
# 2024.12.17 : Display->Navigation. button swaps for more vert space. font_size_toolbar.
# 2024.12.17 : Added screen_window_rle_time, time range at upper right corner. 
# 2024.12.17 : Update cursor deltas so text and GUI delta always match. Don't bold triggerables
# 2024.12.18 : Added y_scrolled_stats feature in upper-left corner when scrolling long signal list. 
# 2025.01.08 : Thread Locking added
# 2025.01.09 : cmd_sump_connect() Bug fix "for i in range(0,31):" to "(0,32)"
# 2025.01.14 : Fixed ERROR-452 with digital_ls crashing when cursors applied.
# 2025.01.15 : Deprecating old rd_status using sump_rd_status_legacy_en = 1.
# 2025.01.16 : Save_Window, Save_Screen, Add_Measure, Remove_Meas added.    
# 2025.01.17 : Numerous analog improvements. Too many to list here.
# 2025.01.20 : Deselect after add_measurement().
# 2025.01.21 : ToolTips in text. Deprecating scroll wheel analog scaling.
# 2025.01.22 : Analog trigger improvements.
# 2025.01.27 : proc_expand_group() fixed bug with rle_masked signals being invisible.
# 2025.01.31 : sump_script_remote fixes
# 2025.02.03 : screen_set_size() added and called when var screen_width / h changes.
# 2025.02.09 : sump_remote_telnet added.
# 2025.03.03 : cmd_load_uut() changes to support batch start script.
# 2025.03.05 : cmd_sump_set_trigs() updated to support CLI by signal name.
# 2025.03.05 : removed WASD keys as problematic with bd_shell.
# 2025.03.07 : Cursor glitch fixes.
# 2025.03.10 : trigger_index +/- 1 fix to update_cursors_to_mouse(), create_cursor_lines()
#              to fix issue with cursor alignment to trigger with RLE vs LS (at 5ms)
# 2025.03.11 : Sump Remote improvements.
# 2025.03.17 : Fix text select bug when waveform font size is changed. mouse_get_text()
#              switch from self.txt_height to self.txt_toolbar_height
# 2025.03.18 : align analog_ls with digital_ls by pre-stuffing 2 Nones
# 2025.03.18 : Fixed broken analog trigger in cmd_sump_set_trigs() due to break.
# 2025.03.18 : mouse_get_text() deselect selected signals so K_UP/DOWN can adjust.
# 2025.03.19 : disable cursors on screen resize as delta time was wrong.
# 2025.03.20 : Text format fixes in display_text_stats()
# 2025.03.20 : Added bd_shell support for UNIX history, !n, !! and "> foo.txt"
# 2025.03.21 : Recursion added to signal copy,cut,delete, and paste.
# 2025.03.24 : Fix binary groups not copy,cut,delete.
# 2025.03.24 : Fixed diagnol drag bug of closing all but one window. Removed feature.
# 2025.03.31 : close_window() added.  Added "sump_remote_file_en" and support CWD or UUT
# 2025.04.03 : sump_remote bug with with rts of nested lists from source a file.
# 2025.04.04 : Fixed analog vertical_offset==0 bug of scrolling with signal name.
# 2025.04.08 : Fixed merge_view_rom_no_view_rom() bug not recognizing create_bit_group.
# 2025.04.10 : Added viewable_value_list_too for rendering single ADC sample as line.
# 2025.04.15 : Backed out 2025.03.18 : align analog_ls with digital_ls by pre-stuffing 2 Nones
#              On zoom_full, trigger location was off by 2 samples in any analog_ls window.
# 2025.04.15 : Added sump_ls_ana_dig_alignment feature. Default to 4.
# 2025.04.17 : Fixed cmd_save_pza() bug not saving to sump_pza directory when fn specified.
# 2025.04.29 : UIPanel hide() show() upgrade to be Pygame-GUI 0.6.13 compatible.
# 2025.04.29 : bd_shell console close_window_button enabled to be Pygame-GUI 0.6.13 compatible.
# 2025.04.29 : Tweaked image offsets in container_builder_waveforms() to align with > 0.6.9 changes.

#
# NOTE: Bug in cmd_create_bit_group(), it just enables triggerable and maskable for
#       bottom 32 RLE bits instead of looking at actual hardware configuration.
#
# TODO: cmd_apply_view doesn't handle user_ctrl clashes correctly, for example if 
#       digital_ls is used it may wrongly reject RLE Pods with user ctrls.
#
# DONE: view filter on user_ctrl bits
# DONE: Offline mode. Should always come up and display last capture data
# TODO: Display trigger relative time in each window bottom left/right corners.
# DONE: RLE rendering without decompression
# TODO: Resolve signal class have both window and parent attributes
# DONE: Cursors are locked to screen and don't pan/zoom with window
# DONE: Zoom/Pan doesn't go back to zero after a new download
# BUG: If now views are present on the download, nothing will show up when
# you start adding views until you download again.
# BUG: Cursors relative to trigger seems off between timezones.
# DONE: Can timezone names of "ls", "hs" and "rle" be default based on source?
# DONE: Scroll Bar isn't working right for "Trig Type" selection.
# DONE: Remote button pressing. Perhaps via text file?
# TODO: Process more than a single DWORD of digital LS bits.
# DONE: Multi clock domain support for RLE pods.
# TODO: AND triggers and Pattern triggers across multiple RLE pods.
# DONE: save_view doesn't save trigger attributes.
# DONE: force_trig doesn't work.
# TODO: scale and offset controls go off into weeds at fine scale.
# TBD:  sump_acquire_continuous command?
# TBD:  LS pre-trig is filling entire RAM, ignoring trigger position.
# TBD:  More decimal places than just 1/10ths for some measurements.
# DONE: Analog triggering not working?
# TODO: sump_read_config() and sump.rd_cfg() should be consolidated.
# DONE: rle_masked should be prevented in GUI if not possible in HW.
#
# Todays Bugs:
#  DONE triggerable = True not in view rom file.
#    2) Strange RLE rendering artifact on "active" and "rxd" signals (simultaneous high and low). 
#    3) clock sig didn't render as rle_masked = True even though it was.
#  DONE No means to toggle rle_masked from GUI. <END> key only toggles hide/show
# TODO: mouse_get_text() needs to filter out RO from being set to bold_i
###############################################################################
import random;
import os;
import glob;
import copy;
import sys;
import math;
import gzip;
import fnmatch;
import re;
import time;
#import gc
from collections import deque

# https://pygame-gui.readthedocs.io/en/v_067/index.html
# python -m pip install pygame-gui

print("Importing module PyGame");
import pygame;
print ( pygame.__version__ );
print("Importing module PyGame-GUI");
import pygame_gui;
#print ( pygame_gui.__version__ );
#print ( dir( pygame_gui ) );
#print ( pygame_gui.__doc__  );
#print ( pygame_gui.__file__  );
#print ( pygame_gui.__loader__  );
#print ( pygame_gui.__name__  );
#print ( pygame_gui.__package__  );
#print ( pygame_gui.__spec__  );

# Python does not come with PyGame and PyGame-GUI by default, so do some text
# based hand holding when those modules are not yet installed.
try:
  print("Importing module PyGame");
  import pygame;
  from pygame import Color
  print("Importing module PyGame-GUI");
  import pygame_gui;
  from pygame_gui import UIManager, PackageResource;
  from pygame_gui.elements import UIWindow;
  from pygame_gui.elements import UITextEntryLine;
  from pygame_gui.elements import UITextEntryBox;
  from pygame_gui.elements import UIPanel;
  from pygame_gui.elements import UIImage;
  from pygame_gui.elements import UIButton;
  from pygame_gui.elements import UIDropDownMenu;
  from pygame_gui.elements import UISelectionList;
  from pygame_gui.windows.ui_console_window import UIConsoleWindow;
  from pygame_gui.windows  import UIFileDialog;
  #from pygame_gui.elements import UIHorizontalSlider;
  #from pygame_gui.elements import UIScreenSpaceHealthBar;
  #from pygame_gui.elements import UILabel;
  #from pygame_gui.windows import UIColourPickerDialog;
  #from pygame_gui.windows import UIMessageWindow;
  #from pygame_gui.windows import UIConfirmationDialog;
except:
  print("-----------------------------------------------------------");
  print("ERROR: Required Package PyGame and/or PyGame-GUI missing");
  print("-----------------------------------------------------------");
  print("Three Python module install choices:");
  print("1) Install on machine with direct internet access:");
  print("  %pip install pygame-gui");
  print("2a) Download WHLs from machine on internet:");
  print("  %pip download pygame-gui");
  print("2b) Install WHLs to offline machine with USB stick:");
  print("  %pip install pygame_ce-2.3.2-cp312-cp312-win_amd64.whl");
  print("  %pip install python_i18n-0.3.9-py3-none-any.whl");
  print("  %pip install pygame_gui-0.6.9-py3-none-any.whl");
  print("3) Install on machine with PIP gateway to internet:");
  print("  Create pip.ini file in python.exe directory then do step 1)");   
  print("  [global]");
  print("  index-url = http://my_gateway_ip:8081/artifactory/api/pypi/PyPI/simple");
  print("  extra-index-url = http://my_gateway_ip:8081/artifactory/api/pypi/PyPI-remote/simple");
  print("  trusted-host = my_gateway_ip");
  print("-----------------------------------------------------------");
  print("Press <ENTER> to exit.");
  rts = input();
  sys.exit();


class Options:
  def __init__(self):
    self.resolution = (800, 600);
    self.fullscreen = False;


###############################################################################
# START_GUI_SECTION
###############################################################################
class main:
  def __init__(self):
    self.vers = "2025.04.29";
    self.copyright = "(C)2025 BlackMesaLabs";
    pid = os.getpid();
    print("sump3.py "+self.vers+" "+self.copyright + " PID="+str(pid));
    self.pygame = pygame;
    init_globals( self );# Internal software variables
    self.vars = init_vars( self, "sump3.ini" );
    create_dirs( self );
    list2file( self.sump_manual, init_manual(self ) );

#   create_view_ontap_list(self);
#   self.color_fg = self.vars["screen_color_foreground"];
#   self.file_log = open ( self.vars["file_log"] , 'w' );
    filename = self.vars["file_log"]+".pid"+str( os.getpid() );
    self.file_log = open ( filename, 'w' );
    log(self,["Welcome to "+self.name+" "+self.vers+" "+self.copyright]);
    log(self,["Licensed under GNU General Public License v3.0"]);

    if int( self.vars["sump_remote_telnet_en"], 10 ) == 1:
      PORT = int( self.vars["sump_remote_telnet_port"], 10 );
      HOST =      self.vars["sump_remote_telnet_host"];
      if HOST == "*.*.*.*":
        HOST = "";# Accept anybody
      log(self,["Starting sump_remote Telnet server on TCP port %d" % PORT]);
      import socket;
      self.telnet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     self.telnet_socket.setblocking(False);
      self.telnet_socket.bind((HOST, PORT));
      self.telnet_socket.listen(4);
#     self.telnet_clients = []; #list of clients connected
    else:
      self.telnet_socket = None;

#   x = 10; y = 10
#   txt = os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
#   log(self,["Window is at %s" % txt ] );

    file_name = "sump_capture_cfg.txt";
    file_path = self.vars["sump_path_ram"];
    file_name = os.path.join( file_path, file_name );
    if os.path.exists( file_name ):
      self.sump = sump_virtual( parent = self);
      self.sump.rd_cfg( file_name );

      file_name = "sump_rle_podlist.txt";
      file_path = self.vars["sump_path_ram"];
      file_name = os.path.join( file_path, file_name );
      if os.path.exists( file_name ):
        self.sump.rd_pod_cfg( file_name );
  
    init_display(self);
    self.font = get_font( self,self.vars["font_name"],self.vars["font_size"]);
    self.font_toolbar = get_font( self,self.vars["font_name"],self.vars["font_size_toolbar"]);

    # Calculate Width and Height of font for future reference
    txt = self.font_toolbar.render("4",True, ( 255,255,255 ) );
    self.txt_toolbar_width  = txt.get_width();
    self.txt_toolbar_height = txt.get_height();

    self.options = Options();

    self.screen_width  = int( self.vars["screen_width"], 10 );
    self.screen_height = int( self.vars["screen_height"], 10 );
    self.screen_windows = int( self.vars["screen_windows"], 16 );
    self.screen_window_rle_time = int( self.vars["screen_window_rle_time"], 16 );

    self.options.resolution = ( self.screen_width, self.screen_height );
    self.ui_manager = UIManager(self.options.resolution)
    self.ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                                   {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                                   {'name': 'fira_code', 'point_size': 10, 'style': 'italic'},
                                   {'name': 'fira_code', 'point_size': 14, 'style': 'italic'},
                                   {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}
                                  ]);
#   self.ui_manager.set_window_resolution(self.options.resolution)
    self.ui_manager.clear_and_reset()
    init_widgets(self);
    resize_containers(self);

    # Set Window and Console visibility based on ini file from last exit
    self.window_list[0].panel.visible = ( ( self.screen_windows & 0x1 ) != 0x0 );
    self.window_list[1].panel.visible = ( ( self.screen_windows & 0x2 ) != 0x0 );
    self.window_list[2].panel.visible = ( ( self.screen_windows & 0x4 ) != 0x0 );
    self.cmd_console.visible          = ( ( self.screen_windows & 0x8 ) != 0x0 );

    #HERE74
    if self.cmd_console.visible:
      self.cmd_console.show();# New 2025.04.29

    resize_containers(self);
    update_toggle_buttons(self);
#   auto_select_window( self );
#   select_window( self, 0 );# Default to 1st window
    if self.window_list[0].panel.visible == True:
      select_window( self, 0 );# Default to 1st window
    elif self.window_list[1].panel.visible == True:
      select_window( self, 1 );# Default to 1st window
    elif self.window_list[2].panel.visible == True:
      select_window( self, 2 );# Default to 1st window

    self.running = True;
    self.all_enabled = True;
    self.all_shown = True;
    self.refresh_waveforms = True;
    self.refresh_window_list = [0,1,2];
    self.refresh_sig_names = True;
    self.refresh_cursors   = False;

    if self.vars["debug_mode"].lower() in [ "true", "1", "yes" ]:
      self.debug_mode = True;
    else:
      self.debug_mode = False;

    file_name = self.vars["sump_script_startup"];
    if os.path.exists( file_name ):
      proc_cmd( self, "source %s" % file_name );
#   self.pygame.event.set_grab(True);
    # Procedural Startup ends here, now going into a GUI event loop
 
  def process_events(self):
    for event in pygame.event.get():
#     button1_handled = False;
#     if event.type != 1024:
#       print("-----");
#       print( event.type );
#       print( dir( event ) );
      if event.type == pygame.QUIT:
        self.running = False
        shutdown(self);
     

      # Keep track of focus, otherwise scroll wheel may click when moving mouse 
      # across the windows screen even though this application doesn't have focus.
      if event.type == pygame.WINDOWFOCUSGAINED:
        self.has_focus = True;
        self.pygame.display.set_caption(self.name + " " + self.vers + " " + self.copyright);
        # When focus is regained, click the mouse button over any button
        mouse_pos = pygame.mouse.get_pos();# (x,y)
        pygame.event.post( pygame.event.Event( pygame.MOUSEBUTTONDOWN,button=1,pos=mouse_pos ) );
        pygame.event.post( pygame.event.Event( pygame.MOUSEBUTTONUP,button=1,pos=mouse_pos ) );
#       for each_window in self.window_list:
#         each_window.border_colour = self.color_white;
      if event.type == pygame.WINDOWFOCUSLOST:
        self.has_focus = False;
        self.pygame.display.set_caption(self.name + " " + self.vers + " " + self.copyright + " (LOST FOCUS)");
#       for each_window in self.window_list:
#         each_window.border_colour = self.color_black;
#     self.has_focus = True;

      # VIDEORESIZE
      if event.type == pygame.VIDEORESIZE:
        self.screen= pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE );
        screen_get_size(self);
        screen_set_size(self);

        # Turn off cursors on a resize as the delta measurement was wrong after resize
        self.cursor_list[0].visible = False;
        self.cursor_list[1].visible = False;
        update_toggle_buttons(self);

#       if True:
#       ( self.screen_width, self.screen_height ) = self.screen.get_size();
#       display_text_stats( self );
#       print(1);
#       create_cursor_lines(self); # Generate cursors
#       print(2);
#       draw_surfaces(self);
#       print(3);
#       print( self.cursor_list[0].delta_txt );
#       self.cursor_list[0].delta_txt = None;
#       self.refresh_waveforms = True;
#       self.refresh_window_list = [0,1,2];
#       self.refresh_cursors   = True;


#       update_cursors_to_window( self );
#       update_cursors_to_mouse(self);

#       self.refresh_waveforms = True;
#       self.refresh_cursors = True;

#       self.refresh_waveforms = True;
#       self.screen= pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE );
#       if True:
#         ( self.screen_width, self.screen_height ) = self.screen.get_size();
#         # Make Widescreen 16:9 SD the minimum allowed
#         if self.screen_width < 720 or self.screen_height < 576:
#           self.screen_width = 720;
#           self.screen_height = 576;
#           self.screen = pygame.display.set_mode( (self.screen_width,self.screen_height), 
#             pygame.RESIZABLE );
#         self.options.resolution = ( self.screen_width, self.screen_height );
#         self.ui_manager.set_window_resolution(self.options.resolution)
#         screen_erase(self);
#         resize_containers(self);
#
#         # Since cursors are mouse positioned, they may go off-screen on a resize
#         # To prevent this, on any resize, place them back on the left.
#         self.cursor_list[0].x = 20;
#         self.cursor_list[1].x = 40;
#
#         self.vars["screen_width"]  = str( self.screen_width );
#         self.vars["screen_height"] = str( self.screen_height );

      # MOUSEMOTION
      self.mouse_motion_prev = self.mouse_motion;
      self.mouse_motion = False;
      if event.type == pygame.MOUSEMOTION:
        self.mouse_motion = True;# Ignore scroll wheel while mouse point is in motion
        rts = mouse_move_cursor( self );
        if rts == True:
          self.refresh_cursors   = True;
        if self.mouse_btn1_select == True: 
          self.refresh_sig_names = True;
        if self.mouse_pinch_dn != (None,None):
          self.refresh_cursors   = True;

      # MOUSEBUTTONDOWN
      if event.type == pygame.MOUSEBUTTONDOWN:
#       button1_handled = False;
#       new_window_selected = False;

        if event.button == 1 : 
          # Note: when file_dialog is open, click to closing would select the window
          # underneath, so check for it and ignore.
          (wave_i, zone_i ) = mouse_get_zone( self );
#         if self.file_dialog == None:
#         print( wave_i , self.window_selected );
#         if wave_i != None and self.window_selected != None and self.file_dialog == None:
          if wave_i != None and                                  self.file_dialog == None:
            # There are delta issues when switching windows with different time_zones
            # Hack fix is to deselect cursors.
            if self.window_selected != None:
              if self.window_list[self.window_selected].timezone != self.window_list[wave_i].timezone:
                self.cursor_list[0].visible = False;
                self.cursor_list[1].visible = False;
                update_toggle_buttons(self);

            if wave_i != self.window_selected:
              select_window( self, wave_i );
            else:
              mouse_event_single_click_waveform( self );
          
#         if wave_i != None and wave_i != self.window_selected and self.file_dialog == None:
#         if wave_i != None and self.window_selected != None and self.file_dialog == None:

#       if event.button == 1 : 
#         self.mouse_btn1_dn = pygame.mouse.get_pos();# (x,y)
#         # Note: when file_dialog is open, click to closing would select the window
#         # underneath, so check for it and ignore.
#         (wave_i, zone_i ) = mouse_get_zone( self );
#         if wave_i != None and self.file_dialog == None:
#           window_selected_old = self.window_selected;
#           if wave_i != window_selected_old:
#             select_window( self, wave_i );
#           # If the button press resulted in a window switch, don't allow the press to
#           # reposition the cursor in the new window.
#           if window_selected_old != self.window_selected:
#             button1_handled = True;
#             new_window_selected = True;

#       if event.button == 1 and button1_handled == False : 
        if event.button == 1 :
          self.mouse_btn1_dn = pygame.mouse.get_pos();# (x,y)
#         (wave_i, zone_i ) = mouse_get_zone( self );
#         if wave_i != None and wave_i == self.window_selected:
          if True:
            rts = mouse_get_cursor(self);# Grab any cursor near the mouse pointer
            if not rts:
              mouse_get_text(self);# Select any adjustable text fields at mouse
              rts = mouse_event_single_click(self);# Select any signal name at mouse
              if rts:
                ( self.mouse_signal_drag_from_window, null ) = mouse_get_zone( self );
                self.refresh_waveforms = True;
#         mouse_event_single_click_waveform( self );
#         update_cursors_to_mouse(self);
#         self.refresh_cursors = True;

        elif event.button == 2 : 
#         print("Button2");
          self.mouse_btn2_dn  = pygame.mouse.get_pos();# (x,y)
          self.mouse_pinch_dn = pygame.mouse.get_pos();# (x,y)
        elif event.button == 3 : 
#         print("Button3");
#         rts = proc_unselect(self);
#         if rts:
#           self.refresh_waveforms = True;
          self.mouse_btn3_dn  = pygame.mouse.get_pos();# (x,y)
          self.mouse_pinch_dn = pygame.mouse.get_pos();# (x,y)

      # MOUSEBUTTONUP
      if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1 : 
          self.mouse_btn1_up  = pygame.mouse.get_pos();# (x,y)
          # Did the MOUSEBUTTONDOWN event select a signal? If so, possible DRAG operation
          if self.mouse_btn1_select:
            (wave_i, zone_i ) = mouse_get_zone( self );
            ( self.mouse_signal_drag_to_window, null ) = mouse_get_zone( self );
            if ( self.mouse_signal_drag_from_window != None and
                 self.mouse_signal_drag_to_window != None       ):
#             print("DRAG to Window ? %s %s" % ( self.mouse_btn1_dn, self.mouse_btn1_up ) );
              a = self.mouse_signal_drag_from_window + 1;
              b = self.mouse_signal_drag_to_window + 1;
              if a != b:
#               print("Signal DRAG from Window-%d to Window-%d" % ( a,b ) );
                cmd_copy_signal( self, [ None,None,None] );
                select_window( self, self.mouse_signal_drag_to_window );
                cmd_paste_signal( self, [ None,None,None] );
          else:
            ( self.mouse_signal_drag_to_window, null ) = mouse_get_zone( self );
            if self.mouse_signal_drag_to_window != None:
              mouse_delta = ( abs(self.mouse_btn1_dn[0]-self.mouse_btn1_up[0]),
                              abs(self.mouse_btn1_dn[1]-self.mouse_btn1_up[1])  );
#             if ( mouse_delta[0] < 5 and mouse_delta[1] < 5 ):
#               (wave_i, zone_i ) = mouse_get_zone( self );
#               if wave_i != None and wave_i == self.window_selected:
#                 mouse_event_single_click_waveform( self );
#                 self.refresh_cursors = True;
#               print("Mouse!");
 

              b = self.mouse_signal_drag_to_window + 1;
              if self.container_view_list[0].visible == True:
#               print("Signal DRAG                to Window-%d" % (   b ) );
#               for (i,each_cont) in enumerate( self.container_list ):
#                 print( i,  each_cont.get_relative_rect() );
#               for (i,each_cont) in enumerate( self.container_view_list ):
#                 print( i,  each_cont.get_relative_rect() );
                (x1,y1,w1,h1) = self.container_list[1].get_relative_rect();
                (x2,y2,w2,h2) = self.container_view_list[0].get_relative_rect();
                (x3,y3,w3,h3) = self.container_view_list[4].get_relative_rect();
                (mx,my) = self.mouse_btn1_dn;
                if ( mx >= ( x1+x2+x3 ) and mx <= ( x1+x2+x3+w3 ) ):
                  if ( my >= ( y1+y2+y3 ) and my <= ( y1+y2+y3+h3 ) ):
                    proc_apply_view(self);
                    # WARNING: Item doesn't get selected until ButtonUp, so a Drag only works if
                    # you selected it first, then click and drag it. Bummer.
#                   print("Oy");
#                   assigned  = len( self.container_view_list )-2;
#                   available = assigned + 1;
#                   for each_view_name in [ self.container_view_list[available].get_single_selection() ]:
#                   for each_view in [ self.container_view_list[available] ]:
#                     print( dir(each_view_name ));
#                     print( each_view.check_pressed() );
#           else:
#             print("Unclaimed Mouse Action");


        if event.button == 2 : 
          self.mouse_btn2_up  = pygame.mouse.get_pos();# (x,y)
          self.mouse_pinch_up = pygame.mouse.get_pos();# (x,y)
          self.mouse_pinch_dn = ( None, None );
        if event.button == 3 : 
          self.mouse_btn3_up  = pygame.mouse.get_pos();# (x,y)
          self.mouse_pinch_up = pygame.mouse.get_pos();# (x,y)
          self.mouse_pinch_dn = ( None, None );

# Note : This works, but decided against using it
#       # Attempt to detect double-click on left-mouse button t<300ms
#       if ( event.button == 1 ):
#         self.mouse_btn1_up_time_last = self.mouse_btn1_up_time;
#         self.mouse_btn1_up_time      = self.pygame.time.get_ticks();
#         if ( ( self.mouse_btn1_up_time - self.mouse_btn1_up_time_last ) < 300 ):
#           rts = mouse_event_double_click( self );# Toggle the hidden attribute on signal
#           if rts:
#             self.refresh_waveforms = True;


        # If the last Button1 down selected a signal, calculate the Y delta
        # between down and up. If it crosses a threshold, reorder the signal
        if event.button == 1 and self.mouse_btn1_select == True:
          (x1,y1) = self.mouse_btn1_dn;
          (x2,y2) = self.mouse_btn1_up;
          if ( abs(y1-y2) > 10 ):
            for ( i,each_sig ) in enumerate( self.signal_list ):
              if each_sig.selected:
                sig_win = each_sig.window;
                # find the visible signal in the same window closest to the drop location
                dropped = False;
                for ( j,each_signal ) in enumerate( self.signal_list ):
                  if dropped == False:
                    if each_signal.window == sig_win and each_signal.visible == True:
                      if ( each_signal.y > each_sig.y + (y2-y1) ):
                        dropped = True; 
                        self.signal_list.insert( j, self.signal_list.pop( i ) );
                self.refresh_waveforms = True;
#               print("What a Drag!");
          self.mouse_btn1_select = False;

        # Center mouse button is a "Pinch" like Zoom To Cursors but without cursors
        # Note that it just uses the ZoomToCursor stuff and clears the cursors at
        # the end. Clicking in place is a ZoomOut
        elif event.button == 2 or event.button == 3:
          if event.button == 2:
            (x1,y1) = self.mouse_btn2_dn;
            (x2,y2) = self.mouse_btn2_up;
          else:
            (x1,y1) = self.mouse_btn3_dn;
            (x2,y2) = self.mouse_btn3_up;

          # Make sure a mouse click down and up in relatively same spot doesn't become a pinch zoom
          dx = abs(x1-x2);
#         if dx > 10:
          if dx > 5:
            x_fudge = 5;# There some wave-window border delta main window mouse position
            for ( i, each_cursor ) in enumerate( self.cursor_list ):
              each_cursor.visible == False;
              each_cursor.selected == False; 
              if i == 0: each_cursor.x = x1 - x_fudge;
              if i == 1: each_cursor.x = x2 + x_fudge;
            update_cursors_to_mouse(self);
            proc_cmd( self, "zoom_to_cursors" );
          else:
            # Btn3 is also "unselect" of selected signals.
            # Only ZoomOut on a zero-delta Btn3 click if no signals are selected
            any_selected = False;
            for each_sig in self.signal_list:
              if each_sig.selected:
                any_selected = True;
            if event.button == 2 or any_selected == False:
              proc_cmd( self, "zoom_out" );
            else:
              rts = proc_unselect(self);
              if rts:
                self.refresh_waveforms = True;

        # For mouse drags in waveform region do ZoomIn ZoomOut in Y direction
        # and ZoomToCursors in X direction
        elif event.button == 1 and self.mouse_btn1_select == False:
          cursor_selected = False;
          for each_cursor in self.cursor_list:
            if each_cursor.selected:
              cursor_selected = True;
          if cursor_selected == False:
            (x1,y1) = self.mouse_btn1_dn;
            (x2,y2) = self.mouse_btn1_up;
            dx = abs(x1-x2);
            dy = abs(y1-y2);
            # When dragging long distances horiz or vert it's easy to drift pels
            # along the other axis, so calculate a ratio to determine direction
            if dy != 0:
              d_x_over_y = dx/dy;# >4 = horizontal, < 0.25 = Vertical
            else:
              d_x_over_y = 1;

            # Left-to_Right 
            if ( dx > 10 and d_x_over_y > 4 and x2 > x1 ):
              proc_cmd( self, "pan_left" );

            # Right-to-Left 
            if ( dx > 10 and d_x_over_y > 4 and x2 < x1 ):
              proc_cmd( self, "pan_right" );

            # Up-Down
            if ( dy > 25 and d_x_over_y < 0.25 ):
              if y2 < y1:
                proc_cmd( self, "zoom_in" );
              else:
                proc_cmd( self, "zoom_out" );

# This was buggy
#           # Diagonal will rotate through windows
#           if ( dy > 50 and dx > 50 and d_x_over_y < 3 and d_x_over_y > 0.5 ):
#             if y2 > y1:
#               proc_cmd( self, "win_pagedown" );
#             else:
#               proc_cmd( self, "win_pageup" );
#             self.vars["screen_windows"] = "%01x" % self.screen_windows;
#             screen_erase(self);
#             resize_containers(self);
#             rts = True;# Force a refresh

        if self.select_text_i != None:
          rate = 8;
          if ( self.pygame.key.get_pressed()[self.pygame.K_LCTRL] or
               self.pygame.key.get_pressed()[self.pygame.K_RCTRL]   ):
            rate = 1;
          if ( event.button == 4 ):
            proc_acq_adj_inc( self, rate );
          if ( event.button == 5 ):
            proc_acq_adj_dec( self, rate );

        # 4==ScrollUp 5==ScrollDown
        # My LogitechMX mouse with momentum wheel can randomly scroll once when just
        # moving the mouse around. Attempt to filter this out by ignoring any scroll
        # that has happened more than a few seconds since the last scroll
        if ( self.has_focus and (  event.button == 4 or event.button == 5 ) ):
          if self.vars["scroll_wheel_glitch_lpf_en" ] == "1":
            tick_time = self.pygame.time.get_ticks();# time in mS
          else:
            tick_time = 0;
            self.last_scroll_wheel_tick = 0;


        # 4==ScrollUp 5==ScrollDown
        if ( self.has_focus and (  event.button == 4 or event.button == 5 ) and \
             self.window_selected != None and \
             (( tick_time - self.last_scroll_wheel_tick ) < 3000 ) and \
             not self.mouse_motion and not self.mouse_motion_prev ):
          (wave_i, zone_i ) = mouse_get_zone( self );
          #   ---------------------
          #  |  1  |2 Zoom  |   4  |
          #  | Amp |--------|Scroll|
          #  |     |3  Pan  |      |
          #   ---------------------
          if wave_i != None:
            ( zoom, pan, scroll ) = self.window_list[wave_i].zoom_pan_list;

            # Scroll wheel behaves different when no signals are selected - it controls
            # timezone window behavior for zoom, pan and signal list vertical scroll
            no_signals_selected = True;
            no_analog_signals_selected = True;
            for each_signal in self.signal_list:
              if each_signal.selected:
                no_signals_selected = False;
              if each_signal.selected and each_signal.type == "analog":
                no_analog_signals_selected = False;

            if int(self.vars["scroll_wheel_analog_en"],10) == 0:
              no_analog_signals_selected = True;

#           if no_signals_selected:
#           if no_signals_selected and self.select_text_i == None:
#           if no_analog_signals_selected and self.select_text_i == None:
#           if no_analog_signals_selected and self.select_text_i == None and \
#              self.container_display_list[0].visible:
            if no_analog_signals_selected and self.select_text_i == None:
              button_press = event.button;
              if self.vars["scroll_wheel_pan_en" ] == "0" and zone_i == 3:
                zone_i = 2;# Force Zoom
              if self.vars["scroll_wheel_zoom_en" ] == "0" and zone_i == 2:
                zone_i = 3;# Force Pan
              if self.vars["scroll_wheel_pan_en" ]  == "1" or \
                 self.vars["scroll_wheel_zoom_en" ] == "1":
                if zone_i == 3 and self.vars["scroll_wheel_pan_reversed" ] == "1":
                  if button_press == 4:
                    button_press = 5;
                  elif button_press == 5:
                    button_press = 4;
              if ( button_press == 4 and zone_i == 3 ):
                proc_cmd( self, "pan_right" );
              elif ( button_press == 5 and zone_i == 3 ):
                proc_cmd( self, "pan_left" );

              elif ( button_press == 4 and zone_i == 2 ):
                proc_cmd( self, "zoom_in" );
              elif ( button_press == 5 and zone_i == 2 ):
                proc_cmd( self, "zoom_out" );

              elif ( button_press == 4 and zone_i == 1 ):
                proc_cmd( self, "scroll_up" );
              elif ( button_press == 5 and zone_i == 1 ):
                proc_cmd( self, "scroll_down" );

#             elif ( button_press == 4 and zone_i == 4 ):
#               proc_cmd( self, "scroll_up" );
#             elif ( button_press == 5 and zone_i == 4 ):
#               proc_cmd( self, "scroll_down" );

              elif ( button_press == 4 and zone_i == 4 ):
                proc_cmd( self, "scroll_analog_up" );
              elif ( button_press == 5 and zone_i == 4 ):
                proc_cmd( self, "scroll_analog_down" );

            
            # Change the vertical scale on the selected analog waveform signal(s) 
#           else:
            elif self.container_display_list[0].visible:
              for each_signal in self.signal_list:
                if each_signal.selected:
                  if ( self.pygame.key.get_pressed()[self.pygame.K_LSHIFT] or
                       self.pygame.key.get_pressed()[self.pygame.K_RSHIFT]   ):
                    if ( event.button == 4 ):
                      each_signal.vertical_offset -= .01;
                    elif ( event.button == 5 ):
                      each_signal.vertical_offset += .01;
                  else:
                    if ( self.pygame.key.get_pressed()[self.pygame.K_LCTRL] or
                         self.pygame.key.get_pressed()[self.pygame.K_RCTRL]   ):
                      if ( event.button == 5 ):
                        proc_cmd( self, "scale_down_fine" );
                      elif ( event.button == 4 ):
                        proc_cmd( self, "scale_up_fine" );
                    else:
                      if ( event.button == 5 ):
                        proc_cmd( self, "scale_down" );
                      elif ( event.button == 4 ):
                        proc_cmd( self, "scale_up" );

              # Only update the windows that have the selected signals in them
              for (i,each_win) in enumerate( self.window_list ):
                for each_signal in self.signal_list:
                  if each_signal.selected:
                    if each_signal in each_win.signal_list:
                      if not i in self.refresh_window_list:
                        self.refresh_window_list += [i];

        if ( self.has_focus and (  event.button == 4 or event.button == 5 ) ):
          self.last_scroll_wheel_tick = tick_time;

#       # 1==LeftButton detect if a waveform window has been selected. Highlight the border
        if event.button == 1 :
          mouse_release_cursor( self );# Release any cursor being dragged
 
#         # Note: when file_dialog is open, click to closing would select the window
#         # underneath, so check for it and ignore.
#         (wave_i, zone_i ) = mouse_get_zone( self );
#         if wave_i != None and self.file_dialog == None:
#           # There are delta issues when switching windows with different time_zones
#           # Hack fix is to deselect cursors.
#           if self.window_list[self.window_selected].timezone != self.window_list[wave_i].timezone:
#             self.cursor_list[0].visible = False;
#             self.cursor_list[1].visible = False;
#             update_toggle_buttons(self);
#           if wave_i != self.window_selected:
#             select_window( self, wave_i );

#           if wave_i != self.window_selected:
#             self.cursor_list = [];
#             self.cursor_list[0].delta_txt = None;
#             for each_cursor in self.cursor_list:
#               each_cursor.delta_txt = None;
#               each_cursor.trig_delta_t = None;
#               each_cursor.trig_delta_unit = None;
#             select_window( self, wave_i );

#           update_cursors_to_window(self);# cursor sample time unit may change
#           display_text_stats( self );# 2025.07.03 update self.cursor_list[0].delta_txt
#           self.refresh_waveforms = True;
#           print("self.window_selected is %d" % self.window_selected);
#           print( self.cursor_list[0].delta_txt );
#           self.refresh_window_list += [ wave_i ];

#   wave_i = self.window_selected;
#   timezone = self.window_list[wave_i].timezone;
#   for (i,each_win) in enumerate( self.window_list ):
#     if (timezone == each_win.timezone ):
#       if i not in self.refresh_window_list:

#           if ( self.window_list[wave_i].panel.visible == True ):
#             if self.window_list[wave_i].panel.border_colour != self.color_white:
#               self.refresh_waveforms = True;
#               self.window_list[wave_i].panel.border_colour = self.color_white;
#               self.window_list[wave_i].panel.rebuild();
#               clr = self.container_list[0].border_colour;# Get default border color
#               for (i,each) in enumerate( self.window_list ):
#                 if i != wave_i:
#                   self.window_list[i].panel.border_colour = clr;
#                   self.window_list[i].panel.rebuild();
#               self.window_selected = wave_i;# 0,1 or 2
#               if self.container_view_list[0].visible:
#                 create_view_selections(self);

      # Convert PyGame events into UI events
      self.ui_manager.process_events(event)

#     if event.type != pygame.MOUSEMOTION:
#       self.refresh_waveforms = True;
#       self.container_list[0].hide(); print("Hide");

      if ( event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
           event.ui_object_id == '#main_text_entry'):
        print("Text Entry:");
        print(event.text)

#     if event.type == pygame_gui.UI_WINDOW_MOVED_TO_FRONT:
#       if event.ui_element == self.cmd_console:
#         print("Oy!");
#     if event.type == 1026:
#         print("Oy!");

      if event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED:
        if event.ui_element == self.cmd_console:
          cmd_str = event.command;
#         print("Oy!");
#         print( dir( self.cmd_console ) );
#         print( self.cmd_console.command_entry.text );
#         print( self.cmd_console.command );
#         print( len( cmd_str ));
          proc_cmd( self, cmd_str );
          # See pygame_gui.elements.ui_text_entry_line module
          # Annoying bug after command the cursor position shifts right
#         self.cmd_console.command_entry.set_text("");
#         self.cmd_console.command_entry.disable();
#         self.cmd_console.command_entry.enable();
#         self.cmd_console.command_entry.set_text_length_limit(0);
#         self.cmd_console.command_entry.set_text_length_limit(80);
#         self.cmd_console.command_entry.redraw();
#         self.cmd_console.command_entry.set_text("\r\n");
#         self.cmd_console.command_entry.set_cursor_position(0);
#         self.cmd_console.command_entry.start_text_offset = 0;
#         print( dir( self.cmd_console.command_entry ));
          self.refresh_waveforms = True;

      if event.type == pygame.KEYDOWN:
        rts = proc_key(self, event );
        if rts:
          self.refresh_waveforms = True;

      if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
        if self.file_dialog != None:
          cmd_str = self.file_dialog + " " + event.text;# ie "load_pza foo.pza"
          self.file_dialog = None;
          screen_erase(self);# Popup doesn't clean itself up
          proc_cmd( self, cmd_str );

      if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
#       if ( event.ui_object_id == "#Controls.#Display.#TimeLock"):
#         print("Hello");
        if self.vars["tool_tips_on_hover"].lower() in [ "true", "1", "yes" ]:
          self.tool_tip_obj_id    = event.ui_object_id;# ie "#Controls.#Display.#TimeLock"
          self.tool_tip_tick_time = self.pygame.time.get_ticks();# time in mS
          self.refresh_text = True;
         
      if event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
#       if ( event.ui_object_id == "#Controls.#Display.#TimeLock"):
#         print("GoodBye");
        self.tool_tip_obj_id    = None;
        self.tool_tip_tick_time = None;
        self.refresh_text = True;

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        cmd_str = convert_object_id_to_cmd( self, str( event.ui_object_id ) );
        if self.debug_mode:
          print("GUI Event %s" %  event.ui_object_id );
        if cmd_str != None:
          proc_cmd( self, cmd_str );
#         print( cmd_str );
#       self.refresh_waveforms = True;

        main_menu_press = False;

        # View applied selected
        if ( event.ui_object_id == "#Controls.#Views.#Visible.#item_list_item" ):
          self.refresh_waveforms = True;

        # View on tap selected
        if ( event.ui_object_id == "#Controls.#Views.#Hidden.#item_list_item" ):
          self.refresh_waveforms = True;


        # TODO: On startup need to select/unselect buttons for Display A+D buttons
        if ( event.ui_object_id == "#Controls.#Display.#Window-1" ):
          self.window_list[0].panel.visible = not self.window_list[0].panel.visible;
          if self.window_list[0].panel.visible :
            self.screen_windows = ( self.screen_windows & 0xE ) + 0x1;
          else:
            self.screen_windows = ( self.screen_windows & 0xE ) + 0x0;
          self.vars["screen_windows"] = "%01x" % self.screen_windows;
          screen_erase(self);
          resize_containers(self);

        if ( event.ui_object_id == "#Controls.#Display.#Window-2" ):
          self.window_list[1].panel.visible = not self.window_list[1].panel.visible;
          if self.window_list[1].panel.visible :
            self.screen_windows = ( self.screen_windows & 0xD ) + 0x2;
          else:
            self.screen_windows = ( self.screen_windows & 0xD ) + 0x0;
          self.vars["screen_windows"] = "%01x" % self.screen_windows;
          screen_erase(self);
          resize_containers(self);

        if ( event.ui_object_id == "#Controls.#Display.#Window-3" ):
          self.window_list[2].panel.visible = not self.window_list[2].panel.visible;
          if self.window_list[1].panel.visible :
            self.screen_windows = ( self.screen_windows & 0xB ) + 0x4;
          else:
            self.screen_windows = ( self.screen_windows & 0xB ) + 0x0;
          self.vars["screen_windows"] = "%01x" % self.screen_windows;
          screen_erase(self);
          resize_containers(self);

#       if ( event.ui_object_id == "#Controls.#Display.#TimeLock"):
#         proc_cmd( self, "time_lock" );
#         update_toggle_buttons(self);

# HERE72
        if ( event.ui_object_id == "#Controls.#Display.#bd_shell"):
#         self.cmd_console.visible = not self.cmd_console.visible;
          vis                      = not self.cmd_console.visible;
          # New 2025.04.28
#         if not self.cmd_console.visible:
          if not vis:
#           print("Hide console!");
#           print( self.cmd_console.ui_container );
#           self.cmd_console.ui_container.visible = False;
#           self.cmd_console.ui_container.hide();
            self.cmd_console.hide();
#           for each in self.cmd_console.get_container():
#             each.hide();
          else:
            self.cmd_console.show( );
#           for each in self.cmd_console.get_container():
#             each.show();

           
#         print("dir(self.cmd_console)");
#         print( dir( self.cmd_console ) );
#         print("__contains__");
#         print( self.cmd_console.__contains__ );
     
          update_toggle_buttons(self);
          # screen_windows is a hex number of 4 binary bits indicating
          # which windows are visible. 3 waveforms and 1 bd_shell
          if ( self.cmd_console.visible == True ):
            self.screen_windows = ( self.screen_windows & 0x7 ) + 0x8;
          else:
            self.screen_windows = ( self.screen_windows & 0x7 ) + 0x0;
          self.vars["screen_windows"] = "%01x" % self.screen_windows;
          screen_erase(self);
          resize_containers(self);
#         pygame.display.update();# New 2025.04.29     
#         self.ui_manager.update( time_delta = 0 );# New 2025.04.29

#       if ( event.ui_object_id == "#console_window.#close_button"):
#         self.cmd_console.visible = False;
#         screen_erase(self);
#         resize_containers(self);
#         id_str = ["#Controls","#Display", "#bd_shell"];
#         update_toggle_buttons(self);

#HERE75
        if ( event.ui_object_id == "#console_window.#close_button"):
#         self.cmd_console.process_event( event );
          self.cmd_console.hide();
#         self.cmd_console.visible = False;

          # Create a new version since PygameGUI just killed the original
          self.cmd_console = UIConsoleWindow(rect=pygame.rect.Rect((10,10), (200,100)),
                                     manager=self.ui_manager,window_title="bd_shell");
#         self.cmd_console.hide();
#         self.cmd_console.show();
#         screen_erase(self);
#         resize_containers(self);
          # And now close it, which is really just hiding it.
          cmd_close_bd_shell(self);

#         self.cmd_console.hide();
#         update_toggle_buttons(self);
#         # screen_windows is a hex number of 4 binary bits indicating
#         # which windows are visible. 3 waveforms and 1 bd_shell
#         if ( self.cmd_console.visible == True ):
#           self.screen_windows = ( self.screen_windows & 0x7 ) + 0x8;
#         else:
#           self.screen_windows = ( self.screen_windows & 0x7 ) + 0x0;
#         self.vars["screen_windows"] = "%01x" % self.screen_windows;
#         screen_erase(self);
#         resize_containers(self);

        if ( event.ui_object_id == "#Controls.#Display.#Cursor-1" ):
          self.cursor_list[0].visible = not self.cursor_list[0].visible;
          if self.window_selected != None:
            w = self.window_list[self.window_selected].surface.get_width();
            self.cursor_list[0].x = ( w / 2 ) - 50;# Init to Left of Center
          update_cursors_to_mouse( self );
          screen_erase(self);
          resize_containers(self);

        if ( event.ui_object_id == "#Controls.#Display.#Cursor-2" ):
          self.cursor_list[1].visible = not self.cursor_list[1].visible;
          if self.window_selected != None:
            w = self.window_list[self.window_selected].surface.get_width();
            self.cursor_list[1].x = ( w / 2 ) + 50;# Init to Right of Center
          update_cursors_to_mouse( self );
          screen_erase(self);
          resize_containers(self);

        # Apply a new view to a Window
        if ( event.ui_object_id == "#Controls.#Views.#Apply" ):
          proc_apply_view( self );
#         create_view_selections( self );
          self.refresh_waveforms = True;
          self.refresh_sig_names = True;

#       if ( "#Controls.#Views.#Preset-" in event.ui_object_id ):
#         preset_i = int( event.ui_object_id[-1] ) - 1;
#         (button_label, file) = self.view_preset_list[ preset_i ];
#         if ( button_label != None and file != None ):
#           proc_cmd( self, "source %s" % file );

        # Remove a view from a Window
        if ( event.ui_object_id == "#Controls.#Views.#Remove" ):
          proc_remove_view( self );
#         create_view_selections( self );
          self.refresh_waveforms = True;
          self.refresh_sig_names = True;

        if ( event.ui_object_id == "#Controls.#Main.#Views" ):
#         self.container_view_list[0].visible        = True;
#         self.container_acquisition_list[0].visible = False;
#         self.container_display_list[0].visible     = False;
#         self.select_text_i = None;# Clear old text selections
#         main_menu_press = True;
#         self.refresh_waveforms = True;# New to highlight triggerable signals in Acquisition
#
#         # Update the view selections whenever view controls are opened
#         if self.container_view_list[0].visible:
#           create_view_selections(self);
          cmd_select_viewconfig( self );

        if ( event.ui_object_id == "#Controls.#Main.#Acquisition" ):
#         self.container_view_list[0].visible        = False;
#         self.container_acquisition_list[0].visible = True;
#         self.container_display_list[0].visible     = False;
#         self.select_text_i = None;# Clear old text selections
#         main_menu_press = True;
#         self.refresh_waveforms = True;# New to highlight triggerable signals in Acquisition
          cmd_select_acquisition( self );

        if ( event.ui_object_id == "#Controls.#Main.#Display" ):
#         self.container_view_list[0].visible        = False;
#         self.container_acquisition_list[0].visible = False;
#         self.container_display_list[0].visible     = True;
#         self.select_text_i = None;# Clear old text selections
#         main_menu_press = True;
#         auto_select_window(self);
#         self.refresh_waveforms = True;# New to highlight triggerable signals in Acquisition
          cmd_select_navigation( self );
#       print( event.ui_object_id );

        if ( main_menu_press == True ):
          proc_main_menu_button_press( self );


      # https://pygame-gui.readthedocs.io/en/v_065/pygame_gui.elements.html
#     if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
#       print("New Selection on %s" % ( str(event.ui_object_id)));
#       self.refresh_waveforms = True;

# Enabling double-click on UI_SELECTION has issues
      if event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
        print("Double-Clicked");
#       self.refresh_waveforms = True;

      # End of event loop


###############################################################################
# the main GUI loop
  def run(self):
    log( self, ["NOTE: GUI should now be up and running."] );
    log( self, ["If you can't see the GUI it might be placed off-screen."] );
    log( self, ["CTRL-C out and delete the following lines from sump3.ini"] );
    log( self, ["  screen_x = 123"]                                        );
    log( self, ["  screen_y = 456"]                                        );
    log( self, ["run()"] );
    spinner = "|";
    while self.running:
      # check for input
      self.process_events()
      self.ui_manager.update( time_delta = 0 );
      if self.mode_acquire and self.sump_connected:
        spinner = rotate_spinner( spinner );
        self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" HW Status: Waiting for trigger " + spinner);

#       cmd_thread_lock(self);
#       self.sump.rd_status();
#       cmd_thread_unlock(self);

        self.sump.rd_status();

        ( stat_str, status ) = self.sump.status;
        log( self, ["mode_acquire status is %s" % stat_str ] );
        if stat_str == "acquired":
          self.mode_acquire = False;
          pygame.time.wait(1000);# time in mS. 
          cmd_sump_download( self );
        elif stat_str == "triggered":
          pygame.time.wait( self.max_pod_acq_time_ms );
          self.mode_acquire = False;
          cmd_sump_download( self );
        else:
          pygame.time.wait(1000);# time in mS. 

      if ( self.refresh_waveforms == False and self.refresh_cursors == False and
           len( self.refresh_window_list) == 0                                    ):
        pygame.time.wait(10);# time in mS. Without this CPU is always 30% busy

      if ( self.refresh_waveforms == True or len( self.refresh_window_list ) != 0 ):
#       print( self.refresh_window_list );
        create_waveforms( self );
        self.refresh_cursors = True;
#     if ( self.refresh_cursors == True ):
#       create_cursor_lines(self); # Generate cursors


      if ( self.refresh_waveforms == True or 
           len( self.refresh_window_list ) != 0 or
           self.refresh_sig_names == True or 
           self.refresh_cursors == True      ):
        # 2024.12.17 update cursor deltas otherwise text and GUI deltas won't match
        # The create_cursor_lines() method uses calculations from display_text_stats()
        # value that is shared is self.cursor_list[0].delta_txt
        if ( self.refresh_cursors == True ):
          display_text_stats( self );
        create_cursor_lines(self); # Generate cursors
        draw_surfaces(self);
        self.refresh_waveforms = False;
        self.refresh_sig_names = False;
        self.refresh_cursors   = False;
        self.refresh_window_list  = [];
#       self.refresh_text = True;
        pygame.time.wait(10);# time in mS. 

      # Note : You can draw raw PyGame stuff here and it will be on top of Widgets
      self.ui_manager.draw_ui(self.screen);

      # Now draw the text stats on top of the widget stuff
#     if self.has_focus:
      if True:
        self.refresh_text = True;
        if self.refresh_text:
          display_text_stats( self );# Warning this happens every loop!
          self.refresh_text = False;
        # Make sure the text doesn't draw on top of any UIFileDialog box
        if self.file_dialog == None:
          draw_text_stats( self, self.text_stats );

      pygame.display.update();# Now off to the GPU

      if not self.has_focus:
        if self.telnet_socket != None:
          import select;
          import socket;
          prompt = "bd_shell>";
          read_list = [ self.telnet_socket ];
          connected_jk = True;
          client_socket = None;
          while ( connected_jk ):
            timeout = 0;# Poll
            readable, writable, errored = select.select(read_list, [], [], timeout);
            for s in readable:
              if s is self.telnet_socket:
                client_socket, address = self.telnet_socket.accept();
#               client_socket.setblocking(False);
                read_list.append(client_socket);
#               print(("Connection established from", address));
                log( self, [ ("Connection established from", address) ] );
                client_socket.send((prompt).encode("utf-8"));# Conv Byte Array to String
                self.sump_remote_in_use = True;
                txt = "";
              else:
                data = client_socket.recv(1024)
                if data:
                  try:
                    txt += data.decode("utf-8");
                  except:
                    txt += "";
                  if "\n" in txt:
#                   print( txt );
                    if "quit" not in txt and "exit" not in txt:
                      rts = proc_cmd( self, txt.rstrip() );
#                     client_socket.send(("\r\n").encode("utf-8"));# Conv Byte Array to String
                      if rts != None:
                        for each_rts in rts:
                          client_socket.send((each_rts+"\r\n").encode("utf-8"));# Conv Byte Array to String
                      txt = "";
                      client_socket.send((prompt).encode("utf-8"));# Conv Byte Array to String
                    else:
                      client_socket.close();
                      client_socket = None;
                      self.telnet_socket.close();
                      # This is a hack. Once a client session has closed it is done for, so start it up again.
#                     self.telnet_socket.detach();
                      self.telnet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                     self.telnet_socket.setblocking(False);
                      HOST =      self.vars["sump_remote_telnet_host"];
                      if HOST == "*.*.*.*":
                        HOST = "";# Accept anybody
                      PORT = int( self.vars["sump_remote_telnet_port"], 10 );
                      self.telnet_socket.bind((HOST, PORT));
                      self.telnet_socket.listen(4);
                      connected_jk = False;
                else:
#                 print(("Connection closed from", address));
                  log( self, [ ("Connection closed from", address) ] );
                  connected_jk = False;
            if len(readable) == 0 and client_socket == None:
              connected_jk = False;
                

        # Don't spin up a CPU when the GUI is out of focus. 
        # Exception is when sump_remote is in use.
        if self.sump_remote_in_use:
          pygame.time.wait(10);# time in mS. GUI is out of focus
        else:
          pygame.time.wait(250);# time in mS. GUI is out of focus

#       if os.path.exists( file_name ):
#         proc_cmd( self, "source %s" % file_name );
#         os.remove( file_name );

        if int( self.vars["sump_remote_file_en"], 10 ) == 1:
          file_name = self.vars["sump_script_remote"];
          # UUT Path is the default path if it exists, otherwise use the CWD
          paths = [];
          if self.path_to_uut != None:
            paths += [ self.path_to_uut ];
#         else:
#           paths += [ os.getcwd() ];
          paths += [ os.getcwd() ];

          # Look for the file specified in the usual places.
          for each_path in paths:
            file_path_name = os.path.join( each_path, file_name );
            if ( os.path.exists( file_path_name )):
              self.sump_remote_in_use = True;
              cmd_list = file2list( file_path_name );
              rts = [];
              dbg_rts = [];
              for each_cmd in cmd_list:
#               print( each_cmd );
                log( self, [ each_cmd ] );
                results = proc_cmd( self, each_cmd );
                # Flatten potential nested list from sourcing a file
                for each_i in results:
                  if type( each_i ) == str:
                    rts += [ each_i ];
                  else:
                    for each_j in each_i:
                      rts += [ each_j ];
#               rts += results;
#               dbg_rts += [ ( each_cmd, results ) ];
#               rts += proc_cmd( self, each_cmd );
#             for each in rts:
#               print( str( type(rts) ) + " " + str(rts ) );
#             for each in dbg_rts:
#               print( each );

              file_out_path_name = os.path.join( each_path, "sump_remote_results.txt" );
              list2file( file_out_path_name, rts );
              pid = os.getpid();
              file_tmp_name = file_path_name + "." + str(pid); 
              try:
                if ( os.path.exists( file_tmp_name )):
                  os.remove( file_tmp_name );
                os.rename( file_path_name, file_tmp_name );# Tells host okay to send next command
                os.remove( file_tmp_name );
              except:
                log( self, ["ERROR mv+rm on %s %s" % ( file_path_name, file_tmp_name ) ] );

      if self.mode_acquire:
        pygame.time.wait(750);# Limit the polling rate


# Rotate a little spinner for acquire loop waiting for trigger
def rotate_spinner( spinner ):
  if   spinner == "|": spinner = "/";
  elif spinner == "/": spinner = "-";
  elif spinner == "-": spinner = "\\";
  else               : spinner = "|";
  return spinner;


###############################################################################
# See if the selected waveform window is not visible and default select
# 1st visible window as the selected window
def auto_select_window( self ):
  i = self.window_selected;
  if i == None:
    i = 0;# Make a default to 1st window
  if self.window_list[i].panel.visible == False:
    for j in range(2,-1,-1):
      if self.window_list[j].panel.visible:
        select_window( self, j );
  else:
    select_window( self, i );
#   select_window( self, i );
#   self.window_selected = i;
#   select_window( self, 0 );# Default to 1st window
# print("self.window_selected is now %s" % self.window_selected );
  return;

def select_window( self, wave_i ):
  if wave_i != None: 
    # New 2023.06.16 If selected window is not visible, make it visible
    if ( self.window_list[wave_i].panel.visible != True ):
# 2025.04.29
#     self.window_list[wave_i].panel.visible = True;   
      self.window_list[wave_i].panel.show();
      resize_containers(self);# Resize based on screen dimensions
    if ( self.window_list[wave_i].panel.visible == True ):
      if self.window_list[wave_i].panel.border_colour != self.color_selected:
        self.refresh_waveforms = True;
        self.window_list[wave_i].panel.border_colour = self.color_selected;
        self.window_list[wave_i].panel.border_width  = 2;
        self.window_list[wave_i].panel.shadow_width = 0;
        self.window_list[wave_i].panel.rebuild();

        clr = self.container_list[0].border_colour;# Get default border color
        for (i,each) in enumerate( self.window_list ):
          if i != wave_i:
            self.window_list[i].panel.border_colour = clr;
            self.window_list[i].panel.border_width  = 2;
            self.window_list[i].panel.shadow_width = 1;
            self.window_list[i].panel.rebuild();
        self.window_selected = wave_i;# 0,1 or 2
        if self.container_view_list[0].visible:
          create_view_selections(self);
  else:
    clr = self.container_list[0].border_colour;# Get default border color
    for (i,each) in enumerate( self.window_list ):
      self.window_list[i].panel.border_colour = clr;
      self.window_list[i].panel.border_width  = 2;
      self.window_list[i].panel.shadow_width = 1;
      self.window_list[i].panel.rebuild();
    self.window_selected = None;
# update_cursors_to_window(self);# cursor sample time unit may change
  return;


def close_window( self, wave_i ):
  if wave_i != None: 
    if ( self.window_list[wave_i].panel.visible == True ):
# 2025.04.29
#     self.window_list[wave_i].panel.visible = False;   
      self.window_list[wave_i].panel.hide();
      resize_containers(self);# Resize based on screen dimensions
      update_toggle_buttons( self );
  return;

def close_bd_shell( self ):
# self.cmd_console.visible = False;
  self.cmd_console.hide();
  resize_containers(self);# Resize based on screen dimensions
  update_toggle_buttons( self );
  return;

def open_bd_shell( self ):
# self.cmd_console.visible = True;
  self.cmd_console.show();
  resize_containers(self);# Resize based on screen dimensions
  update_toggle_buttons( self );
  return;

###############################################################################
# The toggle buttons aren't real toggle buttons. I just make them look that way
# using select() and unselect() methods.
# This function calls either select() or unselect() based on the visibility of 
# the object it controls
def update_toggle_buttons( self ):
  toggle_list = [ ("#bd_shell", self.cmd_console.visible          ),
                  ("#Window-1", self.window_list[0].panel.visible ),
                  ("#Window-2", self.window_list[1].panel.visible ),
                  ("#Window-3", self.window_list[2].panel.visible ),
                  ("#Cursor-1", self.cursor_list[0].visible       ),
                  ("#Cursor-2", self.cursor_list[1].visible       ),
                  ("#TimeLock", self.time_lock                    ),
                ];
  for each_button in self.display_button_list:
    (a,b,c) = each_button.object_ids;
    for ( each_object_id, each_visible ) in toggle_list:
      if each_object_id == c:
        if each_visible:
          each_button.select();
        else:
          each_button.unselect();
  return;


###############################################################################
# Display raw PyGame text lines at specified raw (x,y) location
# What is diplayed changed based on the screen mode of Display,Acquisition,Views
# WARNING: This gets called every PyGame tick
def display_text_stats( self ):
  # Wait 100ms instead of recalculating everything every pygame tick
  if self.pygame.time.get_ticks() - self.text_stats_tick_time < 100:
    return;
  else:
    self.text_stats_tick_time = self.pygame.time.get_ticks();

  self.select_text_rect = ( 0,0,0,0 );
  bold_i = self.select_text_i;
  l_time = None;

  x1 = None;
  y1 = None;
  extra_txt_list = [];

  # Views Panel is open
  if self.container_view_list[0].visible == True :
    (x,y,w,h) = self.container_view_list[0].rect;
    x1 = x;
    y1 = y+h;
    rts = [];
    if self.window_selected != None:
      win_num = self.window_selected;
      my_win = self.window_list[win_num];
      rts += [ "Window   = %s" % my_win.name ];
      rts += [ "timezone = %s" % my_win.timezone ];
 

      for (i, each_view) in enumerate( my_win.view_list ):
        if i == 0:
          rts += ["Views:"];
        if each_view.name != None:
          rts += [" "+each_view.name];
    else:
        rts += ["No Window Selected"];

#   assigned = 4+3;
#   available = 4+4;
    assigned  = len( self.container_view_list )-2;
    available = assigned + 1;
#   selected = [ self.container_view_list[available].get_single_selection() ];
#   if selected != [None]:

#   assigned_selected  = self.container_view_list[assigned].get_multi_selection();
#   available_selected = self.container_view_list[available].get_multi_selection();
    assigned_selected  = [ self.container_view_list[assigned].get_single_selection() ]; 
    available_selected = [ self.container_view_list[available].get_single_selection()];
    
    if len(available_selected) != 0 or len(assigned_selected) != 0:
#     rts += ["------------------"];
      rts = [];
    for each_sel in assigned_selected + available_selected:
      if each_sel != None:
        rts += [ each_sel+ ":" ];
        for each_view in self.view_ontap_list:
          if each_view.name == each_sel:
            (file_path,filename) = os.path.split( each_view.filename );
            rts += [" %s" % filename ];
            if each_view.timezone != None:
              rts += [" timezone = %s" % each_view.timezone ];
            if   len( each_view.user_ctrl_list ) != 0:
              for (a,b) in each_view.user_ctrl_list:
                rts += [" user_ctrl%s = %s" % (a,b) ];
            try:
              rts += [" signal_list:"];
              file_list = file2list( each_view.filename );
              for each_line in file_list:
                words = " ".join(each_line.split()).split(' ') + [None] * 4;
                if words[0] != None:
#                 if words[0] == "create_signal":
                  if words[0] == "create_signal" or words[0] == "create_bit_group":
                    if words[1] != None:
                      rts += ["  " + words[1] ];
            except:
              rts += [" Failed to open %s" % (each_view.filename) ];
            
              
    self.text_stats = ( rts, extra_txt_list, (x1,y1), bold_i );

  # Display Panel is open. For the selected window, display info about it and 
  # cursors. If any signals are selected, display info about them as well but don't
  # display the main stuff as there's limited space.
  if self.container_display_list[0].visible == True :
    delta = "\u0394";# unicode for delta triangle. I like source code in 7bit ASCII.
    indent = " ";
    (x,y,w,h) = self.container_display_list[0].rect;
    x1 = x;
    y1 = y+h;
    if self.cursor_list[0].visible:
      line1 = "Cursor-1 = %d" % self.cursor_list[0].x;
    else:
      line1 = "";
    if self.cursor_list[1].visible:
      line2 = "Cursor-2 = %d" % self.cursor_list[1].x;
    else:
      line2 = "";

#   if any( each.selected for each in self.signal_list ):
#     short_text = True;
#   else:
#     short_text = False;
    short_text = False;

    rts = [];
    min_time = 0; max_time = 0;
    for each_win in self.window_list:
      if ( each_win.sample_period != None and each_win.sample_unit != None and
           each_win.panel.visible ):
        ( period, unit ) = time_ps( each_win.sample_period, each_win.sample_unit );
        total   = each_win.samples_total;
        shown   = each_win.samples_shown;
        trigger = each_win.trigger_index;
        if trigger != None and total != None:
          l_time = -( trigger * period );
          r_time = +( (total - trigger) * period );
          if l_time < min_time:
            min_time = l_time;
          if r_time > max_time:
            max_time = r_time;
    total_time = abs(min_time) + max_time;

    (a,b) = time_rounder( min_time, "ps" );
    (c,d) = time_rounder( max_time, "ps" );
    if not short_text:
      wheel_txt = "";
      (wave_i, zone_i ) = mouse_get_zone( self );

      if wave_i != None: 
        if self.window_list[ wave_i ].grid_enable:
          if   zone_i == 1:
            wheel_txt = "Signal Scroll";
          elif zone_i == 2:
            wheel_txt = "H-Scale";
          elif zone_i == 3:
            wheel_txt = "H-Position";
          elif zone_i == 4:
            wheel_txt = "V-Position";
        else:
          if   zone_i == 1:
            wheel_txt = "Signal Scroll";
          elif zone_i == 2:
            wheel_txt = "Zoom";
          elif zone_i == 3:
            wheel_txt = "Pan";
          elif zone_i == 4:
            wheel_txt = "";

      if wave_i != self.window_selected and wave_i != None:
        rts += ["--Window Not Selected--"];
      else:
        rts += ["MouseWheel: %s" % wheel_txt ];

      rts += ["Time: %d%s to +%d%s" % (a,b,c,d) ];
#     rts += ["View: %d%s to +%d%s" % (a,b,c,d) ];

#   font_size = int( self.vars["font_size"] );
    font_size = int( self.vars["font_size_toolbar"] );
    if font_size > 20:
      w = 10.0;
    elif font_size < 14:
      w = 30.0; 
    else:
      w = 20.0;

    first_pass = True;
    for (i,each_win) in enumerate(self.window_list):
      if ( each_win.sample_period != None and each_win.sample_unit != None and
           each_win.panel.visible ):
        ( period, unit ) = time_ps( each_win.sample_period, each_win.sample_unit );
        total   = each_win.samples_total;
        shown   = each_win.samples_shown;
        start   = each_win.samples_start_offset;
        trigger = each_win.trigger_index;
        if trigger != None and total != None:
          l_time = -( trigger * period );# Trigger is T=0, so l_time will be like -10 uS
          r_time = +( (total - trigger) * period );# r_time will be like +10 uS
          # Make extreme left T=0 and remove negative numbers
          l_time += abs(min_time);# Now l_time is 0.
          r_time += abs(min_time);
#       w = 20.0;

        if first_pass:
          first_pass = False;
          if total_time != 0:
            # Trigger Position
            line = " " * int(w);
            j = int( ( abs(min_time) / total_time ) * w);
            line = line[:j] + "T" + line[j+ 1:]
            if not short_text:
              rts += ["   %s" % line ];

        # Window Total and Shown positions
        #  "[   {  }    ]"
        if l_time != None:
          line = " " * int(w);
          ls_time = l_time + ( start * period );
          rs_time = ls_time + ( shown * period );

#         j1 = round( ( ls_time / total_time ) * w);
#         j2 = round( ( rs_time / total_time ) * w);
          # New 2024.11.05, fixed the varying width of "{ }" issue
          j1 = round( ( ls_time / total_time ) * w);
          j2 = j1+round( ( (rs_time-ls_time) / total_time ) * w);
#         print( ls_time, rs_time, j1, j2 );
          if j1 == j2:
            if j1 == int( w ):
              j1 = int( w - 1 );
            if j1 == 0:
              j1 = 1;
            line = line[:j1] + "|" + line[j1+ 1:]
          else:
            line = line[:j1] + "{" + line[j1+ 1:]
            line = line[:j2] + "}" + line[j2+ 1:]

          j = round( ( l_time / total_time ) * w);
          line = line[:j] + "[" + line[j+ 1:]
          j = round( ( r_time / total_time ) * w);
          line = line[:j] + "]" + line[j+ 1:]
          if "|" not in line and "{" not in line and "}" in line:
            line = line.replace("[ ","[{" );
          elif "|" not in line and "}" not in line and "{" in line:
            line = line.replace(" ]","}]" );

          if "[" not in line:
            line = line.replace("]","[]" );
          if "[}" in line:
            line = line.replace("[}","[|" );
          if "{]" in line:
            line = line.replace("{]","|]" );
          if "{" not in line and "}" not in line and "|" not in line:
            line = line.replace("[ ","[{" );
            line = line.replace(" ]","}]" );
          if not short_text:
#           rts += ["W%d %s" % (i+1,line) ];
            rts += ["W%d%s" % (i+1,line) ];

    if self.window_selected != None:
      win_num = self.window_selected;
      my_win  = self.window_list[win_num];
      x_space       = my_win.x_space;
      samples_start_offset  = my_win.samples_start_offset;
      sample_unit  = my_win.sample_unit;
      sample_period = my_win.sample_period;
      trigger_index = my_win.trigger_index;

    if self.window_selected != None and not short_text:
#     win_num = self.window_selected;
#     my_win  = self.window_list[win_num];
#     x_space       = my_win.x_space;
#     samples_start_offset  = my_win.samples_start_offset;
#     sample_unit  = my_win.sample_unit;
#     sample_period = my_win.sample_period;
#     trigger_index = my_win.trigger_index;
#     if my_win.samples_viewport != None:
#       rts += [ my_win.samples_viewport ];# ie "[  ---T-- ]"
#     rts += [ ""];
#     rts += [ "Window   = %s" % my_win.name ];
#     rts += [ "timezone = %s" % my_win.timezone ];
#     rts += [ "Window: %s,%s" % ( my_win.name, my_win.timezone ) ];

      if ( my_win.sample_period != None and
           my_win.sample_unit   != None and
           my_win.samples_total != None and
           my_win.samples_shown != None      ):
        capture_width = my_win.sample_period * my_win.samples_total;
        visible_width = my_win.sample_period * my_win.samples_shown;
        (a,b) = time_rounder( capture_width, my_win.sample_unit );
        (c,d) = time_rounder( visible_width, my_win.sample_unit );
#       rts += [ "capture width = %d %s" % (a,b) ];
#       rts += [ "visible width = %d %s" % (c,d) ];

# New 2025.01.17
        if my_win.grid_enable:
          rts += [ "Window-%s %.1f%s/div" % ( my_win.name, (round((c/1.0),3)/10.0),d ) ];
        else:
          rts += [ "Window-%s" % ( my_win.name                  ) ];
        rts += [ " Visible: %d%s of %d%s" % (c,d,a,b) ];

#       if my_win.grid_enable:
#         rts += [ "%d %s per division" % ( round((c/10.0),3),d ) ];

#       if my_win.grid_enable:
#         rts += [ "%d %s per division" % ( round((a/10.0),3),b ) ];

#     else:
#       print(my_win.sample_period, my_win.sample_unit, my_win.samples_total, my_win.samples_shown );

#   if self.window_selected != None and not short_text:
#     # List all the Views assigned to this window
#     for (i, each_view) in enumerate( my_win.view_list ):
#       if i == 0:
#         rts += ["views:"];
#       rts += [" "+each_view.name];
      
#   if self.window_selected != None and not short_text:
    if self.window_selected != None :
      # List all the cursors
      if trigger_index != None and x_space != 0:
        txt = "";
        self.cursor_list[0].delta_txt = None;
        if self.cursor_list[0].visible and sample_unit != None and sample_period != None:
          c1_i = float( self.cursor_list[0].x / x_space ) + samples_start_offset - trigger_index;
          c1_t = c1_i * sample_period;
        if self.cursor_list[1].visible and sample_unit != None and sample_period != None:
          c2_i = float( self.cursor_list[1].x / x_space ) + samples_start_offset - trigger_index;
          c2_t = c2_i * sample_period;

        if self.cursor_list[0].visible and self.cursor_list[1].visible:
          if sample_period != None and sample_unit != None:
            c12_t_delta = abs( c1_t - c2_t );# Delta in time
            (a,b) = time_rounder( c12_t_delta, sample_unit );
            txt = "%0.1f%s" % ( a,b);
            self.cursor_list[0].delta_txt = txt;
            txt  = indent+delta+txt;
#           print("sample_period is %d : sample_unit is %s" % ( sample_period, sample_unit ) );

        if self.cursor_list[0].visible or self.cursor_list[1].visible:
          rts += ["Cursors:" + txt];

        if self.cursor_list[0].visible and sample_unit != None and sample_period != None:
          (a,b) = time_rounder( c1_t, sample_unit );
          rts += [indent+"C1: %+0.3f%s" % ( a,b )];

        if self.cursor_list[1].visible and sample_unit != None and sample_period != None:
          (a,b) = time_rounder( c2_t, sample_unit );
          rts += [indent+"C2: %+0.3f%s" % ( a,b )];

      elif x_space == 0:
        # This will happen if you collapse all the signals and the cursors are on.
#       print("ERROR-948 : Divide-by-zero on x_space == %d" % x_space );
        pass; # NOP

#           t_delta = c_delta * my_win.sample_period;# Delta in time units
#             v_delta = abs( analog_value_list[0] - analog_value_list[1] );
#             rts += [indent+delta+"A = %0.1f %s" % ( v_delta, each_sig.units )];

#       if self.cursor_list[0].visible and self.cursor_list[1].visible:
#         c_delta = abs( c1 - c2 );# Delta in sample units
#           if each_sig.sample_period != None:
#             t_delta = c_delta * each_sig.sample_period;# Delta in time units
#             rts += [indent+delta+"T = %0.1f %s" % ( t_delta, each_sig.sample_unit )];
#             v_delta = abs( analog_value_list[0] - analog_value_list[1] );
#             rts += [indent+delta+"A = %0.1f %s" % ( v_delta, each_sig.units )];

    # Display Measurements then Selected signals
    tall_measurements = int( self.vars["screen_measurements_tall"],10 );
    for j in range(0,2):
      if self.window_selected != None :
        # Display info about selected visible signals in the selected window 
        display_measurements = False;
        if ( j == 0 ):
          for each_sig in self.signal_list:
            if ( each_sig in self.measurement_list ) and \
                 each_sig.visible and each_sig.parent == my_win and each_sig.type != "group":
              display_measurements = True;
          if display_measurements:
            rts += ["Measurements:"];
        else:
          for each_sig in self.signal_list:
            if ( each_sig.selected ) and \
                 each_sig.visible and each_sig.parent == my_win and each_sig.type != "group":
              display_measurements = True;
          if display_measurements:
            rts += ["Selected:"];

        for each_sig in self.signal_list:
          if ( each_sig.selected or each_sig in self.measurement_list ) and \
               each_sig.visible and each_sig.parent == my_win and each_sig.type != "group":
            sig_name = ""; delta_txt=""; upd_txt=""; min_max_txt=""; range_txt=""; vo_txt="";
            sig_name = each_sig.name;
            if len(sig_name) > 16:
              sig_name = sig_name[0:14] + "..";
            sig_name = " %s:" % sig_name;

#           print("each_sig.type is %s " % each_sig.type );
            rts_sig = [];
            if each_sig.type == "analog":

              if each_sig.selected and each_sig.units_per_division != None and each_sig.units != None:
                # Round the decimal to one digit and add command separators for thousands
                units_per_division = round( each_sig.units_per_division,3 );
                if j == 1:
                  upd_txt = " "+comma_separated(units_per_division) + each_sig.units + " per div";

              if each_sig.selected and j == 1:
                vo_txt = " "+ "%0.2f Vertical Offset" % each_sig.vertical_offset;

              if each_sig.selected and each_sig.units_per_division != None and \
                 each_sig.units != None and len( each_sig.values ) != 0:
                signal_val_list = [];
                # TODO: This should be a list comprehension
                for val_raw in each_sig.values: 
                  if val_raw != None:
                    val_raw *= each_sig.units_per_code;
                    val_raw += each_sig.offset_units;
                    val_raw = round( val_raw, 3 );
                    signal_val_list += [ val_raw ];
                # ADC samples may be None, which results in zero length min/max
                if len( signal_val_list ) != 0:
                  val_min = three_decimal_places( min( signal_val_list ) );
                  val_max = three_decimal_places( max( signal_val_list ) );
                  val_min_str = comma_separated(val_min); # Comma thousand separator
                  val_max_str = comma_separated(val_max); # Comma thousand separator
                  val_min_str += each_sig.units;
                  val_max_str += each_sig.units;
                  min_max_txt = " "+"Min/Max "+val_min_str+"/"+val_max_str;

                  range_min = three_decimal_places( each_sig.offset_units );
                  range_max = three_decimal_places( each_sig.offset_units + ( each_sig.range * each_sig.units_per_code ));
                  range_min_str = comma_separated(range_min); # Comma thousand separator
                  range_max_str = comma_separated(range_max); # Comma thousand separator
                  range_min_str += each_sig.units;
                  range_max_str += each_sig.units;
                  range_txt = " "+"Range "+range_min_str+"/"+range_max_str;
  #                 print( range_txt );

              # Display the values for the selected signals at each cursor
              analog_value_list = [];
              c_txt_list = ["",""];
              for (i,each_cur) in enumerate( self.cursor_list ):  
                if each_cur.visible and x_space != 0:
                  sample_index = samples_start_offset + int( float(each_cur.x) / x_space );
                  if sample_index < len( each_sig.values ) and sample_index > 0:
                    val_raw = each_sig.values[sample_index];
                    if val_raw != None:
                      val_raw *= each_sig.units_per_code;
                      val_raw += each_sig.offset_units;
                      analog_value_list += [ val_raw ];
                      if each_sig.format == "analog":
                        val_raw = round( val_raw, 3 );
                        val_str = comma_separated(val_raw); # Comma thousand separator

                      elif each_sig.format == "hex":
                        val_str = "%08x" % int(val_raw);
                        val_str = val_str[-each_sig.nibble_cnt:]+" ";
                      else:
                        val_str = "%d " % int(val_raw);

                      if each_sig.units != None:
                        val_str += " " + each_sig.units;
                      c_txt_list[i] = indent+" C%d: %s" % ( (i+1), val_str );

              # Measure the amplitude delta between the two cursors on selected signal
              if ( each_sig.format == "analog" and len( analog_value_list ) == 2 ):
                if self.cursor_list[0].visible and self.cursor_list[1].visible:
                  v_delta = abs( analog_value_list[0] - analog_value_list[1] );
                  delta_txt = indent+" "+delta+" = %0.3f %s" % ( v_delta, each_sig.units );

              delta_txt = delta_txt.replace(" ","");
              delta_txt = delta_txt.replace("=","");

              if len( self.measurement_list ) >= 4:
                tall_measurements = 0;

              tall_measurements = 0;
              # rts_sig is a list of measurement text for a single signal, either from 
              # the measurements list or just a selected signal. There are two possible
              # formats, tall or wide. Tall may be specified in ini file for really 
              # long signal names and or tall monitor displays. Default is wide which
              # attempts to cram as much info in just a few lines of text.
              rts_sig = [];
              if tall_measurements == 0:
                c_txt_list[0] = c_txt_list[0].replace(" ","");
                c_txt_list[1] = c_txt_list[1].replace(" ","");

                if self.cursor_list[0].visible and self.cursor_list[1].visible:
                  rts_sig += [ sig_name + " " + delta_txt ];
                  if c_txt_list[0] != "" and c_txt_list[1] != "":
                    rts_sig += [ "  " + c_txt_list[0] +", "+ c_txt_list[1] ];
                  elif c_txt_list[0] != "" or c_txt_list[1] != "":
                    rts_sig += [ "  " + c_txt_list[0] + c_txt_list[1] ];
                  else:
                    rts_sig += [ "  " ];
                  
                elif self.cursor_list[0].visible or self.cursor_list[1].visible:
                  rts_sig += [ sig_name + " " + c_txt_list[0] + c_txt_list[1] ];
                else:
                  rts_sig += [ sig_name ];
                
                if range_txt != "":
                  rts_sig += [ " "+range_txt ];
                if min_max_txt != "":
                  rts_sig += [ " "+min_max_txt ];
                if upd_txt != "":
                  rts_sig += [ " "+upd_txt ];
                if vo_txt != "":
                  rts_sig += [ " "+vo_txt ];
              else:
                rts_sig += [ sig_name ];
                if range_txt != "":
                  rts_sig += [ " "+range_txt ];
                if min_max_txt != "":
                  rts_sig += [ " "+min_max_txt ];
                if upd_txt != "":
                  rts_sig += [ " "+ upd_txt ];
                if vo_txt != "":
                  rts_sig += [ " "+vo_txt ];
                if self.cursor_list[0].visible and self.cursor_list[1].visible:
                  rts_sig += ["  "+ delta_txt ];
                if self.cursor_list[0].visible:
                  rts_sig += [ c_txt_list[0] ];
                if self.cursor_list[1].visible:
                  rts_sig += [ c_txt_list[1] ];

            if ( ( j == 0 and ( each_sig in self.measurement_list ) ) or
                 ( j == 1 and     each_sig.selected                 )    ):
              rts += rts_sig;

    # Display any tool tips at the very bottom
    if self.vars["tool_tips_text_stats_en"].lower() in [ "true", "1", "yes" ]:
      analog_signals_selected = False;
      digital_signals_selected = False;
      for each_signal in self.signal_list:
        if each_signal.selected and each_signal.type == "analog":
          analog_signals_selected = True;
        if each_signal.selected and each_signal.type == "digital":
          digital_signals_selected = True;
      if analog_signals_selected:
        rts += ["ToolTip: ArrowKeys"];
        rts += [" Up/Down: Vert Scale"];
        rts += [" +Ctrl  : Fine Scale  "];
        rts += [" +Shift : Vert Offset"];
      if digital_signals_selected:
        if self.file_dialog == None and not self.cmd_console.visible:
          rts += ["ToolTip: Search"];
          rts += [" ? : Prev Transition"];
          rts += [" / : Next Transition"];

    max_txt_width = int( self.vars["screen_max_text_stats_width"],10 );
    rts = [ each[0:max_txt_width] for each in rts ];# list comprehension
    self.text_stats = ( rts, extra_txt_list, (x1,y1), bold_i );
#   display_raw_text( self, rts, ( x1,y1 ), bold_i );
         

  # Acquisition panel is open. Display HW cfg, status and user adjustable
  # fields for trigger and low speed sample rate.
  if self.container_acquisition_list[0].visible == True:
    (x,y,w,h) = self.container_acquisition_list[0].rect;
    x1 = x;
    y1 = y+h;
    acq_list = [];
#   acq_status = [];
    if self.vars["uut_name"] == None:
      acq_list += ["UUT not defined"];
    else:
      acq_list += [ "UUT = %s" % self.vars["uut_name"] ];

    if self.sump_connected:
      hw_cfg = "HW Config  =";
      if self.sump.cfg_dict['dig_hs_enable'] == 1:
        hw_cfg += " HS";
      if self.sump.cfg_dict['ana_ls_enable'] == 1:
        hw_cfg += " LS";
      if self.sump.cfg_dict['rle_hub_num'] > 0:
        hw_cfg += " RLE";
      acq_list += [ hw_cfg ];

      ( stat_str, status ) = self.sump.status;
      if self.status_downloading:
        stat_str = "Downloading";
      acq_list += ["HW Status  = %s" % stat_str ];
      for (i,each) in enumerate( self.acq_parm_list ):
        rts = create_text_stats( self, each, i );
        if rts != False:
          acq_list += [ rts ];
# if self.container_acquisition_list[0].visible == True:
      extra_txt_list += ["Trigger List:"];
      for each_sig in self.signal_list:
        if each_sig.trigger:
          extra_txt_list += [" "+each_sig.name];
    else:
#     acq_list += ["SUMP not connected"];
      acq_list += ["HW Status: Not Connected"];
#   ( x,y,w,h ) = display_raw_text( self, acq_list, ( x1,y1 ), bold_i );
#   self.select_text_rect = ( x,y,w,h );
    self.text_stats = ( acq_list, extra_txt_list, (x1,y1), bold_i );

# if self.tool_tip_obj_id != None and self.tool_tip_tick_time != None:
#   # Delay the hover to popup by 1 second as too fast popup is annoying.
#   if self.pygame.time.get_ticks() - self.tool_tip_tick_time > 1000:
#     rts = convert_object_id_to_tool_tip( self, self.tool_tip_obj_id );
#     if ( x1 != None and y1 != None and rts != None ):
#       self.text_stats = ( rts, (x1,y1), bold_i );
  return;

def draw_text_stats( self, stat_tuple ):
  if stat_tuple != None:
    ( txt_list, extra_txt_list, (x1,y1), bold_i ) = stat_tuple;
    ( x,y,w,h ) = display_raw_text( self, txt_list, extra_txt_list, ( x1,y1 ), bold_i );
    self.select_text_rect = ( x,y,w,h );
  return;


# convert "1015.0 ns" to "1.0 us", etc
def time_rounder( input_time, input_unit ):
  reduced_time = input_time;
  reduced_unit = input_unit;
  while abs(reduced_time) >= 1000.0:
    reduced_time = reduced_time / 1000.0;
    if reduced_unit == "ps":
      reduced_unit = "ns";
    elif reduced_unit == "ns":
      reduced_unit = "us";
    elif reduced_unit == "us":
      reduced_unit = "ms";
    elif reduced_unit == "ms":
      reduced_unit = "s";
  return ( reduced_time, reduced_unit );


# convert "1015.0 ns" to "1015000.0 ps", etc
def time_ps( input_time, input_unit ):
  reduced_time = input_time;
  reduced_unit = input_unit;
  while (reduced_unit) != "ps":   
    reduced_time = reduced_time * 1000.0;
    if reduced_unit == "ns":
      reduced_unit = "ps";
    elif reduced_unit == "us":
      reduced_unit = "ns";
    elif reduced_unit == "ms":
      reduced_unit = "us";
    elif reduced_unit == "s":
      reduced_unit = "ms";
  return ( reduced_time, reduced_unit );


############################################################################
# When an acquisition control param is selected, we needed to calculate
# a slider value that corresponds to the current variable value.
# Later when the slider has moved, we need to reverse this process to change
# the variable value to what the user adjusted it to.
def create_text_stats( self, single_stat, which_i ):
  ( disp_name, var_name, disp_units ) = single_stat;
  val = self.vars[var_name];
  rts = "%s = %s %s" % ( disp_name, val, disp_units );# Default

  # Don't display stats for components that don't exist
  if self.sump.cfg_dict['dig_hs_enable'] == 0 and "HS " in disp_name:
    return False;
  if self.sump.cfg_dict['ana_ls_enable'] == 0 and "LS " in disp_name:
    return False;


  if False:
# if which_i == self.select_text_i:
    if var_name == "sump_trigger_nth":
      pass;
#     self.acq_slider.increment = 2;
#     val_int = int( val, 10 );
#     val_float = 1000.0 * float( val_int / 500.0 );   
#     self.acq_slider.set_current_value( val_float );

#   elif var_name == "sump_trigger_type":
#     self.acq_slider.increment = 1000.0 / len( self.acq_trig_list );
#     for (i,each) in enumerate( self.acq_trig_list ):
#       if each.lower() == val.lower(): 
#         self.acq_slider.set_current_value( i * self.acq_slider.increment );

#   elif var_name == "sump_trigger_delay":
#     self.acq_slider.increment = 2;
#     val_int = float( val );# Float in uS units
#     time_ns = 1000.0 * val_int;
#     clk_ns = 1000.0 / float( self.vars["sump_hs_clock_freq"] );
#     delay_int = int( time_ns / clk_ns );
#     if ( delay_int > 0xFFFFFFFF ):
#       delay_int = 0xFFFFFFFF;
#     max = math.log( (2**32-1),10 );# 9.632959861146281
#     if delay_int == 0: delay_int = 1;
#     delay_log = math.log( delay_int,10 );# 0-9.632959861146281
#     delay_slider = (1000.0 * delay_log )/max;
#     self.acq_slider.set_current_value( delay_slider );

    elif var_name == "sump_trigger_analog_level":
      rts = "%s = %s %s" % ( disp_name, "NA"   , "NA"       );
#     rts = "%s = %s %s" % ( disp_name, val_int, disp_units );

    elif var_name == "sump_trigger_location":
#     self.acq_slider.increment = 250.0;
      val_int = float( val );# "50.0" -> 50.0
#     val_float = float( val_int );   
#     self.acq_slider.set_current_value( val_float * 10.0 );
      rts = "%s = %d %s" % ( disp_name, val_int, disp_units );

    # User dials in a LS Sample Period which then becomes a clock divisor
    # based on the ls tick clock period.
    elif var_name == "sump_ls_clock_div":
#     self.acq_slider.increment = 1.0;
      val_int = int( val,10 );# tick divisor
      val_float = float( val_int );   
      if val_float < 1.0:
        val_float = 1.0;
#     self.acq_slider.set_current_value( val_float * 1.0 );
      clk_us = 1.0 / float( self.vars["sump_ls_clock_freq"] );
      sample_period_us = clk_us * val_float;
      rts = "%s = %d %s" % ( disp_name, sample_period_us, disp_units );

  # Format the units when not default
  if ( disp_name.rstrip() == "Trig Delay" or
       disp_name.rstrip() == "HS Period"  or
       disp_name.rstrip() == "LS Period"  or
       disp_name.rstrip() == "LS Window"     ):
    val = float( val );
 
    # The variable used for LS Period is clock divisor, so calculate
    if disp_name.rstrip() == "LS Period":
      clk_us = float( 1.0 / float( self.vars["sump_ls_clock_freq"] ));
      sample_period_us = clk_us * val;
      val = sample_period_us;

      if self.sump_connected:
        ana_ram_depth    = self.sump.cfg_dict['ana_ram_depth'];
        ana_rec_profile  = self.sump.cfg_dict['ana_record_profile'];
        record_len       = ( ana_rec_profile & 0xFF000000 ) >> 24;
        ana_sample_depth = int( ana_ram_depth / record_len );
        sample_window_us = ana_sample_depth * sample_period_us;
        self.vars["sump_ls_sample_window"] = "%d" % sample_window_us;
      else:
        self.vars["sump_ls_sample_window"] = "%d" % 0;

    if ( val > 1000000 ):
      val = val / 1000000.0; disp_units = "S";
    elif ( val > 1000 ):
      val = val / 1000.0; disp_units = "mS";
    else:
      val = val / 1.0; disp_units = "uS";
    rts = "%s = %0.1f %s" % ( disp_name, val, disp_units );

  return rts;

###############################################################################
# Acquisition ( trigger ) text has been selected and either scroll wheel or
# arrow has been pressed to increase parameter
def proc_acq_adj_inc( self, rate ):
  proc_acq_adj(self, 1*rate );
  return;


###############################################################################
# Acquisition ( trigger ) text has been selected and either scroll wheel or
# arrow has been pressed to increase parameter
def proc_acq_adj_dec( self, rate ):
  proc_acq_adj(self, -1*rate );
  return; 


###############################################################################
# Acquisition ( trigger ) text has been selected and either scroll wheel or
# arrow has been pressed to increase parameter
def proc_acq_adj( self, step ):
# print("proc_acq_adj() : self.select_text_i = %s" % self.select_text_i );
  ( acq_list, extra_txt_list, (x1,y1), bold_i ) = self.text_stats;
  acq_list_len = len( acq_list );# Needed to calculate offset into parms from gen text


  if self.select_text_i != None:
    value = 0;
    new_val = value / 10.0;# This will be between 0.0 and 100.0

    i_offset = len( self.acq_parm_list ) - acq_list_len;
#   i_offset = -2;# Subtract the SUMP Status line and UUT name from up top

    try:
      ( disp_name, var_name, disp_units ) = self.acq_parm_list[ self.select_text_i + i_offset ];
    except:
      ( disp_name, var_name, disp_units ) = ( None, None , None );
      log( self, [ "ERROR-5623" ] );

    # Trigger level has coarse (+/-8) and fine (+/-1) rates. Everything else is just +/-1
    if var_name != "sump_trigger_analog_level" and \
       var_name != "sump_trigger_delay"              :
      if step > 1:
        step = 1;
      elif step < 1:
        step = -1;

    if var_name == "sump_trigger_nth":
      val_int = int( self.vars[var_name], 10 );
      val_int += step;
      if val_int < 1:
        val_int = 1;
      val_str = "%d" % val_int;
      self.vars[var_name] = val_str;

    elif var_name == "sump_trigger_type":
      val_str = self.vars[var_name];
      i = self.acq_trig_list.index(val_str);
      # Don't wrap - just keep in bounds
      i += step;
      if i < 0:                          i = 0;
      if i >= len( self.acq_trig_list ): i = len( self.acq_trig_list )-1;
      self.vars[var_name] = self.acq_trig_list[i].lower();
      
    elif var_name == "sump_trigger_analog_level":
      val_f = float( self.vars[var_name] );
      min_val = 0; max_val = 0;
      # The trigger assigned signal determines the range for analog trigger level
      for each_sig in self.signal_list:
#       print( each_sig.name, each_sig.trigger, each_sig.type );
        if each_sig.trigger and each_sig.type == "analog":
# 2025.01.20
#         max_val = each_sig.range * each_sig.units_per_code;
#         min_val = 0;
#         step_adc = step * ((each_sig.range+1)//128);# Roughly 1% +/- change 
          if each_sig.range+1 <= 256:
            step_adc = step;
          else:
            step_adc = step * ((each_sig.range+1)//1024);# Roughly 1% +/- change when step is 8
          max_val = each_sig.offset_units + ( each_sig.range * each_sig.units_per_code );
          min_val = each_sig.offset_units + 0.0;
          val_f += step_adc * each_sig.units_per_code;
          val_f = round( val_f, 3 );

          # Re-assign the units from say mV to uA
          disp_units = each_sig.units;
          self.acq_parm_list[ self.select_text_i + i_offset ] = ( disp_name, var_name, disp_units );  
#         print("name    = %s" % each_sig.name );
#         print("  max_val = %f" % max_val );
#         print("  min_val = %f" % min_val );
#         print("  val_f l = %f" % val_f   );
      if val_f < min_val : val_f = min_val;
      if val_f > max_val : val_f = max_val;
      self.vars[var_name] = "%.3f" % val_f;
      

    elif var_name == "sump_trigger_delay":
      # Trigger delay is specified in us but actual hardware delay counter is
      # in ns units. Range is 0 to hs_clock * 2^32
      clk_ns = 1000.0 / float( self.vars["sump_hs_clock_freq"] );
      min_delay = 0;
      max_delay = int((2**32-1) * clk_ns / 1000.0 );# us units
      val_f = float( self.vars[var_name] );
      if val_f < 100:
        val_f += step;
      elif val_f >= 100 and val_f < 1000:
        val_f += step * 10;
      elif val_f >= 1000 and val_f < 10000:
        val_f += step * 100;
      elif val_f >= 10000 and val_f < 100000:
        val_f += step * 1000;
      elif val_f >= 100000 and val_f < 1000000:
        val_f += step * 10000;
      else:
        val_f += step * 100000;
      if val_f < min_delay : val_f = min_delay;
      if val_f > max_delay : val_f = max_delay;
      self.vars[var_name] = "%0.0f" % val_f;

#     print("max_delay = %d" % max_delay );
#     trig_delay = int( 1000.0 * trig_delay / clk_ns );
#     max = math.log( (2**32-1),10 );# 9.632959861146281
#     mult = max / 100.0;
#     new_val = new_val * mult;
#     time_clks = 10 ** new_val;
#     clk_ns = 1000.0 / float( self.vars["sump_hs_clock_freq"] );
#     time_us = (time_clks * clk_ns ) / 1000.0;
#     self.vars[var_name] = "%0.1f" % time_us;

    elif var_name == "sump_trigger_location":
      val_int = float( self.vars[var_name] );
      val_int += 25*step;
      if   ( val_int > 90 )                  : val_int = 100;
      elif ( val_int < 10 )                  : val_int = 0;
      elif ( val_int > 40 and val_int < 60 ) : val_int = 50;
      elif ( val_int <= 40 )                 : val_int = 25;
      elif ( val_int >= 60 )                 : val_int = 75;
      self.vars[var_name] = "%d" % val_int;

    elif var_name == "sump_ls_clock_div" or var_name == "sump_ls_sample_window":
      if var_name == "sump_ls_sample_window":
        var_name = "sump_ls_clock_div";# They're connected
      val_int = int( self.vars[var_name], 10 );
      if val_int < 100:
        val_int += step;
      elif val_int >= 100 and val_int < 1000:
        val_int += step * 10;
      elif val_int >= 1000 and val_int < 10000:
        val_int += step * 100;
      elif val_int >= 10000 and val_int < 100000:
        val_int += step * 1000;
      elif val_int >= 100000 and val_int < 1000000:
        val_int += step * 10000;
      else:
        val_int += step * 100000;
      max_div = 2**24-1;
      if val_int < 1:
        val_int = 1;
      if val_int > max_div:
        val_int = max_div;
      self.vars[var_name] = "%d" % val_int;
      try:
        clk_us = float( 1.0 / float( self.vars["sump_ls_clock_freq"] ));
      except:
        clk_us = 0;# Div by zero probably
      sample_period_us = clk_us * float( val_int );

      if self.sump_connected:
        ana_ram_depth    = self.sump.cfg_dict['ana_ram_depth'];
        ana_rec_profile  = self.sump.cfg_dict['ana_record_profile'];
        record_len       = ( ana_rec_profile & 0xFF000000 ) >> 24;
        ana_sample_depth = int( ana_ram_depth / record_len );
        dig_sample_depth = self.sump.cfg_dict['dig_ram_depth'];
#       sample_window_us = ana_sample_depth * sample_period_us;
#       self.vars["sump_ls_sample_window"] = "%d" % sample_window_us;
#     else:
#       self.vars["sump_ls_sample_window"] = "%d" % 0;
  return;


###############################################################################
# Display raw PyGame text lines at specified raw (x,y) location and return
# a (x,y,w,h) tuple of the rectangle area that the text occupies
# bold_i is the selected text line, if any, that the user may modify value.
def display_raw_text( self, txt_list, extra_txt_list, position, bold_i ):
  (x,y) = position;
  x1 = x;
  y1 = y + self.txt_toolbar_height/3;
  h = self.txt_toolbar_height / 3; w = 0;
# for (i,each_line) in enumerate(txt_list):
  for (i,each_line) in enumerate(txt_list + extra_txt_list ):
    clr = self.color_fg;
    if bold_i != None:
      self.font_toolbar.set_bold( i == bold_i );
      self.font_toolbar.set_underline( i == bold_i );
      if i == bold_i:
        clr = self.color_selected;
    # Don't render off screen
    if y1 + 5 + self.txt_toolbar_height < self.screen_height:
      txt = self.font_toolbar.render( each_line,True, clr );
      self.screen.blit(txt, (x1,y1) );
    y1 += self.txt_toolbar_height;
    h += self.txt_toolbar_height;
    if txt.get_width() > w:
      w = txt.get_width();
  return ( x,y,w,h);


###############################################################################
# On button-1 press, see if it is over selectable text in Acquisition pane.
def mouse_get_text( self ):
  (self.mouse_x,self.mouse_y) = pygame.mouse.get_pos();
  ( x,y,w,h ) = self.select_text_rect;
  if ( ( self.mouse_x > x ) and ( self.mouse_x < x+w ) and
       ( self.mouse_y > y ) and ( self.mouse_y < y+h )     ):
    self.select_text_i = int( ( self.mouse_y - y - self.txt_toolbar_height/3 ) / self.txt_toolbar_height );

    # Deselect any selected signals as K_UP and K_DOWN won't be available
    # if an analog signal is selected.
    for each_sig in self.signal_list:
      each_sig.selected = False;

  # Prevent selecting Read Only text fields like HS Clock and HS Window
  # this is a bit of a hardcoded hack knowing HS Clock and HS Window are at 0,1
# if ( self.select_text_i == 0 or
#      self.select_text_i == 1 or
#      self.select_text_i == 2 or
#      self.select_text_i == 3    ):
#   self.select_text_i = None;
  # Only the acquisition panel has selectable text
  if not self.container_acquisition_list[0].visible:
    self.select_text_i = None;

  return;

###############################################################################
# On button-1 press, see if it is over a signal name and select it.
# Check first to see if it is a collapsable (group) parent and toggle that
# instead if clicked by the [+]/[-] area.
def mouse_event_single_click( self ):
  (self.mouse_x,self.mouse_y) = pygame.mouse.get_pos();
  margin = 5;
  rts = False;# Assume nothing select and no redraw
  self.mouse_btn1_select = False;# True if last Btn1 Down selected a signal
  for each_signal in self.signal_list:
#   if each_signal.visible == True and each_signal.type != "spacer":
    if each_signal.visible == True:
      if each_signal.parent != None and each_signal.name_rect != None:
        (x1,y1,w1,h1) = each_signal.parent.panel.rect;# Waveform panel
        (x2,y2,w2,h2) = each_signal.name_rect;# signal name text rectangle

        if ( ( self.mouse_x > ( x1+x2    ) ) and
             ( self.mouse_x < ( x1+x2+w2 ) ) and
             ( self.mouse_y > ( y1+y2    ) ) and
             ( self.mouse_y < ( y1+y2+h2 ) )     ):
          rts = True;#Force a redraw
#         # If left 1/4 of text is clicked on a collapsable, toggle it
#         # otherwsie select it if right 3/4 of text is clicked.
#         if each_signal.collapsable and ( self.mouse_x < ( x1+x2+w2/4 ) ):

#         # If left 1/2 of text is clicked on a collapsable, toggle it
#         # otherwise select it if right 1/2 of text is clicked.
#         if each_signal.collapsable and ( self.mouse_x < ( x1+x2+w2/2 ) ):

          # If left 1/3 of text is clicked on a collapsable, toggle it
          # otherwise select it if right 2/3 of text is clicked.
          if each_signal.collapsable and ( self.mouse_x < ( x1+x2+w2/3 ) ):
            each_signal.collapsed = not each_signal.collapsed;
            # Now find any children and change their visibility
            if each_signal.collapsed:
              proc_collapse_group(self, each_signal );
            else:
#             # Expand one level down only
              proc_expand_group(self, each_signal );
            self.mouse_btn1_up_time = 0;# Used for double-click detection
            self.mouse_btn1_up_time_last = 0;
          else:
            self.mouse_btn1_select = True;
            # DeSelect All signals unless a CTRL key is held down
            if ( self.pygame.key.get_pressed()[self.pygame.K_LCTRL] == False and
                 self.pygame.key.get_pressed()[self.pygame.K_RCTRL] == False     ):
              for each_sig in self.signal_list:
                if each_sig != each_signal:
                  each_sig.selected = False;
            # Now select the selected signal
            each_signal.selected = not each_signal.selected;# Toggle
  return rts;


def mouse_event_single_click_waveform( self ):
  (self.mouse_x,self.mouse_y) = pygame.mouse.get_pos();
  margin = 5;
  rts = False;# Assume nothing select and no redraw
  for each_signal in self.signal_list:
    if each_signal.visible == True:
      if each_signal.parent != None and each_signal.name_rect != None:
        (x1,y1,w1,h1) = each_signal.parent.panel.rect;# Waveform panel
        (x2,y2,w2,h2) = each_signal.name_rect;# signal name text rectangle
        # Is click right of the signal name?
        if ( ( self.mouse_x > ( x1+x2+w2 ) ) and
             ( self.mouse_y > ( y1+y2    ) ) and
             ( self.mouse_y < ( y1+y2+h2 ) )     ):
          # Find the nearest cursor to the mouse
          min_delta_x = 1000000000;
          min_cur = None;
          for each_cursor in self.cursor_list:
            if each_cursor.visible == True and each_cursor.parent != None:
              delta_x = abs( self.mouse_x - each_cursor.x );
              if delta_x < min_delta_x:
                min_delta_x = delta_x;
                min_cur     = each_cursor; 
          if min_cur != None:
            min_cur.x = self.mouse_x - (3*margin);
            update_cursors_to_mouse(self);
            break;

#         print( each_signal.name );
#         for each_cursor in self.cursor_list:
#           if ( each_cursor.visible == True ):
#             each_cursor.x = self.mouse_x - (3*margin);
#             update_cursors_to_mouse(self);
#             break;

#         if self.container_display_list[0].visible and self.window_selected != None :
#           win_num      = self.window_selected;
#           my_win       = self.window_list[win_num];
#           timezone     = my_win.timezone;
#           samples_start_offset = my_win.samples_start_offset;
#           samples_shown        = my_win.samples_shown;
#           samples_total        = my_win.samples_total;
#           if my_win.samples_shown != None:
#             if each_signal.source != None and "digital_rle" in each_signal.source:
#               center_time = samples_start_offset + ( samples_shown // 2 );
#               center_i = None;
#               for (i,rle_time) in enumerate( each_sig.rle_time ):
#                 if ( rle_time + my_win.trigger_index ) > center_time:
#                   break;
  return rts;

def proc_expand_group( self, my_sig ):
# print("proc_expand_group() %s" % my_sig.name );
  # Expand one level down only and stop. Only collapse uses recursion
  my_sig.collapsed = False;
  for each_sig in self.signal_list:
    if each_sig.member_of == my_sig:
#   if each_sig.member_of == my_sig.name:
#   if each_sig.member_of == my_sig.name and each_sig.timezone == my_sig.timezone:
      if my_sig.collapsed:
        each_sig.visible = False;
      else:
# 2025.01.27
#       if each_sig.rle_masked == False:
        each_sig.visible = True;
  return;

def proc_collapse_group( self, my_sig ):
  my_sig.collapsed = True;
# print("proc_collapse_group() %s" % my_sig.name );
  recursive_signal_collapse( self, parent = my_sig );
  return;

def recursive_signal_collapse( self, parent ):
# print("recursive_signal_collapse() %s" % parent.name );
  for each_sig in self.signal_list:
    if each_sig.member_of == parent:
      each_sig.visible = False;
      each_sig.selected = False;
      if each_sig.collapsable and not each_sig.collapsed:
#       print("recursive_signal_collapse() Found Collapsable child %s" % each_sig.name );
        each_sig.collapsed = True;
        recursive_signal_collapse( self, parent = each_sig );
  return;




# Note : this works but decided against using it. <END> key only 
###############################################################################
# On button-1 double-click see if it is over a signal name and toggle the
# hidden attribute of the signal and leave the signal not selected.
#def mouse_event_double_click( self ):
#  (self.mouse_x,self.mouse_y) = pygame.mouse.get_pos();
#  margin = 5;
#  rts = False;# Assume nothing select and no redraw
#  self.mouse_btn1_select = False;# True if last Btn1 Down selected a signal
#  for each_signal in self.signal_list:
#    if each_signal.visible == True:
#      if each_signal.parent != None and each_signal.name_rect != None:
#        (x1,y1,w1,h1) = each_signal.parent.panel.rect;# Waveform panel
#        (x2,y2,w2,h2) = each_signal.name_rect;# signal name text rectangle
#
#        if ( ( self.mouse_x > ( x1+x2    ) ) and
#             ( self.mouse_x < ( x1+x2+w2 ) ) and
#             ( self.mouse_y > ( y1+y2    ) ) and
#             ( self.mouse_y < ( y1+y2+h2 ) )     ):
#          rts = True;#Force a redraw
#          each_signal.hidden = not each_signal.hidden;   
#          each_signal.selected == False;
#          for each_sig in self.signal_list:
#            each_sig.selected = False;# Unselect ALL signals
#  return rts;


###############################################################################
# On button-1 press, see if it is over a cursor and set cursor.selected = True
# Note that if the cursors are too close, it will select the closest.
def mouse_get_cursor( self ):
  (self.mouse_x,self.mouse_y) = pygame.mouse.get_pos();
  (wave_i, zone_i ) = mouse_get_zone( self );
  rts = False;# Did not grab a cursor

  # Only allow cursor drag on a selected window
  if wave_i == self.window_selected:
    margin = 5;
    mouse_x = self.mouse_x - ( 2 * margin );
    distance_window = 15;# +/- pels from cursor

    # Of the two cursors, find the closest one to the mouse and if that one
    # is visible and within the distance_window, select it.
    my_cur_delta_x = None;
    my_cur         = None;
    for each_cursor in self.cursor_list:
      if each_cursor.visible == True and each_cursor.parent != None:
        each_cursor.selected = False;
        cur_x = each_cursor.x;
        delta_x = abs( mouse_x - cur_x );
        if my_cur == None:
          my_cur = each_cursor;
          my_cur_delta_x = delta_x;
        elif delta_x < my_cur_delta_x:
          my_cur = each_cursor;
          my_cur_delta_x = delta_x;
    if my_cur != None and my_cur_delta_x < distance_window:
      my_cur.selected = True;
      rts = True;
  return rts;

###############################################################################
# On button-1 drag, move a cursors that are in a selected state
# Note that if the cursors are too close, it will select the closest.
def mouse_move_cursor( self ):
  (self.mouse_x,self.mouse_y) = pygame.mouse.get_pos();
  margin = 5;
  mouse_x = self.mouse_x - ( 3 * margin );
  rts = False;
  vasili = True;
  for each_cursor in self.cursor_list:
    if ( each_cursor.visible == True and each_cursor.selected == True ):
      if vasili:
        each_cursor.x = mouse_x;
        update_cursors_to_mouse(self);
        rts = True;
        vasili = False;
      else:
        each_cursor.selected = False;
#       print("WARNING: Two cursors were selected. Dropping 2nd");
  return rts;


###############################################################################
# On button-1 release, ungrab any selected cursors
def mouse_release_cursor( self ):
  for each_cursor in self.cursor_list:
    if ( each_cursor.visible == True and each_cursor.selected == True ):
      each_cursor.selected = False;
# 2025.03.07 : Note, this resulted in cursor changing on button release
#     update_cursors_to_mouse(self);
#     print("Released!");
  return;

# wave_win = None;# 0,1 or 2 for Analog,Digital-LS,Digital-HS
# win_reg = None;# 4 different regions, see above ASCII art
# for (i, each) in enumerate( self.waveform_list ):
#   if each.visible == True:
# return;


###############################################################################
# When the mouse scroll wheel is used, determine the wave window and also the
# region. Also use for selecting one wave window and deselecting others
# OLD:
#   ---------------------
#  |  1  |2 Zoom  |   4  |
#  | Amp |--------|Scroll|
#  |     |3  Pan  |      |
#   ---------------------
# NEW
#   ---------------------
#  |      2 Zoom         |
#  |---------------------|
#  |      3  Pan         |
#   ---------------------
def mouse_get_zone( self ):
  (self.mouse_x,self.mouse_y) = pygame.mouse.get_pos();
  wave_win = None;# 0,1 or 2 for Analog,Digital-LS,Digital-HS
  win_reg = None;# 4 different regions, see above ASCII art
  for (i, each_window) in enumerate( self.window_list ):
    each = each_window.panel;
    if each.visible == True:
      (x,y,w,h ) = each.relative_rect;# Dimensions
      if ( ( self.mouse_x > x )   and
           ( self.mouse_x < x+w ) and
           ( self.mouse_y > y   ) and
           ( self.mouse_y < y+h )     ):
        wave_win = i;
#       if (     self.mouse_x < (x + w/4    ) ):
        if (     self.mouse_x < (x + w/8    ) ):
          win_reg = 1;
#       elif (   self.mouse_x > (x + w - w/4) ):
        elif (   self.mouse_x > (x + w - w/8) ):
          win_reg = 4;
        elif (   self.mouse_y < (y + h/2    ) ):
          win_reg = 2;
        else:
          win_reg = 3;
#       if (   self.mouse_y < (y + h/2    ) ):
#         win_reg = 2;
#       else:
#         win_reg = 3;
  return ( wave_win, win_reg );


###############################################################################
# Convert Button object_id to tool tip string
def convert_object_id_to_tool_tip( self, id_str ):
# print( id_str );
  cmd_str = None;
  if id_str == "#Controls.#Main.#Exit"                 : cmd_str = "exit";
  elif id_str == "#Controls.#Main.#Acquisition"        : cmd_str = "acquisition";
  elif id_str == "#Controls.#Main.#Display"            : cmd_str = "display";
  elif id_str == "#Controls.#Main.#Views"              : cmd_str = "views";   
  elif id_str == "#Controls.#Main.#Help"               : cmd_str = "help";
  elif id_str == "#Controls.#Acquisition.#Arm"         : cmd_str = "sump_arm";
  elif id_str == "#Controls.#Acquisition.#Acquire"     : cmd_str = "sump_acquire";
  elif id_str == "#Controls.#Acquisition.#Connect"     : cmd_str = "sump_connect";
  elif id_str == "#Controls.#Acquisition.#Download"    : cmd_str = "sump_download";
  elif id_str == "#Controls.#Acquisition.#Query"       : cmd_str = "sump_query";
  elif id_str == "#Controls.#Acquisition.#Force_Trig"  : cmd_str = "sump_force_trig";
  elif id_str == "#Controls.#Acquisition.#Set_Trigs"   : cmd_str = "sump_set_trigs";
# elif id_str == "#Controls.#Acquisition.#Clr_Trigs"   : cmd_str = "sump_clr_trigs";
  elif id_str == "#Controls.#Acquisition.#Clear_Trigs" : cmd_str = "sump_clear_trigs";
  elif id_str == "#Controls.#Acquisition.#Force_Stop"  : cmd_str = "sump_force_stop";
  elif id_str == "#Controls.#Acquisition.#Save_PZA"    : cmd_str = "save_pza";
  elif id_str == "#Controls.#Acquisition.#Load_PZA"    : cmd_str = "load_pza";
  elif id_str == "#Controls.#Acquisition.#Save_VCD"    : cmd_str = "save_vcd";
  elif id_str == "#Controls.#Acquisition.#Load_VCD"    : cmd_str = "load_vcd";
# elif id_str == "#Controls.#Acquisition.#Save_PNG"    : cmd_str = "save_png";
# elif id_str == "#Controls.#Acquisition.#Save_JPG"    : cmd_str = "save_jpg";
  elif id_str == "#Controls.#Acquisition.#Save_List"   : cmd_str = "save_list";
  elif id_str == "#Controls.#Acquisition.#Save_View"   : cmd_str = "save_view";

# elif id_str == "#Controls.#Display.#Save_PNG"        : cmd_str = "save_png";
# elif id_str == "#Controls.#Display.#Save_JPG"        : cmd_str = "save_jpg";
# elif id_str == "#Controls.#Display.#Save_List"       : cmd_str = "save_list";
# elif id_str == "#Controls.#Display.#Save_View"       : cmd_str = "save_view";

  elif id_str == "#Controls.#Acquisition.#UUT"         : cmd_str = "load_uut";
  elif id_str == "#Controls.#Acquisition.#Target"      : cmd_str = "load_uut";
  elif id_str == "#Controls.#Views.#ApplyAll"          : cmd_str = "apply_view_all";
  elif id_str == "#Controls.#Views.#RemoveAll"         : cmd_str = "remove_view_all";
  elif id_str == "#Controls.#Display.#Window-1"        : cmd_str = "window1";
  elif id_str == "#Controls.#Display.#Window-2"        : cmd_str = "window2";
  elif id_str == "#Controls.#Display.#Window-3"        : cmd_str = "window3";
  elif id_str == "#Controls.#Display.#bd_shell"        : cmd_str = "bd_shell";
  elif id_str == "#Controls.#Display.#Cursor-1"        : cmd_str = "cursor1";
  elif id_str == "#Controls.#Display.#Cursor-2"        : cmd_str = "cursor2";
  elif id_str == "#Controls.#Display.#ZoomIn"          : cmd_str = "zoom_in";
  elif id_str == "#Controls.#Display.#ZoomOut"         : cmd_str = "zoom_out";
  elif id_str == "#Controls.#Display.#ZoomCurs"        : cmd_str = "zoom_to_cursors";
  elif id_str == "#Controls.#Display.#ZoomFull"        : cmd_str = "zoom_full";
  elif id_str == "#Controls.#Display.#<-Search"        : cmd_str = "search_backward";
  elif id_str == "#Controls.#Display.#Search->"        : cmd_str = "search_forward";
  elif id_str == "#Controls.#Display.#<-Pan"           : cmd_str = "pan_left";
  elif id_str == "#Controls.#Display.#Pan->"           : cmd_str = "pan_right";
# elif id_str == "#Controls.#Display.#Save_PNG"        : cmd_str = "save_png";
# elif id_str == "#Controls.#Display.#Save_JPG"        : cmd_str = "save_jpg";
# elif id_str == "#Controls.#Display.#Save_List"       : cmd_str = "save_list";
# elif id_str == "#Controls.#Display.#Save_View"       : cmd_str = "save_view";
# elif id_str == "#Controls.#Display.#Save_VCD"        : cmd_str = "save_vcd";
  elif id_str == "#Controls.#Display.#TimeSnap"        : cmd_str = "time_snap";
  elif id_str == "#Controls.#Display.#TimeLock"        : cmd_str = "time_lock";

  elif id_str == "#Controls.#Display.#MaskSig"         : cmd_str = "mask_toggle_signal";
  elif id_str == "#Controls.#Display.#HideSig"         : cmd_str = "hide_toggle_signal";
  elif id_str == "#Controls.#Display.#CopySig"         : cmd_str = "copy_signal";
  elif id_str == "#Controls.#Display.#PasteSig"        : cmd_str = "paste_signal";
  elif id_str == "#Controls.#Display.#DeleteSig"       : cmd_str = "delete_signal";
  elif id_str == "#Controls.#Display.#CutSig"          : cmd_str = "cut_signal";
  elif id_str == "#Controls.#Display.#Font++"          : cmd_str = "font_larger";
  elif id_str == "#Controls.#Display.#Font--"          : cmd_str = "font_smaller";

# elif id_str == "#Controls.#Display.#InsertSig"       : cmd_str = "insert_signal";
# elif id_str == "#Controls.#Display.#CloneSig"        : cmd_str = "clone_signal";

  rts = []; text = None;
  if cmd_str == "help":
    text = "View a Sump3 manual using an external text editor";
  elif cmd_str == "acquisition":
    text = "Enable the Acquisition controls for connecting to Sump3 hardware, "+ \
           "specifying triggers, arming and downloading acquisitions.";
  elif cmd_str == "views":
    text = "Enable the Views controls for adding and removing signal views from "+ \
           "waveform windows.";
  elif cmd_str == "display":
    text = "Enable the Display controls for viewing acquired signal samples.";

  elif cmd_str in [ "window1", "window2", "window3" ]:
    text = "Toggle the waveform Window for being displayed. <PageUp> and <PageDown> " +\
           "may be used to rapidly rotate through all three waveform windows.";

  elif cmd_str == "bd_shell":
    text = "Toggle the bd_shell CLI for being displayed.";
  elif cmd_str == "cursor1":
    text = "Toggle Cursor-1 for being displayed.";
  elif cmd_str == "cursor2":
    text = "Toggle Cursor-2 for being displayed.";

  elif cmd_str == "sump_arm":
    text = "Connect to Sump3 hardware and arm for triggering.";
  elif cmd_str == "sump_connect":
    text = "Connect to Sump3 hardware and retrieve configuration.";
  elif cmd_str == "sump_query":
    text = "Connect to Sump3 hardware and retrieve trigger status.";
  elif cmd_str == "sump_acquire":
    text = "Arm Sump3 hardware, query until triggered and download samples.";
  elif cmd_str == "sump_download":
    text = "Connect to Sump3 hardware and download acquired samples.";
  elif cmd_str == "sump_force_trig":
    text = "Connect to Sump3 hardware and issue an asynch software trigger.";
  elif cmd_str == "sump_set_trigs":
    text = "Set selected signal(s) as triggers.";
  elif cmd_str == "sump_clr_trigs":
    text = "Clear any previously set triggers.";
  elif cmd_str == "sump_force_stop":
    text = "Connect to Sump3 hardware and cancel armed state without acquisition.";
  elif cmd_str == "save_pza":
    text = "Create and save a single *.PZA file which contains current hardware " + \
           "configuration and downloaded samples.";
  elif cmd_str == "load_pza":
    text = "Load a saved *.PZA file of a previous acquisition.";
  elif cmd_str == "load_uut":
    text = "Load an *.INI file which specifies the 32bit address of the Sump3 hardware "+\
           "for the Unit Under Test.";
  elif cmd_str == "zoom_in":
    text = "Zoom In on current selected waveform window in time. Also <UpArrow> key.";
  elif cmd_str == "zoom_out":
    text = "Zoom Out on current selected waveform window in time. Also <DownArrow> key.";
  elif cmd_str == "zoom_to_cursors":
    text = "Zoom to time region specified by C1 and C2 cursors.";
  elif cmd_str == "zoom_full":
    text = "Zoom out completely in selected waveform window.";
  elif cmd_str == "search_backward":
    text = "Search backward in time for previous transition of selected signal.";
  elif cmd_str == "search_forward":
    text = "Search forward in time for next transition of selected signal.";
  elif cmd_str == "pan_left":
    text = "Pan left in time to earlier samples. Also <LeftArrow> key.";
  elif cmd_str == "pan_right":
    text = "Pan right in time to later samples. Also <RightArrow> key.";
  elif cmd_str == "save_png":
    text = "Save a *.PNG image file of either selected waveform window or entire GUI.";
  elif cmd_str == "save_vcd":
    text = "Save a *.VCD Verilog Value-Change-Dump of selected waveform window.";
  elif cmd_str == "save_list":
    text = "Save a text *.LST 'List' of selected waveform window time samples.";
  elif cmd_str == "save_view":
    text = "Save a single view file of selected waveform window.";
  elif cmd_str == "time_snap":
    text = "Snap all windows to same time (pan) and zoom settings. All Pan and Zoom " +\
           "commands will continue to only apply to the selected window.";
  elif cmd_str == "time_lock":
    text = "Lock all windows to have a single time and zoom setting. With TimeLock on " +\
           "all Pan and Zoom commands will be applied to all windows.";
  elif cmd_str == "mask_toggle_signal":
    text = "Toggle <END> the RLE Mask attribute of selected signal. An RLE signal that is " +\
           "masked will not be captured, increasing the RLE compression for other signals.";
  elif cmd_str == "hide_toggle_signal":
    text = "Toggle the hide attribute of selected signal. A signal that is hidden will " +\
           "have only its name displayed and no waveform.";
  elif cmd_str == "delete_signal":
    text = "Delete <DEL> the selected signal from the waveform display. Pressing <HOME> will " +\
           "restore ALL previously deleted signals. Pressing <INS> will insert last deleted.";
  elif cmd_str == "copy_signal":
    text = "Copy the selected signal from the waveform window into clipboard buffer.";
  elif cmd_str == "paste_signal":
    text = "Paste the signal from the clipboard buffer into the selected waveform window.";
  elif cmd_str == "cut_signal":
    text = "Cut the signal into the clipboard buffer.";
# elif cmd_str == "insert_signal":
#   text = "Insert <INS> the last deleted signal to the waveform display.";
  elif cmd_str == "font_larger":
    text = "Increase the font size of signal names.";
  elif cmd_str == "font_smaller":
    text = "Decrease the font size of signal names.";

  # This RegEx function parses a single sentence into a list of words that 
  # don't exceed a specified character width. There's a conversion from pels to chars
  # based on current selected font size.
  if text != None and cmd_str != None:
    # print( dir( self.container_list[1] ) );
    #print( self.container_list[1].get_relative_rect() );
    (x,y,right_w,h) = self.container_list[1].get_relative_rect();# 275 expected
    max_chars_per_line = int( ( right_w / self.txt_width ) - 2 ) ;
    rts += [ "Command: %s" % cmd_str ]; 
    regex_str = r'.{1,%d}(?:\s+|$)' % max_chars_per_line;
    rts += re.findall( regex_str, text );
  return rts;

###############################################################################
# Convert Button object_id to internal command line commands
def convert_object_id_to_cmd( self, id_str ):
  cmd_str = None;
  if id_str == "#Controls.#Main.#Exit"                 : cmd_str = "exit";
  elif id_str == "#Controls.#Main.#Help"               : cmd_str = "help";
  elif id_str == "#Controls.#Acquisition.#Arm"         : cmd_str = "sump_arm";
  elif id_str == "#Controls.#Acquisition.#Acquire"     : cmd_str = "sump_acquire";
  elif id_str == "#Controls.#Acquisition.#Connect"     : cmd_str = "sump_connect";
  elif id_str == "#Controls.#Acquisition.#Download"    : cmd_str = "sump_download";
  elif id_str == "#Controls.#Acquisition.#Query"       : cmd_str = "sump_query";
  elif id_str == "#Controls.#Acquisition.#Force_Trig"  : cmd_str = "sump_force_trig";
  elif id_str == "#Controls.#Acquisition.#Set_Trigs"   : cmd_str = "sump_set_trigs";
# elif id_str == "#Controls.#Acquisition.#Clr_Trigs"   : cmd_str = "sump_clr_trigs";
  elif id_str == "#Controls.#Acquisition.#Clear_Trigs" : cmd_str = "sump_clear_trigs";
  elif id_str == "#Controls.#Acquisition.#Force_Stop"  : cmd_str = "sump_force_stop";
  elif id_str == "#Controls.#Acquisition.#Save_PZA"    : cmd_str = "save_pza";
  elif id_str == "#Controls.#Acquisition.#Save_VCD"    : cmd_str = "save_vcd";
# elif id_str == "#Controls.#Acquisition.#Load_VCD"    : cmd_str = "load_vcd";
# elif id_str == "#Controls.#Acquisition.#Save_PNG"    : cmd_str = "save_png";
# elif id_str == "#Controls.#Acquisition.#Save_JPG"    : cmd_str = "save_jpg";
  elif id_str == "#Controls.#Acquisition.#Save_List"   : cmd_str = "save_list";
  elif id_str == "#Controls.#Acquisition.#Save_View"   : cmd_str = "save_view";
  elif id_str == "#Controls.#Acquisition.#Save_Window" : cmd_str = "save_window";
  elif id_str == "#Controls.#Acquisition.#Save_Screen" : cmd_str = "save_screen";
  elif id_str == "#Controls.#Views.#ApplyAll"          : cmd_str = "apply_view_all";
  elif id_str == "#Controls.#Views.#RemoveAll"         : cmd_str = "remove_view_all";

  elif id_str == "#Controls.#Display.#ZoomIn"          : cmd_str = "zoom_in";
  elif id_str == "#Controls.#Display.#ZoomOut"         : cmd_str = "zoom_out";
  elif id_str == "#Controls.#Display.#ZoomCurs"        : cmd_str = "zoom_to_cursors";
  elif id_str == "#Controls.#Display.#ZoomFull"        : cmd_str = "zoom_full";
  elif id_str == "#Controls.#Display.#<-Search"        : cmd_str = "search_backward";
  elif id_str == "#Controls.#Display.#Search->"        : cmd_str = "search_forward";
  elif id_str == "#Controls.#Display.#<-Pan"           : cmd_str = "pan_left";
  elif id_str == "#Controls.#Display.#Pan->"           : cmd_str = "pan_right";
# elif id_str == "#Controls.#Display.#Save_PNG"        : cmd_str = "save_png";
# elif id_str == "#Controls.#Display.#Save_JPG"        : cmd_str = "save_jpg";
# elif id_str == "#Controls.#Display.#Save_List"       : cmd_str = "save_list";
# elif id_str == "#Controls.#Display.#Save_View"       : cmd_str = "save_view";
# elif id_str == "#Controls.#Display.#Save_VCD"        : cmd_str = "save_vcd";
  elif id_str == "#Controls.#Display.#TimeSnap"        : cmd_str = "time_snap";
  elif id_str == "#Controls.#Display.#TimeLock"        : cmd_str = "time_lock";
  elif id_str == "#Controls.#Display.#Save_Window"     : cmd_str = "save_window";
  elif id_str == "#Controls.#Display.#Save_Screen"     : cmd_str = "save_screen";
  elif id_str == "#Controls.#Display.#Add_Measure"     : cmd_str = "add_measurement";
  elif id_str == "#Controls.#Display.#Remove_Meas"     : cmd_str = "remove_measurement";

  elif id_str == "#Controls.#Views.#MaskSig"           : cmd_str = "mask_toggle_signal";
  elif id_str == "#Controls.#Views.#HideSig"           : cmd_str = "hide_toggle_signal";
  elif id_str == "#Controls.#Views.#CopySig"           : cmd_str = "copy_signal";
  elif id_str == "#Controls.#Views.#PasteSig"          : cmd_str = "paste_signal";
  elif id_str == "#Controls.#Views.#DeleteSig"         : cmd_str = "delete_signal";
  elif id_str == "#Controls.#Views.#CutSig"            : cmd_str = "cut_signal";
  elif id_str == "#Controls.#Views.#Font++"            : cmd_str = "font_larger";
  elif id_str == "#Controls.#Views.#Font--"            : cmd_str = "font_smaller";

# elif id_str == "#Controls.#Display.#MaskSig"         : cmd_str = "mask_toggle_signal";
# elif id_str == "#Controls.#Display.#HideSig"         : cmd_str = "hide_toggle_signal";
# elif id_str == "#Controls.#Display.#CopySig"         : cmd_str = "copy_signal";
# elif id_str == "#Controls.#Display.#PasteSig"        : cmd_str = "paste_signal";
# elif id_str == "#Controls.#Display.#DeleteSig"       : cmd_str = "delete_signal";
# elif id_str == "#Controls.#Display.#CutSig"          : cmd_str = "cut_signal";
# elif id_str == "#Controls.#Display.#Font++"          : cmd_str = "font_larger";
# elif id_str == "#Controls.#Display.#Font--"          : cmd_str = "font_smaller";


# elif id_str == "#Controls.#Display.#InsertSig"       : cmd_str = "insert_signal";
# elif id_str == "#Controls.#Display.#CloneSig"        : cmd_str = "clone_signal";

  # Unselect active window when the bd_shell title bar is clicked so that
  # the arrow keys don't pan and zoom while you are typing
  elif id_str == "#console_window.#title_bar":  
    select_window( self, None );
    cmd_str = "";
  elif id_str == "#Controls.#Acquisition.#UUT" or id_str == "#Controls.#Acquisition.#Target" : 
    name = "load_uut";
    ext = "ini";
    path = os.path.abspath( self.vars["sump_path_uut"] );# Solve Relative
    cmd_file_dialog( self, name, path, ext );

# elif id_str == "#Controls.#Acquisition.#Save_PZA": 
#   name = "save_pza";
#   ext = "pza";
#   path = os.path.abspath( self.vars["sump_path_pza"] );
#   print(path);
#   cmd_file_dialog( self, name, path, ext );

  elif id_str == "#Controls.#Acquisition.#Load_PZA": 
    name = "load_pza";
    ext = "pza";
    path = os.path.abspath( self.vars["sump_path_pza"] );
    cmd_file_dialog( self, name, path, ext );

  elif id_str == "#Controls.#Acquisition.#Load_VCD": 
    name = "load_vcd";
    ext = "vcd";
    path = os.path.abspath( self.vars["sump_path_vcd"] );
    cmd_file_dialog( self, name, path, ext );

  elif cmd_str == None:
    if self.debug_mode:
      cmd_str = id_str;
    else:
      cmd_str = None;
  return cmd_str;

###############################################################################
# shutdown process
def shutdown(self):
  log( self, ["shutdown()"] );
  if self.sump_connected:
    cmd_thread_pool_surrender_id(self);
    cmd_sump_sleep(self);
    if self.vars["bd_server_quit_on_close"].lower() in ["true","yes","1"]:
      log( self, ["bd_server( quit )"] );
      self.bd.quit();
    self.bd.close();

# This doesn't work as SDL variable doesn't update after window has moved.
# See https://python-forum.io/thread-30200.html
# txt = os.environ['SDL_VIDEO_WINDOW_POS'];
# (txt_x,txt_y) = txt.split(',');
# self.vars["screen_x"] = txt_x;
# self.vars["screen_y"] = txt_y;
  ms_windows_title_bar_height = 30;# this seems right on Windows-10
  ms_windows_x_fudge          = 8; # I just guessed on this value

# This works on Windows only. UNIX clients won't be able to save screen x,y
  import platform;
  if "Windows" in platform.platform():
    # See https://stackoverflow.com/questions/4135928/pygame-display-position
    from ctypes import POINTER, WINFUNCTYPE, windll
    from ctypes.wintypes import BOOL, HWND, RECT
    # get our window ID:
    hwnd = pygame.display.get_wm_info()["window"]
    # Jump through all the ctypes hoops:
    prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
    paramflags = (1, "hwnd"), (2, "lprect")
    GetWindowRect = prototype(("GetWindowRect", windll.user32), paramflags)
    # finally get our data!
    rect = GetWindowRect(hwnd)
    #print("top, left, bottom, right: ", rect.top, rect.left, rect.bottom, rect.right);
    self.vars["screen_x"] = str( rect.left + ms_windows_x_fudge );
    self.vars["screen_y"] = str( rect.top  + ms_windows_title_bar_height );

  var_dump( self, "sump3.ini" ); # Dump all variable to INI file

  # Close the log file
  self.file_log.close();
  # Now rename it from "sump3_log.txt.pid1234" to "sump3_log.txt"
  if os.path.exists( self.vars["file_log"] ):
    os.remove( self.vars["file_log"] );
  filename = self.vars["file_log"]+".pid"+str( os.getpid() );
  if os.path.exists( filename ):
    os.rename( filename, self.vars["file_log"] );

  print("Bye");
  return;

###############################################################################
# Create the surface 
def init_surfaces(self):
  log( self, ["init_surfaces()"] );
  rect = self.window_list[0].panel.relative_rect;# Dimensions
  (x,y,w,h) = rect;
  self.window_list[0].surface = pygame.Surface( (w-2,h-2) );# You draw on a Surface
  self.window_list[0].image.set_dimensions( (w-2,h-2) );# UIImage displays a Surface

  rect = self.window_list[1].panel.relative_rect;# Dimensions
  (x,y,w,h) = rect;
  self.window_list[1].surface = pygame.Surface( (w-2,h-2) );# You draw on a Surface
  self.window_list[1].image.set_dimensions( (w-2,h-2) );# UIImage displays a Surface

  rect = self.window_list[2].panel.relative_rect;# Dimensions
  (x,y,w,h) = rect;
  self.window_list[2].surface = pygame.Surface( (w-2,h-2) );# You draw on a Surface
  self.window_list[2].image.set_dimensions( (w-2,h-2) );# UIImage displays a Surface

  # Warning : Every UIImage call is a 5MB memory leak for some reason.
  # Workaround is to not call this every refresh, instead use the set_image()
  # method every refresh. Only drawback is having to erase what was drawn 
  # last time. This will still leak 5MB every screen resize event.
  # self.test_image = UIImage( relative_rect=(1,1,w-2,h-2),
  #                            image_surface=self.my_surface,
  #                            manager=self.ui_manager,
  #                            container=self.waveform_list[1] );# Digital Container
  return;

###############################################################################
# Draw the graphics on the surfaces
def draw_surfaces(self):
  draw_digital_lines( self, self.window_list[0] );
  draw_digital_lines( self, self.window_list[1] );
  draw_digital_lines( self, self.window_list[2] );
  return;


###############################################################################
# Create the cursor lines for on top of the selected waveform window
def create_cursor_lines(self):
# self.cursor_line_list = [];

  cursors_visible = False;# Bail out fast if cursors are not visible
  for each_cursor in self.cursor_list:
    if each_cursor.visible == True:
      cursors_visible = True;

  wave_i = None;# wave_i is 0,1,2 or None index of the parent of cursors
  if cursors_visible == True:
    if self.window_selected != None:
      wave_i = self.window_selected;
      for each_cursor in self.cursor_list:
        each_cursor.parent = self.window_list[wave_i].panel;

  # Generate the x locations for the cursors based on their time position
  # relative to the trigger.
  # each_cur.trig_delta_t and *.trig_delta_units tell us where C1 and C2 are in 
  # time relative to the trigger.
  # The window attributes tell us where that is in x pixel space.
  for (i,each_cur) in enumerate(self.cursor_list):
    if each_cur.trig_delta_t != None:
      t1 = each_cur.trig_delta_t;
      if   each_cur.trig_delta_unit == "ms": t1 *= 1000000.0;
      elif each_cur.trig_delta_unit == "us": t1 *= 1000.0;
      elif each_cur.trig_delta_unit == "ns": t1 *= 1.0;
      elif each_cur.trig_delta_unit == "ps": t1 *= 0.001;
      else                                 : t1  = 0.0;# Invalid time unit
      for (j,each_win) in enumerate(self.window_list):
        if each_win.trigger_index != None and each_win.sample_period != None:
          t2 = each_win.sample_period;
          if   each_win.sample_unit == "ms": t2 *= 1000000.0;
          elif each_win.sample_unit == "us": t2 *= 1000.0;
          elif each_win.sample_unit == "ns": t2 *= 1.0;
          elif each_win.sample_unit == "ps": t2 *= 0.001;
          else                             : t2 *= 1.0;# Don't allow Div-0

          # How many samples is this cursor from the trigger?
          cur_sample_delta = t1 / t2;
          cur_index_location = each_win.trigger_index + cur_sample_delta;
#         cur_index_offset   = cur_index_location - each_win.samples_start_offset;
# New 2025.03.10  this +1 aligns LS trigger with RLE trigger
          cur_index_offset   = cur_index_location - each_win.samples_start_offset + 1;
          cur_x              = cur_index_offset * each_win.x_space;
#         print("Cursor is %d : Window is %d : trig_delta_t = %d : sample_period = %d" %
#                (i,j,t1,t2) );
          each_win.cursor_x_list[i] = int( cur_x );
          if wave_i != None:
            if each_win == self.window_list[wave_i]:
              self.cursor_list[i].x = int( cur_x );
  return;

###############################################################################
# Majority of the time cursors are defined by their time position relative
# to the trigger. Exception is when the user drag a cursor around on the 
# screen. During these times, the trigger is defined by the mouse x position
# and the time relative to trigger needs to be calculated as trigger x moves
def update_cursors_to_mouse( self ):
  if self.window_selected != None:
    wave_i = self.window_selected;
    my_win = self.window_list[wave_i];
    if my_win.x_space != 0:
      for each_cur in self.cursor_list:
        # New 2023.09.05
        if each_cur.selected or \
          ( not self.cursor_list[0].selected and not self.cursor_list[1].selected ):
          try:
            cur_i = my_win.samples_start_offset + ( each_cur.x / my_win.x_space );
#           cur_delta_t = ( cur_i -  my_win.trigger_index ) * my_win.sample_period;
# New 2025.03.10 this -1 aligns LS trigger with RLE trigger
            cur_delta_t = ( cur_i -  my_win.trigger_index-1 ) * my_win.sample_period;
            each_cur.trig_delta_t    = cur_delta_t;# distance from cursor to trigger
            each_cur.trig_delta_unit = my_win.sample_unit;
          except:
#           print("ERROR-452");
            log( self, [ "ERROR-452" ] );
            print( cur_i, my_win.trigger_index, my_win.sample_period );
#                                None             None  digital_ls_0

#         print( cur_delta_t );

#   if my_win.timezone == "rle":
#     for each_cur in self.cursor_list:
#       cur_i = my_win.samples_start_offset + ( each_cur.x                  );
#       cur_delta_t = ( cur_i -  my_win.trigger_index ) * my_win.sample_period;
#       each_cur.trig_delta_t    = cur_delta_t;# distance from cursor to trigger
#       each_cur.trig_delta_unit = my_win.sample_unit;
#       if each_cur.visible:
#         print( each_cur.x, cur_i );

  self.refresh_waveforms = True;
  self.refresh_cursors = True;
  return;


###############################################################################
# When the active window switches, the cursors need to have their trigger
# relative positions updated as the sample units may change ( ie ns to us )
# Deprecated 2025.03.10 and is no longer called. Cursors now close 
# when switching active windows
def update_cursors_to_window( self ):
  if self.window_selected != None:
    for each_cur in self.cursor_list:
      if each_cur.trig_delta_unit != None and each_cur.trig_delta_t != None:
        # 1st Convert to ns
        if   each_cur.trig_delta_unit == "ms":
          each_cur.trig_delta_t *= 1000000.0;
        elif each_cur.trig_delta_unit == "us":
          each_cur.trig_delta_t *= 1000.0;
        elif each_cur.trig_delta_unit == "ns":
          each_cur.trig_delta_t *= 1.0;
        each_cur.trig_delta_unit = "ns";

        # 2nd, adjust to the selected window sample unit
        wave_i = self.window_selected;
        my_win = self.window_list[wave_i];
        if my_win.sample_unit != None:
          if   my_win.sample_unit == "ms":
            each_cur.trig_delta_t /= 1000000.0;
          elif my_win.sample_unit == "us":
            each_cur.trig_delta_t /= 1000.0;
          elif my_win.sample_unit == "ns":
            each_cur.trig_delta_t /= 1.0;
          each_cur.trig_delta_unit = my_win.sample_unit;
#         print("my_win.sample_unit is %s" % my_win.sample_unit );
  self.refresh_cursors = True;
  return;


###############################################################################
# Draw the lists that were created earlier on the screen
def draw_digital_lines( self, my_window ):
  if not my_window.panel.visible:
    return;
  my_image     = my_window.image;
  my_surface   = my_window.surface;
  my_draw_list = my_window.draw_list[:-1];
  my_trigger_x = my_window.draw_list[-1];

  if len( my_window.view_list ) == 0:
    my_window.y_offset = 0;

  # https://stackoverflow.com/questions/1634509/is-there-any-way-to-clear-a-surface
  my_surface.fill(self.color_bg);
# HERE81
# my_surface.fill(self.color_fg);

  w = my_surface.get_width();
  h = my_surface.get_height();

# if ( my_window.samples_shown != None and
#      my_window.samples_total != None     ):
#   start = ( ( my_window.samples_start_offset ) / my_window.samples_total );
#   stop  = ( ( (my_window.samples_start_offset+my_window.samples_shown)/ my_window.samples_total));
#   print( start, stop );
#       if samples_to_draw != 0:
#         rle_time_to_pixels = float( w / samples_to_draw ); # ratio that converts time in ps to pixels

  # Draw the gridlines Graticule
  if my_window.grid_enable :
    x_step = int( w / 10.0 );
    y_step = int( h / 10.0 );
#enumerate
    for x in range( 0,w,x_step):
      self.pygame.draw.line(my_surface,self.color_grid,(x,0),(x,h), 1);
#   for y in range( 0,h,y_step):
    for (i,y) in enumerate( range( 0,h,y_step) ):
      thickness = 1;
      if i == 5:
        thickness = 3;
      self.pygame.draw.line(my_surface,self.color_grid,(0,y),(w,y), thickness);

  analog_line_width = int( self.vars["screen_analog_line_width"], 10 );
  analog_bold_width = int( self.vars["screen_analog_bold_width"], 10 );

  # Draw the analog waveforms           
  for (each_sig, y_space, each_line_list, each_point_list) in my_draw_list:
    if len( each_line_list ) != 0 and each_sig.format == "analog" and each_sig.hidden == False:
      sig_color = rgb2color( each_sig.color );
#     if each_sig.selected:
#       sig_color = self.color_selected;
#     elif each_sig.trigger and each_sig.triggerable:
      if each_sig.trigger and each_sig.triggerable:
        sig_color = self.color_trigger;
      if each_sig.selected:
        sig_line_width = analog_bold_width;# 1 is hard to see
      else:
        sig_line_width = analog_line_width;# 1 is hard to see
      try:
        self.pygame.draw.lines(my_surface,sig_color,False,each_line_list,sig_line_width);
        circle_radius = 2;
#       if int( self.vars["screen_adc_sample_points"], 10 ) == 1:
        if True:
          for (x,y) in each_point_list:
            self.pygame.draw.line(my_surface,sig_color, (x,y-1),(x,y+1), 2);
#           self.pygame.draw.circle(my_surface,sig_color,(x,y),circle_radius,0);
      except:
        log(self,["ERROR-2011 : Analog drawing failure"]);

  # Draw the trigger
  if my_trigger_x != None:
    if ( my_trigger_x+7 ) >= w:
      my_trigger_x = w - 7;# Draw at far right if off screen
    x1 = my_trigger_x;
    x2 = my_trigger_x;
    y1 = 0;
    y2 = h;
    self.pygame.draw.line(my_surface,self.color_trigger,(x1,y1),(x2,y2), 1);

  # Draw the binary digital signals
  for (each_sig, y_space, each_line_list, each_point_list) in my_draw_list:
    if len( each_line_list ) != 0 and each_sig.format == "binary" and each_sig.hidden == False:
      sig_color = rgb2color( each_sig.color );
      if each_sig.selected:
        sig_color = self.color_selected;
#     elif each_sig.trigger and each_sig.triggerable:
#       sig_color = self.color_trigger;
      if len( each_line_list ) >= 2 :
        try:
          self.pygame.draw.lines(my_surface,sig_color,False,each_line_list,1);
        except:
          log(self,["ERROR-1993 %d %s" % ( len(each_line_list), each_line_list )]);

  # Draw the gridlines
# if my_window.grid_enable :
#   x_step = int( w / 10.0 );
#   y_step = int( h / 10.0 );
#   for x in range( 0,w,x_step):
#     self.pygame.draw.line(my_surface,self.color_grid,(x,0),(x,h), 1);
#   for y in range( 0,h,y_step):
#     self.pygame.draw.line(my_surface,self.color_grid,(0,y),(w,y), 1);

  txt_y_offset = 1;

  # Draw hex values if there is enough vertical spacing
  for (each_sig, y_space, each_line_list, each_point_list) in my_draw_list:
    if self.txt_height < y_space:
      if len( each_line_list ) != 0 and each_sig.format == "hex" and each_sig.hidden == False:
        for each_val in each_line_list:
          (x1,y1,txt) = each_val;
          if txt != None:
            try:
              my_surface.blit(txt, (x1,int(y1+txt_y_offset)) );
            except:
              log(self,["ERROR-2041 (%s,%s)" % (x1,int(y1+txt_y_offset))]);

  # Draw the signal names - 1st drawing a black box beneath. 
  # Don't draw if spacing is less than font height
  assigned  = len( self.container_view_list )-2;
  assigned_selected  = [ self.container_view_list[assigned].get_single_selection() ]; 
# print("assigned_selected == %s " % assigned_selected );
  y = 0.0; i = 0;
  for (each_sig, y_space, each_line_list, each_point_list) in my_draw_list:
    # Highlight entire views if the view is selected in the applied box
    view_selected = False;
    if len( assigned_selected ) != 0:
      if each_sig.view_name == assigned_selected[0]:
        view_selected = True;

#   # Only bother drawing the text if there is enough room
#   if self.txt_height < y_space:

    # Only bother drawing the text if it is visible in the window
    y = ( i * y_space ) + my_window.y_offset;
    if y >= 0 and y < h:
#   if True:
      x1 = 5;
      x1 += each_sig.hier_level * 2 * self.txt_width; # Indent for hier level
      y1 = int( y + txt_y_offset );
      txt = each_sig.name;

      if each_sig.collapsable:
        if each_sig.collapsed:
          txt = "[+]"+txt;
        else:
          txt = "[-]"+txt;
#     if each_sig.selected:
      # Only color highlight the digital selected. 
      # Analog keeps normal color and goes bold and underlined.
#     if each_sig.selected:
      if each_sig.selected and each_sig.type != "analog":
        sig_color = self.color_selected;
      elif view_selected:
        sig_color = self.color_selected;
      elif each_sig.hidden:
        sig_color = self.color_fg_dim ;
      elif each_sig.trigger and each_sig.triggerable:
        sig_color = self.color_trigger;
#       txt = txt+"(T)";# Assigned as trigger 
      elif each_sig.triggerable:
        sig_color = rgb2color( each_sig.color );
#       sig_color = self.color_triggerable;
#       txt = txt+"(t)";# Capable of being a trigger
#       txt = "_/"+txt;# TODO: Add Rising/Falling Edge
#       txt = "T "+txt;# TODO: Add Rising/Falling Edge
      else:
        sig_color = rgb2color( each_sig.color );

#     if each_sig.hidden:
      if each_sig.rle_masked:
        self.font.set_strikethrough( True );
      if each_sig.selected:
        self.font.set_bold( True  );# Bold for selected signal
        self.font.set_underline( True );
#       txt = "["+txt+"]";
        txt =     txt;
      txt = txt + each_sig.offscreen;


      # While in Acquisition display, triggerable signals in bold italic
#     if self.container_acquisition_list[0].visible == True:
#       self.font.set_bold( each_sig.triggerable );
#       self.font.set_italic( each_sig.triggerable );
        
      # Now render the text with the specified font
      txt = self.font.render(txt,True, sig_color     );

      # Finally set the font back to normal
      self.font.set_bold( False );
      self.font.set_underline( False );
      self.font.set_strikethrough( False );

#     if each_sig.selected:
#       self.font.set_bold( False );# Back to Normal
#       self.font.set_underline( False );
#     if each_sig.hidden:
#       self.font.set_strikethrough( False );


      w1 = txt.get_width();
      h1 = txt.get_height();
      if each_sig.type != "spacer":
# 2024.12.17
        self.pygame.draw.rect(my_surface,self.color_bg, pygame.Rect(0,y1-1,(x1+w1),h1+1) );
#       self.pygame.draw.rect(my_surface,self.color_bg, pygame.Rect(x1,y1,w1,h1) );
        my_surface.blit(txt, (x1,y1) );

#     y += y_space; i += 1;
      i += 1;
      each_sig.name_rect = (x1,y1,w1,h1);

#     # Draw Max line indicator for any selected analog waveforms
#     if each_sig.selected:
#       y3 = y1 - ( each_sig.range * 2.0 * each_sig.vertical_scale );
#       txt = self.font.render("###MAX###",True, sig_color     );
#       my_surface.blit(txt, (x1,y3) );
    else:
      i += 1;# Have to increment i since we can start with signals scrolled offscreen
      each_sig.name_rect = None;
 
  y_scrolled_stats = None; 
  try:
    a = len( my_draw_list ); # Total
    b = int( my_window.y_offset / y_space );# Culled at top
    c = int(h / y_space );# Drawn in Center
#   print( b, c, ( a-b-c ), a );
    y_scrolled_stats = (a,b,c);# Total, Culled at top (neg), Drawn in Center
  except:  
    pass;

  # draw zoom pinch lines - which are a lot like cursor lines
  if self.container_display_list[0].visible and self.window_selected != None and \
    my_window.panel.border_colour == self.color_selected:
    if self.mouse_pinch_dn != ( None, None ):
      (x1,y1) = self.mouse_pinch_dn;
      (x2,y2) = pygame.mouse.get_pos();# (x,y)
#     (self.mouse_x,self.mouse_y) = pygame.mouse.get_pos();
      color_cursor = self.cursor_list[0].color;
      border = 10;
      line_list  = [ [(x1-border,0), ( x1-border, 0+h )] ];
      line_list += [ [(x2-border,0), ( x2-border, 0+h )] ];
      for each_line_list in line_list:
        try:
          self.pygame.draw.lines(my_surface,color_cursor,False,each_line_list,1);
        except:
          log( self, [ "ERROR-254" ] );
          print("ERROR: Points must be numbered pairs");
          print(len(each_line_list));
          print( each_line_list );

  # draw cursors 
  if self.container_display_list[0].visible and self.window_selected != None:
    for (i,each_cur_x) in enumerate( my_window.cursor_x_list ):
#     print("each_cur_x = %s " % each_cur_x );
      if each_cur_x != None and self.cursor_list[i].visible:
        color_cursor = self.cursor_list[i].color;
        line_list = [ [(each_cur_x,0), ( each_cur_x, 0+h )] ];
        for each_line_list in line_list:
          if len(each_line_list) >= 2:
            try:
              self.pygame.draw.lines(my_surface,color_cursor,False,each_line_list,1);
            except:
              log( self, [ "ERROR-255" ] );
              print("ERROR: Points must be numbered pairs");
              print(len(each_line_list));
              print( each_line_list );
        txt = "-C%d" % (i+1);
        txt = self.font.render(txt,True, color_cursor );
        h1 = txt.get_height();
        try:
          my_surface.blit(txt,(each_cur_x,h-2*h1) );# Place C1 and C2 at window bottom
        except:
          log(self,["ERROR-2117 : Failed to my_surface.blit() C%d at %d,%d" % (i+1,each_cur_x,(h-2*h1))]);

        # Draw time delta between C1 and C2
        if i == 1 and self.cursor_list[0].visible and self.cursor_list[1].visible:
          x1 = my_window.cursor_x_list[0];
          x2 = my_window.cursor_x_list[1];
          xd = abs(x2-x1);
          if x1 < x2:
            xm = x1 + int(xd/2);
          else:
            xm = x2 + int(xd/2);
          if self.cursor_list[0].delta_txt != None:
            txt = self.cursor_list[0].delta_txt;
            txt_r = self.font.render(txt,True, color_cursor );
            w1 = txt_r.get_width();
            h1 = txt_r.get_height();
            try:
              y1 = h-2.5*h1;
              self.pygame.draw.line(my_surface,color_cursor,(x1,y1),(x2,y1), 1);
              y1 = h-3*h1;
              x1 = (xm-(w1/2));
              self.pygame.draw.rect(my_surface,self.color_bg, pygame.Rect(x1,y1,w1,h1) );
              my_surface.blit(txt_r,(x1,y1) );# Place at window bottom
            except:
              log(self,["ERROR-2118"]);

        # Display hex values at each cursor
        for y_key in self.cursor_list[i].sig_value_list:
          cur_val_list = self.cursor_list[i].sig_value_list[y_key];
          vasili = True;# Find the one appropriate value in the list and then stop
          last_x = -1; last_txt = "";
          for (the_win, x,y,txt) in cur_val_list:
            if the_win == my_window and vasili:
              txt_disp = None;
              (the_win, x3,y3,txt3) = cur_val_list[0]; # Left most value to display
              (the_win, x4,y4,txt4) = cur_val_list[-1];# Right most value to display

              if each_cur_x >= last_x and each_cur_x < x and last_x != -1:
                txt_disp = last_txt;
              elif each_cur_x >= x4:
                txt_disp = txt4;
              elif each_cur_x <= x3:
                txt_disp = txt3;

              if txt_disp != None:
                vasili = False;
                txt_r = self.font.render(txt_disp,True, color_cursor );
                try:
                  w1 = txt_r.get_width();
                  h1 = txt_r.get_height();
                  x1 = each_cur_x - int(w1/2);
                  y = y - int(h1/8);# Put cursor value slight higher above regular values
                  self.pygame.draw.rect(my_surface,self.color_bg, pygame.Rect(x1,y,w1,h1) );
                  my_surface.blit(txt_r,(x1,y) );# Place signal value at cursor location
                except:
                  log(self,["ERROR-2119"]);
              last_x = x;
              last_txt = txt;

  # Draw RLE Time Range in upper right corner and Window Number in upper left corner
  my_color = self.color_fg;
  my_window_name_drawn = False;
  if self.window_selected != None:
    my_win = self.window_list[self.window_selected];
    if my_win == my_window:
      my_color = self.color_selected;

  if my_window.rle_time_range != None:
    (a,b,c,d) = my_window.rle_time_range;
    txt = "[%0.1f%s,%+0.1f%s] " % ( a,b,c,d );
    txt = self.font.render(txt,True, my_color );
    w1 = txt.get_width();
    h1 = txt.get_height();
    self.pygame.draw.rect(my_surface,self.color_bg, pygame.Rect((w-w1),0,w1,h1) );
    my_surface.blit(txt, (w-w1,0));


  if y_scrolled_stats != None:
    (a,b,c) = y_scrolled_stats; # Total, Culled at top (neg), Drawn in Center
    if b != 0:
      d = abs(b)+c;
      if d > a:
        d = a;
      txt = "%s [%d:%d]of[0:%d] " % (my_window.name, abs(b),d,a);
      txt = self.font.render(txt,True, my_color );
      w1 = txt.get_width();
      h1 = txt.get_height();
      self.pygame.draw.rect(my_surface,self.color_bg, pygame.Rect(0,0,w1,h1) );
      my_surface.blit(txt, (0,0));
      my_window_name_drawn = True;
  if not my_window_name_drawn:
    txt = my_window.name;# Window number 1,2 or 3
    txt = self.font.render(txt,True, my_color );
    w1 = txt.get_width();
    h1 = txt.get_height();
    self.pygame.draw.rect(my_surface,self.color_bg, pygame.Rect(0,0,w1,h1) );
    my_surface.blit(txt, (0,0));

# if self.screen_shot:
#   my_color = self.color_selected;
#   txt = self.name + " " + self.vers + " " + self.copyright;
#   txt = self.font.render(txt,True, my_color );
#   w1 = txt.get_width();
#   h1 = txt.get_height();
#   self.pygame.draw.rect(my_surface,self.color_bg, pygame.Rect(0,0,w1,h1) );
#   my_surface.blit(txt, (0,0));

  my_image.set_image( my_surface );
  return;


########################################################################
# Create the waveforms for the 3 different windows. Windows get assigned
# views and views are assigned signals. This creates lists of graphic
# elements to draw. They are drawn later.
def create_waveforms( self ):
  for each_cur in self.cursor_list:
    each_cur.sig_value_list = {};

# self.digital_line_list = [];
  # Iterate the 3 Windows
  if self.debug_mode:
#   print("Refreshing %s %s" % ( self.refresh_waveforms, self.refresh_window_list ) );
    start_time = self.pygame.time.get_ticks();
  for ( i,each_win ) in enumerate( self.window_list ):
    if ( each_win.panel.visible and
         ( self.refresh_waveforms or i in self.refresh_window_list ) ):
      each_win.signal_list = [];
      each_win.grid_enable = False;
      # Iterate the views that this single window has
      for each_view in each_win.view_list:
        # Iterate the giant single signal list looking for signals of this view
        # and if they are visible or not
        for each_sig in self.signal_list:
          if each_sig.view_obj  == each_view:
            each_win.signal_list += [ each_sig ];
            each_sig.parent = each_win;
            # Automatically turn on the grid if any analog signals in this window
            if each_sig.type == "analog":
              each_win.grid_enable = True;
      each_win.draw_list = create_drawing_lines( self, each_win );
#     create_samples_viewport( self, each_win );

  if self.debug_mode:
    stop_time = self.pygame.time.get_ticks();
    render_time = stop_time - start_time;
    log( self, ["create_waveforms() Render Time = %d mS" % render_time] );
  return;


################################################################################
# Make a list of things to draw ( like binary waveforms ). This is slow but
# the actual drawing of the list later is fast. Only call this as-needed when
# something changes (zoom,pan, new signals added, etc )
def create_drawing_lines( self, my_win ):
  draw_list = [];
  my_surface = my_win.surface;
  my_sig_list = my_win.signal_list;
  w = my_surface.get_width();
  h = my_surface.get_height();
  (zoom,pan,scroll) = my_win.zoom_pan_list;
  trigger_x = None;
  rle_time_to_pixels = None;
  y_space = 0;
  rle_min_max = None;
  my_win.rle_time_range = None;

  # self.txt_height = txt.get_height();
  # y_space is spacing between slots. Maximum is 2x the font height. There is no minimum.
  # Take the window height and divide by the number of visible digital signals.
  # If that number is larger than 2x the font height, then y_space is 2x the font height,
  # otherwise scale y_space to fit. If y_space becomes less than 1.5x the font height, 
  # don't draw any fonts.
  vis_sigs = 0;
  for each_sig in my_sig_list:
#   print( each_sig.name );
#   print( each_sig.visible );
    if each_sig.visible == True:
      vis_sigs += 1;
#   if each_sig.type == "digital_rle":
    if each_sig.type == "digital" and each_sig.timezone == "rle":
      if each_sig.values == None or len(each_sig.values) == 0:
        if each_sig.rle_masked == False:
#         print("WARNING: %s has no samples" % each_sig.name );
          if self.sump_connected:
            download_rle_ondemand( self, each_sig.source );

# if vis_sigs != 0:
#   y_space = h / vis_sigs;
# else:
#   y_space = self.txt_height * 2;
# if y_space > ( self.txt_height * 2 ):
#   y_space = self.txt_height * 2;

# if vis_sigs != 0:
#   y_space = h / vis_sigs;
# else:
#   y_space = self.txt_height * 1.2;
# if y_space > ( self.txt_height * 1.2 ):
#   y_space = self.txt_height * 1.2;
  if vis_sigs != 0:
    y_space = self.txt_height * 1.2;

  # Determine if this window contains RLE signals.
  type_rle = False;
  for each_sig in my_sig_list:
    if type_rle == False:
      if each_sig.source != None:
        if "digital_rle" in each_sig.source:
          type_rle = True;
          break;

  if len( my_sig_list ) != 0:
    if not type_rle:
      # Not all signals have values ( groups ), so find signal with max number of values.
      samples_to_draw = max([ len(each.values) for each in my_sig_list ]);# list comprehension
    else:
      rle_flat_time_list = [];
# New 2024.12.16 : This doesn't work as the short time is never displayed relative to long
# time from two RLE pods in two different windows. This means that "zoom_full" is always
# relative to the longest RLE capture. This is better than alternative of never seeing short
# time relative to long time
#     if True:
#       each_win = my_win;
      for each_win in self.window_list:
        if each_win.timezone == "rle":
          for each_sig in each_win.signal_list:
            rle_flat_time_list += each_sig.rle_time;# List of all the times of all the signals

      if len( rle_flat_time_list ) != 0:
        rle_time_min = min( rle_flat_time_list );
        rle_time_max = max( rle_flat_time_list );
        rle_time_total = abs(rle_time_min) + rle_time_max;
        my_win.samples_total = rle_time_total;
        my_win.trigger_index = abs(rle_time_min);
        samples_to_draw = abs(rle_time_min) + rle_time_max;# Actually time in ps to draw
#       print( rle_time_min, rle_time_max );
        rle_min_max = ( rle_time_min, rle_time_max );
      else:
        samples_to_draw = 0;

#       print("RLE Captured:");
#       print(" rle_time_min   = %f ms" % ( rle_time_min   /1000000000 ));
#       print(" rle_time_max   = %f ms" % ( rle_time_max   /1000000000 ));
#       print(" rle_time_total = %f ms" % ( rle_time_total /1000000000 ));
#       my_win.trigger_index = abs(rle_time_min);
# New 2023.09.05
#       my_win.trigger_index = abs(rle_time_min) - float(self.vars["sump_rle_trigger_latency"]);
#       my_win.trigger_index = 0.0;
#       print("rle_time_total", rle_time_total );
#       print("rle_time_min",   rle_time_min   );
#       print("rle_time_max",   rle_time_max   );
#       print("my_win.trigger_index", my_win.trigger_index);
#       print("sump_rle_trigger_latency", float(self.vars["sump_rle_trigger_latency"]));


    # Zoom reduces the samples_to_draw so we only see a fraction on the display
    samples_to_draw = int( samples_to_draw / zoom );
    my_win.samples_shown = samples_to_draw;

    # Now we know the display width (w) and the number of samples to draw, so calculate
    # floating point pixel spacing between samples.
    if samples_to_draw != 0:
      x_space = float( ( w ) / samples_to_draw );
    else:
      x_space = 0;

    # A pan "click" is 1/10th the number of samples on the screen
    # Use the pan value (mouse wheel controlled) and this ratio to figure 1st sample drawn
    samples_start_offset = pan;

    # Assign the x_space and samples_start_offset value to the parent window. This is done for 
    # every signal that has samples, but the values will all be the same.
    my_win.x_space = x_space;
    # Note that sample(0) isn't drawn and is used for "Previous sample"
    # because of this, there's a +1 offset that cursor uses for it's calculations
    if not type_rle:
      my_win.samples_start_offset = samples_start_offset+1;
    else:
      my_win.samples_start_offset = samples_start_offset;

    # Now that we know viewport timing ( even for invisible signals ), cull the invisible 
    # so they don't take up any Y-spaces
    my_sig_list_culled = [];
    for each_sig in my_sig_list:
      if each_sig.visible:
        my_sig_list_culled += [ each_sig ];

    bit_space = y_space * 0.7;# Height of a binary signal, must be less than y_space.
#   for ( i, each_sig ) in enumerate( my_sig_list ):
    for ( i, each_sig ) in enumerate( my_sig_list_culled ):
#     y = i * y_space;
      y = ( i * y_space ) + my_win.y_offset;
      each_sig.y = y;# Used for drag operations of moving signals around
      x = 0.0;
      # ___ or \__ or /-- or ---
      y1 = int(y);
      y2 = int(y+bit_space);
      line_list = [];
      point_list = [];
      viewable_value_list = [];
      rle_value_time_pairs = [];
      if each_sig.format == "analog":
        x = - x_space;

      # Save time by only rendering signals that are not scrolled off screen
      if y >= 0 and y < h:
        visible_on_screen = True;
      else:
        visible_on_screen = False;# Scrolled offscreen, so don't draw
#       print("Not drawing %s" % each_sig.name );

      # Cull the samples down to what will be visible
      # Note the +2 is a fudge to get the ls_ana samples to fill the screen entirely.
      if not type_rle:
        value_list = each_sig.values;
        if samples_start_offset+samples_to_draw < len( value_list ):
#         viewable_value_list = value_list[samples_start_offset:samples_start_offset+samples_to_draw];
          viewable_value_list = value_list[samples_start_offset:samples_start_offset+samples_to_draw+2];
          stop_i  = samples_start_offset+samples_to_draw-1;
          start_i = samples_start_offset
        else:
#         viewable_value_list = value_list[-samples_to_draw:];
          viewable_value_list = value_list[-(samples_to_draw+2):];
          stop_i  = len( value_list ) -1;
          start_i = stop_i - samples_to_draw + 1;
#     else:
      elif type_rle and visible_on_screen:
        # Cull the RLE samples to just what are visible.
#       viewable_value_list = [];
#       rle_value_time_pairs = [];

        # Need to grab one invisible RLE sample each left and right of screen
        need_pre_leftmost   = True;
        need_post_rightmost = True;
#       print( each_sig.name, samples_to_draw );
        for ( i, each_value ) in enumerate( each_sig.values ):
          rle_time = each_sig.rle_time[i];
          # Adjust time so T=0 starts relative to most negative of ALL signal samples
          rle_time += abs( rle_time_min );
          # Draw one sample left of visible, all visible samples and one sample right of visible.
          if ( rle_time-samples_start_offset > 0 and
              ( ( rle_time-samples_start_offset < samples_to_draw                          ) or 
                ( rle_time-samples_start_offset >= samples_to_draw and need_post_rightmost )   )
             ):
            if need_pre_leftmost and i != 0:
              rle_value_time_pairs += [ ( prev_rle_value, prev_rle_time-samples_start_offset )];
              need_pre_leftmost   = False;
            if ( rle_time-samples_start_offset >= samples_to_draw and need_post_rightmost ):
              need_post_rightmost = False;
            rle_value_time_pairs += [ ( each_value, rle_time-samples_start_offset )];
          prev_rle_time  = rle_time;
          prev_rle_value = each_value;
        if rle_min_max != None and self.screen_window_rle_time == 1:
          ( rle_time_min, rle_time_max ) = rle_min_max;
          t_start = rle_time_min+samples_start_offset;
          t_stop =  rle_time_min+samples_start_offset+samples_to_draw;
          sample_unit = "ps";
          (a,b) = time_rounder( t_start , sample_unit );
          (c,d) = time_rounder( t_stop  , sample_unit );
          my_win.rle_time_range = ( a,b,c,d );
#          print( rle_time_min+samples_start_offset, rle_time_min+samples_start_offset+samples_to_draw );
#         print( a,b,c,d );


      # Calculate the visible sample index where the trigger is - just once
      if trigger_x == None and each_sig.trigger_index != None:
        if not type_rle:
          if ( each_sig.trigger_index >= start_i and
               each_sig.trigger_index <= stop_i        ):
            trigger_x = float( each_sig.trigger_index - start_i     ) * x_space;

      if type_rle and my_win.trigger_index != None:
        trigger_time_ps = ( my_win.trigger_index - samples_start_offset ); 
        if samples_to_draw != 0:
          rle_time_to_pixels = float( w / samples_to_draw ); # ratio that converts time in ps to pixels
          trigger_x = trigger_time_ps * rle_time_to_pixels;
#         print("trigger_x = %d , w = %d" % ( trigger_x, w ) );
#         if ( ( trigger_x + 5 ) > w ):
#           trigger_x = w - 5;# Handle case of seconds of pre-trig and trig on far right
        else:
#         log(self,["ERROR-2330 : samples_to_draw = %d" % samples_to_draw] );
          rle_time_to_pixels = None;


      if type_rle and visible_on_screen:
        if each_sig.format != "binary" and rle_time_to_pixels != None:
          if each_sig.format == "hex":
            if each_sig.selected:
              sig_color = self.color_selected;
            else:
              sig_color = rgb2color( each_sig.color );

            txt_r_nospace = self.font.render("<>",True, sig_color );
#           txt_open_bracket = self.font.render("<",True, sig_color );
            txt_close_bracket = self.font.render(">",True, sig_color );
            w2 = txt_close_bracket.get_width();
            if len( rle_value_time_pairs ) > 1:
              ( last_value, last_time ) = rle_value_time_pairs[0];
              cur_val_list = [];
              vasili = True;
              last_hex_str = None;
              first_drawn = False;
              for (each_value, each_time) in rle_value_time_pairs[1:]:
                x1 = int( each_time * rle_time_to_pixels );
                # Pygame will crash if pels are too far off screen
                if x1 < 0 : x1 = -1;
                if x1 > w : x1 = w+1;

                # The sample BEFORE the 1st onscreen sample
                if len( cur_val_list ) == 0:
                  hex_str = None;
                  if len( each_sig.fsm_state_dict ) != 0:
                    if each_sig.fsm_state_dict.get(last_value) != None:
                      hex_str = each_sig.fsm_state_dict[last_value];
                  if hex_str == None:
                    hex_str = "%08x" % last_value;
                    hex_str = hex_str[ - each_sig.nibble_cnt :];
                  txt = "<"+hex_str+" ";
                  cur_val_list += [(my_win,x1-1,y1,txt+">")];

                if each_value != last_value:
                  hex_str = None;
                  if len( each_sig.fsm_state_dict ) != 0:
                    if each_sig.fsm_state_dict.get(each_value) != None:
                      hex_str = each_sig.fsm_state_dict[each_value];
                  if hex_str == None:
                    hex_str = "%08x" % each_value;
                    hex_str = hex_str[ - each_sig.nibble_cnt :];
                  txt = "<"+hex_str+" ";

                  if True:
                    cur_val_list += [(my_win,x1,y1,txt+">")];
#                   print(txt);
                  txt_r = self.font.render(txt,True, sig_color );
                  if vasili:
                    w1 = txt_r.get_width();
                    vasili = False;
                else:
                  txt_r = None;

                # Draw the sample BEFORE the 1st sample drawn on the display. 
                # The RLE time of it may be off screen. We're showing value before new value.
                if txt_r != None and not first_drawn:
                  first_drawn = True;
                  hex_str2 = None;
                  if len( each_sig.fsm_state_dict ) != 0:
                    if each_sig.fsm_state_dict.get(last_value) != None:
                      hex_str2 = each_sig.fsm_state_dict[last_value];
                  if hex_str2 == None:
                    hex_str2 = "%08x" % last_value;
                    hex_str2 = hex_str2[ - each_sig.nibble_cnt :];
                  txt2 = ""+hex_str2+">";
                  txt_r2 = self.font.render(txt2,True, sig_color );
                  w3 = txt_r2.get_width();
                  line_list += [ (x1-w3,y1,txt_r2) ];# Draw to left of current sample

#                 if len( line_list ) > 0:
#                   current_sample = line_list[-1];
#                   list_list.pop();# Remove last item
#                   line_list += [ (x1-w3,y1,txt_r2) ];# Draw to left of current sample
#                   line_list += [ current_sample ];
#                 print("%s = %s" % ( each_sig.name, hex_str2 ) );

                # Don't render text that is getting overwritten by new sample, backup and
                # draw "<>" instead of full sample. Both a performance and clutter feature
                if len(line_list) >= 1 and txt_r != None:
                  (last_x,last_y,last_txt_r) = line_list[-1];
                  w4 = last_txt_r.get_width();
                  if last_x + w4 > x1:
                    line_list[-1] = (last_x,last_y,txt_r_nospace);
                  else:
                    if last_hex_str != None:
                      if ( x1 - last_x ) > ( w1 + w2 ):
                        txt_wider = self.font.render("< "+last_hex_str,True, sig_color );
                        line_list[-1] = (last_x,last_y,txt_wider );
                    line_list += [ (x1-w2,y1,txt_close_bracket) ];# Turn "<01   " into "<01  >"
                  last_hex_str = hex_str;

#               # Don't render text that is getting overwritten by new sample, backup and
#               # draw "<>" instead of full sample. Both a performance and clutter feature
#               if len(line_list) >= 1 and txt_r != None:
#                 (last_x,last_y,last_txt_r) = line_list[-1];
#                 if last_x + w1 > x1:
#                   line_list[-1] = (last_x,last_y,txt_r_nospace);
#                 else:
#                   if last_hex_str != None:
#                     if ( x1 - last_x ) > ( w1 + w2 ):
#                       txt_wider = self.font.render("< "+last_hex_str,True, sig_color );
#                       line_list[-1] = (last_x,last_y,txt_wider );
#                   line_list += [ (x1-w2,y1,txt_close_bracket) ];# Turn "<01   " into "<01  >"
#                 last_hex_str = hex_str;

                # If there is new text to render, render it now
                if txt_r != None:
                  line_list += [ (x1,y1,txt_r) ];

                last_value   = each_value;
                last_time    = each_time;
                # end of for (each_value, each_time) in rle_value_time_pairs[1:]:
              for (i, each_cur) in enumerate(self.cursor_list):
                each_cur.sig_value_list[ y1 ] = cur_val_list;
              draw_list += [ ( each_sig, y_space, line_list, point_list ) ];
            else:
              draw_list += [ ( each_sig, y_space, [], []    ) ];
          else:
            draw_list += [ ( each_sig, y_space, [], []    ) ];
        else:
          # Nominally, x_space is the spacing between each sample for non-RLE samples
          # for RLE, calculate the 
          # x = 0
          # x_space = float( ( w ) / samples_to_draw );
          # samples_start_offset = Offset in pS from rle_min_time
          # samples_to_draw      = Total time in pS to draw
          # Create a ratio that converts time in ps to pixels
          if samples_to_draw != 0:
            rle_time_to_pixels = float( w / samples_to_draw );
          else:
#           log(self,["ERROR-2372 : samples_to_draw = %d" % samples_to_draw]);
            rle_time_to_pixels = None;
          if len( rle_value_time_pairs ) > 1 and rle_time_to_pixels != None:
            ( last_value, last_time ) = rle_value_time_pairs[0];
            for (each_value, each_time) in rle_value_time_pairs[1:]:
              x1 = int( last_time * rle_time_to_pixels );
              x2 = int( each_time * rle_time_to_pixels );
              # NEW 2023.11.28 Only render valid samples
              # Pygame will crash if pels are too far off screen
              if x1 < 0 : x1 = -1;
              if x2 < 0 : x2 = -1;
              if x1 > w : x1 = w+1;
              if x2 > w : x2 = w+1;

              if   ( each_value == 0 and last_value == 0 ):
                line_list += [ ( x1, y2 ) , ( x2, y2 ) ];
              elif ( each_value == 1 and last_value == 1 ):
                line_list += [ ( x1, y1 ) , ( x2, y1 ) ];
              elif ( each_value == 0 and last_value == 1 ):
                line_list += [ (x1,y1), ( x2, y1 ) , ( x2, y2 ) ];
              elif ( each_value == 1 and last_value == 0 ):
                line_list += [ (x1,y2), ( x2, y2 ) , ( x2, y1 ) ];

              last_value = each_value;
              last_time  = each_time;
          draw_list += [ ( each_sig, y_space, line_list, point_list ) ];

      elif len( viewable_value_list ) == 0:
        draw_list += [ ( each_sig, y_space, [], []    ) ];

      # Only draw the samples that are visible and in binary format
#     elif each_sig.format == "binary":
      elif each_sig.format == "binary" and visible_on_screen:
        last_value = viewable_value_list[0];
        for each_value in viewable_value_list[1:]:
          x1 = int(float(x));
          x += float(x_space);
          x2 = int(float(x));
          # Pygame will crash if pels are too far off screen
          if x1 < 0 : x1 = -1;
          if x2 < 0 : x2 = -1;
          if x1 > w : x1 = w+1;
          if x2 > w : x2 = w+1;
          if   ( each_value == 0 and last_value == 0 ):
            line_list += [ ( x1, y2 ) , ( x2, y2 ) ];
          elif ( each_value == 1 and last_value == 1 ):
            line_list += [ ( x1, y1 ) , ( x2, y1 ) ];
          elif ( each_value == 0 and last_value == 1 ):
            line_list += [ (x1,y1), ( x2, y1 ) , ( x2, y2 ) ];
          elif ( each_value == 1 and last_value == 0 ):
            line_list += [ (x1,y2), ( x2, y2 ) , ( x2, y1 ) ];
          last_value = each_value;
        line_list = compress_line_list( line_list );
        draw_list += [ ( each_sig, y_space, line_list, point_list ) ];

      # Draw hex format text
#     elif each_sig.format == "hex":
      elif each_sig.format == "hex" and visible_on_screen:
        sig_color = rgb2color( each_sig.color );
        if each_sig.selected:
          sig_color = self.color_selected;
        last_value = viewable_value_list[0];
        for each_value in viewable_value_list[1:]:
          x1 = int(float(x));
          x += float(x_space);
          if each_value != last_value:
            hex_str = "%08x" % each_value;
            hex_str = hex_str[ - each_sig.nibble_cnt :];
            txt = self.font.render("<"+hex_str+">",True, sig_color );
          else:
            txt = None;
          last_value = each_value;
          if txt != None:
            line_list += [ (x1,y1,txt) ];
        draw_list += [ ( each_sig, y_space, line_list, point_list ) ];

      # Draw analog waveform
      elif each_sig.format == "analog":
        last_value = viewable_value_list[0];
        last_x     = int(float(x));
        y0 = int( h * each_sig.vertical_offset);# Note that it scales with screen height
        y0 += my_win.y_analog_offset;

        # Calculate the vertical scale using units_per_division
        # Note, if units_per_division is None then look for divisions_per_range and calculate from that.
        # If that is also None, go with 1.0 unit per division as a default.
        if each_sig.units_per_division == None:
          if each_sig.divisions_per_range == None:
            each_sig.units_per_division = 1.0;
          else:
            range_in_units = each_sig.units_per_code * each_sig.range;
            each_sig.units_per_division = float( range_in_units / each_sig.divisions_per_range );

        try:
          pels_per_division = float( h / 10.0 );
          pels_per_unit = float( pels_per_division / each_sig.units_per_division );
          pels_per_code = float( pels_per_unit * each_sig.units_per_code );
          v_scale = pels_per_code;
        except:
          print("WARNING: Bad Analog Math on Signal %s" % each_sig.name );
          pels_per_division = 0;
          pels_per_unit = 0;
          pels_per_code = 0;
          v_scale = 0;
 
     
        # If selected, Draw bars for Min/Max range
#       if each_sig.selected:
        if False:
          sig_color = self.color_selected;
          if each_sig.vertical_offset == 0.0 :
            y3 = y2 - int( 0 * v_scale );
            y4 = y2 - int( each_sig.range * v_scale );
          else:
            y3 = y0 - int( 0 * v_scale );
            y4 = y0 - int( each_sig.range * v_scale );
          line_list += [ ( 0,y4 ) , ( w, y4 ), ];
          line_list += [ ( w,y3 ) , ( 0, y3 ) ];

#       for each_value in viewable_value_list[1:]:
#       Last ADC sample is never present in RAM, so skip it.
        offscreen_top = True;
        offscreen_bot = True;

        # If only one sample exists, draw a horizontal line from sample point to end
        valid_sample_cnt = 0; last_valid_sample = None;
        for each_value in viewable_value_list[1:-1]:
          if each_value != None:
            valid_sample_cnt +=1;
            last_valid_sample = each_value;
        if valid_sample_cnt == 1:
          viewable_value_list_too = viewable_value_list[1:-2] + tuple([ last_valid_sample ]);
        else:
          viewable_value_list_too = viewable_value_list[1:-1];

#       for each_value in viewable_value_list[1:-1]:
        for each_value in viewable_value_list_too:
          x1 = int(float(x));
          x += float(x_space);
          x2 = int(float(x));
          # ADC values don't always exist at each sample point
          if each_value != None and last_value != None:

# Removed 2025.04.04 - Problematic when scrolling signal names, any analog
#  signals with vertical_offset==0 would scroll with name. All by itself.
#           # By default, waveform "gnd" reference is the signal name slot.
#           # If the user has specified a vertical offset, use that instead.
#           if each_sig.vertical_offset == 0.0 :
#             y3 = y2 - int( last_value * v_scale );
#             y4 = y2 - int( each_value * v_scale );
#           else:
#             y3 = y0 - int( last_value * v_scale );
#             y4 = y0 - int( each_value * v_scale );
            y3 = y0 - int( last_value * v_scale );
            y4 = y0 - int( each_value * v_scale );

            if each_sig.selected:
              if y3 < 0 and y4 < 0:
                offscreen_bot = False;
              if y3 > h and y4 > h:
                offscreen_top = False;
              if y3 > 0 and y3 < h:
                offscreen_top = False;
                offscreen_bot = False;
              if y4 > 0 and y4 < h:
                offscreen_top = False;
                offscreen_bot = False;

            line_list += [ ( last_x, y3 ) , ( x2, y4 ) ];
            if int( self.vars["screen_adc_sample_points"], 10 ) == 1:
              point_list += [ ( x2,y4 ) ];
          if each_value != None:
            last_value = each_value;
            last_x     = x2;
        # end for each_value in viewable_value_list[1:-1]:

        each_sig.offscreen = "";
        if each_sig.selected:
          if offscreen_top:
            each_sig.offscreen = "--^^";
          if offscreen_bot:
            each_sig.offscreen = "--vv";

        # If selected, Draw dotted bars for Min/Max range
        if each_sig.selected:
          y3 = y0 - int( 0 * v_scale );
          y4 = y0 - int( each_sig.range * v_scale );
          for x3 in range(0,w,+10):
            point_list += [ (x3,y3), (x3,y4) ];

        # If selected, Draw bars for Min/Max range
#       if each_sig.selected:
#         if each_sig.vertical_offset == 0.0 :
#           y3 = y2 - int( 0 * v_scale );
#           y4 = y2 - int( each_sig.range * v_scale );
#         else:
#           y3 = y0 - int( 0 * v_scale );
#           y4 = y0 - int( each_sig.range * v_scale );
#         line_list += [ ( w+10,y4 ) , ( w, y4 ), ];
#         line_list += [ ( w-10,y4 ) , ( w, y4 ), ];
#         line_list += [ ( w,y3 ) , ( w-10, y3 ) ];


        draw_list += [ ( each_sig, y_space, line_list, point_list ) ];
      else:
        draw_list += [ ( each_sig, y_space, [], []    ) ];
  draw_list += [ trigger_x ];
  return draw_list;


###############################################################################
# [  --- T ]
def create_samples_viewport( self, my_win ):
# bar = "                    ";
  font_size = int( self.vars["font_size"] );
  if font_size > 20:
    bar = 10*" ";
  elif font_size < 14:
    bar = 30*" ";
  else:
    bar = 20*" ";

  bar_len = len(bar);
# print ( my_win.samples_start_offset );
# print ( my_win.samples_shown );
# print ( my_win.samples_total );
  if ( my_win.trigger_index != None and 
       my_win.samples_shown != None and
       my_win.samples_total != None     ):
    t     = int( (bar_len * my_win.trigger_index) / my_win.samples_total);
    start = int( (bar_len * my_win.samples_start_offset ) / my_win.samples_total );
    stop  = int( (bar_len * (my_win.samples_start_offset+my_win.samples_shown)/ my_win.samples_total));
    if t >= 1:
      t = t - 1;
    if stop == start:
      stop = start+1;# Force a minimum of a single "-"
    for i in range( start, stop ):
      bar = string_i_replace(bar,i,"-");
    bar = string_i_replace(bar,t,"T");
#   print (t,start,stop);
  my_win.samples_viewport = "["+ bar + "]";
  return;

def string_i_replace( s, i, char ):
  s = s[:i] + char + s[i+1:]
  return s;


###############################################################################
# A line_list for a binary signal has a lot of redundant data when zoomed out
# This function removes that extra data to speed up rendering
def compress_line_list( line_list ):
  x1 = None; y1 = None;
  new_line_list = [];
  for (x,y) in line_list:
    if x != x1 or y != y1:
      new_line_list += [ (x,y) ];
    x1 = x; y1 = y;
  line_list = new_line_list;

  # In:  (1,0) (2,0) (3,0) (4,0) (4,1)
  # Out: (1,0)             (4,0) (4,1)
  new_line_list = [];
  x1 = None; x2 = None; y1 = None; y2 = None; run_jk = False;
  line_list += [ (None,None) ];# Make sure the last sample get drawn
  for (x,y) in line_list:
    if not run_jk:
      new_line_list += [ (x,y) ];
    if ( y == y1 ):
      run_jk = True;
    else:
      if run_jk:
        new_line_list += [ (x1,y1) ];
        new_line_list += [ (x,y) ];
      run_jk = False;
    y2 = y1; x2 = y1;
    y1 = y;  x1 = x;
  return new_line_list[:-1];# Remove the final (None,None)


###############################################################################
# Initialize the Display
def init_display(self):
  log( self, ["init_display()"] );
  self.screen_width  = int( self.vars["screen_width"], 10 );
  self.screen_height = int( self.vars["screen_height"], 10 );
  pygame.init();
  self.pygame = pygame;
  self.pygame.display.set_caption(self.name + " " + self.vers + " " + self.copyright);
  self.screen = pygame.display.set_mode( (self.screen_width,self.screen_height), pygame.RESIZABLE );
  self.pygame.display.set_icon( create_icon( self ) );
  return;


###############################################################################
# Erase entire screen. Needed as making things like the Console not visible
# leaves residues that must be erased ourselves.
def screen_erase(self):
  self.screen.fill( (0x00,0x00,0x00) );


def screen_get_size(self):
  ( self.screen_width, self.screen_height ) = self.screen.get_size();
  return;

def screen_set_size(self):
  self.refresh_waveforms = True;
# self.screen= pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE );

  # Make Widescreen 16:9 SD the minimum allowed
  if self.screen_width < 720 or self.screen_height < 576:
    self.screen_width = 720;
    self.screen_height = 576;

  self.screen = pygame.display.set_mode( (self.screen_width,self.screen_height), 
      pygame.RESIZABLE );
  self.options.resolution = ( self.screen_width, self.screen_height );
  self.ui_manager.set_window_resolution(self.options.resolution)
  screen_erase(self);
  resize_containers(self);
 
  # Since cursors are mouse positioned, they may go off-screen on a resize
  # To prevent this, on any resize, place them back on the left.
  self.cursor_list[0].x = 20;
  self.cursor_list[1].x = 40;

  self.vars["screen_width"]  = str( self.screen_width );
  self.vars["screen_height"] = str( self.screen_height );
  return;


###############################################################################
# Resize the 4 containers whenever the window is resized
# Containers 0-1 can be turned off. The height of each is therefore 
# Container 3 has a fixed height.
# Container 4 is screen height - Container 3 Height
# #2 is fixed height
# #3 = Window Height - #2 Height
#
# #1 is fixed height based on number of digital signals
# #0 is Window Height - #1 Height
def resize_containers(self):
  log( self, ["resize_containers()"] );
# console_h = 200;
  console_h = int( self.vars["screen_console_height" ],10 );
  right_w = 275;# Fixed width based on two buttons wide

# margin = 5;
  margin = 3;
  w = self.screen_width;

  w = w - ( margin * 3 );
  left_w = w - right_w;
  console_w = left_w;# Width of the 3 Wave windows

  # Figure out how many waveforms to diplay ( 0-3 )
  waves_to_display = 0;
  for each in self.window_list:
    if each.panel.visible == True:
      waves_to_display += 1;

  screen_h = self.screen_height - (margin*2);
  if self.cmd_console.visible == True:
    waves_h = screen_h - console_h;
  else:
    waves_h = screen_h;

  # Height of each wave is fraction of total
  if waves_to_display == 0:
    wave_h = 100;# A valid resolution for surface needed even if not displayed.
    waves_h = 0;# A valid resolution for surface needed even if not displayed.
    if self.cmd_console.visible == True:
      console_h = screen_h - margin;
  else:
#   wave_h = int(( waves_h - ( margin * waves_to_display ) ) / waves_to_display);
#   wave_h = wave_h - margin;
# 2025.04.29
    wave_h = int(( waves_h - float( margin * waves_to_display ) ) / waves_to_display);
    if waves_to_display == 1:
      wave_h = wave_h - margin;

  # Now place everybody
  if self.cmd_console.visible == True:
    x1 = 0 - margin;
    y1 = screen_h - console_h;
    self.cmd_console.set_position  ( (x1,y1) );
    self.cmd_console.set_dimensions( (console_w+margin,console_h+margin) );
    self.cmd_console.clear_log();# Fixes resize glitch
    self.cmd_console.show();
  else:
    self.cmd_console.hide();

  # 0 = Waves, 1 = Controls on Right
  h = waves_h;
  self.container_list[0].set_dimensions( (left_w,h) );
  self.container_list[1].set_dimensions( (right_w,screen_h) );

  x = margin; y = margin;
  self.container_list[0].set_relative_position( (x,y) );

  x = 2*margin + left_w; 
  self.container_list[1].set_relative_position( (x,y) );

  y = margin; x = margin; w = left_w; h = wave_h;
  for (i, each) in enumerate( self.window_list ):
    self.window_list[i].panel.set_relative_position( (x,y) );
    self.window_list[i].panel.set_dimensions( (w-(margin*3),h-margin) );
    if self.window_list[i].panel.visible == True:
      y += wave_h;

  # For all the waveform windows, decide to show() or hide() based on their
  # visibility and also select() or unselect() their Toggle buttons
  # Match the button names up with the waveforms they represent
  button_wf_order_list = ["#Window-1","#Window-2","#Window-3" ];
  for (i,each) in enumerate(self.window_list):
    id_str = ["#Controls","#Display", button_wf_order_list[i] ];
    for each_button in self.display_button_list:
      if each_button.object_ids == id_str:
        if each.panel.visible:
          each.panel.show();
        else:
          each.panel.hide();

  update_toggle_buttons(self);
  init_surfaces(self);# NEW
  self.refresh_waveforms = True;
  return;


###############################################################################
# When the views panel is opened, populate the two lists of:
# 1) Views that are assigned to the selected Window.
# 2) Views thar are available to the selected Window.
def create_view_selections( self ):
  log( self, ["create_view_selections()"] );
  self.toggle = not self.toggle;
# assigned = 4+3;  # Constant for the GUI selector list of assigned view
# available = 4+4; # Constant for the GUI selector list of available views
  assigned  = len( self.container_view_list )-2;
  available = assigned + 1;

  # The selector windows need to be completely emptied and repopulated
  # as their contents depend on which 1 of 3 windows is selected.
  # Probably easiest just to recalculate rather than store 3 copies.
  # 1st, empty both selectors
  for i in [ assigned, available ]:
    for each_item in self.container_view_list[i].item_list:
      self.container_view_list[i].remove_items( each_item["text"] );

  # Look at the assigned views for all three windows and make a list of
  # user_ctrl attributes. This list will then be used to remove any 
  # conflicting user_ctrl from the available list.
  # for example, if Window-1 has a user_ctrl[3:0]=A attribute, remove
  # all user_ctrl[3:0] views EXCEPT for those with user_ctrl[3:0]=A
  self.user_ctrl_assigned_list = [];
  for each_win in self.window_list:
    for each_view in each_win.view_list:
      for each_user_ctrl in each_view.user_ctrl_list:
        self.user_ctrl_assigned_list += [ each_user_ctrl ];

  # Now if there is a selected window, populate them appropriately
  if self.window_selected != None:
    my_win = self.window_list[self.window_selected];
    assigned_list = [];# Make list of views already assigned to this window
    for each_view in my_win.view_list:
      if each_view.name != None:
        assigned_list += [each_view.name];

#   # A view can only be used once. Signals can show up in two windows, but
#   # not views. This was a decision to simplify view selection and other things.
#   # Populate the view_ontap_list with views that are not being used by anyone.
#   available_list = [];
#   for each_view in self.view_ontap_list:
#     if not ( (any( each_view.name in each_win_view.name for each_win_view in self.window_list[0].view_list )) or
#              (any( each_view.name in each_win_view.name for each_win_view in self.window_list[1].view_list )) or
#              (any( each_view.name in each_win_view.name for each_win_view in self.window_list[2].view_list ))    ):
    # A view may be used across multiple windows. With time_lock off, this allows seeing same 
    # signals at different points in time.
    available_list = [];
    for each_view in self.view_ontap_list:
#     print("View Analysis on : %s" % each_view.name );
      if True:
        # Check to make sure this doesn't have conflicting user_ctrl values
        rejected = False;
        for each_applied_view in self.view_applied_list:
          for (apld_hub,apld_pod,apld_user_ctrl_list) in each_applied_view.rle_hub_pod_user_ctrl_list:
            for (hub,pod,user_ctrl_list) in each_view.rle_hub_pod_user_ctrl_list:
              if apld_hub == hub and apld_pod == pod:
                for (apld_bitrip,apld_val) in apld_user_ctrl_list:
                  for (bitrip,val) in user_ctrl_list:
#                   print( apld_bitrip, apld_val, bitrip, val );
                    if apld_bitrip == bitrip and apld_val != val:
                      rejected = True;
#                     print("View Rejection due to user_ctrl : %s" % each_view.name );
                
# from class view
#   self.rle_hub_pod_list = [];# (hub,pod) tuples assigned to this view
#   self.rle_hub_pod_user_ctrl_list = [];# (hub,pod,user_ctrl_list) tuples assigned to this view

        # Once a window has a timezone, reject views of different timezones
        if each_view.timezone != None and my_win.timezone != None:
          if each_view.timezone.lower() != my_win.timezone.lower():
            rejected = True;
#           print("View Rejection due to Timezone : %s" % each_view.name );
        if not rejected:
          # New 2023.12.13 Not sure where this "None" is coming from. Related to adding save_view
          if each_view.name != None:
            available_list += [ each_view.name ];
#           print("create_view_selections() : Adding view %s" % each_view.name );

      # TODO: Check for uut_rev timezone and user_ctrl conflicts
#     if not any( each_view.name in each_name for each_name in assigned_list ):
#       available_list += [ each_view.name ];

    # Populate the two selection widgets
#   print("Populating assigned_list:");
    for each_view_name in assigned_list:
#     print( each_view_name );
      if each_view_name != None:
        self.container_view_list[assigned].add_items( [ each_view_name ] );
#   print("Populating available_list:");
    for each_view_name in available_list:
#     print( each_view_name );
      if each_view_name != None:
        self.container_view_list[available].add_items( [ each_view_name ] );
  return;


###############################################################################
# Initialize the Widgets
#  Controls
#
# Actions = VertScale, VertPos, HorizScale, HorizPos
# Actions = SampleRate 
# Actions = Channel, Rising Edge, Falling Edge, 
#           Analog Level, Digital OR, Digital AND, 
#           Delay, Nth, Force 
# Actions = CursorsOFF, CursorsH, CursorsV,Cur-1,Cur-2
# 
#  2 Containers. 
#  UI Controls is always on and has a minimum height
#  The Analog and Digital containers are only on when
#  signals are made visible.
#  Initially they consume either 1/2 or Full height.
#  --------------------------------------------
# | -------------------------   -------------- | 
# ||    Analog Waveforms     | | UI Controls  || 
# | -------------------------  | ------------ || 
# | -------------------------  |              || 
# ||   Digital-LS Waveforms  | |  Popup Area  || 
# | -------------------------  |              || 
# ||   Digital-HS Waveforms  | |              || 
# | -------------------------   -------------- |
#  --------------------------------------------
def init_widgets(self):
  log( self, ["init_widgets()"] );
  self.container_list = [];
  # Note that you can't add object_id attributes after the fact - only on creation.
  object_id_list = [ "#Waveforms", "#Controls"];
  for i in range( 0,2 ):
    self.container_list += [ UIPanel(relative_rect=pygame.Rect(10, 10, 200, 100), 
#                            starting_layer_height=4, manager=self.ui_manager,
                             manager=self.ui_manager,
                             object_id = object_id_list[i] ) ];

# print( dir( self.container_list[0] ) );
# print( self.container_list[0].border_width );
# self.container_list[0].border_width = 3;# Default is 1
# self.container_list[0].rebuild();
# print( self.container_list[0].shadow_width );
# print("--");

  rect = self.container_list[0].relative_rect;# Get dimensions based on screen size
  object_id_list = [ "#Window-1", "#Window-2","#Window-3"];
  container_builder_waveforms( self, rect, object_id_list );

  self.cmd_console = UIConsoleWindow(rect=pygame.rect.Rect((10,10), (200,100)),
                                     manager=self.ui_manager,window_title="bd_shell");
# HERE73
  self.cmd_console.hide();# New 2025.04.28
# self.cmd_console.resizable = False;
# self.cmd_console.draggable = False;
# self.cmd_console.visible = False;
# self.cmd_console.close_window_button = False;
# self.cmd_console.enable_close_button = False;
# self.cmd_console.bring_to_front_on_focused = True;
# self.cmd_console.set_log_prefix('bd_shell>');

# print( dir( self.cmd_console ) );
# self.cmd_console.add('bd_shell>');

  resize_containers(self);# Resize based on screen dimensions

# self.acq_slider = None;

  # Populate the UI Control container
  rect = self.container_list[1].relative_rect;# Get dimensions based on screen size
  y_top = 0;# Keep track of where to draw each container based on height of last

# button_txt_list = [ "Acquisition", "Display",
#                     "Views",       "Help",    ];
  button_txt_list = [ "Acquisition", "Navigation",
                      "ViewConfig",  "Help",    ];
  y_top += container_builder_main_menu(self, rect, y_top,  button_txt_list);

  self.y_top = y_top;

# button_txt_list = [ "UUT",         "Connect",
  button_txt_list = [ "Target",      "Connect",
                      "Arm",         "Acquire",
                      "Query",       "Download",
                      "Force_Trig",  "Force_Stop",    
                      "Set_Trigs",   "Clear_Trigs",
#                     "Set_Trigs",   "Clr_Trigs",
                      "",
                      "Save_PZA",    "Load_PZA",
                      "Save_VCD",    "Load_VCD",
#                     "Save_PNG",    "Save_JPG",      
                      "Save_List",   "Save_View",      
                      "Save_Window", "Save_Screen",
                    ];

  y_top += container_builder_acquisition( self, rect, self.y_top, button_txt_list );

# button_txt_list = [ "Apply",       "Remove",   ];
# button_txt_list = [ "Apply",       "Remove", 
#                     "ApplyAll",    "RemoveAll",
#                                                ];

  button_txt_list = [ "Font--",       "Font++",
                      "MaskSig",      "HideSig",     
                      "CopySig",      "PasteSig",     
                      "CutSig",       "DeleteSig",     
                      "",
                      "Apply",       "Remove", 
                      "ApplyAll",    "RemoveAll",
                                                 ];

  y_top += container_builder_views(self, rect, self.y_top, button_txt_list);

# left_arrow  = "\u2190PanLeft";# unicode for left arrow. I like source code in 7bit ASCII.
# right_arrow = "PanRight\u2192";# unicode for right arrow. I like source code in 7bit ASCII.

  # Note the null strings provide some extra spacing for unrelated
  button_txt_list = [ "Window-1",     "Window-2",     
                      "Window-3",     "bd_shell",
                      "",
                      "Save_Window",  "Save_Screen",
                      "",
                      "Cursor-1",     "Cursor-2",     
                      "Add_Measure",  "Remove_Meas",

#                     "Font--",       "Font++",
#                     "",
#                     "Save_PNG",     "Save_JPG",      
#                     "Save_List",    "Save_View",      
#                     "",
#                     "MaskSig",      "HideSig",     
#                     "CopySig",      "PasteSig",     
#                     "CutSig",       "DeleteSig",     
                      "",
                      "TimeSnap",     "TimeLock",     
                      "ZoomIn",       "ZoomOut",      
                      "ZoomCurs",     "ZoomFull",      
                      "<-Search",     "Search->",      
                      "<-Pan",        "Pan->",         ];

  # Remove these buttons if the screen is really short. User will have to use
  # bd_shell CLI interface to get these features.
# small_scrn_list = [ "Font--",       "Font++",
#                     "",
#                     "Save_List",    "Save_View",      
#                     "",
#                     "CopySig",      "PasteSig",     
#                     "CutSig",       "DeleteSig",     
#                     "TimeSnap",     "TimeLock",     
#                     "<-Search",     "Search->",      
#                     "",
#                    ];
# really_small_scrn_list = [ 
#                            "CopySig",      "PasteSig",     
#                            "CutSig",       "DeleteSig",     
#                          ];

# screen_height_small = int( self.vars["screen_height_small"], 10 );
# if self.screen_height <= ( screen_height_small * 1.2 ):
#   for each in small_scrn_list:
#     button_txt_list.remove( each );

# if self.screen_height <= (screen_height_small/2):
#   for each in really_small_scrn_list:
#     button_txt_list.remove( each );

  y_top += container_builder_display(self, rect, self.y_top, button_txt_list);


# resize_containers(self);# Resize based on screen dimensions

  return;


# self.cmd_console.command_entry.set_text('A line of text to log')
# self.cmd_console.set_log_prefix('bd>')
# self.cmd_console.command_entry.set_text( event.text );
# self.cmd_console.add_output_line_to_log('line to add',is_bold=True, remove_line_break=True)

###############################################################################
# Three waveform windows for Analog and two Digital domains
def container_builder_waveforms( self, rect, object_id_list ):
  log( self, ["container_builder_waveforms()"] );
  self.window_list = [];
  for i in range( 0,3 ):
    new_window = window( name = "%d" % (i+1) );
    new_window.panel    = UIPanel(relative_rect=pygame.Rect(1,1,1,1), 
#                            starting_layer_height=4, manager=self.ui_manager,
                             manager=self.ui_manager,
                             container=self.container_list[0],
                             object_id = object_id_list[i] );
    new_window.surface  = pygame.Surface( (10,10) );
#   new_window.image    = UIImage( relative_rect=(1,1,10,10),

# 6 is an offset so that black waveform image will be centered in the UIPanel
#   note that the Panel's offset has changed slightly from Pygame-GUI 0.6.9 to 0.6.13
#   new_window.image    = UIImage( relative_rect=pygame.Rect(1,1,10,10),
    new_window.image    = UIImage( relative_rect=pygame.Rect(6,6,10,10),
                             image_surface=new_window.surface,
                             manager=self.ui_manager,
                             container=new_window.panel );
    self.window_list += [ new_window ];

  return;

  # Warning : Every UIImage call is a 5MB memory leak for some reason.
  # Workaround is to not call this every refresh, instead use the set_image()
  # method every refresh. Only drawback is having to erase what was drawn 
  # last time. This will still leak 5MB every screen resize event.
# self.test_image = UIImage( relative_rect=(1,1,w-2,h-2),
#                            image_surface=self.my_surface,
#                            manager=self.ui_manager,
#                            container=self.waveform_list[1] );# Digital Container

###############################################################################
# The main menu are the buttons that select which mode buttons and widgets to display
def container_builder_main_menu( self, rect, y_top, button_txt_list ):
  log( self, ["container_builder_main_menu()"] );
  margin = 5;
  (x,y,w1,h) = rect;
  y = y_top + margin; x = margin;
  h = h - margin * 2;
  w = w1 - margin * 3;
  my_container = UIPanel( relative_rect=pygame.Rect(x,y,w,h), container=self.container_list[1],
#                         starting_layer_height=4, manager=self.ui_manager, visible = True,
                          manager=self.ui_manager, visible = True,
                          object_id="#Main" );
  y = margin; 
  h = 30;
  screen_height_small = int( self.vars["screen_height_small"], 10 );
  if self.screen_height <= screen_height_small:
    h = 20;
  w = w1 / 2 - ( margin * 4 );
  col = 0;
  self.main_menu_buttons = [];
  for each in button_txt_list:
    x1 = x + ( col * w ) + ( col*margin*2 );
    col += 1;
    text = each;
    object_id = "#"+each;
    object_id = object_id.replace("Navigation","Display");
    object_id = object_id.replace("ViewConfig","Views");
    self.main_menu_buttons += [ UIButton( relative_rect = pygame.Rect(x1,y,w,h),
      text = text, object_id=object_id, tool_tip_text = each+" Tool Tip",
      visible = True, container = my_container, manager = self.ui_manager,
      allow_double_clicks = False) ];
    if ( col == 2 ):
      y += h + margin;
      col = 0;
  h1 = y + margin;
  ( x,y1,w,h ) = my_container.relative_rect;
  my_container.set_dimensions( (w,h1 ) );
  self.gui_font = self.main_menu_buttons[0].font;
  return ( y + margin ); 


###############################################################################
# The signal mode is for selecting which analog and digital signals are visible
def container_builder_views( self, rect, y_top, button_txt_list ):
  log( self, ["container_builder_views()"] );
  margin = 5;
  vis = False;
  (x,y,w1,h1) = rect;
  y = y_top + margin; x = margin;
  h = h1 - margin * 2;
  w = w1 - margin * 3;
  self.container_view_list = [];
  self.container_view_list += [ UIPanel( relative_rect=pygame.Rect(x,y,w,h), 
                          container=self.container_list[1],object_id="#Views",
#                         starting_layer_height=4, manager=self.ui_manager,visible=vis)];
                          manager=self.ui_manager,visible=vis)];
  my_container = self.container_view_list[0];
  y = margin;
  w = w1 / 2 - margin * 4;
  h = 30;
  screen_height_small = int( self.vars["screen_height_small"], 10 );
  if self.screen_height <= screen_height_small:
    h = 20;
  col = 0;
  for each in button_txt_list:
    if each != "":
      x1 = x + ( col * w ) + ( col*margin*2 );
      col += 1;
      self.container_view_list += [ UIButton( relative_rect = pygame.Rect(x1,y,w,h),
        text = each, object_id="#"+each, tool_tip_text = each+" Tool Tip",
        visible = vis, container = my_container, manager = self.ui_manager,
        allow_double_clicks = False) ];
      if ( col == 2 ):
        y += h + margin;
        col = 0;
    else:
      y += int(1.5 * margin);# Extra spacing between unrelated buttons

  x = margin; w = w1 - margin*6;
  h = ( h1 - y ) / 4;
# Note: Had issues with allow_double_clicks so don't use.   
  self.container_view_list += [ UISelectionList(pygame.Rect(x,y,w,h), item_list=[],
    manager=self.ui_manager, container= my_container,object_id="#Visible",
    allow_multi_select=False,allow_double_clicks=False,visible=vis)];
#   allow_multi_select=True,allow_double_clicks=False,visible=vis)];

#   allow_multi_select=False,allow_double_clicks=True,visible=vis)];
#   allow_multi_select=False,allow_double_clicks=False,visible=vis)];
  y += h;

  self.container_view_list += [ UISelectionList(pygame.Rect(x,y,w,h), item_list=[],
    manager=self.ui_manager, container= my_container,object_id="#Hidden",
    allow_multi_select=False,allow_double_clicks=False,visible=vis)];
#   allow_multi_select=True,allow_double_clicks=False,visible=vis)];

#   allow_multi_select=False,allow_double_clicks=True,visible=vis)];
#   allow_multi_select=False,allow_double_clicks=False,visible=vis)];
  y += h;
  h1 = y + margin;
  ( x,y1,w,h ) = self.container_view_list[0].relative_rect;
  self.container_view_list[0].set_dimensions( (w,h1 ) );
  return ( y + margin ); 


###############################################################################
# The acquisition mode is for acquiring and downloading new data
def container_builder_acquisition( self, rect, y_top, button_txt_list ):
  log( self, ["container_builder_acquisition()"] );
  margin = 5;
  vis = False;
  (x,y,w1,h1) = rect;
  y = y_top + margin; x = margin;
  h = h1 - margin * 2;
  w = w1 - margin * 3;
  self.container_acquisition_list = [];
  self.container_acquisition_list += [
                     UIPanel( relative_rect=pygame.Rect(x,y,w,h), 
                          container=self.container_list[1], visible = vis,object_id="#Acquisition",
                          manager=self.ui_manager) ];
                          #starting_layer_height=4, manager=self.ui_manager) ];
  my_container = self.container_acquisition_list[0];
  y = margin;
  w = w1 / 2 - margin * 4;
  h = 30;
  screen_height_small = int( self.vars["screen_height_small"], 10 );
  if self.screen_height <= screen_height_small:
    h = 20;
  col = 0;
  for each in button_txt_list:
    if each != "":
      x1 = x + ( col * w ) + ( col*margin*2 );
      col += 1;
      self.container_acquisition_list += [ UIButton( relative_rect = pygame.Rect(x1,y,w,h),
        text = each, object_id="#"+each, tool_tip_text = each+" Tool Tip",
        visible = True, container = my_container, manager = self.ui_manager,
        allow_double_clicks = False) ];
      if ( col == 2 ):
        y += h + margin;
        col = 0;
    else:
      y += int(1.5 * margin);# Extra spacing between unrelated buttons

  x1 = x; w = w * 2 + (margin*2);
# self.container_acquisition_list += [ UIHorizontalSlider( (x1,y,w,h),
# 0.001526 allows for +1 increment on 16 bit values 0-65535.
#                         start_value=25.0, value_range = (0.0, 100.0), click_increment=0.001526,
# self.acq_slider = UIHorizontalSlider( pygame.Rect(x1,y,w,h),
#                         start_value=25.0, value_range = (0.0, 1000.0), click_increment=5.0,
#                         container= my_container, visible = True,
#                         manager=self.ui_manager, object_id='#acq_slider');
# y += h + margin;


  ( x,y1,w,h ) = self.container_acquisition_list[0].relative_rect;
  h1 = y + margin;
  self.container_acquisition_list[0].set_dimensions( (w,h1 ) );
  
  return ( y + margin ); 


###############################################################################
# The display mode is for modifying how signals are displayed. Position, Scale, Pan, etc
def container_builder_display( self, rect, y_top, button_txt_list ):
  log( self, ["container_builder_display()"] );
  margin = 5;
  vis = False;
  (x,y,w1,h1) = rect;
  y = y_top + margin; x = margin;
  h = h1 - margin * 2;
  w = w1 - margin * 3;
  self.container_display_list = [];
  my_list = self.container_display_list;
  my_list += [
                     UIPanel( relative_rect=pygame.Rect(x,y,w,h), 
                          container=self.container_list[1], visible = vis,object_id="#Display",
#                         starting_layer_height=4, manager=self.ui_manager) ];
                          manager=self.ui_manager) ];
  my_container = my_list[0];
  y = margin;
  w = w1 / 2 - margin * 4;
  h = 30;
  screen_height_small = int( self.vars["screen_height_small"], 10 );
  if self.screen_height <= screen_height_small:
    h = 20;
  col = 0;
  self.display_button_list = [];
  for each in button_txt_list:
    if each != "":
      x1 = x + ( col * w ) + ( col*margin*2 );
      col += 1;
      self.display_button_list += [ UIButton( relative_rect = pygame.Rect(x1,y,w,h),
        text = each, object_id="#"+each, tool_tip_text = each+" Tool Tip",
        visible = True, container = my_container, manager = self.ui_manager,
        allow_double_clicks = False) ];
      if ( col == 2 ):
        y += h + margin;
        col = 0;
    else:
      y += int(1.5 * margin);# Extra spacing between unrelated buttons
  h1 = y + margin;
  ( x,y1,w,h ) = my_list[0].relative_rect;
  my_list[0].set_dimensions( (w,h1 ) );
  
  # Can't use Tooltips unfortunately as
  # Tooltips don’t allow a container as they are designed to overlap normal UI boundaries and be
  # contained only within the ‘root’ window/container, which is synonymous with the pygame display surface.
  # Source https://pygame-gui.readthedocs.io/en/v_040/pygame_gui.elements.html#:~:text=A%20tool%20tip%20is%20a,an%20option%20on%20UIButton%20elements.
# for each_button in self.display_button_list:
#   if "#Controls.#Display.#TimeLock" in each_button.object_ids: 
#     UITooltip( html_text = "Hello", manager = self.ui_manager, parent_element = each_button );
  
  return ( y + margin ); 


def cmd_select_acquisition( self ):
# for each in self.display_button_list:
#   each.visible = False;
#   each.hide();
  self.container_acquisition_list[0].visible = True;
  self.container_display_list[0].visible     = False;
  self.container_view_list[0].visible        = False;
  self.select_text_i                         = None;# Clear old text selections
  self.refresh_waveforms                     = True;
  proc_main_menu_button_press( self );
  hide_the_invisibles( self );
  return [];

def cmd_select_navigation( self ):
# for each in self.display_button_list:
#   each.visible = False;
#   each.hide();
  self.container_acquisition_list[0].visible = False;
  self.container_display_list[0].visible     = True;
  self.container_view_list[0].visible        = False;
  self.select_text_i                         = None;# Clear old text selections
  self.refresh_waveforms                     = True;
  proc_main_menu_button_press( self );
  hide_the_invisibles( self );
  return [];

def cmd_select_viewconfig( self ):
# for each in self.display_button_list:
#   each.visible = False;
#   each.hide();
  self.container_acquisition_list[0].visible = False;
  self.container_display_list[0].visible     = False;
  self.container_view_list[0].visible        = True;
  self.select_text_i                         = None;# Clear old text selections
  self.refresh_waveforms                     = True;
  proc_main_menu_button_press( self );
  hide_the_invisibles( self );
  # Update the view selections whenever view controls are opened
  create_view_selections(self);
  return [];

def stats( self ):
  print("------");
  print( len( self.container_acquisition_list ));
  print( len( self.container_display_list     ));
  print( len( self.container_view_list        ));
  print( len( self.display_button_list        ));
  return;

def hide_all( self ):
  for each in self.container_acquisition_list:
    each.visible = False;
    each.hide();

  for each in self.container_display_list:
    each.visible = False;
    each.hide();

  for each in self.container_view_list:
    each.visible = False;
    each.hide();

  for each in self.display_button_list:
    each.visible = False;
    each.hide();

  return;

# I can't explain why acquisition_list and view_list have buttons added to 
# their lists, but display_list is length=1 just for the panel and has
# a completely separate display_button_list for its buttons.
# TODO: Look into refactoring this as is very confusing to look at.

def hide_the_invisibles( self ):
  vis = self.container_acquisition_list[0].visible;
  for each in self.container_acquisition_list:
    if vis:
      each.show();
    else:
      each.hide();

  vis = self.container_display_list[0].visible;
# for each in self.container_display_list:
  for each in self.display_button_list:
    if vis:
      each.show();
    else:
      each.hide();

  vis = self.container_view_list[0].visible;
  for each in self.container_view_list:
    if vis:
      each.show();
    else:
      each.hide();

  return;


def debug_containers( self ):
  print("container_acquisition_list");
  for each in self.container_acquisition_list:
    print( each.visible );
  print("container_view_list");
  for each in self.container_view_list:
    print( each.visible );
  print("container_display_list");
  for each in self.container_display_list:
    print( each.visible );
  print("display_button_list");
  for each in self.display_button_list:
    print( each.text, each.object_ids );
  return;


###############################################################################
# When a main menu button is pressed, we open or close control containers and
# the console. For example, when "Signals" is pressed, we close the console
# and display the "Signals" container. The "Signals" button is then lit up.
# If we press "Signals" button again, we close the signals container and open
# the console window and unlight the "Signals" button.
def proc_main_menu_button_press( self ):
  # Note that show() and hide() on a parent also applies to all children. 
  # whereis just modifying the .visible attribute does NOT.
  self.display_console = True;
  if self.container_view_list[0].visible == True:
    self.container_view_list[0].show();
    self.display_console = False;
    radio_button_select( self.main_menu_buttons, "#Views" );
  else:
    self.container_view_list[0].hide();

  if self.container_acquisition_list[0].visible == True:
    self.container_acquisition_list[0].show();
    self.display_console = False;
    radio_button_select( self.main_menu_buttons, "#Acquisition" );
  else:
    self.container_acquisition_list[0].hide();

  if self.container_display_list[0].visible == True:
    self.container_display_list[0].show();
    self.display_console = False;
    radio_button_select( self.main_menu_buttons, "#Display" );
  else:
    self.container_display_list[0].hide();
  update_toggle_buttons(self);
  return;


###############################################################################
# select one button and unselect all the others
def radio_button_select( button_list, my_id ):
  for each in button_list:
#   print( dir( each ) );
    ( null, null, object_id ) = each.object_ids;
    each.unselect();
    if object_id == my_id:
      each.select();
  return;


###############################################################################
# Find a monospaced font to use
def get_font( self , font_name, font_height ):
  log( self, ["get_font( %s, %s )" % (font_name, font_height)] );
  if True:
    import fnmatch;
    font_height = int( font_height, 10 ); # Conv String to Int
    if ( self.os_platform == "mac" ):
      font_height = int( font_height, 20 ); # Conv String to Int
    font_list = self.pygame.font.get_fonts(); # List of all fonts on System
    self.font_list = [];
    for each in font_list:
      # Make a list of fonts that might work based on their name
      if ( ( "mono"    in each.lower()    ) or
           ( "courier" in each.lower()    ) or
           ( "fixed"   in each.lower()    )    ):
        self.font_list.append( each );

    if ( font_name == None or font_name == "" ):
      font_list = self.pygame.font.get_fonts(); # List of all fonts on System
      ends_with_mono_list = fnmatch.filter(font_list,"*mono");
      if  ends_with_mono_list :
        font_name = ends_with_mono_list[0];# Take 1st one
      else:
        font_name = self.font_list[0]; # Take 1st one
    try:
      font = self.pygame.font.SysFont( font_name , font_height );
    except:
      font = self.pygame.font.Font( None , font_height );# Default Pygame Font

    # Calculate Width and Height of font for future reference
    txt = font.render("4",True, ( 255,255,255 ) );
    self.txt_width  = txt.get_width();
    self.txt_height = txt.get_height();
  return font;


########################################################
# When <tab> is pressed, rotate thru the selected window
def cmd_win_tab( self ):
  rts = [];
  if self.window_selected != None:
    i = self.window_selected;
  else:
    i = 2;# Select Win-0 if none selected
  looping = True;
  start_i = i;
  while ( looping ):
    i+=1;
    if i == 3:
      i = 0;
    if ( self.window_list[i].panel.visible ):
      select_window( self, i );
      looping = False;
# print( start_i, i );
  return rts;

########################################################
# When <pageup> is pressed, rotate up the selected window
def cmd_win_pageup( self ):
  rts = [];
# for i in range( 0, 3 ):
#   if self.window_list[i].panel.visible:
#     if i > 0:
#       self.window_list[i].panel.visible = False;
#       self.window_list[i-1].panel.visible = True;
#       self.window_selected = i-1;
#       select_window( self, i-1 );
#       break;
  for i in range( 0, 3 ):
    self.window_list[i].panel.visible = False;

  i = self.window_selected;
  if i == None:
    i = 0;
  if i > 0:
    i = i - 1;
  self.window_list[i].panel.visible = True;
# self.window_selected = i;
  select_window( self, i );
  return rts;


########################################################
# When <pagedown> is pressed, rotate down the selected window
def cmd_win_pagedown( self ):
  rts = [];
# for i in range( 0, 3 ):
#   if self.window_list[i].panel.visible:
#     if i < 2:
#       self.window_list[i].panel.visible = False;
#       self.window_list[i+1].panel.visible = True;
#       self.window_selected = i+1;
#       select_window( self, i+1 );
#       break;
  for i in range( 0, 3 ):
    self.window_list[i].panel.visible = False;

  i = self.window_selected;
  if i == None:
    i = 0;
  if i < 2:
    i = i + 1;
  self.window_list[i].panel.visible = True;
# self.window_selected = i;
  select_window( self, i );
  return rts;
  

########################################################
# Pan Left 1 click ( 1/10th of screen )
def cmd_pan_left( self ):
  rts = [];
# if self.window_selected != None:
  if self.container_display_list[0].visible and self.window_selected != None :
    win_num      = self.window_selected;
    my_win       = self.window_list[win_num];
    timezone     = my_win.timezone;
    (zoom,pan,null ) = my_win.zoom_pan_list;
#   pan = pan - 1;
#   print("sample_shown = %d " % my_win.samples_shown );
    if my_win.samples_shown != None:
      delta = int( my_win.samples_shown / 10 );
      if delta == 0:
        delta = 1;# For Analog Samples
      pan = pan - delta;
      if pan < 0:
        pan = 0;
    my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
    my_win.zoom_pan_list = (zoom,pan,0 );
    if self.time_lock == True:
      for each_win in self.window_list:
#       if each_win.timezone == "rle" and each_win != my_win:
        if each_win.timezone == timezone and each_win != my_win:
          each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
          each_win.zoom_pan_list = (zoom,pan,0 );
# Time Lock attempt
#   for each_win in self.window_list:
#     if timezone == each_win.timezone:
#       each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
#       each_win.zoom_pan_list = (zoom,pan,0 );


#   self.refresh_waveforms = True;
    refresh_same_timezone(self);
  return rts;


########################################################
# Pan Right 1 click ( 1/10th of screen )
def cmd_pan_right( self ):
  rts = [];
# if self.window_selected != None:
  if self.container_display_list[0].visible and self.window_selected != None :
    win_num      = self.window_selected;
    my_win       = self.window_list[win_num];
    timezone     = my_win.timezone;
    samples_start_offset = my_win.samples_start_offset;
    samples_shown        = my_win.samples_shown;
    samples_total        = my_win.samples_total;
    (zoom,pan,null ) = my_win.zoom_pan_list;
#   pan = pan + 1;
#   print("sample_shown = %d " % my_win.samples_shown );
    if my_win.samples_shown != None:
      delta = int( my_win.samples_shown / 10 );
      if delta == 0:
        delta = 1;# For Analog Samples
      pan = pan + delta;
      try:
        if pan + samples_shown > samples_total:
          pan = samples_total - samples_shown;
      except:
        print("ERROR: cmd_pan_right()");

    my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
    my_win.zoom_pan_list = (zoom,pan,0 );
    if self.time_lock == True:
      for each_win in self.window_list:
#       if each_win.timezone == "rle" and each_win != my_win:
        if each_win.timezone == timezone and each_win != my_win:
          each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
          each_win.zoom_pan_list = (zoom,pan,0 );
# Time Lock attempt
#   for each_win in self.window_list:
#     if timezone == each_win.timezone:
#       each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
#       each_win.zoom_pan_list = (zoom,pan,0 );
#   self.refresh_waveforms = True;
    refresh_same_timezone(self);
  return rts;


########################################################
# Search forward ( right ) for transition on signal
def cmd_search_forward( self ):
  rts = [];
  if self.container_display_list[0].visible and self.window_selected != None :
    rts += ["search_forward()"];
    win_num      = self.window_selected;
    my_win       = self.window_list[win_num];
    timezone     = my_win.timezone;
    samples_start_offset = my_win.samples_start_offset;
    samples_shown        = my_win.samples_shown;
    samples_total        = my_win.samples_total;
    (zoom,pan,null ) = my_win.zoom_pan_list;
    if my_win.samples_shown != None:
      for each_sig in self.signal_list:
        if each_sig.source != None and each_sig.selected == True:
          if "digital_rle" in each_sig.source:
            center_time = samples_start_offset + ( samples_shown // 2 );
            center_i = None;
            for (i,rle_time) in enumerate( each_sig.rle_time ):
              if ( rle_time + my_win.trigger_index ) > center_time:
                center_i = i-1;
                break;
            if center_i != None:
              start_value = each_sig.values[center_i];
              found_i = None;
              for i in range(0, len(each_sig.values)-center_i ):
                if each_sig.values[center_i+i] != start_value:
                  found_i = center_i+i;
                  break;
              if found_i != None:
                pan = pan + ( (each_sig.rle_time[found_i]+my_win.trigger_index) - center_time );
              else:
                rts += ["no transition found"];
            else:
              rts += ["WARNING: no center_i found"];

    my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
    my_win.zoom_pan_list = (zoom,pan,0 );
    if self.time_lock == True:
      for each_win in self.window_list:
        if each_win.timezone == "rle" and each_win != my_win:
          each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
          each_win.zoom_pan_list = (zoom,pan,0 );
# Time Lock attempt
#   for each_win in self.window_list:
#     if timezone == each_win.timezone:
#       each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
#       each_win.zoom_pan_list = (zoom,pan,0 );
    refresh_same_timezone(self);
  return rts;

########################################################
# Search backward ( left ) for transition on signal
def cmd_search_backward( self ):
  rts = [];
  if self.container_display_list[0].visible and self.window_selected != None :
    rts += ["search_backward()"];
    win_num      = self.window_selected;
    my_win       = self.window_list[win_num];
    timezone     = my_win.timezone;
    samples_start_offset = my_win.samples_start_offset;
    samples_shown        = my_win.samples_shown;
    samples_total        = my_win.samples_total;
    (zoom,pan,null ) = my_win.zoom_pan_list;
    if my_win.samples_shown != None:
      for each_sig in self.signal_list:
        if each_sig.source != None and each_sig.selected == True:
          if "digital_rle" in each_sig.source:
            center_time = samples_start_offset + ( samples_shown // 2 );
            center_i = None;
            for (i,rle_time) in enumerate( each_sig.rle_time ):
              if ( rle_time + my_win.trigger_index ) > center_time:
                center_i = i-1;
                break;
            if center_i != None:
              start_value = each_sig.values[center_i];
              found_i = None;
              for i in range(0,center_i ):
                if each_sig.values[center_i-i] != start_value:
                  found_i = center_i-i;
                  break;
              if found_i != None:
                pan = pan + ( (each_sig.rle_time[found_i]+my_win.trigger_index) - center_time );
              else:
                rts += ["no transition found"];
            else:
              rts += ["WARNING: no center_i found"];

    my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
    my_win.zoom_pan_list = (zoom,pan,0 );
    if self.time_lock == True:
      for each_win in self.window_list:
        if each_win.timezone == "rle" and each_win != my_win:
          each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
          each_win.zoom_pan_list = (zoom,pan,0 );
# Time Lock attempt
#   for each_win in self.window_list:
#     if timezone == each_win.timezone:
#       each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
#       each_win.zoom_pan_list = (zoom,pan,0 );
    refresh_same_timezone(self);
  return rts;


########################################################
# page_up
def cmd_page_up( self ):
  rts = [];
  if self.container_display_list[0].visible and self.window_selected != None :
    win_num = self.window_selected;
    my_win  = self.window_list[win_num];
    my_surface = my_win.surface;
    h = my_surface.get_height();
    y_delta = h/2;
    if my_win.y_offset < 0:
      my_win.y_offset += y_delta;
    else:
      my_win.y_offset = 0;
    self.refresh_waveforms = True;
  return rts;


########################################################
# page_down
def cmd_page_down( self ):
  rts = [];
  if self.container_display_list[0].visible and self.window_selected != None :
    win_num = self.window_selected;
    my_win  = self.window_list[win_num];
    my_surface = my_win.surface;
    h = my_surface.get_height();
    y_delta = h/2;
    if True:
      my_win.y_offset -= y_delta;
    self.refresh_waveforms = True;
  return rts;


########################################################
# scroll_up 
def cmd_scroll_up( self ):
  rts = [];
# if self.container_display_list[0].visible and self.window_selected != None :
# Support scrolling on Acquisition tab since that's were triggers are selected
  if self.window_selected != None :
    win_num = self.window_selected;
    my_win  = self.window_list[win_num];
    y_delta = self.txt_height/1;
    if my_win.y_offset < 0:
      my_win.y_offset += y_delta;
    else:
      my_win.y_offset = 0;
    self.refresh_waveforms = True;
  return rts;


########################################################
# scroll_down
def cmd_scroll_down( self ):
  rts = [];
# if self.container_display_list[0].visible and self.window_selected != None :
# Support scrolling on Acquisition tab since that's were triggers are selected
  if self.window_selected != None :
    win_num = self.window_selected;
    my_win  = self.window_list[win_num];
    y_delta = self.txt_height/1;
    if True:
      my_win.y_offset -= y_delta;
    self.refresh_waveforms = True;
#   print(  my_win.y_offset );
  return rts;


########################################################
# scroll_analog_up 
def cmd_scroll_analog_up( self ):
  rts = [];
  if self.window_selected != None :
    win_num = self.window_selected;
    my_win  = self.window_list[win_num];
    y_delta = self.txt_height/1;
#   if my_win.y_analog_offset < 0:
    if True:
      my_win.y_analog_offset += y_delta;
#   else:
#     my_win.y_analog_offset = 0;
    self.refresh_waveforms = True;
  return rts;


########################################################
# scroll_analog_down
def cmd_scroll_analog_down( self ):
  rts = [];
  if self.window_selected != None :
    win_num = self.window_selected;
    my_win  = self.window_list[win_num];
    y_delta = self.txt_height/1;
    if True:
      my_win.y_analog_offset -= y_delta;
    self.refresh_waveforms = True;
  return rts;


########################################################
# Zoom In on center of screen
def cmd_zoom_in( self ):
  rts = [];
# if self.window_selected != None:
  if self.container_display_list[0].visible and self.window_selected != None :
    win_num          = self.window_selected;
    my_win           = self.window_list[win_num];
    samples_start_offset = my_win.samples_start_offset;
    samples_shown     = my_win.samples_shown;
    timezone         = my_win.timezone;

    if samples_shown == None:
      return rts;

    center_sample = samples_start_offset + int( samples_shown / 2 );
    (zoom,pan,null ) = my_win.zoom_pan_list;
#   zoom_ratio = 1.25;
    zoom_ratio = 2.00;# 2023.06.26
    zoom = zoom * zoom_ratio;

    samples_shown = int( samples_shown / zoom_ratio );
    samples_start_offset = center_sample - int( samples_shown / 2 );
    if samples_start_offset < 0:
      samples_start_offset = 0;
    pan = samples_start_offset;

    my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
    my_win.zoom_pan_list = (zoom,pan,0 );
    if self.time_lock == True:
      for each_win in self.window_list:
#       if each_win.timezone == "rle" and each_win != my_win:
        if each_win.timezone == timezone and each_win != my_win:
          each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
          each_win.zoom_pan_list = (zoom,pan,0 );
#   self.refresh_waveforms = True;
    refresh_same_timezone(self);
  return rts;


########################################################
# Zoom Out on center of screen
def cmd_zoom_out( self ):
  rts = [];
# if self.window_selected != None:
  if self.container_display_list[0].visible and self.window_selected != None :
    win_num          = self.window_selected;
    my_win           = self.window_list[win_num];
    samples_start_offset     = my_win.samples_start_offset;
    samples_shown     = my_win.samples_shown;
    samples_total     = my_win.samples_total;
    timezone         = my_win.timezone;
    if samples_shown == None or samples_total == None:
      return rts;

    center_sample = samples_start_offset + int( samples_shown / 2 );

    (zoom,pan,null ) = my_win.zoom_pan_list;
#   zoom_ratio = 1.25;
    zoom_ratio = 2.00;# 2023.06.26
    zoom = zoom / zoom_ratio;

    samples_shown = int( samples_shown * zoom_ratio );
    samples_start_offset = center_sample - int( samples_shown / 2 );
    pan = samples_start_offset;

    # Have to adjust the pan offset if zooming out and panned too far right
#   if ( pan + samples_shown > samples_total ):
#     pan = samples_total - samples_shown + 1;
#     if pan < 0:
#       pan = 0;
#     my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
#     my_win.zoom_pan_list = (zoom,pan,0 );


#     pan = samples_total - samples_shown - 1;
# New 2024.01.22
#     pan = 0;
#     cmd_zoom_full(self);
#     print("Oy1 - Punting to zoom_full");

    if pan < 0:
      pan = 0;

    if ( pan + samples_shown >= samples_total ):
      pan = samples_total - samples_shown - 1;
      if pan < 0:
        pan = 0;

    if ( pan + samples_shown < samples_total ):
      my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
      my_win.zoom_pan_list = (zoom,pan,0 );
      if self.time_lock == True:
        for each_win in self.window_list:
#         if each_win.timezone == "rle" and each_win != my_win:
          if each_win.timezone == timezone and each_win != my_win:
            each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
            each_win.zoom_pan_list = (zoom,pan,0 );
      refresh_same_timezone(self);
    else:
      cmd_zoom_full(self);
#     pan = 0;
#     print("Oy2 - Punting to zoom_full");
#
#   if ( pan + samples_shown < samples_total ):
#     my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
#     my_win.zoom_pan_list = (zoom,pan,0 );
#     if self.time_lock == True:
#       for each_win in self.window_list:
#         if each_win.timezone == "rle" and each_win != my_win:
#           each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
#           each_win.zoom_pan_list = (zoom,pan,0 );
#     refresh_same_timezone(self);
#   else:
#     pan = 0;
#     cmd_zoom_full(self);
#     print("Oy2 - Punting to zoom_full");
  return rts;

########################################################
# Zoom Out Full
# for the selected window and any window with same timezone
# set the zoom back to 1.0 and the pan ( samples_start_offset ) back to 0
def cmd_zoom_full( self ):
  rts = [];

  if self.container_display_list[0].visible and self.window_selected != None :
    win_num          = self.window_selected;
    my_win           = self.window_list[win_num];
    my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
    my_win.zoom_pan_list = ( 1.0,0,0 );
    timezone         = my_win.timezone;
    if self.time_lock == True:
      for each_win in self.window_list:
#       if each_win.timezone == "rle" and each_win != my_win:
        if each_win.timezone == timezone and each_win != my_win:
          each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
          each_win.zoom_pan_list = (1.0,0,0 );

# if self.window_selected != None:
#   timezone = self.window_list[ self.window_selected ].timezone;
#   for each_win in self.window_list:
#     if timezone == each_win.timezone:
#       each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
#       each_win.zoom_pan_list = ( 1.0,0,0 );
#   
# else:
#   rts += ["WARNING: No window selected"];
  self.refresh_waveforms = True;
  return rts;

########################################################
# Lock non-selected windows to selected window
def cmd_time_lock( self ):
  rts = [];
  self.time_lock = not self.time_lock;
  if self.time_lock == True:
    cmd_time_snap(self);
  update_toggle_buttons(self);
  return rts;

########################################################
# Snap non-selected windows to selected window
def cmd_time_snap( self ):
  rts = [];
# if self.window_selected != None:
  if self.container_display_list[0].visible and self.window_selected != None :
    win_num          = self.window_selected;
    my_win           = self.window_list[win_num];
    samples_start_offset = my_win.samples_start_offset;
    samples_shown     = my_win.samples_shown;
    timezone         = my_win.timezone;

    if samples_shown == None:
      return rts;

    (zoom,pan,null ) = my_win.zoom_pan_list;
    for each_win in self.window_list:
      if timezone == each_win.timezone:
        each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
#       (each_zoom,each_pan,null ) = each_win.zoom_pan_list;
#       each_win.zoom_pan_list = (each_zoom,pan,0 );
        each_win.zoom_pan_list = (zoom,pan,0 );
#   self.refresh_waveforms = True;
    refresh_same_timezone(self);
  return rts;

########################################################
# Zoom to cursor region
def cmd_zoom_to_cursors( self ):
  rts = [];

# if self.window_selected != None:
  if self.container_display_list[0].visible and self.window_selected != None :
    win_num = self.window_selected;
    my_win  = self.window_list[win_num];
    x_space       = my_win.x_space;
    samples_start_offset  = my_win.samples_start_offset;
    samples_total = my_win.samples_total;
    timezone      = my_win.timezone;

#   print("samples_start_offset  = %d" % samples_start_offset );
#   print("samples_total = %d" % samples_total );
#   print("x_space       = %d" % x_space       );

    if samples_total == 0 or samples_total == None or x_space == 0:
      return rts;
#   if self.cursor_list[0].visible and self.cursor_list[1].visible:
#   if x_space != 0:
    if True:
      c1_i = float( self.cursor_list[0].x / x_space ) + samples_start_offset;
      c2_i = float( self.cursor_list[1].x / x_space ) + samples_start_offset;
      if c1_i < c2_i:
        c_i_left  = int( c1_i );
        c_i_right = int( c2_i );
      else:
        c_i_left  = int( c2_i );
        c_i_right = int( c1_i );
      samples_to_draw = c_i_right - c_i_left;
      samples_start_offset = c_i_left;

      # We actually want to see the cursors, so decrease the zoom by 20%
      # and then subtract 10% from the start offset
      samples_to_draw = int( samples_to_draw * 1.2 );
      samples_start_offset -= int( samples_to_draw * 0.10 );


#     print("c_i_left        = %d" % c_i_left      );
#     print("c_i_right       = %d" % c_i_right     );
#     print("samples_start_offset    = %d" % samples_start_offset  );
#     print("samples_to_draw = %d" % samples_to_draw  );

      # Zoom reduces the samples_to_draw so we only see a fraction on the display
      if samples_to_draw != 0:
        zoom = float( samples_total / samples_to_draw );
#       print("zoom            = %f" % zoom );

#       # A pan "click" unit is 1/10th the number of samples on the screen
#       # samples_start_offset = ( samples_to_draw / 10 ) * pan;
#       pan = int( ( 10 * samples_start_offset ) / samples_to_draw );
#       pan = c_i_left;
#       pan = c_i_left - int( samples_to_draw * 0.10 );# 10% adjust to left so C1 visible
        pan = samples_start_offset;

        my_win.zoom_pan_history += [ my_win.zoom_pan_list ];
        my_win.zoom_pan_list = (zoom,pan,0 );
        if self.time_lock == True:
          for each_win in self.window_list:
#           if each_win.timezone == "rle" and each_win != my_win:
            if each_win.timezone == timezone and each_win != my_win:
              each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
              each_win.zoom_pan_list = (zoom,pan,0 );

        # Time Lock attempt
#       for each_win in self.window_list:
#         if timezone == each_win.timezone:
#           each_win.zoom_pan_history += [ each_win.zoom_pan_list ];
#           each_win.zoom_pan_list = (zoom,pan,0 );
#       self.refresh_waveforms = True;
        refresh_same_timezone(self);

  return rts;

########################################################
# scale_ analog signal 1,2,5, 10,20,50, 100,200,500
def cmd_scale_down( self ):
  rts = [];
  for each_sig in self.signal_list:
    if each_sig.selected:
      each_sig.vertical_scale_rate += 1;
      if each_sig.vertical_scale_rate == 3:
        each_sig.vertical_scale_rate = 0;

      if each_sig.units_per_division != None:
        if each_sig.vertical_scale_rate == 0:
          each_sig.units_per_division *= 2.0;
        elif each_sig.vertical_scale_rate == 1:
          each_sig.units_per_division *= 2.5;
        elif each_sig.vertical_scale_rate == 2:
          each_sig.units_per_division *= 2.0;
  return rts;


########################################################
def cmd_scale_up( self ):
  rts = [];
  for each_sig in self.signal_list:
    if each_sig.selected and each_sig.units_per_division != None :
      each_sig.vertical_scale_rate -= 1;
      if each_sig.vertical_scale_rate < 0:
        each_sig.vertical_scale_rate = 2;
      if each_sig.units_per_division > 0.01:
        if each_sig.vertical_scale_rate == 2:
          each_sig.units_per_division /= 2.0;
        elif each_sig.vertical_scale_rate == 0:
          each_sig.units_per_division /= 2.5;
        elif each_sig.vertical_scale_rate == 1:
          each_sig.units_per_division /= 2.0;
  return rts;


########################################################
def cmd_scale_down_fine( self ):
  rts = [];
  for each_sig in self.signal_list:
    if each_sig.selected:
      if each_sig.units_per_division != None:
        each_sig.units_per_division *= 1.025;
        each_sig.units_per_division = round( each_sig.units_per_division, 3 );
  return rts;


########################################################
def cmd_scale_up_fine( self ):
  rts = [];
  for each_sig in self.signal_list:
    if each_sig.selected and each_sig.units_per_division != None :
      if each_sig.units_per_division > 0.01:
        each_sig.units_per_division /= 1.025;
        each_sig.units_per_division = round( each_sig.units_per_division, 3 );
  return rts;



########################################################
# Refresh all the windows of the same timezone as selected
def refresh_same_timezone(self):
  if self.window_selected != None:
    wave_i = self.window_selected;
    timezone = self.window_list[wave_i].timezone;
    for (i,each_win) in enumerate( self.window_list ):
      if (timezone == each_win.timezone ):
        if i not in self.refresh_window_list:
          self.refresh_window_list += [ i ];
  return;


########################################################
def cmd_sump_force_stop( self ):
  log( self, ["sump_force_stop()"] );
  rts = [];
  if not self.sump_connected:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
    return;
  else:
    self.sump.wr( self.sump.cmd_state_reset, 0x00000000 );
    self.sump.wr( self.sump.cmd_state_idle,  0x00000000 );
    self.sump.rd_status();
    self.mode_acquire = False;
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright );
  return rts;


########################################################
# force_trig has two different modes.
# 1) Legacy Sump mode assumed sump_arm has been called
#    and that sump_download will be called after force_trig.
# 2) New "Scope Mode" - checks to see if Sump is armed
#    and if it isn't, arms the hardware - waits until it 
#    reaches the armed state and then issues the soft
#    trigger. Then waits for a complete acquisition and 
#    finally downloads the data.
def cmd_sump_force_trig( self ):
  log( self, ["sump_force_trig()"] );
  rts = [];
  if not self.sump_connected:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
    return;
  else:
#   log( self, ["1"] );
    self.sump.rd_status();
    ( stat_str, status ) = self.sump.status;
#   print( stat_str );
#   if stat_str != "armed":
#     log( self, ["2"] );
#     log( self, ["Arming Sump Hardware"] );
#     cmd_sump_acquire( self );
#     pygame.time.wait( 250 );# time in mS. 
#     log( self, ["Waiting for Armed state"] );
#     stat_str = "";
#     while( stat_str != "armed" ):
#       self.sump.rd_status();
#       ( stat_str, status ) = self.sump.status;
#       print( stat_str );
#       pygame.time.wait( 250 );# time in mS. 
#     log( self, ["3"] );
    if True:
#     log( self, ["4"] );
      log( self, ["Issuing a Software Force Trigger"] );
      self.sump.wr( self.sump.cmd_state_arm, 0x00000000 );# Bit is rising edge detect
      self.sump.wr( self.sump.cmd_state_arm, self.sump.sw_force_trig);
      self.sump.wr( self.sump.cmd_state_arm, 0x00000000 );# Bit is NOT self clearing
#     pygame.time.wait( 250 );# time in mS. 
#     self.sump.rd_status();
#     log( self, ["Waiting for acquisition to finish"] );
#     while( stat_str != "acquired" ):
#       self.sump.rd_status();
#       ( stat_str, status ) = self.sump.status;
#       print( stat_str );
#       pygame.time.wait( 1000 );# time in mS. 
#     log( self, ["Acquisition Complete"] );
#     log( self, ["5"] );
#     print(" mode_acquire = ", self.mode_acquire );
  return rts;


########################################################
def cmd_test_dialog( self, words ):
  rts = ["test_dialog()"];
# self.file_dialog = name;# The single handler needs to know the source
  # See https://github.com/MyreMylar/pygame_gui_examples/blob/master/file_dialog_test.py
  # WARNING: If object_id is not default "#file_dialog" the little widgets don't display
# test_dialog =  UITextEntryLine( manager=self.ui_manager,
  test_dialog =  UITextEntryBox( manager=self.ui_manager,
                     relative_rect=pygame.Rect(100, 100, 400, 300),
                     object_id="#test_dialog", visible = True,
                     initial_text = "A B C" );
  test_dialog.set_text("Hello Hello Hello");
  test_dialog.show();
  return rts;


########################################################
def cmd_file_dialog( self, name, path, ext ):
  self.file_dialog = name;# The single handler needs to know the source
  # See https://github.com/MyreMylar/pygame_gui_examples/blob/master/file_dialog_test.py
  # WARNING: If object_id is not default "#file_dialog" the little widgets don't display
  test_file =  UIFileDialog(rect=pygame.Rect(100, 100, 800, 500),
                     manager=self.ui_manager,
                     window_title=name,
                     object_id="#file_dialog", 
                     allow_picking_directories=True,
                     allowed_suffixes={ext},
                     initial_file_path=path  );
  test_file.show();
  return;


########################################################
def cmd_gui_refresh( self, words ):
  log( self, ["gui_refresh()"] );
  rts = [];
  self.refresh_waveforms = True;
  self.refresh_sig_names = True;
  self.refresh_cursors = True;
  return rts;

########################################################
def cmd_gui_minimize( self, words ):
  log( self, ["gui_minimize()"] );
  rts = [];
  self.pygame.display.iconify();
  return rts;

########################################################
#def cmd_gui_fullscreen( self, words ):
#  rts = [];
#  self.pygame.display.toggle_fullscreen();
#  return rts;

########################################################
def cmd_load_uut( self, words ):
# rts = [];
  log( self, ["cmd_load_uut()"] );
  uut_ini_file = words[1];
  (file_path,filename) = os.path.split( uut_ini_file );
  log( self, [" file_path = %s , file_name = %s" % ( file_path, filename )] );
  self.path_to_uut = file_path;# Note this is different from var sump_path_uut
# old_cwd = os.getcwd();
# os.chdir( file_path );# Need to support relative path sourcing
# self.vars["sump_path_views"] = file_path;
  cmd_str = "source " + filename;
  self.view_ontap_list = [];# Erase any old views from a different UUT
  rts = [ proc_cmd( self, cmd_str ) ];

  # Look for any view files in the uut directory
  view_file_list = glob.glob(os.path.join(file_path, "*.txt" ) );# New 2024.11.04
  m = len( view_file_list ); 
  for (i, each_file_name) in enumerate( view_file_list ):
    perc = int((100*i)/m );
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" %d%% Importing Saved Views" % perc);
    (fn_path, fn_nopath ) = os.path.split( each_file_name );
    (fn_noext, fn_ext ) = os.path.splitext( fn_nopath );
    if (i+1) < m:
      defer_gui_update = True;
    else:
      defer_gui_update = False;
    cmd_add_view_ontap(self, ["add_view_ontap", fn_nopath ], defer_gui_update );

# create_view_ontap_list(self);
# os.chdir( old_cwd );
# for each in self.view_ontap_list:
#   print("#", each );
# print("cmd_load_uut() done");
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright);
  return rts;


########################################################
# Creating a pizza file is finding all the text files in sump_path_ram
# and creating a single pza file that contains them.
# "[pza_" is the escape sequence
# [pza_start foo.txt]
# asfasf lines of text
# [pza_stop foo.txt]
# That single list is then saved as a Gzipped file.
# So basically it's a gzipped tarball, but human readable.
# To manually decompress, just rename foo.pza to foo.txt.gz and gunzip it.
def cmd_save_pza( self, words ):
  log( self, ["save_pza()"] );
  rts = [];
  start_time = self.pygame.time.get_ticks();
  file_out = words[1];

  download_rle_ondemand_all( self );

  if file_out == None:
    filename_path = self.vars["sump_path_pza"];
    filename_base = os.path.join( filename_path, "sump3_" );
    file_out = make_unique_filename( self, filename_base, ".pza" );
  else:
    if ".pza" not in file_out:
      file_out = file_out + ".pza";
    (fp,fn) = os.path.split( file_out );
    if fp == "":
      filename_path = self.vars["sump_path_pza"];
      file_out      = os.path.join( filename_path, file_out );

  path = os.path.abspath( self.vars["sump_path_ram"] );
  ext = "txt";
  file_inc_filter = os.path.join( path, "*."+ext );
  file_exc_filter = os.path.join( path, "foo.txt" );# Keeping as an example
  glob_list = set(glob.glob(file_inc_filter))-set(glob.glob(file_exc_filter));
  pza_list = [];
  for each_file_name in sorted( glob_list ):
    (fn_path, fn_nopath ) = os.path.split( each_file_name );
    pza_list += ["[pza_start "+fn_nopath+"]"];
    pza_list += file2list( each_file_name );
    pza_list += ["[pza_stop "+fn_nopath+"]"];
# list2file( file_out, pza_list );# Clear Text file instead of Gzipped
  list2filegz( file_out, pza_list );# Gzipped
  count = len( glob_list );
  rts += ["save_pza() saved %d files to %s" % ( count, file_out ) ];
  stop_time = self.pygame.time.get_ticks();
  delta_time = stop_time - start_time;
  log( self, ["cmd_save_pza() %s : Download Time = %d mS" % ( file_out, delta_time )] );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Saved %s" % file_out);
  return rts;


########################################################
def cmd_load_pza( self, words ):
  log( self, ["load_pza()"] );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Loading PZA..");
  rts = [];
  file_in = words[1];
  if os.path.exists( file_in ):
    ( null , file_no_path ) = os.path.split( file_in );
    self.vars["uut_name"] = file_no_path;
    log( self, ["gunzipping %s" % file_no_path ] );
#   pza_list = file2list( file_in );# Clear Text
    pza_list = filegz2list( file_in );# Gzipped

    view_rom_list = [];
    view_rom_found = False;

    # Go thru the pizza and extract all the individual files
    count = 0;
    txt_list = [];
    for each_line in pza_list:
      if each_line[0:5] == "[pza_":
        tag = each_line.replace("[","");
        tag = tag.replace("]","");
        tag_words = " ".join(tag.split()).split(' ') + [None] * 4;
        if tag_words[0] == "pza_stop":
          file_name = tag_words[1];
          file_path = self.vars["sump_path_ram"];
          file_name = os.path.join( file_path, file_name );
          list2file( file_name, txt_list );
          txt_list = [];
          count += 1;
          if view_rom_found == True:
            view_rom_list += [ file_name ];
          view_rom_found = False;
      else:
        txt_list += [ each_line ];
        my_words = " ".join(each_line.split()).split(' ') + [None] * 4;
        if my_words[0] == "create_view":
          view_rom_found = True;

    file_name = "sump_capture_cfg.txt";
    file_path = os.path.abspath( self.vars["sump_path_ram"] );
    file_name = os.path.join( file_path, file_name );
    if os.path.exists( file_name ):
      self.sump = sump_virtual( parent = self);
      self.sump.rd_cfg( file_name );
      self.sump_connected = False;# New 2024.12.12
    file_name = "sump_rle_podlist.txt";
    file_path = self.vars["sump_path_ram"];
    file_name = os.path.join( file_path, file_name );
    if os.path.exists( file_name ):
      self.sump.rd_pod_cfg( file_name );
    rts += ["load_pza() created %d files." % count ];
  else:
    rts += ["ERROR %s file not found" % file_in ];

  # Add any view roms in the pizza
# print( view_rom_list );

  m = len( view_rom_list ); 
  for ( i,each_file_name ) in enumerate( view_rom_list ):
    perc = int((100*i)/m );
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" %d%% Importing View ROMs" % perc);
    self.pygame.event.pump();
#   print("Importing View ROM file %s from PZA" % each_file_name );
#   cmd_add_view_ontap(self, ["add_view_ontap", each_file_name ] );
    (fn_path, fn_nopath ) = os.path.split( each_file_name );
    if (i+1) < m:
      defer_gui_update = True;
    else:
      defer_gui_update = False;
    cmd_add_view_ontap(self, ["add_view_ontap", fn_nopath ], defer_gui_update );

  # look for saved view files
  file_path = self.vars["sump_path_view"];
  view_file_list = glob.glob(os.path.join(file_path, "*.txt" ) );# New 2023.12.13
  m = len( view_file_list ); 
  for (i, each_file_name) in enumerate( view_file_list ):
    perc = int((100*i)/m );
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" %d%% Importing Saved Views" % perc);
    self.pygame.event.pump();
    (fn_path, fn_nopath ) = os.path.split( each_file_name );
    (fn_noext, fn_ext ) = os.path.splitext( fn_nopath );
    if (i+1) < m:
      defer_gui_update = True;
    else:
      defer_gui_update = False;
    cmd_add_view_ontap(self, ["add_view_ontap", fn_nopath ], defer_gui_update );

  # Snap Zoom/Pan back to zero. TODO this REALLY doesn't belong here.
  for each_win in self.window_list:
    each_win.startup();
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Populating samples");
  self.pygame.event.pump();
  populate_signal_values_from_samples( self );
  self.refresh_waveforms = True;
  self.refresh_sig_names = True;
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright);
  self.pygame.event.pump();
  return rts;


###############################################################################
# END_GUI_SECTION
###############################################################################

###############################################################################
def log( self, txt_list ):
  for each in txt_list:
    print( str( each ) );
    self.file_log.write( str(each) + "\n" );
  self.file_log.flush();# without flush(), a crash results in zero length file
  return;


###############################################################################
# START_SUMP_SECTION
###############################################################################

########################################################
# Establish connection to Sump3 hardware
def cmd_sump_connect( self ):
  log( self, ["sump_connect()"] );
  erase_old_sump_ram_files( self );
  time_start = time.time();
  txt = "Attempting to establish communication to hardware at %s : %d" % \
        ( self.vars["bd_server_ip"], int( self.vars["bd_server_socket"], 10 ));
  log( self, [ txt ] );

  rts = [];
# self.bd=Backdoor(  self.vars["bd_server_ip"],
#                    int( self.vars["bd_server_socket"], 10 ) );# Note dec
  self.bd=Backdoor(  self,
                     self.vars["bd_server_ip"],
                     int( self.vars["bd_server_socket"], 10 ),
                     int( self.vars["aes_key"], 16 ),          
                     int( self.vars["aes_authentication"], 10 ) 
                  );

  if ( self.bd.sock == None ):
    a = self.vars["bd_server_ip"];
    b = self.vars["bd_server_socket"];
    txt = "cmd_sump_connect(): ERROR: Unable to connect to BD_SERVER : Socket %s : IP %s" % (b,a);
    log( self, [ txt ] );
    return rts;

  thread_lock_en = int( self.vars["sump_thread_lock_en"], 10 );
  self.thread_lock_en = thread_lock_en == 1;

  rd_status_legacy_en = int( self.vars["sump_rd_status_legacy_en"], 10 );
  self.rd_status_legacy_en = rd_status_legacy_en == 1;

  self.sump = sump3_hw( self, self.bd, int( self.vars["sump_uut_addr"],16 ) );

  cmd_thread_pool_request_id(self);
  cmd_thread_lock(self);

  self.sump.wr( self.sump.cmd_state_idle,  0x00000000 );# In case in sleep state
  self.sump.rd_status();
  ( stat_str, status ) = self.sump.status;
  print( stat_str );

  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Reading HW Configuration..");
  self.pygame.event.pump();
  found_sump3_hw = self.sump.rd_cfg();# populate sump.cfg_dict[] with HW Configuration

# if ( self.sump.cfg_dict['hw_id'] != 0x0ADC ):
# if ( self.sump.cfg_dict['hw_id'] != 0x53 ):
  if found_sump3_hw == False:
    txt = "cmd_sump_connect(): ERROR: Unable to locate SUMP Hardware at %08x" % self.sump.addr_ctrl; 
    log( self, [ txt ] );
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" "+txt);
    return rts;
  else:
    self.sump_connected = True;
  self.sump.wr( self.sump.cmd_state_idle,  0x00000000 );
  self.sump.rd_status();
  ( stat_str, status ) = self.sump.status;
  print( stat_str );

  # Get the entire hardware configuration 
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Reading HW Configuration...");
  self.pygame.event.pump();
  found_sump3_hw = sump_read_config(self );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright);
  self.pygame.event.pump();

# rts += ["hw_id         = %04x" % self.sump.cfg_dict['hw_id']];
  rts += ["--------------------------------------------------"];
  rts += ["hw_id           = %02x" % self.sump.cfg_dict['hw_id']];
  rts += ["hw_rev          = %02x" % self.sump.cfg_dict['hw_rev']];
  rts += ["view_rom_en     = %01x" % self.sump.cfg_dict['view_rom_en'  ]];
  rts += ["bus_busy_bit_en = %01x" % self.sump.cfg_dict['bus_busy_bit_en' ]];
  rts += ["thread_lock_en  = %01x" % self.sump.cfg_dict['thread_lock_en' ]];
  rts += ["ana_ls_enable   = %01x" % self.sump.cfg_dict['ana_ls_enable']];
  rts += ["dig_hs_enable   = %01x" % self.sump.cfg_dict['dig_hs_enable']];
  rts += ["rle_hub_num     = %d"   % self.sump.cfg_dict['rle_hub_num']];
  rts += ["ana_ram_depth   = %dK"  % ( self.sump.cfg_dict['ana_ram_depth'] / 1024 )];
  rts += ["ana_ram_width   = %d"   % ( self.sump.cfg_dict['ana_ram_width'] *32 )];
  rts += ["dig_ram_depth   = %dK"  % ( self.sump.cfg_dict['dig_ram_depth'] / 1024 )];
  rts += ["dig_ram_width   = %d"   % ( self.sump.cfg_dict['dig_ram_width'] *32 )];
  rts += ["view_rom_kb     = %dKb" % ( self.sump.cfg_dict['view_rom_kb'] )];

# New 2023.08.23
  self.vars["sump_hs_clock_freq" ] = "%f" % self.sump.cfg_dict['dig_freq'];
  self.vars["sump_ls_clock_freq" ] = "%f" % self.sump.cfg_dict['tick_freq'];

# generate_view_rom_files( self );
# generate_rlepodlist_file( self, file_name="sump_rle_podlist.txt", pod_list=self.sump.rle_hub_pod_list );

  a = [""];
  triggerable_list = [];
  maskable_list = [];
  if len(self.sump.rle_hub_pod_list) != 0:
    a += ["RLE Hub+Pod Configuration"];
    a += ["sump3_core"];
  total_latency = 0.0;
  rle_ram_total_bits = 0;
  rle_rom_total_bits = 0;
  self.max_pod_acq_time_ms = 0;
  for (hub,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    pod = 0;
    self.sump.wr( self.sump.cmd_wr_rle_pod_inst_addr, (hub << 16) );

    hub_ck_freq = self.sump.rd( self.sump.cmd_rd_rle_hub_ck_freq)[0];
    hub_ck_freq_mhz = float( float(hub_ck_freq) / float( 2**20 ) );
    hub_hw_cfg      = self.sump.rd( self.sump.cmd_rd_rle_hub_hw_cfg)[0];
    if ( hub_hw_cfg & 0x00000001 ) == 0:
      hub_name_0_3  = self.sump.rd( self.sump.cmd_rd_rle_hub_name_0_3)[0];
      hub_name_4_7  = self.sump.rd( self.sump.cmd_rd_rle_hub_name_4_7)[0];
      hub_name_8_11 = self.sump.rd( self.sump.cmd_rd_rle_hub_name_8_11)[0];
      hub_name =  self.sump.dword_to_ascii( hub_name_0_3 );
      hub_name += self.sump.dword_to_ascii( hub_name_4_7 );
      hub_name += self.sump.dword_to_ascii( hub_name_8_11 );
      hub_name = hub_name.replace(" ","");
    else:
      hub_name = "%d" % hub;
#   a += ["  |"];
    a += ["  + Hub-%d : %s : %f MHz" % ( hub, hub_name, hub_ck_freq_mhz ) ];
    if hub == len(self.sump.rle_hub_pod_list)-1:
      t = " ";
    else:
      t = "|";
#   a += ["  "+t+"   |"];

    for (pod,each_pod) in enumerate( each_pod_list ):
      self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Reading (Hub,Pod) (%d,%d)" % (hub,pod));
      self.pygame.event.pump();
      pod_hw_cfg      = self.sump.rd_pod( hub=hub,pod=pod,reg=self.sump.rle_pod_addr_pod_hw_cfg )[0];
      pod_ram_cfg     = self.sump.rd_pod( hub=hub,pod=pod,reg=self.sump.rle_pod_addr_pod_ram_cfg )[0];
      pod_instance    = self.sump.rd_pod( hub=hub,pod=pod,reg=self.sump.rle_pod_addr_pod_instance  )[0];
      pod_triggerable = self.sump.rd_pod( hub=hub,pod=pod,reg=self.sump.rle_pod_addr_triggerable )[0];
      pod_view_rom_kb = self.sump.rd_pod( hub=hub,pod=pod,reg=self.sump.rle_pod_addr_pod_view_rom_kb )[0];

      if ( pod_hw_cfg & 0x00000020 ) == 0:
        pod_name_0_3    = self.sump.rd_pod( hub=hub,pod=pod,reg=self.sump.rle_pod_addr_pod_name_0_3  )[0];
        pod_name_4_7    = self.sump.rd_pod( hub=hub,pod=pod,reg=self.sump.rle_pod_addr_pod_name_4_7  )[0];
        pod_name_8_11   = self.sump.rd_pod( hub=hub,pod=pod,reg=self.sump.rle_pod_addr_pod_name_8_11 )[0];
        pod_name        =  self.sump.dword_to_ascii( pod_name_0_3 );
        pod_name        += self.sump.dword_to_ascii( pod_name_4_7 );
        pod_name        += self.sump.dword_to_ascii( pod_name_8_11 );
        pod_name        = pod_name.replace(" ","");
      else:
        pod_name = "%d" % pod;# pod_name_en parameter was 0

      for i in range(0,32):
        bit = 2**i;
        if ( ( pod_triggerable & bit ) != 0x00000000 ):
          triggerable_list += ["digital_rle[%d][%d][%d]" % ( hub,pod,i ) ];

#     print("pod_hw_cfg = %08x" % pod_hw_cfg );
      if ( ( pod_hw_cfg & 0x00000010 ) != 0x00000000 ):
        pod_maskable = 0xFFFFFFFF;
      else:
        pod_maskable = 0x00000000;
#     print("pod_maskable = %08x" % pod_maskable );
      for i in range(0,32):
        bit = 2**i;
        if ( ( pod_maskable & bit ) != 0x00000000 ):
          maskable_list += ["digital_rle[%d][%d][%d]" % ( hub,pod,i ) ];

      pod_hw_rev    = ( pod_hw_cfg & 0xFF000000 ) >> 24;
      pod_view_rom_en = ( pod_hw_cfg & 0x00000002 ) >> 1;
      pod_num_addr_bits = ( pod_ram_cfg & 0x000000FF ) >> 0;
      pod_num_data_bits = ( pod_ram_cfg & 0x00FFFF00 ) >> 8;
      pod_num_ts_bits   = ( pod_ram_cfg & 0xFF000000 ) >> 24;
      rle_ram_length = 2**pod_num_addr_bits;
      total_bits = pod_num_data_bits+pod_num_ts_bits+2;
      ram_kb = ( rle_ram_length * total_bits ) / 1024;
      ram_cfg = "%dx%d (%d+%d+%d) = %dKb" % (rle_ram_length,total_bits,2,pod_num_ts_bits,
        pod_num_data_bits,ram_kb);
      a += ["  "+t+"   + Pod-%d : %s : %s" % ( pod, pod_name, ram_cfg )];

      max_time = ((2**pod_num_ts_bits)/hub_ck_freq_mhz)/1000000;
      if ( max_time * 1000  ) > self.max_pod_acq_time_ms:
        self.max_pod_acq_time_ms = int( max_time * 1000);# used for acquire wait from trig to download
      if max_time < 0.000001 :
        max_time = max_time * 1000000000;
        units = "nS";
      elif max_time < 0.001 :
        max_time = max_time * 1000000;
        units = "uS";
      elif max_time < 1.0   :
        max_time = max_time * 1000;
        units = "mS";
      else:
        units = "Sec";
      a[-1] += " : Time = %d %s" % ( max_time, units );

      if pod_view_rom_en == 1 :
        a[-1] += " : view_rom_kb = %dKb" % pod_view_rom_kb;
        rle_rom_total_bits += pod_view_rom_kb * 1024;
      rle_ram_total_bits += ( rle_ram_length * total_bits );

#     # HACK to calculate a single trigger latency based on Hub-0,Pod-0 values
#     # Need to think about this long term. Should it be an average betwen clock domains?
#     # If there are N Hubs of all different clock domains, what is the trigger latency to be drawn?
#     if hub == 0 and pod == 0:
#       rle_trigger_latency_reg = self.sump.rd_pod( hub=hub,pod=pod,
#         reg=self.sump.rle_pod_addr_trigger_latency )[0];
#       latency_core = ( rle_trigger_latency_reg & 0x000000FF ) >> 0;
#       latency_mosi = ( rle_trigger_latency_reg & 0x0000FF00 ) >> 8;
#       latency_miso = ( rle_trigger_latency_reg & 0x00FF0000 ) >> 16;
#       
#       hub_ck_freq = self.sump.rd( self.sump.cmd_rd_rle_hub_ck_freq)[0];
#       hub_ck_freq_mhz = float( float(hub_ck_freq) / float( 2**20 ) );
#       hub_ck_ns = 1000.0 / hub_ck_freq_mhz;
#       hs_clk_ns = 1000.0 / float( self.vars["sump_hs_clock_freq"] );
#       total_latency = ( hub_ck_ns * ( latency_miso + latency_mosi ) );
#       total_latency += hs_clk_ns * latency_core;
#       self.vars["sump_rle_trigger_latency" ] = "%f" % ( 1000.0 * total_latency );# in ps
# a += ["Calculated RLE trigger latency is %0.3f ns" % total_latency]; 

  # Display total number of RLE ram bits in either Kb or Mb
  if len(self.sump.rle_hub_pod_list) != 0:
    if rle_ram_total_bits < (1024*1024):
      a += ["rle_ram_bits = %dKb" % int( rle_ram_total_bits / 1024 )];
    else:
      a += ["rle_ram_bits = %dMb" % int( rle_ram_total_bits / (1024*1024) )];
    if rle_rom_total_bits < (1024*1024):
      a += ["rle_rom_bits = %dKb" % int( rle_rom_total_bits / 1024 )];
    else:
      a += ["rle_rom_bits = %dMb" % int( rle_rom_total_bits / (1024*1024) )];

  a += [""];
  rts += a;


  # By default, the 1st 32 event signals going into an RLE pod are triggerable.
  # The parameter trig_bits on sump3_rle_pod.v may be set so that only a few
  # events can be triggers. Read this register and assign "-triggerable True"
  # attribute for single bits that are in the view_rom_list
  # TODO: This doesn't handle vectors ( counter bits, fsm bits, etc ) only bits
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Generating View ROM files..");
  self.pygame.event.pump();
  view_rom_list = [];
  for each in self.sump.view_rom_list:
    new_line = each;
    # -source can either be digital_rle[0][1][2] or hub0.pod1[2]
    # look for hub0.pod1[2] and if found replace with digital_rle[0][1][2] 
    # since the triggerable_list is in this format.
    if "create_signal" in each:
      new_each = each;
      for key in self.sump.rle_hub_pod_dict:
        search_str = "-source " + key;
        if search_str in each:
          (hub_num,pod_num) = self.sump.rle_hub_pod_dict[key];
          new_each = each.replace(search_str,"-source digital_rle[%d][%d]" % ( hub_num,pod_num ));
      for each_triggerable in triggerable_list:
        if each_triggerable in new_each:
          new_line += " -triggerable True" 
      for each_maskable in maskable_list:
        if each_maskable in new_each:
          new_line += " -maskable True" 
    view_rom_list += [ new_line ]; 
  
# print("Triggerable List:");
# for each_triggerable in triggerable_list:
#   print("  %s" % each_triggerable );
# print("View ROM List:");
# for each in view_rom_list:
#   print("  %s" % each );
  

# generate_view_rom_files( self, self.sump.view_rom_list );
# delete_view_rom_files( self );
  log( self, ["generate_view_rom_files() view_rom_list of length %d" % len( view_rom_list ) ] );
  generate_view_rom_files( self, view_rom_list );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Generating View ROM files......");
  self.pygame.event.pump();
  generate_rlepodlist_file( self, file_name="sump_rle_podlist.txt", pod_list=self.sump.rle_hub_pod_list );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright);
  self.pygame.event.pump();
  time_stop = time.time();
  connect_time_ms = int((time_stop-time_start)*1000);
  log( self, ["sump_connect time = %d ms" % connect_time_ms ] );
  file_path = self.vars["sump_path_dbg"];
  file_name = os.path.join( file_path,"hw_config.txt" );
  list2file( file_name, rts );
  self.triggerable_list = triggerable_list;
  self.maskable_list    = maskable_list;
  cmd_thread_unlock(self);
  return rts;


def erase_old_sump_ram_files( self ):
  log( self, ["erase_old_sump_ram_files()"] );
  file_path = self.vars["sump_path_ram"];
  import glob, os;

  file_header = "*";
  file_name = file_header+"*.txt";
  file_name = os.path.join( file_path, file_name );

  # Delete any existing *.txt files in sump_ram directory
  file_list = glob.glob( file_name );
  for each in file_list:
    log( self,["Removing %s" % each]);
    try:
      os.remove( each );
    except:
      log( self,["ERROR: Unable to delete %s" % each]);
  return;

#def generate_view_rom_files( self ):
def generate_view_rom_files( self, view_rom_list ):
  log( self, ["generate_view_rom_files()"] );
  file_path = self.vars["sump_path_ram"];
  view_name = None;
  view_list = [];
  import glob, os;

  file_header = "rom_";
  file_name = file_header+"*.txt";
  file_name = os.path.join( file_path, file_name );

  # Delete any existing sump_view_rom*.txt files in sump_ram directory
  file_list = glob.glob( file_name );
  for each in file_list:
    log( self,["Removing %s" % each]);
    try:
      os.remove( each );
    except:
      log( self,["ERROR: Unable to delete %s" % each]);

  view_i = 0;
  m = len( view_rom_list );
  for (i,each) in enumerate( view_rom_list ):
    view_list += [ each ];
    words = each.strip().split() + [None] * 8; # Avoid IndexError
    if words[0] == "create_view":
      view_name = words[1];
      view_list = [ each ];
      view_i += 1;
      file_name = file_header + view_name + ".txt";
      perc = int( (100 * i) / m );# Percentage done based on line number
      self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+ \
        " %d%% Creating View %d %s %s." % (perc, view_i,view_name,file_name));
      self.pygame.event.pump();
    if words[0] == "end_view":
      view_list += [ "add_view" ];
      log( self,["Creating %s %s" % ( view_name, file_name ) ]);
      if "*" not in file_name:
        file_name = os.path.join( file_path, file_name );
        list2file( file_name, view_list );
        view_list = [];
        # Update the GUI List
        ( null , file_no_path ) = os.path.split( file_name );
        cmd_add_view_ontap(self, ["add_view_ontap", file_no_path, "defer_gui_update" ] ); 
      else:
        log( self,["ERROR-8675309 : Invalid file_name %s" % ( file_name ) ]);
  create_view_selections( self );# Ugly putting this here
  return;


########################################################
# Download RLE Pod List to a file       
# The podlist maps the physical mosi/miso wire instances
# to long names using 2 words.
#  ---- Hub instance 0-255
# |  -- Pod instance 0-255
# | |
# | |     Name       Name
# 0,0 0.0.clk_80.0.0.u0_pod
# 0,1 0.0.clk_80.1.0.u1_pod
# 1,0 1.0.clk_100.0.0.u2_pod
#
# Note the "0." before each name is for multiple instances
# of the same pod with the same name. When implemented, 
# this would eventually allow a single View ROM to be 
# used for multiple instances of a pod that has all the
# same signal names, just
def generate_rlepodlist_file( self, file_name, pod_list ):
  log( self,["generate_rlepodlist_file()"]);
  from os import path;
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  file_name = os.path.join( file_path, file_name );

  # 2D array of Hubs and Pods
  txt = [];
  for (i,each_pod_list) in enumerate( pod_list ):
      for (j,each_pod) in enumerate( each_pod_list ):
        txt += [ "%d,%d %s" % ( i,j,each_pod) ];
  list2file( file_name, txt );
  return;


########################################################
# Arm the sump engine and sit in a polling loop until
# trigger happens and data is ready to be downloaded
def cmd_sump_acquire( self ):
  log( self, ["sump_acquire()"] );
  if self.sump_connected:
    self.mode_acquire = True;
    cmd_sump_arm(self);
  else:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
  return;


########################################################
# Force sump engine to idle state
def cmd_sump_idle( self ):
  log( self, ["sump_idle()"] );
  if self.sump_connected:
    self.sump.wr( self.sump.cmd_state_idle, 0x00000000 );
  else:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
  return;


########################################################
# Force sump engine to reset state
def cmd_sump_reset( self ):
  log( self, ["sump_reset()"] );
  if self.sump_connected:
    self.sump.wr( self.sump.cmd_state_reset, 0x00000000 );
  else:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
  return;

########################################################
# Force sump engine to sleep ( clock gating of sump_is_awake )
def cmd_sump_sleep( self ):
  log( self, ["sump_sleep()"] );
  if self.sump_connected:
    self.sump.wr( self.sump.cmd_state_sleep, 0x00000000 );
  else:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
  return;

########################################################
# Load the user_addr register and read the user_stat
def cmd_sump_user_read( self, words ):
  log( self, ["sump_user_read()"] );
  addr = int(words[1],16);
  if not self.sump_connected:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
    return;

  cmd_thread_lock(self);
  self.sump.wr( self.sump.cmd_wr_rle_hub_user_addr, addr );
  # Only one RLE Hub should have non-zero data
  data = 0x00000000;
  rle_hub_cnt   = self.sump.rd( self.sump.cmd_rd_rle_hub_config)[0];
  print("RLE Hub Count is %d" % rle_hub_cnt );
  for i in range(0,rle_hub_cnt):
    self.sump.wr( self.sump.cmd_wr_rle_pod_inst_addr, (i << 16) );
    hub_data = self.sump.rd( self.sump.cmd_rd_rle_hub_user_rd_d )[0];
    if hub_data != 0x00000000:
      data = hub_data;
  txt_rts = [ "%08x" % data ];
  cmd_thread_unlock(self);
  return txt_rts;
  

########################################################
# Load the user_addr register and write the user_stim 
def cmd_sump_user_write( self, words ):
  log( self, ["sump_user_write()"] );
  if not self.sump_connected:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
    return;

  cmd_thread_lock(self);
  addr = int(words[1],16);
  data_list = [ int( each,16) for each in filter(None,words[2:]) ];
  for each in data_list:
    self.sump.wr( self.sump.cmd_wr_rle_hub_user_addr, addr );
    self.sump.wr( self.sump.cmd_wr_rle_hub_user_wr_d, each );
    addr += 4;
  cmd_thread_unlock(self);
  return;


########################################################
# Up to 32 software threads may access Sump3 hardware 
# Thread IDs are either statically or dynamically 
# assigned. If sump_thread_id in ini file is 00000000
# then assignment is dynamic. This function will 
# contact the hardware and find out what thread IDs are
# already taken (1) and grab lowest ID that is free (0)
# and set that bit from 0->1 which requests that ID.
#
# WARNING : Reading cmd_wr_thread_pool sets a JK that
# will then report all threads are taken until a Write
# to cmd_wr_thread_pool. This prevents a 2nd software
# process from getting the same thread ID. Trust me.
def cmd_thread_pool_request_id( self ):
  thread_lock_en = int( self.vars["sump_thread_lock_en"], 10 );
  thread_id      = int( self.vars["sump_thread_id"], 16 );

  # loop until no other thread is using the hardware and bus_busy_timer isn't busy
  if thread_lock_en == 1:
    busy_bit = 1;
    lock_bit = 1;
    # Loop until the HW is free and remember the ctrl_status of Sump HW going in
    while busy_bit == 1 or lock_bit == 1:
      ctrl_status = self.sump.rd_ctrl();
      busy_bit = ( ctrl_status & 0x80000000 ) >> 31;
      lock_bit = ( ctrl_status & 0x40000000 ) >> 30;
      log( self, ["cmd_thread_pool_request_id() ctrl_status == %08x" % ctrl_status ] );
      pygame.time.wait( 100 );# time in mS. 

    # If we already have a thread_id, surrender it now.
    if self.thread_id != None:
      self.sump.wr( self.sump.cmd_wr_thread_pool_clear, self.thread_id );
      log( self, ["cmd_thread_pool_request_id() : Surrendering thread_id  %08x" % self.thread_id ] );

    # Locate a free ID from the pool of IDs, unless there is a static assigned one
    free_thread_id = False; 
    if thread_id == 0x00000000:
      while free_thread_id == False:
        # Request a list of all in use thread_id's
        in_use_thread_id = self.sump.rd( self.sump.cmd_wr_thread_pool_set )[0];
        log( self, ["cmd_thread_pool_request_id() : thread_id in use %08x" % in_use_thread_id ] );
        if in_use_thread_id != 0xFFFFFFFF:
          for i in range(0,32):
            bit = 2**i;# 1,2,4,8, etc
            # Find the lowest free thread_id
#           print("%08x %08x" % ( bit, in_use_thread_id ) );
            if ( in_use_thread_id & bit ) == 0x00000000:
              free_thread_id = bit;
              break;
        else:
          log( self, ["cmd_thread_pool_request_id() : ERROR zero thread_id available!!"]);
          pygame.time.wait( 100 );# time in mS. 
    else:
      free_thread_id = thread_id;# Use the static assigned thread ID

    # Reserve the ID for this application
    if free_thread_id != False:
      self.sump.wr( self.sump.cmd_wr_thread_pool_set, free_thread_id );
      log( self, ["cmd_thread_pool_request_id() : Acquired thread_id  %08x" % free_thread_id ] );
      self.thread_id = free_thread_id;

    self.sump.wr_ctrl( ctrl_status );# Put that Sump3 HW ctrl state back
  return;


def cmd_thread_pool_surrender_id( self ):
  thread_lock_en = int( self.vars["sump_thread_lock_en"], 10 );

  # loop until no other thread is using the hardware and bus_busy_timer isn't busy
  if thread_lock_en == 1:
    busy_bit = 1;
    lock_bit = 1;
    # Loop until the HW is free and remember the ctrl_status of Sump HW going in
    while busy_bit == 1 or lock_bit == 1:
      ctrl_status = self.sump.rd_ctrl();
      busy_bit = ( ctrl_status & 0x80000000 ) >> 31;
      lock_bit = ( ctrl_status & 0x40000000 ) >> 30;
      log( self, ["cmd_thread_pool_surrender_id() ctrl_status == %08x" % ctrl_status ] );
      pygame.time.wait( 100 );# time in mS. 

    if self.thread_id != None:
      self.sump.wr( self.sump.cmd_wr_thread_pool_clear, self.thread_id );
      log( self, ["cmd_thread_pool_request_id() : Surrendering thread_id  %08x" % self.thread_id ] );

    self.sump.wr_ctrl( ctrl_status );# Put that Sump3 HW ctrl state back
  return;

########################################################
# Up to 32 software threads may access Sump3 hardware
# using a shared thread locking register in sump3_core.v
def cmd_thread_lock( self ):
# return;
  thread_lock_en = int( self.vars["sump_thread_lock_en"], 10 );
  if thread_lock_en == 1 and self.thread_id != None:
#   thread_id = int( self.vars["sump_thread_id"], 16 );
    thread_id = self.thread_id;
    ctrl_status = self.sump.rd_ctrl();# Remember the ctrl state of Sump3 HW

    # Clear our own Thread ID in case we crashed
    self.sump.wr( self.sump.cmd_wr_thread_lock_clear, thread_id );

    # Now loop until no other thread is using the hardware
    got_lock = False;
    while got_lock == False:
      thread_lock_status = self.sump.rd( self.sump.cmd_wr_thread_lock_set )[0];
      if thread_lock_status != 0x00000000:
        log( self, ["cmd_thread_lock() : %08x" % thread_lock_status ] );
        pygame.time.wait( 100 );# time in mS. 
      else:
        self.sump.wr( self.sump.cmd_wr_thread_lock_set, thread_id );
        thread_lock_status = self.sump.rd( self.sump.cmd_wr_thread_lock_set )[0];
        if thread_lock_status == thread_id:  
          got_lock = True;
        else:
          self.sump.wr( self.sump.cmd_wr_thread_lock_clear, thread_id );
          a = self.sump.rd( self.sump.cmd_wr_thread_lock_set )[0];
          log( self, ["cmd_thread_lock() : %08x %08x" % ( thread_lock_status, a ) ] );
    self.sump.wr_ctrl( ctrl_status );# Put that Sump3 HW ctrl state back
    log( self, ["cmd_thread_lock() : Locked to sump_thread_id %08x" % ( thread_lock_status ) ] );
  return;

def cmd_thread_unlock( self ):
# return;
  thread_lock_en = int( self.vars["sump_thread_lock_en"], 10 );
  if thread_lock_en == 1 and self.thread_id != None:
    ctrl_status = self.sump.rd_ctrl();# Remember the ctrl state of Sump3 HW
    self.sump.wr( self.sump.cmd_wr_thread_lock_clear, self.thread_id );
    self.sump.wr_ctrl( ctrl_status );# Put that Sump3 HW ctrl state back
    log( self, ["cmd_thread_unlock()"] );
  return;

########################################################
# Arm the sump engine to acquire data with specified trigger
def cmd_sump_arm( self ):
  log( self, ["sump_arm()"] );
  if not self.sump_connected:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
    return;

  cmd_thread_lock(self);

  hub_pod_user_ctrl_dword_hash = generate_pod_user_ctrl_list( self );
# sort_pod_user_ctrl_list( self );

  # Get the hardware configuration 
  found_sump3_hw = sump_read_config(self );
  if not found_sump3_hw:
    txt = "cmd_sump_arm(): ERROR: Sump3 HW Communication";
    log( self, [ txt ] );
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" "+txt);
    return;

  # Support changing sump hard on the fly.
  sump_uut_addr = int( self.vars["sump_uut_addr"   ],16 );
  self.sump.addr_ctrl = sump_uut_addr;
  self.sump.addr_data = sump_uut_addr + 0x4;
  log( self, ["sump_uut_addr = %08x" % sump_uut_addr] );

  trig_type     =        self.vars["sump_trigger_type"  ];
  trig_field    = int(   self.vars["sump_trigger_field" ],16 );
  trig_delay    = float( self.vars["sump_trigger_delay" ]    );# delay in float uS
  trig_nth      = int(   self.vars["sump_trigger_nth"   ],10 );
  user_ctrl     = int(   self.vars["sump_user_ctrl"     ],16 );
# user_stim     = int(   self.vars["sump_user_stim"     ],16 );
  tick_divisor  = int(   self.vars["sump_ls_clock_div"  ],10 );
  trig_loc      = float( self.vars["sump_trigger_location" ] );# Float percentage 
  trig_ana_lvl  = float( self.vars["sump_trigger_analog_level"] );


  print("Arming with tick_divisor of %d" % ( tick_divisor ) );
#   self.cfg_dict['dig_hs_enable'] = 0;

  if self.sump.cfg_dict['ana_ls_enable'] == 1:
    ana_ram_depth    = self.sump.cfg_dict['ana_ram_depth'];
    ana_rec_profile  = self.sump.cfg_dict['ana_record_profile'];
    record_len       = ( ana_rec_profile & 0xFF000000 ) >> 24;
    ana_sample_depth = int( ana_ram_depth / record_len );
  else:
    ana_ram_depth    = 0;
    ana_rec_profile  = 0;
    record_len       = 0;
    ana_sample_depth = 0;

  if self.sump.cfg_dict['dig_hs_enable'] == 1:
    dig_sample_depth = self.sump.cfg_dict['dig_ram_depth'];
  else:
    dig_sample_depth = 0;

  # Note the inversion trig_loc gets converted to post_trigger samples
  if (   trig_loc < 25.0 ):
    ana_post_trig = int( ana_sample_depth *15/16 );# 0%
    dig_post_trig = int( dig_sample_depth *15/16 );
    rle_pod_trig  = self.sump.rle_pod_trig_position_10;
  elif ( trig_loc < 50.0 ):
    ana_post_trig = int( ana_sample_depth *3/4 );# 25%
    dig_post_trig = int( dig_sample_depth *3/4 );
    rle_pod_trig  = self.sump.rle_pod_trig_position_25;
  elif ( trig_loc < 75.0 ):
    ana_post_trig = int( ana_sample_depth / 2  );# 50%
    dig_post_trig = int( dig_sample_depth / 2  );
    rle_pod_trig  = self.sump.rle_pod_trig_position_50;
  elif ( trig_loc < 100.0 ):
    ana_post_trig = int( ana_sample_depth / 4  );# 75%
    dig_post_trig = int( dig_sample_depth / 4  );
    rle_pod_trig  = self.sump.rle_pod_trig_position_75;
  else:
    ana_post_trig = int( ana_sample_depth / 16 );# 100%
    dig_post_trig = int( dig_sample_depth / 16 );
    rle_pod_trig  = self.sump.rle_pod_trig_position_90;

  clk_ns = 1000.0 / float( self.vars["sump_hs_clock_freq"] );
  trig_delay = int( 1000.0 * trig_delay / clk_ns );

  # Convert trigger ASCII into integers
  if ( trig_type == "or_rising" ):
    trig_type_int = self.sump.trig_or_ris;
    rle_pod_trig  += self.sump.rle_pod_trig_or_rising;
  elif ( trig_type == "or_falling" ):
    trig_type_int = self.sump.trig_or_fal;
    rle_pod_trig  += self.sump.rle_pod_trig_or_falling;
  elif ( trig_type == "and_rising" ):
    trig_type_int = self.sump.trig_and_ris;
    rle_pod_trig  += self.sump.rle_pod_trig_and_rising;
  elif ( trig_type == "and_falling" ):
    trig_type_int = self.sump.trig_and_fal;
    rle_pod_trig  += self.sump.rle_pod_trig_and_falling;
  elif ( trig_type == "analog_rising" ):
    trig_type_int = self.sump.trig_analog_ris;
    rle_pod_trig  += self.sump.rle_pod_trig_disabled;
  elif ( trig_type == "analog_falling" ):
    trig_type_int = self.sump.trig_analog_fal;
    rle_pod_trig  += self.sump.rle_pod_trig_disabled;
  elif ( trig_type == "ext_in_rising" ):
    trig_type_int = self.sump.trig_in_ris;
    rle_pod_trig  += self.sump.rle_pod_trig_disabled;
  elif ( trig_type == "ext_in_falling" ):
    trig_type_int = self.sump.trig_in_fal;
    rle_pod_trig  += self.sump.rle_pod_trig_disabled;
  else:
    trig_type_int = 0;
    rle_pod_trig  += self.sump.rle_pod_trig_disabled;

  trig_ana_field = 0x00000000;# Analog CH + Comparator Value
  if ( trig_type == "analog_rising" or trig_type == "analog_falling" ):
    trig_ana_lvl = float( self.vars["sump_trigger_analog_level"] );
    for each_sig in self.signal_list:
#     print( each_sig.name );
      if each_sig.trigger and each_sig.units_per_code != None:
        # 2025.01.20
        trig_ana_lvl -= each_sig.offset_units;
        ch = decode_adc_ch_number( each_sig );
        trig_ana_field = ( ch << 24 ) + ( 0x00FFFFFF & int( trig_ana_lvl / each_sig.units_per_code ));
#       print("Oy %s is your trigger of source %s %d" % ( each_sig.name, each_sig.source, ch ) );
      #  trigger_adc_level   <= ctrl_25_reg[23:0];
      #  trigger_adc_ch      <= ctrl_25_reg[31:24];

  self.sump.wr( self.sump.cmd_wr_trig_analog_field,  trig_ana_field );
  self.sump.wr( self.sump.cmd_wr_trig_type,          trig_type_int );
  self.sump.wr( self.sump.cmd_wr_trig_digital_field, trig_field    );
  self.sump.wr( self.sump.cmd_wr_trig_delay,         trig_delay    );
  self.sump.wr( self.sump.cmd_wr_trig_nth,           trig_nth      );
  self.sump.wr( self.sump.cmd_wr_user_ctrl,          user_ctrl     );
# self.sump.wr( self.sump.cmd_wr_user_stim,          user_stim     );
  self.sump.wr( self.sump.cmd_wr_tick_divisor,       tick_divisor  );
  self.sump.wr( self.sump.cmd_wr_ana_post_trig_len,  ana_post_trig );
  self.sump.wr( self.sump.cmd_wr_dig_post_trig_len,  dig_post_trig );

  log( self, ["trig_ana_field = %08x" % trig_ana_field ] );
  log( self, ["trig_type      = %08x" % trig_type_int  ] );
  log( self, ["trig_field     = %08x" % trig_field     ] );
  log( self, ["trig_delay     = %08x" % trig_delay     ] );
  log( self, ["trig_nth       = %08x" % trig_nth       ] );
  log( self, ["user_ctrl      = %08x" % user_ctrl      ] );
# log( self, ["user_stim      = %08x" % user_stim      ] );
  log( self, ["tick_divisor   = %08x" % tick_divisor   ] );
  log( self, ["ana_post_trig  = %08x" % ana_post_trig  ] );
  log( self, ["dig_post_trig  = %08x" % dig_post_trig  ] );


#   self.rle_pod_addr_pod_user_ctrl   = 0x0B;# Ext user control bits           
#   self.rle_pod_addr_pod_user_stim   = 0x0C;# Ext user stimulus bits           
  log( self, ["Processing RLE user_ctrl"] );
  for (hub,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    for (pod,each_pod) in enumerate( each_pod_list ):
      reg = self.sump.rle_pod_addr_pod_user_ctrl;
      pod_user_ctrl = hub_pod_user_ctrl_dword_hash[(hub,pod)];
      self.sump.wr( self.sump.cmd_wr_rle_pod_inst_addr, ((hub<<16)+(pod<<8)+(reg<<0)) );
      self.sump.wr( self.sump.cmd_wr_rle_pod_data, pod_user_ctrl );
#     log( self, ["  RLE Hub-%d, Pod-%d : user_ctrl=%08x" % \
#       (hub,pod,pod_user_ctrl)] );

  log( self, ["Processing RLE Mask Bits"] );
  rle_mask_hash = proc_rle_mask(self, self.sump.rle_hub_pod_list );
  for (hub,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    for (pod,each_pod) in enumerate( each_pod_list ):
#     (bit_mask,bulk_mask) = rle_mask_hash[(hub,pod)];
      (bit_mask          ) = rle_mask_hash[(hub,pod)];
      reg = self.sump.rle_pod_addr_rle_bit_mask;# RLE Bit Mask bits 0-31              
      self.sump.wr( self.sump.cmd_wr_rle_pod_inst_addr, ((hub<<16)+(pod<<8)+(reg<<0)) );
      self.sump.wr( self.sump.cmd_wr_rle_pod_data, bit_mask  );

#     reg = self.sump.rle_pod_addr_rle_bulk_mask;# RLE Bulk Mask bits 0-31              
#     self.sump.wr( self.sump.cmd_wr_rle_pod_inst_addr, ((hub<<16)+(pod<<8)+(reg<<0)) );
#     self.sump.wr( self.sump.cmd_wr_rle_pod_data, bulk_mask );
#     log( self, ["  RLE Hub-%d, Pod-%d : Bit Mask=%08x Bulk Mask=%08x" % \
#       (hub,pod,bit_mask,bulk_mask)] );

  log( self, ["Processing RLE Triggers"] );
  for (hub,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    self.sump.wr( self.sump.cmd_wr_rle_pod_inst_addr, (hub << 16) );
    self.sump.wr( self.sump.cmd_wr_rle_pod_trigger_width, 0x3 );# Fix 4 clocks wide

    for (pod,each_pod) in enumerate( each_pod_list ):
      reg  = self.sump.rle_pod_addr_trigger_cfg;
      trig_type = rle_pod_trig;# Packed Type and Position    
      self.sump.wr( self.sump.cmd_wr_rle_pod_inst_addr, ((hub<<16)+(pod<<8)+(reg<<0)) );
      self.sump.wr( self.sump.cmd_wr_rle_pod_data, trig_type );
    
      try:
        trig_field = int(self.vars["sump_rle_hub_%d_pod_%d_trigger_field" % (hub,pod) ],16);
      except:
        trig_field = 0x00000000;
      reg  = self.sump.rle_pod_addr_trigger_en;
      self.sump.wr( self.sump.cmd_wr_rle_pod_inst_addr, ((hub<<16)+(pod<<8)+(reg<<0)) );
      self.sump.wr( self.sump.cmd_wr_rle_pod_data, trig_field );
#     log( self, ["  RLE Hub-%d, Pod-%d : Trigger Field=%08x" % \
#       (hub,pod,trig_field)] );

  self.sump.wr( self.sump.cmd_state_reset, 0x00000000 );
  self.sump.wr( self.sump.cmd_state_init,  0x00000000 );# Initialize Sump RAM
  pygame.time.wait(250);# time in mS. 
  self.sump.wr( self.sump.cmd_state_idle,  0x00000000 );# Initialize Sump RAM
  self.sump.rd_status();
  ( stat_str, status ) = self.sump.status;
  print( stat_str );

  self.sump.wr( self.sump.cmd_state_arm,   0x00000000 );
  pygame.time.wait(100);# time in mS. 
  self.sump.rd_status();
  ( stat_str, status ) = self.sump.status;
  print( stat_str );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" HW Status: "+stat_str);
  cmd_thread_unlock(self);
  return;

#  Decode the analog ch number from the source attribute
def decode_adc_ch_number( each_sig ):
  rts = 0;
  if each_sig.type == "analog":
    a = each_sig.source;
    a = a.replace("["," [ ");
    a = a.replace("]"," ] ");
    words = " ".join(a.split()).split(' ') + [None] * 5;
    if ( words[1] == "[" and words[3] == "]" ) : 
      rts = int( words[2],10 );
  return rts;

# OLD vvvv
# RLE Pods have individual mask bits for signals 0-31. For signals
# above 32, there are 32 bulk mask bits which are divided evenly.
# Instead of calculating the bulk mask bits, masking of any signal
# in that region will mask ALL the signals in that region. This is
# to keep the initial software simple.
# OLD ^^^^

# RLE Pods have individual mask bits for signals 0-31 only.       
def proc_rle_mask( self, rle_hub_pod_list ):
  rle_mask_hash = {};
  for (hub,each_pod_list) in enumerate( rle_hub_pod_list ):
    for (pod,each_pod) in enumerate( each_pod_list ):
      bit_mask  = 0x00000000;
#     bulk_mask = 0x00000000;
      # signal.source = "digital_rle[0][1][3:0]"
      for each_sig in self.signal_list:
        if each_sig.source == None:
          pass;# Probably a group
        elif each_sig.rle_masked and "digital_rle" in each_sig.source:
          a = each_sig.source;
          a = a.replace("["," [ ");
          a = a.replace("]"," ] ");
          a = a.replace(":"," : ");
          #           0      1 2 3 4 5 6 7 8 9 10 11
          # a = "digital_rle [ 0 ] [ 1 ] [ 3 : 0 ]"
          words = " ".join(a.split()).split(' ') + [None] * 5;
          hub_i = int( words[2],10 );
          pod_i = int( words[5],10 );
          if words[9] == ":":
            bit_top = int( words[8],10 );
            bit_bot = int( words[10],10 );
          else:
            bit_top = int( words[8],10 );
            bit_bot = bit_top;
          if ( hub == hub_i and pod == pod_i ):
            for i in range( bit_bot, bit_top+1 ):
#             if i >= 32:
#               bulk_mask = 0xFFFFFFFF;
#             else:
#               bit_mask = bit_mask | ( 2**i );
              if i < 32:
                bit_mask = bit_mask | ( 2**i );
#           print("Masked : %s %s %s %s %s %s %08x %08x" % \
#            ( each_sig.name, each_sig.source,\
#            hub_i,pod_i,bit_top,bit_bot,bit_mask,bulk_mask) );

            # If bulk_mask is non-zero we have to delete and set rle_masked
            # for all signals in the bulk mask region. This is a short term
            # solution until I figure out how to use bulk mask bits with
            # granularity
#           if bulk_mask == 0xFFFFFFFF:
#             for my_sig in self.signal_list:
#               if my_sig.source != None and "digital_rle" in my_sig.source:
#                 a = my_sig.source;
#                 a = a.replace("["," [ ");
#                 a = a.replace("]"," ] ");
#                 a = a.replace(":"," : ");
#                 #           0      1 2 3 4 5 6 7 8 9 10 11
#                 # a = "digital_rle [ 0 ] [ 1 ] [ 3 : 0 ]"
#                 words = " ".join(a.split()).split(' ') + [None] * 5;
#                 hub_i = int( words[2],10 );
#                 pod_i = int( words[5],10 );
#                 if words[9] == ":":
#                   bit_top = int( words[8],10 );
#                   bit_bot = int( words[10],10 );
#                 else:
#                   bit_top = int( words[8],10 );
#                   bit_bot = bit_top;
#                 if ( hub == hub_i and pod == pod_i ):
#                   if bit_top >= 32 or bit_bot >= 32:
#                     if not my_sig.rle_masked:
#                       my_sig.visible = False;
#                       my_sig.rle_masked = True;
#                       print("Bulk Mask removal of : %s %s" % \
#                         ( each_sig.name, each_sig.source ));
#       
#     rle_mask_hash[(hub,pod)] = ( bit_mask, bulk_mask );
      rle_mask_hash[(hub,pod)] = ( bit_mask );
  return rle_mask_hash;



########################################################
# given the selected signals, create the 32bit sump trigger field
def cmd_sump_set_trigs( self, words ):
  rts = [];
  trig_names = "";

  for each_sig in self.signal_list:
#   print("1: " + each_sig.name );
    if ( each_sig.name == words[1] or words[1] == "*" or each_sig.selected ):
#     print("2: " + each_sig.name );
      # If the selected signal is analog, clear all existing triggers
      # since there is only a single analog comparator trigger
      if "analog" in each_sig.source:
        cmd_sump_clear_trigs(self,["",""]);

      # Assign the trigger attribute if the selected signal is triggerable
      if each_sig.triggerable:
        if not each_sig.trigger:
          each_sig.trigger = True;
          each_sig.selected = False;# Deselect so it will turn red
        else:
          each_sig.trigger = False; # Toggle off if already trigger
          each_sig.selected = False;# Deselect so it will turn green
      else:
        rts +=["ERROR: %s is not triggerable" % each_sig.name];
      trig_names += each_sig.name + " ";
  log( self, ["sump_set_trigs( %s )" % trig_names ] );

  # Iterate looking for plain LS digital triggers
  trig_field = 0x00000000;
  for each_sig in self.signal_list:
    if each_sig.trigger and "digital_rle" not in each_sig.source:
      trig_field = trig_field | each_sig.trigger_field;
  self.vars["sump_trigger_field" ] = "%08x" % trig_field;
  rts += [ "sump_trigger_field = %08x" % trig_field ];

  # Now iterate looking for rle_pod triggers which are more complicated
  for each_sig in self.signal_list:
    if each_sig.trigger and "digital_rle" in each_sig.source:
      for (hub,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
        for (pod,each_pod) in enumerate( each_pod_list ):
          total_bits = 32;
          for i in range( 0, total_bits ):
            source_rle = "digital_rle[%d][%d][%d]" % (hub,pod,i);
            if each_sig.source == source_rle:
              print("Assigning %s as Trigger for Hub-%d,Pod-%d %s" % \
                ( each_sig.name,hub,pod,each_pod ) );
              try:
                trig_field = int(self.vars["sump_rle_hub_%d_pod_%d_trigger_field" % (hub,pod) ],16);
              except:
                trig_field = 0x00000000;
              trig_field = trig_field | 2**i;
              self.vars["sump_rle_hub_%d_pod_%d_trigger_field" % (hub,pod) ] = "%08x" % trig_field;
              rts +=   ["sump_rle_hub_%d_pod_%d_trigger_field = %08x" % ( hub,pod,trig_field )];
  sump_trigger_count = sum(bool(each.trigger) for each in self.signal_list);      
  self.vars["sump_trigger_count"] =  "%d" % sump_trigger_count;
  self.refresh_sig_names = True;
  return rts;


########################################################
# clear all triggers
#def cmd_sump_clr_trigs( self, words ):
def cmd_sump_clear_trigs( self, words ):
# log( self, ["sump_clr_trigs()"] );
  log( self, ["sump_clear_trigs()"] );
  rts = [];
  trig_field = 0x00000000;
  for each_sig in self.signal_list:
    if each_sig.trigger:
      each_sig.trigger = False;
  self.vars[ "sump_trigger_field" ] = "%08x" % trig_field;
  rts +=   [ "sump_trigger_field = %08x" % trig_field ];
  for (hub,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    for (pod,each_pod) in enumerate( each_pod_list ):
      trig_field = 0x00000000;
      self.vars["sump_rle_hub_%d_pod_%d_trigger_field" % (hub,pod) ] = "%08x" % trig_field;

  sump_trigger_count = sum(bool(each.trigger) for each in self.signal_list);      
  self.vars["sump_trigger_count"] =  "%d" % sump_trigger_count;
  self.refresh_sig_names = True;
  return;


########################################################
# Query status of sump hardware
def cmd_sump_query( self ):
  log( self, ["sump_query()"] );
  rts = [];
  if not self.sump_connected:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
  else:
    self.sump.rd_status();# Old status required ctrl in arm state
    ( stat_str, status ) = self.sump.status;
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" HW Status: "+stat_str);
    rts = [stat_str];
  return rts;


########################################################
# Download sump capture data to RAM text files
def cmd_sump_download( self ):
  log( self, ["sump_download()"] );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Downloading...");
  self.pygame.event.pump();
  start_time = self.pygame.time.get_ticks();
  if not self.sump_connected:
    txt = "ERROR-1977: Sump HW not connected";
    log( self, [ txt ]);
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright + " "+txt );
    return;
  else:
    cmd_thread_lock(self);
    self.sump.rd_status();
    ( stat_str, status ) = self.sump.status;
#   while( stat_str != "acquired" ):
#     log( self, ["Waiting for acquisition to finish : %s" % stat_str ] );
#     self.sump.rd_status();
#     ( stat_str, status ) = self.sump.status;
#     pygame.time.wait( 1000 );# time in mS. 
    self.sump.wr( self.sump.cmd_state_idle, 0x00000000 );
    self.status_downloading = True;

    # Get the hardware configuration that captured the data
    found_sump3_hw = sump_read_config(self );
    if not found_sump3_hw:
      txt = "cmd_sump_download(): ERROR: Sump3 HW Communication";
      self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" "+txt);
      log( self, [ txt ] );
      return;

    capture_cfg_list = [];
    for key in self.sump.cfg_dict:
      value = self.sump.cfg_dict[key];
      capture_cfg_list += ["%s = %s" % ( key, value ) ];

    from os import path;
    file_path = os.path.abspath( self.vars["sump_path_ram"] );

    # Delete any old files
    for each in ["sump_ls_ram.txt","sump_hs_ram.txt","sump_rle_ram.txt",
      "sump_ls_samples.txt","sump_hs_samples.txt","sump_rle_samples.txt" ]:
      file_name = os.path.join( file_path, each );
      if os.path.exists( file_name ):
        log( self, ["Deleting old %s" % file_name ]);
        os.remove( file_name );

    file_name = "sump_capture_cfg.txt";
    file_name = os.path.join( file_path, file_name );
    list2file( file_name, capture_cfg_list ); 
    
    disable_ls  = int( self.vars["sump_download_disable_ls"], 10 );
    disable_hs  = int( self.vars["sump_download_disable_hs"], 10 );
    disable_rle = int( self.vars["sump_download_disable_rle"], 10 );
    dl_ondemand = int( self.vars["sump_download_ondemand"], 10 );

    if self.sump.cfg_dict['ana_ls_enable'] == 0:
      disable_ls = 1;
    if self.sump.cfg_dict['dig_hs_enable'] == 0:
      disable_hs = 1;
    if self.sump.cfg_dict['rle_hub_num'] == 0:
      disable_rle = 1;

    # Dump RAM contents to hex dwords files
    if disable_ls == 0:
      log( self, ["Downloading LS RAM"]);
      self.pygame.display.set_caption(\
        self.name+" "+self.vers+" "+self.copyright+" Downloading LS Samples...");
      sump_ram2file( self, "analog",  "sump_ls_ram.txt");

    if disable_hs == 0:
      log( self, ["Downloading HS RAM"]);
      self.pygame.display.set_caption(\
        self.name+" "+self.vers+" "+self.copyright+" Downloading HS Samples...");
      sump_ram2file( self, "digital", "sump_hs_ram.txt");

    if disable_rle == 0:
      log( self, ["Downloading RLE RAM"]);
      self.pygame.display.set_caption(\
        self.name+" "+self.vers+" "+self.copyright+" Downloading RLE Samples...");
      sump_ram2file( self, "rle",     "sump_rle_ram.txt");

    self.sump.wr( self.sump.cmd_state_idle, 0x00000000 );

  # Extract the sample data from the raw hex dwords
# work_list = [("LS",  "sump_ls_ram.txt", "sump_ls_samples.txt"),
#              ("HS",  "sump_hs_ram.txt", "sump_hs_samples.txt"),
#              ("RLE", "sump_rle_ram.txt","sump_rle_samples.txt") ];
  work_list = [];
  if disable_ls == 0:
    work_list += [("LS",  "sump_ls_ram.txt", "sump_ls_samples.txt")];
  if disable_hs == 0:
    work_list += [("HS",  "sump_hs_ram.txt", "sump_hs_samples.txt")];
  if disable_rle == 0:
    work_list += [("RLE", "sump_rle_ram.txt","sump_rle_samples.txt")];

  for ( title, file_in, file_out ) in work_list:
    self.pygame.display.set_caption(\
      self.name+" "+self.vers+" "+self.copyright+" Calculating %s Samples..." % title );
    file_name = os.path.join( file_path, file_in );
    if os.path.exists( file_name ):
      if title == "LS":
        create_sump_digital_slow(self, file_in, file_out );
      elif title == "HS":
        create_sump_digital_fast(self, file_in, file_out );
      elif title == "RLE":
        create_sump_digital_rle(self,  file_in, file_out );

  # Emulate an on-demand RLE pod download. Iterate the list of pods
  # and download the specified pod if "[download_needed]" is found
  # instead of samples in the sump_rle_ram.txt file
  # once the operation is completed, call create_sump_digital_rle() to
  # create a new sump_rle_samples.txt file.
  #
  # This is all about plumbing the software for supporting the day when
  # dozens or hundreds of RLE pods exist and it is too slow to download
  # all at once and better to download only when a view is applied.
# filename = "sump_rle_ram.txt";
# from os import path;
# file_path = os.path.abspath( self.vars["sump_path_ram"] );
# filename  = os.path.join( file_path, filename );
# rle_ram_list = file2list( filename );
# rle_ram_updated = False;
# for (i,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
#   for (j,each_pod) in enumerate( each_pod_list ):
#     log( self,[ "RLE Hub,Pod List : %d,%d %s" % ( i,j,each_pod) ]);
#     new_rle_ram_list = sump_rlepod_download(self, hub_num=i, pod_num=j,
#                                              rle_ram_list=rle_ram_list );
#     if new_rle_ram_list != None:
#       rle_ram_list = new_rle_ram_list;
#       rle_ram_updated = True;

  # Generate a new rle_samples file if the rle_ram file changed
# if rle_ram_updated == True:
#   list2file( filename, rle_ram_list );
#   file_in  = "sump_rle_ram.txt";
#   file_out = "sump_rle_samples.txt";
#   log( self,[ "Changes to %s" % file_in ]);
#   log( self,[ "Updating %s" % file_out ]);
#   create_sump_digital_rle(self,  file_in, file_out );

  if dl_ondemand == 0:
    download_rle_ondemand_all(self);

# self.pygame.display.set_caption(\
#   self.name+" "+self.vers+" "+self.copyright+" Populating user signals..");
  populate_signal_values_from_samples( self );

  # Snap Zoom/Pan back to zero. TODO this REALLY doesn't belong here.
  for each_win in self.window_list:
    each_win.startup();

  self.status_downloading = False;
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright);
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  stop_time = self.pygame.time.get_ticks();
  delta_time = stop_time - start_time;
  log( self, ["sump_download() : Completed in %d mS.\n" % delta_time] );
  cmd_thread_unlock(self);
  return;

# create_drawing_lines() will check to see if a signal has no values
# and call this to download RLE samples ondemand
def download_rle_ondemand( self, rle_sig_source ):
# print("download_rle_ondemand( %s )" % rle_sig_source );
# start_time = self.pygame.time.get_ticks();
  if "digital_rle" in rle_sig_source:
    # "digital_rle[0][1][1:0]"
    source_name = rle_sig_source.replace("["," ");
    source_name = source_name.replace("]"," ");
    words_tmp = " ".join(source_name.split()).split(" ");
    hub = int( words_tmp[1] );
    pod = int( words_tmp[2] );
#   print("Downloading RLE HubPod (%d,%d)" % (hub,pod) );
    download_rle_ondemand_hubpod( self, hub, pod );
# stop_time = self.pygame.time.get_ticks();
# delta_time = stop_time - start_time;
# log( self, ["download_rle_ondemand() : Completed in %d mS.\n" % delta_time]);
  return;

def download_rle_ondemand_hubpod( self, hub, pod ):
  filename = "sump_rle_ram.txt";
  from os import path;
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  filename  = os.path.join( file_path, filename );
  if not os.path.exists( filename ):
    return;

  self.pygame.display.set_caption(\
    self.name+" "+self.vers+" "+self.copyright+" download_rle_ondemand_hubpod()..");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();

  rle_ram_list = file2list( filename );
  rle_ram_updated = False;
  new_rle_ram_list = sump_rlepod_download(self, hub_num=hub, pod_num=pod, rle_ram_list=rle_ram_list );
  if new_rle_ram_list != None:
    rle_ram_list = new_rle_ram_list;
    rle_ram_updated = True;

  # Generate a new rle_samples file if the rle_ram file changed
  if rle_ram_updated == True:
    list2file( filename, rle_ram_list );
    file_in  = "sump_rle_ram.txt";
    file_out = "sump_rle_samples.txt";
    log( self,[ "Changes to %s" % file_in ]);
    log( self,[ "Updating %s" % file_out ]);
    create_sump_digital_rle(self,  file_in, file_out );
    populate_signal_values_from_samples( self );

  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+"");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  return;

# Called by cmd_save_pza()
def download_rle_ondemand_all( self ):
  log( self,[ "download_rle_ondemand_all()"]);
  start_time = self.pygame.time.get_ticks();
  filename = "sump_rle_ram.txt";
  from os import path;
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  filename  = os.path.join( file_path, filename );
  rle_ram_list = file2list( filename );
  rle_ram_updated = False;
  spinner = "|";
  for (i,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    for (j,each_pod) in enumerate( each_pod_list ):
      log( self,[ "RLE Hub,Pod List : %d,%d %s" % ( i,j,each_pod) ]);
      txt = "(%d,%d) " % ( i,j );
      spinner = rotate_spinner( spinner );
      self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Downloading "+txt+spinner);
      self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
      self.pygame.event.pump();
      new_rle_ram_list = sump_rlepod_download(self, hub_num=i, pod_num=j,
                                               rle_ram_list=rle_ram_list );
      if new_rle_ram_list != None:
        rle_ram_list = new_rle_ram_list;
        rle_ram_updated = True;

  # Generate a new rle_samples file if the rle_ram file changed
  if rle_ram_updated == True:
    list2file( filename, rle_ram_list );
    file_in  = "sump_rle_ram.txt";
    file_out = "sump_rle_samples.txt";
    log( self,[ "Changes to %s" % file_in ]);
    log( self,[ "Updating %s" % file_out ]);
    create_sump_digital_rle(self,  file_in, file_out );

  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright);
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  populate_signal_values_from_samples( self );
  stop_time = self.pygame.time.get_ticks();
  delta_time = stop_time - start_time;
  log( self, ["download_rle_ondemand_all() : Completed in %d mS.\n" % delta_time]);
  return;


########################################################
# assign the sample values to the signals that point to them
# Note, this called:
#   1) from sump_download 
#   2) whenever a view is assigned
#   3) whenever a Pizza is loaded
def populate_signal_values_from_samples( self ):
  log( self,["populate_signal_values()"]);
  self.pygame.display.set_caption(\
    self.name+" "+self.vers+" "+self.copyright+" populate_signal_values_from_samples()...");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  f1 = "sump_ls_samples.txt";
  f2 = "sump_hs_samples.txt";
  f3 = "sump_rle_samples.txt";
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  fp1 = os.path.join( file_path, f1 );
  fp2 = os.path.join( file_path, f2 );
  fp3 = os.path.join( file_path, f3 );
# if ( os.path.exists( fp1 ) and os.path.exists( fp2 ) and os.path.exists( fp3 ) ):
  if True:
    create_signal_values_digital(self, f1, f2, f3 );
    inherit_sample_timing(self);
    identify_invalid_signals( self );
    self.refresh_waveforms = True;
  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright);
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  return;


########################################################
# Signals may have user_ctrl attributes that must match
# the acquisition user_ctrl settings. 
# If they don't, any samples are invalid so the hidden
# attribute is applied. Note that sample must still be
# visible as pre-acquisition you need to be able to 
# assigned a trigger to a signal even if it has no old
# values to display.
def identify_invalid_signals( self ):
  log( self,["identify_invalid_signals()"]);
  for each_sig in self.signal_list:
    if each_sig.source != None:
      if "digital_rle" not in each_sig.source:
        sump_user_ctrl = self.sump.cfg_dict["user_ctrl"];
        match_jk = True;
        for each_user_ctrl in each_sig.user_ctrl_list:
          (rip_str, hex_val) = each_user_ctrl;
          hex_int = int(hex_val,16);
          # Given "[7:4]" return ( 0x000000F0, 0xFFFFFF0F, 4 )
          (a,b,c) = gen_bit_rip( rip_str );
          sump_user_ctrl_masked = a & sump_user_ctrl;
          if ( sump_user_ctrl_masked != hex_int << c ):
            match_jk = False; # print("no match!");
        if not match_jk:
          each_sig.hidden  = True;
#         log( self,["Keeping invalid %s not hidden (just for now)" % each_sig.name]);
  return;


########################################################
# Make a list of the user_ctrl values for each pod
def generate_pod_user_ctrl_list( self ):
  log( self,["generate_pod_user_ctrl_list()"]);

  hub_pod_hash = {};
  for each_win in self.window_list:
    for each_view in each_win.view_list:
      for (hub,pod,user_ctrl_list) in each_view.rle_hub_pod_user_ctrl_list:
        if hub_pod_hash.get( (hub,pod) ) == None:
          hub_pod_hash[ (hub,pod) ] = user_ctrl_list;
        else:
          hub_pod_hash[ (hub,pod) ] += user_ctrl_list;
  for key in hub_pod_hash:
    # Cast to a set to remove redundant entries
    hub_pod_hash[key] = set( hub_pod_hash[key] );
    print("%s = %s" % ( key, hub_pod_hash[key] ) );

  # TODO: This section below could use some enhancements. Fancy stuff like ANDing
  # in only bits that aren't being specified. Currently it's just adding
  # which only works if there are no bit overlaps ( there shouldn't be ).  

  # Init all Pod user_ctrl's to 0x0 - even those not specified with a user_ctrl value
  hub_pod_user_ctrl_dword_hash = {};
  for (hub,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    for (pod,each_pod) in enumerate( each_pod_list ):
      hub_pod_user_ctrl_dword_hash[(hub,pod)] = 0x00000000;

  for (hub,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    for (pod,each_pod) in enumerate( each_pod_list ):
      if ( hub_pod_user_ctrl_dword_hash.get( (hub,pod) ) != None ):
        dword = hub_pod_user_ctrl_dword_hash[(hub,pod)];
        # New 2024.01.30
        if ( hub_pod_hash.get( (hub,pod) ) != None ):
          user_ctrl_list = hub_pod_hash[ (hub,pod) ];
          for ( bit_rip, bit_val ) in user_ctrl_list:
            bit_rip = bit_rip.replace("[","");
            bit_rip = bit_rip.replace("]","");
            if ":" in bit_rip:
              (bit_h,bit_l) = bit_rip.split(":");
            else:
              bit_l = bit_rip;# "[0]" instead of "[1:0]"
              bit_h = bit_l;
            bit_l = int(bit_l,10);
            bit_h = int(bit_h,10);
#           print("Oy %d:%d %s" % ( bit_h, bit_l, bit_val ));# ("[1:0]", "1");
            dword += int(bit_val,16) << bit_l;
        hub_pod_user_ctrl_dword_hash[(hub,pod)] = dword;

  return hub_pod_user_ctrl_dword_hash;


########################################################
# As soon as signals have samples, they also have sample timing info
# like sample_period and sample_unit
# those need to get inherited up to their parent views and windows
def inherit_sample_timing( self ):
  # Signal -> View
  for each_sig in self.signal_list:
    for each_view in self.view_applied_list:
      if each_view      == each_sig.view_obj:
#     if each_view.name == each_sig.view_name:
        if each_sig.sample_period != None:
          each_view.sample_period = each_sig.sample_period;
        if each_sig.sample_unit  != None:
          each_view.sample_unit  = each_sig.sample_unit;
        if each_sig.trigger_index != None:
          each_view.trigger_index = each_sig.trigger_index;
        if len(each_sig.values) != 0:
          each_view.samples_total = len(each_sig.values);
  # View -> Window
  for each_win in self.window_list:
    for each_view in each_win.view_list:
      if each_view.sample_period != None:
        each_win.sample_period = each_view.sample_period;
      if each_view.sample_unit  != None:
        each_win.sample_unit  = each_view.sample_unit;
      if each_view.trigger_index != None:
        each_win.trigger_index = each_view.trigger_index;
      if each_view.samples_total != None:
        each_win.samples_total = each_view.samples_total;
  return;

########################################################
# Read all of the capture parameters on a download. Doing this since it's possible 
# that some other software host armed sump and this instance is downloading.
# Unlikely, but safest to plan for it.
def sump_read_config( self ):
  log( self,["sump_read_config()"]);
  hwid_data       = self.sump.rd( self.sump.cmd_rd_hw_id_rev            )[0];
  ana_ram_data    = self.sump.rd( self.sump.cmd_rd_ana_ram_width_len    )[0];
  dig_ram_data    = self.sump.rd( self.sump.cmd_rd_dig_ram_width_len    )[0];
  dig_freq_data   = self.sump.rd( self.sump.cmd_rd_dig_ck_freq          )[0];
  tick_freq_data  = self.sump.rd( self.sump.cmd_rd_tick_freq            )[0];
  tick_divisor    = self.sump.rd( self.sump.cmd_wr_tick_divisor         )[0];
  ana_first_ptr   = self.sump.rd( self.sump.cmd_rd_ana_first_sample_ptr )[0];
  dig_first_ptr   = self.sump.rd( self.sump.cmd_rd_dig_first_sample_ptr )[0];
  ana_post_trig   = self.sump.rd( self.sump.cmd_wr_ana_post_trig_len    )[0];
  dig_post_trig   = self.sump.rd( self.sump.cmd_wr_dig_post_trig_len    )[0];
  user_ctrl       = self.sump.rd( self.sump.cmd_wr_user_ctrl            )[0];
# user_stim       = self.sump.rd( self.sump.cmd_wr_user_stim            )[0];
  ana_rec_config  = self.sump.rd( self.sump.cmd_wr_record_config        )[0];
  ana_rec_profile = self.sump.rd( self.sump.cmd_rd_record_profile       )[0];
  trig_type       = self.sump.rd( self.sump.cmd_wr_trig_type            )[0];
  trig_dig_field  = self.sump.rd( self.sump.cmd_wr_trig_digital_field   )[0];
  trig_ana_field  = self.sump.rd( self.sump.cmd_wr_trig_analog_field    )[0];
  trig_delay      = self.sump.rd( self.sump.cmd_wr_trig_delay           )[0];
  trig_nth        = self.sump.rd( self.sump.cmd_wr_trig_nth             )[0];
# rle_pod_cnt     = self.sump.rd( self.sump.cmd_rd_rle_hub_config       )[0];
  trig_src_core   = self.sump.rd( self.sump.cmd_rd_trigger_src          )[0];
  view_rom_kb     = self.sump.rd( self.sump.cmd_rd_view_rom_kb          )[0];

  # New 2023.11.14
  a = self.sump.cfg_dict;
  a['hw_id']                 = ( hwid_data & 0xFF000000 ) >> 24;
  a['hw_rev']                = ( hwid_data & 0x00FF0000 ) >> 16;
  a['rle_hub_num']           = ( hwid_data & 0x0000FF00 ) >> 8;
  a['bus_busy_bit_en']       = ( hwid_data & 0x00000010 ) >> 4;
  a['thread_lock_en']        = ( hwid_data & 0x00000008 ) >> 3;
  a['view_rom_en']           = ( hwid_data & 0x00000004 ) >> 2;
  a['ana_ls_enable']         = ( hwid_data & 0x00000002 ) >> 1;
  a['dig_hs_enable']         = ( hwid_data & 0x00000001 ) >> 0;

  if a['hw_id'] != self.sump.hw_id:
    return False;

# HACK
# a['ana_ls_enable']         = 0;
# a['dig_hs_enable']         = 0;
 
  if a['view_rom_en'] == 1:
    a['view_rom_kb']         = view_rom_kb;
  else:
    a['view_rom_kb']         = 0;

# a['hw_id']                 = ( hwid_data & 0xFF000000 ) >> 24;
# a['hw_rev']                = ( hwid_data & 0x00FF0000 ) >> 16;
  if a['ana_ls_enable'] == 1:
    a['ana_ram_depth']         = ( ana_ram_data  & 0x00FFFFFF ) >> 0;
    a['ana_ram_width']         = ( ana_ram_data  & 0xFF000000 ) >> 24;
    a['tick_freq']             =  float(tick_freq_data) / float( 0x00100000 );# MHz
    a['tick_divisor']          =  tick_divisor;
  else:
    a['ana_ram_depth']         = 0;
    a['ana_ram_width']         = 0;
    a['tick_freq']             = 0;
    a['tick_divisor']          = 0;

# print("Oy"); 
# print("tick_freq_data = %08x" % tick_freq_data );
# print("tick_freq      = %f" % a['tick_freq']    );

  if a['dig_hs_enable'] == 1:
    a['dig_ram_depth']         = ( dig_ram_data  & 0x00FFFFFF ) >> 0;
    a['dig_ram_width']         = ( dig_ram_data  & 0xFF000000 ) >> 24;
  else:
    a['dig_ram_depth']         = 0;
    a['dig_ram_width']         = 0;
  # Note that even when dig_hs_enable = 0, there is still a core dig_freq clock
  # as it is used for the main trigger and trigger delays, etc
  a['dig_freq']              =  float(dig_freq_data)  / float( 0x00100000 );# MHz 

# a['rle_pod_cnt']           = rle_pod_cnt;
# Note that existing hardware doesn't truncate unused MSB bits, so do it here.
  a['ana_first_sample_ptr']  =  ana_first_ptr & ((ana_ram_data & 0x00FFFFFF)-1);
  a['dig_first_sample_ptr']  =  dig_first_ptr & ((dig_ram_data & 0x00FFFFFF)-1);
  a['ana_post_trig_samples'] =  ana_post_trig;
  a['dig_post_trig_samples'] =  dig_post_trig;
  a['user_ctrl']             =  user_ctrl;
# a['user_stim']             =  user_stim;
  a['ana_record_config']     =  ana_rec_config;
  a['ana_record_profile']    =  ana_rec_profile;
  a['trig_type']             =  trig_type;
  a['trig_dig_field']        =  trig_dig_field;
  a['trig_ana_field']        =  trig_ana_field;
  a['trig_delay']            =  trig_delay;
  a['trig_nth']              =  trig_nth;
  a['trig_src_core']         =  trig_src_core;

  return True;

########################################################
# Download one of three RAM types to a file       
def sump_ram2file( self, ram_type, file_name ):
  log( self,["sump_ram2file()"]);
  from os import path;
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  file_name = os.path.join( file_path, file_name );

  if ram_type == "rle":
    time_sample_list = sump_rleram2file( self );
    list2file( file_name, time_sample_list );
#   hexlist2file( file_name, time_sample_list );
    return;

  if ram_type == "analog":
    record_profile = self.sump.rd( self.sump.cmd_rd_record_profile )[0];
    ram_depth  = self.sump.cfg_dict['ana_ram_depth'];
    ram_width  = self.sump.cfg_dict['ana_ram_width'];
    read_ptr   = self.sump.rd( self.sump.cmd_rd_ana_first_sample_ptr )[0];
    bank = 0x80;
    # Warning: the ana_first_sample_ptr is really the last sample +1.
    # For REALLY slow acquisitions, it's possible for the pre-trig not to be
    # filled and also possible for download to be forced before post-trig is full.
  elif ram_type == "digital":
    ram_depth  = self.sump.cfg_dict['dig_ram_depth'];
    ram_width  = self.sump.cfg_dict['dig_ram_width'];
    read_ptr   = self.sump.rd( self.sump.cmd_rd_dig_first_sample_ptr )[0];
    bank = 0x00;

  data_list = [];
  for i in range( 0, ram_width ):
    self.sump.wr( self.sump.cmd_wr_ram_rd_page, bank + i );
    self.sump.wr( self.sump.cmd_wr_ram_rd_ptr, read_ptr );
    data_list += [ self.sump.rd( self.sump.cmd_rd_ram_data, num_dwords=ram_depth )];

  # Note that the zip* here creates a list of time samples from the bank lists 
  # Input is   [ [ dword0@T=0, dword0@T=1, dword0@T=2 ], 
  #              [ dword1@T=0, dword1@T=1, dword1@T=2 ]  ];
  # Output is  [ ( dword0@T=0, dword1@T=0 ),
  #              ( dword0@T=1, dword1@T=1 ),
  #              ( dword0@T=2, dword1@T=2 ) ];
  time_sample_list = list(zip(*data_list));

  hexlist2file( file_name, time_sample_list );
  return;


########################################################
# Download RLE RAM to a file
def sump_rleram2file( self ):
  log( self,["sump_rleram2file()"]);
  rts = [];
  for (i,each_pod_list) in enumerate( self.sump.rle_hub_pod_list ):
    for (j,each_pod) in enumerate( each_pod_list ):
      log( self,[ "%d,%d %s" % ( i,j,each_pod) ]);
      rts += sump_rlepod_placeholder(self, hub_num=i, pod_num=j );
#     rts += sump_rlepod_download(self, hub_num=i,pod_num=j,download_en=False);
# rts += sump_rlepod_download(self, hub_num=0,pod_num=0);
  return rts;

########################################################
# Given the Hub and Pod number, create placeholder for on-demand downloaded samples 
#   pod_txt_list +=[ ("#[download_needed]")];
# pod_txt_list +=[ ("#[rle_pod_stop]")];
def sump_rlepod_placeholder( self, hub_num, pod_num ):
  log( self,["sump_rlepod_placeholder()"]);
  self.bd.wr( self.sump.addr_ctrl, [ 0x32 ] );
  self.bd.wr( self.sump.addr_data, [ (hub_num<<16)+(0<<8)+(0x00<<0) ] );
  hub_ck_freq = self.sump.rd( self.sump.cmd_rd_rle_hub_ck_freq)[0];
  hub_ck_freq_mhz = float( float(hub_ck_freq) / float( 2**20 ) );

  a = [];
  a+=[ ("#[rle_pod_start]"                                   )];
  a+=[ ("# rle_hub_instance = %d"   % ( hub_num            ) )];
  a+=[ ("# rle_pod_instance = %d"   % ( pod_num            ) )];
  a+=[ ("# rle_hub_clock    = %f"   % ( hub_ck_freq_mhz    ) )];
  a+=[ ("#[download_needed]"                                 )];
  a+=[ ("#[rle_pod_stop]"                                    )];
  pod_txt_list = a;
  return pod_txt_list;

########################################################
# Given the Hub and Pod number, download a single RLE Pod if needed
# If it isn't needed, return None
def sump_rlepod_download( self, hub_num, pod_num, rle_ram_list ):
  log( self,["sump_rlepod_download()"]);
  self.pygame.display.set_caption(\
    self.name+" "+self.vers+" "+self.copyright+" sump_rlepod_download()");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  need_to_download = False;
  hub_i = None;
  pod_i = None;
  insert_line = None;
  for (i,each_line) in enumerate( rle_ram_list ):
    words = " ".join(each_line.split()).split(' ') + [None] * 5;
    if words[1] == "rle_hub_instance":
      hub_i = int( words[3], 10 );
    if words[1] == "rle_pod_instance":
      pod_i = int( words[3], 10 );
    if words[0] == "#[download_needed]":
      if hub_i == hub_num and pod_i == pod_num:
        need_to_download = True;
        insert_line = i;
        log( self,["download_needed for (%d,%d)" % ( hub_num,pod_num) ]);
    if words[0] == "#[rle_pod_stop]":
      hub_i = None;
      pod_i = None;

  if need_to_download == False:
    return None;

  new_rle_ram_list = rle_ram_list[0:insert_line] + ["# New Line"] + rle_ram_list[insert_line+1:];

  pod_txt_list = [];

  self.bd.wr( self.sump.addr_ctrl, [ 0x32 ] );
  self.bd.wr( self.sump.addr_data, [ (hub_num<<16)+(0<<8)+(0x00<<0) ] );
  hub_ck_freq = self.sump.rd( self.sump.cmd_rd_rle_hub_ck_freq)[0];
  hub_ck_freq_mhz = float( float(hub_ck_freq) / float( 2**20 ) );

  trig_src_hub = self.sump.rd( self.sump.cmd_rd_rle_pod_trigger_src)[0];

  pod_hw_cfg    = self.sump.rd_pod( hub=hub_num,pod=pod_num,reg=self.sump.rle_pod_addr_pod_hw_cfg )[0];
  pod_hw_rev    = ( pod_hw_cfg & 0xFF000000 ) >> 24;

  pod_ram_cfg   = self.sump.rd_pod( hub=hub_num,pod=pod_num,reg=self.sump.rle_pod_addr_pod_ram_cfg )[0];
  pod_num_addr_bits = ( pod_ram_cfg & 0x000000FF ) >> 0;
  pod_num_data_bits = ( pod_ram_cfg & 0x00FFFF00 ) >> 8;
  pod_num_ts_bits   = ( pod_ram_cfg & 0xFF000000 ) >> 24;

  pod_trig_lat  = self.sump.rd_pod( hub=hub_num,pod=pod_num,reg=self.sump.rle_pod_addr_trigger_latency )[0];
  pod_trig_lat_core_cks = ( pod_trig_lat & 0x000000FF ) >> 0;
  pod_trig_lat_mosi_cks = ( pod_trig_lat & 0x0000FF00 ) >> 8;
  pod_trig_lat_miso_cks = ( pod_trig_lat & 0x00FF0000 ) >> 16;

  pod_user_ctrl = self.sump.rd_pod( hub=hub_num,pod=pod_num,reg=self.sump.rle_pod_addr_pod_user_ctrl)[0];

  trig_src_pod  = self.sump.rd_pod( hub=hub_num,pod=pod_num,reg=self.sump.rle_pod_addr_pod_trigger_src)[0];
# log( self,["Trigger Source : Hub-%d = %08x and Pod-%d = %08x" % ( hub_num, trig_src_hub, pod_num, trig_src_pod)]);

  print("pod_hw_cfg  is %08x" % pod_hw_cfg  );
  print("pod_ram_cfg is %08x" % pod_ram_cfg );
  print("  pod_num_addr_bits is %d" % pod_num_addr_bits );
  print("  pod_num_data_bits is %d" % pod_num_data_bits );
  print("  pod_num_ts_bits is %d" % pod_num_ts_bits );
  
  if pod_num_addr_bits == 0:
    return None;
  
  rle_state_bits = 2;# 0=Invalid,1=Pre-Trig,2=Trigger,3=Post-Trigger
  rle_total_bits = rle_state_bits + pod_num_ts_bits + pod_num_data_bits;
  rle_ram_length = 2**pod_num_addr_bits;
  rle_timestamp_bits = pod_num_ts_bits;


  # TODO: Don't recalulate this every time. Use a stored version
  rle_mask_hash = proc_rle_mask(self, self.sump.rle_hub_pod_list );
# (rle_bit_mask,rle_bulk_mask) = rle_mask_hash[(hub_num,pod_num)];
  (rle_bit_mask )              = rle_mask_hash[(hub_num,pod_num)];

  a = [];
# a+=[ ("#[rle_pod_start]"                                   )];
# a+=[ ("# rle_hub_instance = %d"   % ( hub_num            ) )];
# a+=[ ("# rle_pod_instance = %d"   % ( pod_num            ) )];
# a+=[ ("# rle_hub_clock    = %f"   % ( hub_ck_freq_mhz    ) )];
  a+=[ ("# hw_rev           = %02x" % ( pod_hw_rev         ) )];
  a+=[ ("# ram_length       = %d"   % ( rle_ram_length     ) )];
# a+=[ ("# state_bits       = %d"   % ( rle_state_bits     ) )];
  a+=[ ("# timestamp_bits   = %d"   % ( pod_num_ts_bits    ) )];
  a+=[ ("# data_bits        = %d"   % ( pod_num_data_bits  ) )];
  a+=[ ("# pod_user_ctrl    = %08x" % ( pod_user_ctrl      ) )];
  a+=[ ("# rle_bit_mask     = %08x" % ( rle_bit_mask       ) )];
# a+=[ ("# rle_bulk_mask    = %08x" % ( rle_bulk_mask      ) )];
# a+=[ ("# trigger_src      = %08x" % ( rle_pod_trig_src   ) )];
  a+=[ ("# trig_lat_core_ck = %d"   % ( pod_trig_lat_core_cks ) )];
  a+=[ ("# trig_lat_mosi_ck = %d"   % ( pod_trig_lat_mosi_cks ) )];
  a+=[ ("# trig_lat_miso_ck = %d"   % ( pod_trig_lat_miso_cks ) )];
  a+=[ ("# trig_src_hub     = %03x" % ( trig_src_hub       ) )];
  a+=[ ("# trig_src_pod     = %08x" % ( trig_src_pod       ) )];

  now = time.time()
  means = time.ctime(now)
  a+=[ ("# download_time    = %08x"   % (int( now ) ) )];

  pod_txt_list += a;

  if True :
#   if pod_num_data_bits % 4 != 0:
#     log( self, ["ERROR: invalid data bit width of %d for RLE Pod" % (pod_num_data_bits)]);

    # Calculate how many DWORD pages need to be read to get total bit count
    num_dwords = rle_total_bits // 32;
    if rle_total_bits % 32 != 0: num_dwords += 1;

    print("rle_total_bits = %d" % rle_total_bits );
    print("num_dwords     = %d" % num_dwords );

    # RAM is DWORD paged in width. Since the address is autoincremented
    # after each read, read entire ram length one dword page at a time
    # and then have python combine the lists together using zip.
    list_of_lists = [];
    for j in range( 0, num_dwords ):
      self.pygame.display.set_caption(\
        self.name+" "+self.vers+" "+self.copyright+" Downloading RLE Hub-%d Pod-%d Page-%d of %d" \
           % ( hub_num,pod_num,j,(num_dwords-1) ) );
      self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads

      # Set the Page to read out RLE samples, timestamps and 2bit codes
      print("sump_rlepod_download() : Hub = %d : Pod = %d : Page %d :  RAM Length = %d " % \
        ( hub_num, pod_num, j, rle_ram_length ) );
      self.sump.wr_pod( hub=hub_num,pod=pod_num,
                        reg=self.sump.rle_pod_addr_ram_page_ptr, data=((j<<20)+0x0000) );
      self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
      dword_list = self.sump.rd_pod(hub=hub_num,pod=pod_num,
                                    reg=self.sump.rle_pod_addr_ram_data,num_dwords=rle_ram_length);
#     self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
#     print("len(dword_list) = %d " % len( dword_list ) );
#     if ( hub_num == 0 and pod_num == 0 ):
#       list2file( ("j%d.txt"%(j)) , ["%08x" % each for each in dword_list ] );
      list_of_lists += [ dword_list ];

    self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright );
    self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
    self.pygame.event.pump();

    # Now reorder so that the DWORDs from each RAM address are together
    # Only store the hex nibbles that have info
    ram_list = list(zip( *list_of_lists ));
    dword_hex_list = [];
    for dword_list in ram_list:
      txt = "";
      for each in reversed(dword_list):
        txt = txt + "%08x" % each;
      num_nibbles = rle_total_bits // 4;
      if rle_total_bits % 4 != 0: num_nibbles += 1;
      txt = txt[-num_nibbles:];
      data_nibbles = pod_num_data_bits // 4;


# Pre 2023.11.30 scheme where data had to be on nibble boundaries
#     # Data has to fall on nibble boundaries but timestamp and state bits 
#     # can span across nibbles, so do things the hard math way here.
#     data_txt = txt[-data_nibbles:];
#     time_txt = txt[:-data_nibbles];
#     num_nibbles = rle_timestamp_bits // 4;
#     if rle_timestamp_bits % 4 != 0: num_nibbles += 1;
#     time_int = int( time_txt, 16 );
#     state_int = time_int >> rle_timestamp_bits;
#     time_int = time_int & ((2**rle_timestamp_bits)-1);
#     time_txt = "%016x" % time_int;
#     time_txt = time_txt[-num_nibbles:];
#     state_txt = "%01x" % state_int;
#     txt = state_txt + " " + time_txt + " " + data_txt;
#     dword_hex_list += [ txt ];

      # New 2023.11.30 scheme allows odd number of data bits
      # First separate data from code+timestamp bits
      # Note, this is done in ASCII hex space and not numerically
      # as RLE pods can be 8192 bits wide. 2^8192 is a REALLY large number.
      extra_bits = 0;
      if pod_num_data_bits % 4 != 0:
        extra_bits = pod_num_data_bits % 4;
        extra_nibble = txt[-data_nibbles-1];
        if   extra_bits == 1 : bit_and = 0x1; bit_mask = 0xE;
        elif extra_bits == 2 : bit_and = 0x3; bit_mask = 0xC;
        elif extra_bits == 3 : bit_and = 0x7; bit_mask = 0x8;
        # print("Extra bits %d : Extra Nibble %s" % ( extra_bits, extra_nibble ) )
        nib_data = "%01x" % ( int( extra_nibble, 16 ) & bit_and  );
        nib_time = "%01x" % ( int( extra_nibble, 16 ) & bit_mask );
        time_txt = txt[:-data_nibbles-1]+nib_time;
        data_txt = nib_data + txt[-data_nibbles:];
      else:
        time_txt = txt[:-data_nibbles];
        data_txt = txt[-data_nibbles:];

      # Now seprate code from timestamp bits 
      num_nibbles = rle_timestamp_bits // 4;
      if rle_timestamp_bits % 4 != 0: num_nibbles += 1;
      time_int = int( time_txt, 16 );
      time_int = time_int >> extra_bits;# Shift off 1-3 data bits

      state_int = time_int >> rle_timestamp_bits;
      time_int = time_int & ((2**rle_timestamp_bits)-1);
      time_txt = "%016x" % time_int;
      time_txt = time_txt[-num_nibbles:];
      state_txt = "%01x" % state_int;
      txt = state_txt + " " + time_txt + " " + data_txt;
      dword_hex_list += [ txt ];


#   list2file("foo1.txt", dword_hex_list );
    dword_hex_list = rle_rotate(self, dword_hex_list );
#   list2file("foo2.txt", dword_hex_list );
    dword_hex_list = rle_time_roll( dword_hex_list, rle_timestamp_bits );
#   list2file("foo3.txt", dword_hex_list );
    dword_hex_list = rle_time_cull( self, dword_hex_list );
#   list2file("foo4.txt", dword_hex_list );
    pod_txt_list += dword_hex_list;
# else:
#   pod_txt_list +=[ ("#[download_needed]")];
# pod_txt_list +=[ ("#[rle_pod_stop]")];

  new_rle_ram_list = rle_ram_list[0:insert_line] + pod_txt_list + rle_ram_list[insert_line+1:];
  return new_rle_ram_list;


########################################################
# Rotate the RLE RAM list so that order is always [1,1,1,2,3,3,3,0,0,0]
# Output looks like this:
# 1 0000006006 00012030 1st Pre-Trig Sample
# 1 0000006007 00012033 Pre-Trig
# 2 0000006008 00012036 Trig
# 3 0000006009 00012039 Post-Trig
# 3 000000600a 0001203c Last Post-Trig
# 0 0000000000 00000000 Null Sample
def rle_rotate( self,rle_list ):
  c = 3 * rle_list;
  b = [ each[0:1] for each in c ];

# TODO: This crashes if "2" isn't in the list ( force_stop )
  try:
    t = b.index("2")+1;
  except:
    log(self,["ERROR-4978 : rle_rotate() did not find a Trigger(2)"]);
    return [];
  b = b[t:];
  c = c[t:];
# print(" t of2 = %d" % t );
# list2file("b.txt", b );

  try:
    t = b.index("1");
  except:
    t = b.index("2");
  b = b[t:];
  c = c[t:];
# print(" t of1 = %d" % t );

  b = b[0:len(rle_list)];
  c = c[0:len(rle_list)];
  return c;


########################################################
# The RLE timestamp is really big, but it's possible to be waiting for
# hours for a trigger to occur. For this corner case, examine the MSB
# time bit for the post-rolled samples. If the bit goes 1 then back 
# to 0, we know the hardware counter rolled. Compensate by adding
# another MSB and set it to 1. For example, if an 8 bit counter goes
# from 128 to less than 128, add 256 to everything less than 128
# after the roll was detected.
#
# Final step is to subtract the Trigger time from all samples so that
# Trigger is Time-0 and pre-Trig is negative and post-Trig is positive
def rle_time_roll( rle_list, rle_timestamp_bits ):
  msb_value = 2**(rle_timestamp_bits-1);# ie 128= 2^^7 for an 8bit timestamp
  msb_found_jk = False;
  new_rle_list = [];
  for each in rle_list:
    words = " ".join(each.split()).split(' ');
    time_int = int( words[1],16 );
    if not msb_found_jk:
      if ( time_int & msb_value ) != 0:
        msb_found_jk = True;
    else:
      if ( time_int & msb_value ) == 0:
        time_int += 2**rle_timestamp_bits;
    # The number o
    num_nibbles = (rle_timestamp_bits+1) // 4;
    if (rle_timestamp_bits+1) % 4 != 0: num_nibbles += 1;
    time_txt = "%016x" % time_int;
    time_txt = time_txt[-num_nibbles:];
    new_rle_list += [ words[0] + " " + time_txt + " " + words[2] ];
  return new_rle_list;

########################################################
# It's possible for the RLE time to wrap multiple times if the number
# of timestamp bits is insufficient. Detect that and toss any bogus
# samples
def rle_time_cull(self, rle_list ):
  trigger_loc = None;
  for (i,each) in enumerate( rle_list ):
    words = " ".join(each.split()).split(' ');
    if words[0] == "2":
      trigger_loc = i; 
      trigger_time = int(words[1],16);
  if trigger_loc != None:
    pre_trig  = rle_list[0:trigger_loc];
    post_trig = rle_list[trigger_loc:];
#   list2file("pre.txt", pre_trig );
#   list2file("post.txt", post_trig );

    new_post_trig = [];
    start_culling = False;
    previous_sample_time = trigger_time;
    for each in post_trig:
      if start_culling == False:
        words = " ".join(each.split()).split(' ');
        sample_time = int(words[1],16);
        if sample_time >= previous_sample_time:
          new_post_trig += [ each ];
        else:
          start_culling = True;
        previous_sample_time = sample_time;
#   if start_culling:
#     log( self,["WARNING: Culled invalid RLE samples in rle_time_cull()"]);

    new_pre_trig = [];
    start_culling = False;
    previous_sample_time = trigger_time;
    for each in list(reversed(pre_trig)):
      if start_culling == False:
        words = " ".join(each.split()).split(' ');
        sample_time = int(words[1],16);
        if sample_time <= previous_sample_time:
          new_pre_trig += [ each ];
        else:
          start_culling = True;
        previous_sample_time = sample_time;
#   if start_culling:
#     log( self,["WARNING: Culled invalid RLE samples in rle_time_cull()"]);
    old_len = len( rle_list );
    rle_list = list(reversed(new_pre_trig)) + new_post_trig;
    new_len = len( rle_list );
    if ( new_len < old_len ):
      log( self,["WARNING: Culled %d invalid RLE samples in rle_time_cull()" % ( old_len-new_len)]);
  
  return rle_list;



########################################################
# Convert the RLE timestamp RAM file to a +/- integer in ps time units
# RAM File Input:
#  [rle_pod_start]
#   rle_hub_instance = 0
#   rle_pod_instance = 0
#   ..
#   1 0bebc1e6 8
#   ..
#   2 23d3b873 d
#   3 23d3b875 c
#   ..
#   0 40000000 c
#  [rle_pod_stop]
# Sample File Output:
# [rle_pod_start]
#  rle_hub_instance = 0
#  rle_pod_instance = 0
#  .. 
#  0001 1 -5,013,473,362,500
#  ..
#  1011 2 400,000
#  0011 3 425,000
# [rle_pod_stop]
#
def create_sump_digital_rle( self, file_in, file_out ):
  log( self,["create_sump_digital_rle()"]);
  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" create_sump_digital_rle()");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  from os import path;
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  file_in   = os.path.join( file_path, file_in );
  file_out  = os.path.join( file_path, file_out );

  ram_list = file2list( file_in );
  lst_list = [];
  
  all_pods_dict = {};

  # 1st pass extracts the header info for each Pod and stores it in 
  # a dictionary. 2nd pass uses this information to translate time
  for each in ram_list:
    # Look for and store header data
    if each[0:1] == "#":
      words = " ".join(each[1:].split()).split(' ') + [None] * 5;
      if words[0] == "[rle_pod_start]":
        pod_dict = {};
      elif words[0] == "[rle_pod_stop]":
        all_pods_dict[(hub_num,pod_num)] = pod_dict;# Add this pod's dict to all_pods_dict
      elif words[0] == "rle_pod_instance":
        pod_num = words[2];
      elif words[0] == "rle_hub_instance":
        hub_num = words[2];
      else:
        pod_dict[ words[0] ] = words[2];
    # Look for timestamp at trigger 
    # Code Time    Data
    # 
    # 1 0000005f2a 00005f34
    else:
      words = " ".join(each.split()).split(' ') + [None] * 5;
      if words[0] == "2":
        pod_dict[ "trigger_time" ] = int( words[1] , 16 );

  # Look for the trigger source as each hub, with a different clock, has a different
  # miso trigger latency that will then be shared with all hubs as a trigger offset
  # rle_hub_clock    = 100.000000 # 100 MHz clock for this hub
  # trig_lat_miso_ck = 12         # 12 clocks at 100 MHz is the latency
  # trig_src_hub     = 300        # Indicates Hub num 0x00 was the trig source
  # trig_src_pod     = 00000001   # Indicated D[0] was the trigger bit
  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" locating trigger...");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  trig_src_miso_latency = 0.0;# in ps
  for each in ram_list:
    # Look for and store header data
    if each[0:1] == "#":
      words = " ".join(each[1:].split()).split(' ') + [None] * 5;
      if words[0] == "[rle_pod_start]":
        trig_src_hub = None;
#       print("Oy!");
      elif words[0] == "[rle_pod_stop]":
#       print("Vay!");
        if ( trig_src_hub != None and trig_src_hub & 0x300 == 0x300 ):
          pod_i = trig_src_hub & 0x0FF;
          if pod_i == pod_num:
            log( self,["Trigger source is Hub-%d, Pod-%d, Bits-%08x" % ( hub_num, pod_num, trig_src_pod )]);
            trig_src_miso_latency = float ( 1000000.0 / hub_clk ) * trig_lat_miso_ck;# Latency in pS
      elif words[0] == "rle_pod_instance":
        pod_num = int( words[2],10 );
      elif words[0] == "rle_hub_instance":
        hub_num = int( words[2], 10 );
      elif words[0] == "rle_hub_clock":
        hub_clk = float( words[2] );
      elif words[0] == "trig_lat_miso_ck":
        trig_lat_miso_ck = int( words[2], 10 );
      elif words[0] == "trig_src_hub":
        trig_src_hub = int( words[2], 16 );
      elif words[0] == "trig_src_pod":
        trig_src_pod = int( words[2], 16 );
#     elif words[0] == "pod_user_ctrl":
#       pod_user_ctrl = int( words[2], 16 );

  # 2nd pass passes header info on through other than parsing the 
  # pod number. Data is modifed to subtract trigger time from all samples
  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" time adjust..");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  calc_trig_offset = True;
  trig_offset = 0;
  for each in ram_list:
    if each[0:1] == "#":
      words = " ".join(each[1:].split()).split(' ') + [None] * 5;
      if words[0] == "rle_hub_instance":
        hub_num = words[2];
        hub_i   = int(hub_num);
      if words[0] == "rle_pod_instance":
        pod_num = words[2];
        pod_i   = int(pod_num);
        pod_dict = all_pods_dict[(hub_num,pod_num)];
#       pod_clk_ps = int(round(1/( float(pod_dict["clock"])/1000000.0)));# clk in ps units
        pod_clk_ps = int(round(1/( float(pod_dict["rle_hub_clock"])/1000000.0)));# clk in ps units
        calc_trig_offset = True;
      lst_list += [ each ];
    else:
      # Trigger Offset
      if calc_trig_offset:
        calc_trig_offset = False;
        trig_offset = 0;
##       core_ck = 12500;
#        miso_ck = 12500;# Trigger Source in 80 MHz Domain
##       miso_ck = 10000;# Trigger Source in 100 MHz Domain
#        if hub_i == 0:
#          mosi_ck = 12500;
#        else:
#          mosi_ck = 10000;

#       trig_offset += ( int(pod_dict["trig_lat_miso_ck"],10) + 0 ) * miso_ck;# HACK FREQ
#       trig_offset += ( int(pod_dict["trig_lat_mosi_ck"],10) - 5 ) * mosi_ck;# HACK FREQ

        trig_offset = trig_src_miso_latency;
        core_ck = float( 1000000.0 / self.sump.cfg_dict['dig_freq'] );# ps
        trig_offset += ( int(pod_dict["trig_lat_core_ck"],10) + 0 ) * core_ck;
        trig_offset += ( int(pod_dict["trig_lat_mosi_ck"],10) - 5 ) * pod_clk_ps;
        trig_offset = int( trig_offset );

#       log( self,["Trigger Offset is %f ps : Hub-%d Pod-%d" % ( trig_offset, hub_i, pod_i ) ]);

      words = " ".join(each.split()).split(' ') + [None] * 5;
      time_hex = words[1];
      time_raw = int(time_hex,16);
      time_int = time_raw - pod_dict["trigger_time"];
#     print("%s : %d - %d = %d" % (time_hex,time_raw,pod_dict["trigger_time"],time_int));

      time_int *= pod_clk_ps;
      
      time_int = time_int + trig_offset;

      data_hex = words[2];
      data_bin = "";
      for each_nib in data_hex: 
        data_bin += nibble2bits(int(each_nib,16) );
      data_bin = data_bin[::-1];# Reverse the string to Put D(0) bit at Col-0 (leftmost)
      # Now iterate the 32bit rle_mask register and convert '0' to 'X' for bits that were masked
      data_bin_masked = "";


      # New 2023.08.18
      for i in range( 0, len(data_bin) ):
        if (i<32) and ( ((2**i) & int(pod_dict["rle_bit_mask"],16) ) != 0 ):
          data_bin_masked += "X";
#       elif (i>=32) and ( int(pod_dict["rle_bulk_mask"],16) == 0xFFFFFFFF ):
#         data_bin_masked += "X";
        else:
          data_bin_masked += data_bin[i];

      # New 2023.06.28 : Only keep valid RAM entries with actual samples.
      if words[0] != "0":
#       time_txt = f"{time_int:,}";# Thousands comma separator
        time_txt = comma_separated(time_int);# Thousands comma separator
        lst_list += [ data_bin_masked + " " + words[0] + " " + time_txt ];
      # D0                           D31    Time in ps
      # X1X01100000001001000000000000000 1 -12500
      # X1X01100000001001000000000000000 2 0
      # X0X11100000001001000000000000000 3 12500
  list2file( file_out, lst_list );
  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+"");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  return;


########################################################
# Read in the raw RAM file and create a digital only file
# TODO: Needs to handle multiple DWORDs
def create_sump_digital_fast( self, file_in, file_out ):
  log( self,["create_sump_digital_fast()"]);
  from os import path;
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  file_in = os.path.join( file_path, file_in );
  file_out = os.path.join( file_path, file_out );

  ram_list = file2list( file_in );
  digital_list = [];
  samples = len( ram_list );

  for i in range( 0, samples ):
    words = " ".join(ram_list[ i ].split()).split(' ');
    bin_str = "";
    for each in words:
      value = int( each, 16 );
      bin_str += dword2bits( value )[::-1];# Reverse string to put LSB at leftmost Col-0
    digital_list += [ bin_str ];

  list2file( file_out, digital_list );
  return;


########################################################
# Read in the raw RAM file and create a digital only file
# TODO: Needs to handle multiple DWORDs
# TODO: Needs to handle dynamic record profile changes
# record_profile 1001 010E
#  [31:24] = DWORDs per Record
#  [23:16] = Header Length
#  [15:8]  = Digital Length
#  [7:0]   = Analog Length
#
# Analog Sample Slot:
#   { id_byte[7:0], CH1[11:0], CH0[11:0] }
#     id_byte[7:0]
#     [7]   = 1=ValidSamples, 0=NoValidSamples
#     [6:5] = CHsPerSlot (0-3).  Slot may contain 1 24 bit ,2 12bit 3 8bit
#     [4:0] = BitsPerCH  (0-24). Samples in slot may be 0-24 bits in width
# Output:
# 01100100111000001101011010001000 a9b 389 None None 1 00000001
# 01100100111000001101011010001000 a9b 389 None None 2 00000007
# 01100100111000001101011010001000 a9b 389 None None 3 00000020
# Single word of digital bits followed by multiple analog CHs
# None represents a missing sample.
# WARNING : The RAM can be incomplete when super slow sampling is used.
def create_sump_digital_slow( self, file_in, file_out ):
  log( self,["create_sump_digital_slow()"]);
  import math;
  from os import path;
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  file_in = os.path.join( file_path, file_in );
  file_out = os.path.join( file_path, file_out );

  ram_list_pre = file2list( file_in );
  ana_rec_profile = self.sump.cfg_dict['ana_record_profile'];
  record_len        = ( ana_rec_profile & 0xFF000000 ) >> 24;
  record_header_len = ( ana_rec_profile & 0x00FF0000 ) >> 16;
  record_dig_len    = ( ana_rec_profile & 0x0000FF00 ) >>  8;
  record_ana_len    = ( ana_rec_profile & 0x000000FF ) >>  0;

  # 1st Pass is to remove any empty records. If the trigger happens before
  # pre-trig is full, or if the user hits "Download" before acquisition is
  # complete there will be empty records that must be removed.
  if record_len != 0:
    samples = len( ram_list_pre ) // record_len;
  else:
    samples = 0;
  print("Number of LS samples is %d" % samples );
  j = 0; blank_record = False;
  ram_list = [];
  for each in ram_list_pre:
    if j == 0:
      if each[0:1] == "0":
        blank_record = True;
    if not blank_record:
      ram_list += [ each ];
    j += 1;
    if j == record_len:
      j = 0;
      blank_record = False;

  digital_list = [];
  digital_offset = record_header_len;
  samples = len( ram_list ) // record_len;
  print("Number of LS samples is now %d" % samples );
# max_time = 0; max_i = 0;
  for i in range( 0, samples ):
    header_time = int( ram_list[ (record_len * i) + ( 0 ) ], 16 );
    header_stamp = ( header_time & 0xC0000000 ) >> 30;
    header_time  = ( header_time & 0x3FFFFFFF ) >> 0;
    header_str = " %01x %08x" % ( header_stamp, header_time );
#   if header_time > max_time:
#     max_time = header_time;
#     max_i = i;
    bin_str = "";
    for j in range( 0, record_dig_len ):
      value = int( ram_list[ (record_len * i) + (digital_offset + j) ], 16 );
      dword_bin_str = dword2bits( value );
      dword_bin_str = dword_bin_str[::-1];# Reverse the string to Put D(0) bit at Col-0 (leftmost)
      bin_str += dword_bin_str;
    ana_str = "";
    analog_offset = record_header_len + record_dig_len;
    for j in range( 0, record_ana_len ):
      value = int( ram_list[ (record_len * i) + (analog_offset + j) ], 16 );
      id_byte = ( value & 0xFF000000 ) >> 24;
      id_valid_samples = ( id_byte & 0x80 ) >> 7;
      id_chs_per_slot  = ( id_byte & 0x60 ) >> 5;
      id_bits_per_ch   = ( id_byte & 0x1F ) >> 0;
      for k in range( 0, id_chs_per_slot ):
        if id_valid_samples == 0:
          ana_str += " None";
        else:
          ch_value = value & ( 2**id_bits_per_ch-1 );
          value = value >> id_bits_per_ch;# Shift down for the next channel if there is one
          hex_str = "%06x" % ch_value;# Max channel size is 24 bits
          nibs = int( math.ceil( id_bits_per_ch / 4 ));# Round up to nearest integer
          hex_str = hex_str[-nibs:];# grab the n nibbles on the right
          ana_str += " "+hex_str;
#   digital_list += [ bin_str + ana_str ];
    # Only save valid samples
    if header_str[1] != "0":
      digital_list += [ bin_str + ana_str + header_str ];


  # Do a roll operation. Look for 1st trigger and then go 1,2,3 from there
  # knowing the 1st 1 after the 1st 2 is the beginning of time
  # "1112333311" becomes 2x
  # "1112333311" "1112333311" 
  #          |-------^---|

# list2file( "test1.txt", digital_list );
  dig_len = len(digital_list);
  digital_list = 2*digital_list;# Concat

  code_list = []
  for each in digital_list:
    words = " ".join(each.split()).split(' ');
    code_list += [ words[-2] ];
  try:
    t = code_list.index("2");
  except:
    log(self,["ERROR-4979 : did not find a Trigger(2) in LS samples"]);
    return [];

  # Remove the 1st "2" and everything before it.
  digital_list = digital_list[(t+1):];
  code_list    = code_list[(t+1):];

  # Now find the 1st "1" and preserve it to the sample length
  # If a "1" doesn't exist, it means trigger happened on very first sample
  # acquire, so use it as the start point.
  try:
    t = code_list.index("1");
  except:
#   t = 0;
# New 2025.01.22
    try:
      t = code_list.index("2");
      log(self,["WARNING: no pre-trig LS samples found!"]);
    except:
      t = 0;
      log(self,["WARNING: no trigger LS samples found!"]);

  digital_list = digital_list[t:(t+dig_len)];
  code_list    = code_list[t:(t+dig_len)];
  new_len = len(digital_list);
  if dig_len != new_len:
    log(self,["ERROR-5150 : LS sample roll operation complete systems failure"]);
    digital_list = [];

  list2file( file_out, digital_list );
  return;


########################################################
# convert each bit into a value list for the signals
# TODO: Needs to handle multiple DWORDs
#def create_signal_values_digital( self, file_ls_name, file_hs_name ):
def create_signal_values_digital( self, file_ls_name, file_hs_name, file_rle_name ):
  log( self,["create_signal_values_digital()"]);
  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" create_signal_values_digital()");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  from os import path;
  file_path = os.path.abspath( self.vars["sump_path_ram"] );
  file_ls_name  = os.path.join( file_path, file_ls_name  );
  file_hs_name  = os.path.join( file_path, file_hs_name  );
  file_rle_name = os.path.join( file_path, file_rle_name );

  ls_list = [];
  hs_list = [];
  rle_list = [];
  
  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" create_signal_values_digital() Reading Files...");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  if os.path.exists( file_ls_name ):
    ls_list = file2list( file_ls_name );
  if os.path.exists( file_hs_name ):
    hs_list = file2list( file_hs_name );
  if os.path.exists( file_rle_name ):
    rle_list = file2list( file_rle_name );

  # Locate the actual ls trigger index by looking for "2" as 2nd to last word
  # This will differ from the trigger location setting since the user may
  # download before the acquisition finishes.
  actual_digital_ls_trig_index = None;
  for (i,each_sample) in enumerate( ls_list ):
    words = " ".join(each_sample.split()).split(' ');
    if len(words) > 2:
      if words[-2] == "2":
        actual_digital_ls_trig_index = i;

  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" create_signal_values_digital() Generating Samples...");
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();

  # Iterate through the signal list and assign samples and attributes
  # to each signal from the specified source ( ls, hs or rle )
# total_bits = 32; 
  pod_cache = {};
  j = len( self.signal_list );
  for (i,each_sig) in enumerate( self.signal_list ):
    self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" create_signal_values() %d of %d" % (i,j));
    self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
    self.pygame.event.pump();
    if each_sig.source != None:
      # Erase old stuff - new 2023.06.29
      each_sig.values = [];
      each_sig.rle_time = [];
      each_sig.trigger_index = None;

      sig_source = each_sig.source;
      # Grab samples from one of two sources
      if sig_source[0:10] == "digital_hs":
        sample_list = hs_list;
      elif sig_source[0:10] == "digital_ls":
        sample_list = ls_list;
      elif sig_source[0:9] == "analog_ls":
        sample_list = ls_list;
      elif sig_source[0:11] == "digital_rle":
        # Format digital_rle[0][1][31:0] :
        #    "0" is the rle_hub 
        #    "1" is the rle_pod 
        #    "31:0" is the bit rip
        #      
        # digital_rle [ 0 ] [ 1 ] [ 31:0 ] :
        # 0           1 2 3 4 5 6 7   8  9    Words
        # Translate to digital_rle[31:0] to be compatible with digital_ls and digital_hs parsing
        # that follows. Extrace the pod_num and rename the sig_source
        sample_list = rle_list;
        a = sig_source;
        a = a.replace("["," [ ");
        a = a.replace("]"," ] ");
        words = " ".join(a.split()).split(' ');

        # Handle both digital_rle[0][1][2] and digital_rle[hub_name][pod_name][2]
        hub_name = words[2];
        pod_name = words[5];
        key = hub_name+"."+pod_name;
        if self.sump.rle_hub_pod_dict.get(key) != None:
          ( hub_num, pod_num ) = self.sump.rle_hub_pod_dict[ key ];
        else:
          hub_num = int( hub_name );
          pod_num = int( pod_name );


        sig_source = words[0] + " ".join(words[7:]).replace(" ","");
        # Now given the pod_num, rip through the rle_list and extract just the pod_num samples
        # #[rle_pod_start]
        # # rle_pod_instance = 0
        # X0X01100111110100000000000000000 1 -2775000
        # #[rle_pod_stop]

        # Use cached results if we already processed this rle_pod instead of doing same op 32 times.
        if pod_cache.get(( hub_num,pod_num )):
          (sample_list,attrib_dict) = pod_cache[(hub_num,pod_num)];
        else:
          self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" pod_cache miss");
          self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
          self.pygame.event.pump();
          sample_list = [];
          parsing_jk = False;
          hub_i = None;
          pod_i = None;
          attrib_dict = {};
          for each_sample in rle_list:
            if each_sample[0:1] == "#":
              a = each_sample;
              a = a.replace("#","");
              words = " ".join(a.split()).split(' ') + [None] * 5;
              if words[0] == "rle_hub_instance":
                hub_i = int(words[2]);
              if words[0] == "rle_pod_instance":
                pod_i = int(words[2]);
                if pod_i == pod_num and hub_i == hub_num:
                  parsing_jk = True;
              if words[0] == "[rle_pod_stop]":
                parsing_jk = False;
                hub_i = None;
                pod_i = None;
# New 2024.01.10
#             if words[1] == "=":
              if words[1] == "=" and parsing_jk == True:
                attrib_dict[words[0]] = words[2];# ie attrib_dict["rle_pod_instance"] = "0"
            elif parsing_jk:
              sample_list += [ each_sample ];
          pod_cache[(hub_num,pod_num)] = (sample_list,attrib_dict);
          self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright+" pod_cache filled");
          self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
          self.pygame.event.pump();

        # Decide if samples for this signal are valid based on pod_user_ctrl
        if attrib_dict.get("pod_user_ctrl") != None:
          pod_user_ctrl = int( attrib_dict["pod_user_ctrl"], 16 );
        else:
          pod_user_ctrl = 0x00000000;
        dword = 0x00000000;
        mask  = 0x00000000;
        for ( bit_rip, bit_val ) in each_sig.user_ctrl_list:
          bit_rip = bit_rip.replace("[","");
          bit_rip = bit_rip.replace("]","");
          if ":" in bit_rip:
            (bit_h,bit_l) = bit_rip.split(":");
          else:
            bit_l = bit_rip;# "[0]" instead of "[1:0]"
            bit_h = bit_l;
          bit_l = int(bit_l,10);
          bit_h = int(bit_h,10);
          dword += int(bit_val,16) << bit_l;
          for i in range(bit_l,bit_h+1):
            mask += 2**i;# ie [7:4] becomes 0xF0

        # Now decide if the pod_user_ctrl bits make the signal valid
        if len( each_sig.user_ctrl_list ) == 0:
          rle_valid_user_ctrl = True;
        else:
          if ( dword & mask ) == ( pod_user_ctrl & mask ):
            rle_valid_user_ctrl = True;
          else:
            rle_valid_user_ctrl = False;

      # Future designs may support both analog_ls and analog_hs
      if sig_source[0:9] == "analog_ls" and len(sample_list) != 0:
        words = " ".join(sample_list[0].split()).split(' ');
        words = words[1:];# Remove the digital samples that were word[0]
        total_words = len( words );
        adc_random_none_samples = int( self.vars["dbg_random_adc_none_samples"],10 );
        ls_ana_dig_alignment    = int( self.vars["sump_ls_ana_dig_alignment"],10 );
        for i in range( 0, total_words ):
          source = "analog_ls[%d]" % i;
          if sig_source == source:
            each_sig.values = [];
            each_sig.type = "analog";
            each_sig.format = "analog";
#           each_sig.triggerable = False;# TODO Must check for events
            # 2025.03.18 align analog_ls with digital_ls by pre-stuffing 2 Nones
#           each_sig.values += 2*[ None ];
#           each_sig.values += 4*[ None ];
            each_sig.values += ls_ana_dig_alignment*[ None ];

#           2025.04.15 : Since we prepended 2 Nones, shorten analog list by 2 samples
#           for each_sample in sample_list:
#           for each_sample in sample_list[0:-4]:
            for each_sample in sample_list[0:-ls_ana_dig_alignment]:
              words = " ".join(each_sample.split()).split(' ');
              words = words[1:];# Remove the digital samples that were word[0]
              word_val = words[i];
              if word_val == "None":
                word_val_int = None;
              else:
                word_val_int = int(word_val,16);
              # This is for software testing of not having an ADC sample
              if adc_random_none_samples == 1:
                rnd = random.randint(0,10);
                if rnd == 0:
                  word_val_int = None;
              each_sig.values += [ word_val_int ];


      # Check for digital bit ripped of multiple bits
      elif ":" in sig_source and sig_source[0:8] == "digital_":
        a = sig_source;
        a = a.replace("["," [ ");
        a = a.replace("]"," ] ");
        a = a.replace(":"," : ");
        words = " ".join(a.split()).split(' ') + [None] * 5;
        if ( words[1] == "[" and
             words[3] == ":" and
             words[5] == "]"     ):
          top_rip = int( words[2],10 );
          bot_rip = int( words[4],10 );
          each_sig.values   = [];
          each_sig.rle_time = [];
          each_sig.type = "digital";
          each_sig.nibble_cnt = (( top_rip-bot_rip)//4 ) + 1;
          if each_sig.format == None:
            each_sig.format = "hex";

          for each_item in sample_list:
            if "digital_rle" in each_sig.source:
              words = " ".join(each_item.split()).split(' ') + [None] * 3;
              each_sample = words[0];
              each_code   = words[1];
              each_time   = words[2].replace(",","");# Remove any thousands separators
            else:
              each_sample = each_item;

            if "digital_rle" in each_sig.source:
              bit_cnt = 0; word_val = 0;
              valid_sample = True;# An RLE masked bit will show up as "X" instead of "1" or "0"
              for j in range( bot_rip, (top_rip+1) ):
                if j < len(each_sample):
                  if each_sample[j] == "X":
                    valid_sample = False;# This will wipe out the entire word
                  else:
                    word_val += (2**bit_cnt) * int( each_sample[j] );
                  bit_cnt += 1;
                else:
                  valid_sample = False;# This will wipe out the entire word
              if valid_sample:
                each_sig.values += [ word_val ];
                each_sig.rle_time += [ int(each_time,10) ];
              else:
                each_sig.values = [];
            # Not digital_rle so must be digital_ls or digital_hs
            else:
              bit_cnt = 0; word_val = 0;
              try:
                for j in range( bot_rip, (top_rip+1) ):
                  word_val += (2**bit_cnt) * int( each_sample[j] );
                  bit_cnt += 1;
                each_sig.values += [ word_val ];
              except:
                each_sig.values = [];# Probably a range error

      # Single binary digital bits
      else:
        # Check for binary single bit signals
        if "digital_" in sig_source and "[" in sig_source and ":" not in sig_source:
          each_sig.values = [];
          each_sig.type = "digital";
          each_sig.format = "binary";
          a = sig_source.replace("[", "[ ");
          a =          a.replace("]", " ]");
          words = " ".join(a.split()).split(' ');
          i = int( words[1] );# Get the index
          if True:

            for each_item in sample_list:
              if "digital_rle" in each_sig.source:
                words = " ".join(each_item.split()).split(' ') + [None] * 3;
                each_sample = words[0];
                each_code   = words[1];
                each_time   = words[2].replace(",","");# Remove any thousands separators
              else:
                each_sample = each_item;

              try:
                if each_sample[i] != "X":
                  bit_val = int( each_sample[i] );
                  each_sig.values   += [ bit_val ];
                  if "digital_rle" in each_sig.source:
                    each_sig.rle_time += [ int(each_time,10) ];
                else:
                  each_sig.values = [];# Must be a RLE Masked bit, so no values at all
              except:
                each_sig.values = [];# Most likely i index was out of range.

      if "digital_rle" in each_sig.source:
        if rle_valid_user_ctrl == False:
          each_sig.values = [];# No Soup for You

      # Convert mutable values list to an immutable tuple to save memory.
      each_sig.values = tuple( each_sig.values );

      # Calculate the trigger index using the ram length and post trig sample info
      hs_hw_pipeline_offset = 7;
#     ls_hw_pipeline_offset = 1;
      ls_hw_pipeline_offset = 0;# New 2023.08.31
#     if sig_source[0:10] == "digital_hs":
      if "digital_hs" in sig_source:
        ram_depth = self.sump.cfg_dict['dig_ram_depth']; 
        each_sig.trigger_index = ( ram_depth - self.sump.cfg_dict['dig_post_trig_samples'] );
        each_sig.trigger_index -= hs_hw_pipeline_offset;
#     else:
# 2025.01.13
#     elif "analog_ls" in sig_source:
      elif "analog_ls" in sig_source or "digital_ls" in sig_source:
        ana_rec_profile = self.sump.cfg_dict['ana_record_profile'];
        record_len      = ( ana_rec_profile & 0xFF000000 ) >> 24;
        if record_len != 0:
          ram_depth = self.sump.cfg_dict['ana_ram_depth'] / record_len; 
          if actual_digital_ls_trig_index != None:
            each_sig.trigger_index = actual_digital_ls_trig_index;
          else:
            each_sig.trigger_index = ( ram_depth - self.sump.cfg_dict['ana_post_trig_samples'] );
          each_sig.trigger_index -= ls_hw_pipeline_offset;

      # Calculate the sample period 
      clock_period = None;
#     if sig_source[0:10] == "digital_hs":
      if "digital_hs" in sig_source:
        clock_period = 1000.0 * ( 1 / self.sump.cfg_dict['dig_freq'] );# ns
#     else:
# 2025.01.13
#     elif "analog_ls" in sig_source:
      elif "analog_ls" in sig_source or "digital_ls" in sig_source:
        try:
          clock_period = 1000.0 * ( 1 / self.sump.cfg_dict['tick_freq'] );# ns
          clock_period *= float( self.sump.cfg_dict['tick_divisor'] );# ns
        except:
          clock_period = None;
          log( self,["ERROR create_signal_values_digital() clock_period math error"]);

      if clock_period != None:
        if clock_period > 1000000:
          each_sig.sample_period = clock_period / 1000000.0;
          each_sig.sample_unit = "ms";
        elif clock_period > 1000:
          each_sig.sample_period = clock_period / 1000.0;
          each_sig.sample_unit = "us";
        else:
          each_sig.sample_period = clock_period;
          each_sig.sample_unit = "ns";

      # RLE samples are all in 1 ps
      if "digital_rle" in sig_source:
        each_sig.sample_period = 1;
        each_sig.sample_unit = "ps";

      log_str = [];
#     log_str +=["%s -type %s samples = %d " % \
#               ( each_sig.name, each_sig.type, len( each_sig.values ))];
      log( self, log_str );
  self.pygame.display.set_caption( self.name+" "+self.vers+" "+self.copyright);
  self.pygame.time.wait( 0 );# Try to avoid timeout spinner during long downloads
  self.pygame.event.pump();
  return;


def nibble2bits( value ):
  bits = 4;
  bin_str = ("%s" % "0"*(bits-len(bin(value)[2:])) + bin(value)[2:] );
  return bin_str;

def dword2bits( value ):
  bits = 32;
  bin_str = ("%s" % "0"*(bits-len(bin(value)[2:])) + bin(value)[2:] );
  return bin_str;


###############################################################################
class cursor(object):
  def __init__( self, name="Cursor-1", visible=False ):
    self.name          = name;
    self.visible       = visible;
    self.selected      = False;
    self.trig_delta_t  = None;# Distance to trig in sample time units ns,us,ms
    self.trig_delta_unit = None;# "ns", "us" or "ms"
    self.x             = 10;
    self.y             = 0;
    self.delta_txt     = None;# Time Measurement between cursors
    self.parent        = None;
    self.sample        = 0;
    self.color         = None;
    self.sig_value_list = {};
  def __del__(self):
    return;
  def __str__(self):
    return "name = " + self.name;


###############################################################################
# A signal contains time samples and various display attributes.
class signal(object):
  def __init__( self, name="cnt_a", visible=True, \
                bits_per_line=32, bits_total=32,format="hex"):
    self.name            = name;
    self.name_rect       = None;# (x,y,w,h) of drawn text
    self.type            = None;# "analog", "digital" "group" "spacer" "clock"
    self.window          = None;# "analog_ls", "digital_ls", "digital_hs"
    self.parent          = None;# parent window
    self.view_name       = None;# like a group, but different
    self.view_obj        = None;# New 2023.12.06 , the actual object
    self.member_of       = None;# Signals can have a group as a parent. -group attrib
    self.hier_level      = 0;
    self.source          = None;  # "digital[0]"
    self.visible         = visible;# If Deleted, Or Group Collapsed, not visible at all.
    self.hidden          = False;# A hidden signal only show name, no values. Removes clutter.
    self.rle_masked      = False;
    self.offscreen       = "";# "^" or "v" indicating where analog signal is offscreen
    self.collapsed       = False;  
    self.collapsable     = False;# A group is collapsable for example
    self.values          = [];  # sample values - None if not available
    self.rle_time        = [];  # For RLE signals, each value has a time
    self.trigger         = False;
    self.triggerable     = False;# Only 32 Event Binary and Analog CHs can be triggers
    self.maskable        = False;# Only 32 Event Binary in RLE Pods can be maskable    
    self.trigger_field   = 0x00000000;# the 1 of 32 trigger bits
    self.trigger_index   = None;# Sample index, like 0 or 205, to where trigger occurred.
    self.selected        = False;
    self.vertical_offset     = 0.0;# Maybe use for analog waveform offset? 
    self.units_per_division  = None;# Units per division. If defined, overrules divisions_per_range
    self.divisions_per_range = 1.0;# Default to 1 division per max range of ADC
    self.vertical_scale_rate = -1;# 0,1,2 for x2,x2.5,x2 (1,2,5, 10,20,50, 100,200,500)
    self.y               = 0;
    self.bits_total      = 0;
    self.range           = 0;# ie 255 for 8bit value
    self.units           = None;# ie "mV" or "uA"
    self.units_per_code  = 1.0; # ie "1.0"
    self.offset_units    = 0.0;  # Only applies to cursor measurements, not drawn lines
    self.offset_codes    = 0;    # Not used yet
    self.sample_period   = None;# ie 10.0 ns
    self.sample_unit     = None;# ie ns us ms
    self.color           = None;
    self.format          = None;     # binary, hex, analog
    self.nibble_cnt      = 0;# Number of nibbles for hex display
    self.timezone        = None;
    self.user_ctrl_list  = [];# List of Tuples of bit rip and value, ie [("1:0","3")]
    self.fsm_state_dict  = {};# Number,Text pairs defining FSM state names
  def __del__(self):
    return;
  def __str__(self):
    return "name     = " + self.name;


###############################################################################
# A window is one of three drawing areas for views.
class window(object):
  def __init__( self, name="foo" ):
    self.name            = name;
    self.timezone        = None;
    self.view_list       = [];
    self.draw_list       = [];
    self.signal_list     = [];# create_waveforms() populates this from self.signal_list
#   self.selected        = False;
    self.grid_enable     = False;
    self.panel           = None;
    self.surface         = None;
    self.image           = None;
    self.y_offset        = 0;# Vertical offset for samples to be drawn at
    self.y_analog_offset = 0;# Vertical offset for samples to be drawn at
    self.zoom_pan_list   = ( 1.0,0,0 );
    self.zoom_pan_history = [];
    self.rle_time_range  = None;# ( float, units, float, units )
    self.sample_period   = None;# inherited from child signal
    self.sample_unit     = None;# inherited from child signal
    self.trigger_index   = None;# inherited from child signal
    self.samples_total   = None;# inherited from child signal
    self.samples_shown   = None;# how many are displayed right now
    self.samples_start_offset = 0;# sample index of 1st sample drawn on the left.
    self.samples_viewport = None;# ASCII represenation of what is being viewed
    self.x_space         = 0.0;# number of pixel spaces between samples
    self.cursor_x_list   = [ None, None ];
  def startup( self ):
    self.zoom_pan_list = ( 1.0,0,0 );
  def __del__(self):
    return;
  def __str__(self):
    return "name = " + self.name;


###############################################################################
# A view is a parent by name only of a bunch of signals. 
# 1) Name - the name which signals link their "-view" attribute to.
# 2) TimeZone - a name which identifies this view as sharing the same TimeZone
#    of some other view. TimeZone is just a name, but indicates common sample
#    rate and number of samples. Views of the same TimeZone may be but in a
#    window together. Views of different TimeZones may not. If two Windows
#    are of the same TimeZone, scroll and zoom operations will act on both.
# 3) user_ctrl_list. A list of sump_user_ctrl bits that must be set
#    for the view to be valid. Ex [ ("[3:0]","a"),("[7:4]","b" ]
#    See def gen_bit_rip
class view(object):
# def __init__( self, name="foo", timezone="bar" ):
  def __init__( self, name="foo" ):
    self.name             = name;
    self.filename         = None;
    self.timezone         = None;
#   self.timezone         = timezone;
    self.window           = None;
    self.color            = None;
#   self.uut_rev_list     = None;
    self.user_ctrl_list   = [];
    self.rle_hub_pod_list = [];# (hub,pod) tuples assigned to this view
    self.rle_hub_pod_user_ctrl_list = [];# (hub,pod,user_ctrl_list) tuples assigned to this view
    self.sample_period    = None;# inherited from child signal
    self.sample_unit      = None;# inherited from child signal
    self.trigger_index    = None;# inherited from child signal
    self.samples_total    = None;# inherited from child signal
  def __del__(self):
    return;
  def __str__(self):
    return "name = " + self.name;


##############################################################################
# Virtual sump provides access to last capture's sump configuration from file
class sump_virtual:
  def __init__ ( self, parent ):
    self.parent = parent;
    self.status = ("",0x00);
    self.cfg_dict = {};
    self.cfg_dict['hw_rev_expected'] = 0x01;# Rev this SW was tested against
    self.rle_hub_pod_dict = {};
    self.rle_hub_pod_list = [[]];# List of Lists of Hub#, Pod# and Names in 0.Hub.0.Pod format
    self.addr_ctrl = 0x00000000;
  def rd_cfg( self, capture_cfg_filename ):
    cfg_list = file2list( capture_cfg_filename );
    for each_line in cfg_list:
      words = " ".join(each_line.split()).split(' ') + [None] * 3;
      if words[1] == "=":
        # tick_freq and dig_freq are floats - all else are ints
        if "freq" in words[0]:
          self.cfg_dict[words[0]] = float(words[2]);
        else:
          self.cfg_dict[words[0]] = int(words[2]);
    return True;
  def rd_pod_cfg( self, filename ):
    # 1,0 1.0.clk_100.0.0.u2_pod
    pod_cfg_list = file2list( filename );
    for each_line in pod_cfg_list:
      words = " ".join(each_line.split()).split(' ') + [None] * 3;
      hub_pod_tuple = words[0];
      hub_pod_name  = words[1];
      words = hub_pod_tuple.split(",") + [None] * 8; # Avoid IndexError
      i = int( words[0], 10 );# Hub 0-255
      j = int( words[1], 10 );# Pod 0-255
      words = hub_pod_name.split(".") + [None] * 8; # Avoid IndexError
      self.rle_hub_pod_dict[ words[2]+"."+words[5] ] = (i,j);
    return;
  def wr ( self, cmd, data ):
    return;
  def rd_ctrl( self ):
    return 0;
  def wr_ctrl( self, data ):
    return;
# def rd_status( self ):
#   self.cfg_dict['hw_id']       = ( hwid_data & 0xFFFF0000 ) >> 16;
  def close ( self ):
    return;

##############################################################################
class sump3_hw:
  def __init__ ( self, parent, backdoor, addr ):
    self.bd     = backdoor;
    self.parent = parent;
    self.status = ("",0x00);

    self.cfg_dict = {};
    self.cfg_dict['hw_rev_expected'] = 0x01;# Rev this SW was tested against
    self.rle_hub_pod_list = [[]];# List of Lists of Hub#, Pod# and Names in 0.Hub.0.Pod format
    self.rle_hub_pod_dict = {};# Lookup where key is "hub_name.pod_name" and returns (hub_i,pod_j)
    self.rom_signal_source = None;
    self.rom_view_name     = None;

    self.addr_ctrl = addr;
    self.addr_data = addr + 0x4;

    self.hw_id                       = 0x53;# Constant meaning "S3" for "Sump3"

    self.cmd_state_idle              = 0x00;
    self.cmd_state_arm               = 0x01;
    self.cmd_state_reset             = 0x02;# Always Reset before Arm.
    self.cmd_state_init              = 0x03;# Initialize RAM prior to Arm
    self.cmd_state_sleep             = 0x04;# Drops sump_is_awake line for clock gating

    self.cmd_rd_hw_id_rev            = 0x0b;
    self.cmd_rd_ana_ram_width_len    = 0x0c;
    self.cmd_rd_tick_freq            = 0x0d;
    self.cmd_rd_ana_first_sample_ptr = 0x0e;
    self.cmd_rd_ram_data             = 0x0f;
    self.cmd_rd_dig_first_sample_ptr = 0x10;
    self.cmd_rd_dig_ck_freq          = 0x11;
    self.cmd_rd_dig_ram_width_len    = 0x12;
    self.cmd_rd_record_profile       = 0x13;
    self.cmd_rd_trigger_src          = 0x14;
    self.cmd_rd_view_rom_kb          = 0x15;
#   self.cmd_rd_user_stat            = 0x16;

    self.cmd_wr_thread_lock_set      = 0x1c;
    self.cmd_wr_thread_lock_clear    = 0x1d;
    self.cmd_wr_thread_pool_set      = 0x1e;
    self.cmd_wr_thread_pool_clear    = 0x1f;

    self.cmd_wr_user_ctrl            = 0x20;
    self.cmd_wr_record_config        = 0x21;
    self.cmd_wr_tick_divisor         = 0x22;

    self.cmd_wr_trig_type            = 0x23;
    self.cmd_wr_trig_digital_field   = 0x24;# Correspond to Event Bits
    self.cmd_wr_trig_analog_field    = 0x25;# Analog CH and Comparator Value
#   self.cmd_wr_trig_position        = 0x26;# Num post trigger samples to capture
    self.cmd_wr_ana_post_trig_len    = 0x26;# Num post trigger samples to capture
    self.cmd_wr_trig_delay           = 0x27;
    self.cmd_wr_trig_nth             = 0x28;
    self.cmd_wr_ram_rd_ptr           = 0x29;
    self.cmd_wr_dig_post_trig_len    = 0x2a;
    self.cmd_wr_ram_rd_page          = 0x2b;
#   self.cmd_wr_user_stim            = 0x2c;
#   self.cmd_wr_user_addr            = 0x2d;

    self.cmd_rd_rle_hub_config        = 0x30;# Number of RLE Hubs
    self.cmd_rd_rle_pod_config        = 0x31;# Number of RLE Pods for selected Hub
    self.cmd_wr_rle_pod_inst_addr     = 0x32;# HubNum,PodNum,RegNum + Broadcast Bits
    self.cmd_wr_rle_pod_data          = 0x33;# Register access to Pod Regs
    self.cmd_rd_rle_pod_trigger_src   = 0x34;# Pod Instance of trigger source
    self.cmd_wr_rle_pod_trigger_width = 0x35;
    self.cmd_rd_rle_hub_ck_freq       = 0x36;# u12.20 MHz for selected Hub
    self.cmd_wr_rle_hub_user_addr     = 0x37;# user_addr[31:0]
    self.cmd_wr_rle_hub_user_wr_d     = 0x38;# user_wr_d[31:0]
    self.cmd_rd_rle_hub_user_rd_d     = 0x39;# user_rd_d[31:0]
    self.cmd_rd_rle_hub_hw_cfg        = 0x3a;
    self.cmd_rd_rle_hub_instance      = 0x3c;
    self.cmd_rd_rle_hub_name_0_3      = 0x3d;
    self.cmd_rd_rle_hub_name_4_7      = 0x3e;
    self.cmd_rd_rle_hub_name_8_11     = 0x3f;

    # See sump3_rle_pod.v
    self.rle_pod_addr_pod_hw_cfg      = 0x00;# RLE HW Rev, View ROM En, Pod Enabled
    self.rle_pod_addr_trigger_latency = 0x02;# Trigger latency bytes ( Read Only )
    self.rle_pod_addr_trigger_cfg     = 0x03;# Trigger Location, Trigger Type  
    self.rle_pod_addr_trigger_en      = 0x04;# Trigger Enable bits 0-31        
    self.rle_pod_addr_rle_bit_mask    = 0x05;# RLE Bit Mask bits 0-31              
#   self.rle_pod_addr_rle_bulk_mask   = 0x06;# RLE Bulk Mask bits 0-31              
    self.rle_pod_addr_comp_value      = 0x07;# Comparator Value                
    self.rle_pod_addr_ram_page_ptr    = 0x08;# Page[7:0], Pointer[19:0]        
    self.rle_pod_addr_ram_data        = 0x09;# RAM Data[31:0] from Page Mux    
    self.rle_pod_addr_pod_ram_cfg     = 0x0A;# Num of Events, Addr Bits, TimeStamp bits
    self.rle_pod_addr_pod_user_ctrl   = 0x0B;# Ext user control bits           
#   self.rle_pod_addr_pod_user_stim   = 0x0C;# Ext user stimulus bits           
#   self.rle_pod_addr_pod_user_stat   = 0x0D;# Ext user status bits           
    self.rle_pod_addr_triggerable     = 0x0E;# Triggerable Bits 0-31
    self.rle_pod_addr_pod_trigger_src = 0x0F;# Triggger Source                
    self.rle_pod_addr_pod_view_rom_kb = 0x10;# Size of View ROM in 1kb units  
    self.rle_pod_addr_pod_instance    = 0x1C;# 0-255 Instance Number
    self.rle_pod_addr_pod_name_0_3    = 0x1D;# ASCII Name of Pod
    self.rle_pod_addr_pod_name_4_7    = 0x1E;# ASCII Name of Pod
    self.rle_pod_addr_pod_name_8_11   = 0x1F;# ASCII Name of Pod

    self.rle_pod_trig_disabled        = 0x0;# D[3:0]
    self.rle_pod_trig_pattern_match   = 0x1;# 
    self.rle_pod_trig_or_rising       = 0x2;# 
    self.rle_pod_trig_or_falling      = 0x3;# 
    self.rle_pod_trig_and_rising      = 0x4;# 
    self.rle_pod_trig_and_falling     = 0x5;# 
    self.rle_pod_trig_or_any_edge     = 0x6;# 

#   self.rle_pod_trig_position_10     = 0x00;# D[7:0]
#   self.rle_pod_trig_position_25     = 0x10;# 
#   self.rle_pod_trig_position_50     = 0x20;# 
#   self.rle_pod_trig_position_75     = 0x30;# 
#   self.rle_pod_trig_position_90     = 0x40;# 

    self.rle_pod_trig_position_10     = 0x40;# D[7:0]
    self.rle_pod_trig_position_25     = 0x30;# 
    self.rle_pod_trig_position_50     = 0x20;# 
    self.rle_pod_trig_position_75     = 0x10;# 
    self.rle_pod_trig_position_90     = 0x00;# 

    self.vrbyte_rom_start             = 0xF0;# View ROM Byte codes
    self.vrbyte_rom_end               = 0xE0;# View ROM Byte codes

    self.sw_force_trig               = 0x80000000;# Write this to cmd_state_arm reg

    self.trig_and_ris                = 0x00;# Bits AND Rising
    self.trig_and_fal                = 0x01;# Bits AND Falling
    self.trig_or_ris                 = 0x02;# Bits OR  Rising
    self.trig_or_fal                 = 0x03;# Bits OR  Falling
    self.trig_analog_ris             = 0x04;# ADC Level Rising
    self.trig_analog_fal             = 0x05;# ADC Level Falling
    self.trig_in_ris                 = 0x06;# External Input Trigger Rising
    self.trig_in_fal                 = 0x07;# External Input Trigger Falling

    self.status_armed                = 0x01;# Engine is Armed, ready for trigger
    self.status_pre_trig             = 0x02;# Engine has pre-trig filled 
    self.status_triggered            = 0x04;# Engine has triggered                  
    self.status_acquired             = 0x08;# Engine has post-trig filled        

  def rd_ctrl( self ):
    return self.bd.rd( self.addr_ctrl )[0];

  def wr_ctrl ( self, cmd ):
    self.bd.wr( self.addr_ctrl, [ cmd  ] );

  def wr ( self, cmd, data ):
#   print("%08x %08x" % ( cmd, data ) );
    self.bd.wr( self.addr_ctrl, [ cmd  ] );
    self.bd.wr( self.addr_data, [ data ] );

  def rd( self, addr, num_dwords = 1):
    # Note: addr of None means use existing ctrl address and just read data
    if ( addr != None ):
      self.bd.wr( self.addr_ctrl, [ addr ] );
    dword_cnt = num_dwords;
    percent = 0;
    percent_total = ((1.0)*num_dwords );
    rts = [];
    while ( dword_cnt > 1024 ):
      rts += self.bd.rd( self.addr_data, num_dwords = 1024, repeat = True);
      dword_cnt -= 1024;
      # This takes a while, so calculate and print percentage as it goes by
#     if ( (float(len(rts)) / percent_total) >= percent ):
#       perc_str = ( str( int(100*percent) ) + "%");
#       txt = ("Downloading samples " + perc_str );
#       draw_header( self.parent , txt); print( txt );
#       percent += .10;
    rts += self.bd.rd( self.addr_data, num_dwords = dword_cnt, repeat = True);
    return rts;


  def rd_pod( self, hub, pod, reg, num_dwords = 1 ):
    dword_list = [];
    if num_dwords == 1:
      if hub != None and pod != None and reg != None:
        self.wr( self.cmd_wr_rle_pod_inst_addr, ((hub<<16)+(pod<<8)+(reg<<0)) );
        dword_list += [ self.rd( self.cmd_wr_rle_pod_data )[0] ];
      else:
        dword_list += [self.bd.rd( self.addr_data )[0]];
    else:
      if hub != None and pod != None and reg != None:
        self.wr( self.cmd_wr_rle_pod_inst_addr, ((hub<<16)+(pod<<8)+(reg<<0)) );
        dword_list = self.rd( addr=self.cmd_wr_rle_pod_data,num_dwords=num_dwords);
      else:
        dword_list = self.rd( addr=self.cmd_wr_rle_pod_data,num_dwords=num_dwords);
    return dword_list;

  def wr_pod( self, hub, pod, reg, data ):
    self.wr( self.cmd_wr_rle_pod_inst_addr, (hub<<16)+(pod<<8)+(reg<<0) );
    self.wr( self.cmd_wr_rle_pod_data, data );
    return;


  def dword_to_ascii( self, dword ):
    rts = "";
    rts += chr( ( dword & 0xFF000000 ) >> 24 );
    rts += chr( ( dword & 0x00FF0000 ) >> 16 );
    rts += chr( ( dword & 0x0000FF00 ) >>  8 );
    rts += chr( ( dword & 0x000000FF ) >>  0 );
    return rts;

  def rd_cfg( self ):
    hwid_data     = self.rd( self.cmd_rd_hw_id_rev     )[0];

    self.cfg_dict['hw_id']           = ( hwid_data & 0xFF000000 ) >> 24;
    self.cfg_dict['hw_rev']          = ( hwid_data & 0x00FF0000 ) >> 16;
    self.cfg_dict['rle_hub_num']     = ( hwid_data & 0x0000FF00 ) >> 8;
    self.cfg_dict['bus_busy_bit_en'] = ( hwid_data & 0x00000010 ) >> 4;
    self.cfg_dict['thread_lock_en']  = ( hwid_data & 0x00000008 ) >> 3;
    self.cfg_dict['view_rom_en']     = ( hwid_data & 0x00000004 ) >> 2;
    self.cfg_dict['ana_ls_enable']   = ( hwid_data & 0x00000002 ) >> 1;
    self.cfg_dict['dig_hs_enable']   = ( hwid_data & 0x00000001 ) >> 0;

    # If we can't read the hw_id then we have nothing. Hard stop.
    if self.cfg_dict['hw_id'] != self.hw_id :
      return False;

    if self.cfg_dict['ana_ls_enable'] == 1:
      ana_ram_data  = self.rd( self.cmd_rd_ana_ram_width_len )[0];
      freq_data     = self.rd( self.cmd_rd_tick_freq     )[0];
    else:
      ana_ram_data  = 0x00000000;
      freq_data     = 0x00000000;

    if self.cfg_dict['dig_hs_enable'] == 1:
      dig_ram_data  = self.rd( self.cmd_rd_dig_ram_width_len )[0];
    else:
      dig_ram_data  = 0x00000000;

    self.cfg_dict['ana_ram_depth']   = ( ana_ram_data  & 0x00FFFFFF ) >> 0;
    self.cfg_dict['ana_ram_width']   = ( ana_ram_data  & 0xFF000000 ) >> 24;
    self.cfg_dict['dig_ram_depth']   = ( dig_ram_data  & 0x00FFFFFF ) >> 0;
    self.cfg_dict['dig_ram_width']   = ( dig_ram_data  & 0xFF000000 ) >> 24;
    self.cfg_dict['tick_freq']       =  float(freq_data) / float( 0x00100000 );# u12.20

    self.view_rom_list = [];    # Gets populated with View ROM Contents from Hardware
    self.no_view_rom_list = []; # Gets populated with Hub+Pod names and number of signal
    # If the Sump3 core has a view rom, process it
    if self.cfg_dict['view_rom_en'] == 1:
      rom_byte_list = self.rd_core_view_rom();
      self.view_rom_list += self.parse_view_rom( rom_byte_list=rom_byte_list, hub=0, pod=0, inst=0 );

    rle_hub_cnt   = self.rd( self.cmd_rd_rle_hub_config)[0];
#   print("RLE Hub Count is %d" % rle_hub_cnt );
    log( self.parent , ["RLE Hub Count is %d" % rle_hub_cnt] );
    hub_list = [];
    for i in range(0,rle_hub_cnt):
      self.wr( self.cmd_wr_rle_pod_inst_addr, (i << 16) );
      rle_pod_cnt   = self.rd( self.cmd_rd_rle_pod_config)[0];
#     print("  RLE Hub #%d has %d Pods" % ( i, rle_pod_cnt ) );

      hub_instance  = self.rd( self.cmd_rd_rle_hub_instance)[0];
      hub_hw_cfg    = self.rd( self.cmd_rd_rle_hub_hw_cfg)[0];
      if ( hub_hw_cfg & 0x00000001 ) == 0:
        hub_name_0_3  = self.rd( self.cmd_rd_rle_hub_name_0_3)[0];
        hub_name_4_7  = self.rd( self.cmd_rd_rle_hub_name_4_7)[0];
        hub_name_8_11 = self.rd( self.cmd_rd_rle_hub_name_8_11)[0];
        hub_name =  self.dword_to_ascii( hub_name_0_3 );
        hub_name += self.dword_to_ascii( hub_name_4_7 );
        hub_name += self.dword_to_ascii( hub_name_8_11 );
        hub_name = hub_name.replace(" ","");
      else:
        hub_name = "%d" % i;

      # Instances are only for when you have multiple instances of same name
      hub_full_name = "%d.%d.%s" % (i,hub_instance,hub_name);
      if hub_instance != 0:
        name = hub_full_name;
      else:
        name = "%s"    % (             hub_name);

#     print("  RLE Hub %d %s has %d Pods" % ( i, name, rle_pod_cnt ) );
      log( self.parent , [ "  RLE Hub %d %s has %d Pods" % ( i, name, rle_pod_cnt ) ] );

      pod_list = [];
      for j in range(0,rle_pod_cnt):
        self.bd.wr( self.addr_ctrl, [ 0x32 ] );
        self.bd.wr( self.addr_data, [ (i<<16)+(j<<8)+(0x00<<0) ] );
        self.bd.wr( self.addr_ctrl, [ 0x33 ] );
        dword = self.bd.rd( self.addr_data )[0];
        pod_hw_cfg    = self.rd_pod( hub=i,pod=j,reg=self.rle_pod_addr_pod_hw_cfg )[0];
        pod_ram_cfg   = self.rd_pod( hub=i,pod=j,reg=self.rle_pod_addr_pod_ram_cfg )[0];
        pod_num_data_bits = ( pod_ram_cfg & 0x00FFFF00 ) >> 8;
        pod_instance  = self.rd_pod( hub=i,pod=j,reg=self.rle_pod_addr_pod_instance  )[0];
        if ( pod_hw_cfg & 0x00000020 ) == 0:
          pod_name_0_3  = self.rd_pod( hub=i,pod=j,reg=self.rle_pod_addr_pod_name_0_3  )[0];
          pod_name_4_7  = self.rd_pod( hub=i,pod=j,reg=self.rle_pod_addr_pod_name_4_7  )[0];
          pod_name_8_11 = self.rd_pod( hub=i,pod=j,reg=self.rle_pod_addr_pod_name_8_11 )[0];
          pod_name =  self.dword_to_ascii( pod_name_0_3 );
          pod_name += self.dword_to_ascii( pod_name_4_7 );
          pod_name += self.dword_to_ascii( pod_name_8_11 );
          pod_name = pod_name.replace(" ","");
        else:
          pod_name = "%d" % j;# pod_name_en parameter was 0
        pod_full_name = "%d.%d.%s" % (j,pod_instance,pod_name);
        if pod_instance != 0:
          name = pod_full_name;
        else:
          name = "%s"    % (             pod_name);
        pod_list += [ hub_full_name+"."+pod_full_name ];

#       print("    RLE Hub %d, Pod #%d %s : HW Rev = %02x" % (i,j, name, ((pod_hw_cfg & 0xFF000000)>>24)));
        log( self.parent , [ "    RLE Hub %d, Pod #%d %s : HW Rev = %02x" % (i,j, name, ((pod_hw_cfg & 0xFF000000)>>24))  ] );
        # If this pod has a view rom, process it
        if ( pod_hw_cfg & 0x00000002 ) != 0:
          pod_view_rom_kb = self.rd_pod( hub=i,pod=j,reg=self.rle_pod_addr_pod_view_rom_kb )[0];
          rom_byte_list = self.rd_pod_view_rom( hub=i,pod=j,size_kb=pod_view_rom_kb );
          self.view_rom_list += self.parse_view_rom( rom_byte_list=rom_byte_list, hub=i, pod=j, inst=pod_instance );

        # Generate a fake view rom with no signal names in case there is no rom at all
        # Use the embedded hub+pod names for signal name
        # TODO: This doesn't handle pod_name_en == 0 . Should replace name with index number
        # TODO: This doesn't handle instance numbers with same name + generates
        norom_view_bits   = ( pod_hw_cfg & 0x00000100 ) != 0;
        norom_view_bytes  = ( pod_hw_cfg & 0x00000200 ) != 0;
        norom_view_words  = ( pod_hw_cfg & 0x00000400 ) != 0;
        norom_view_dwords = ( pod_hw_cfg & 0x00000800 ) != 0;
        view_name = hub_name + "." + pod_name;
        self.no_view_rom_list += [ "create_view %s" % view_name ];
        self.no_view_rom_list += [ "create_group %s" % view_name ];

        if norom_view_bytes == 1 or norom_view_words == 1 or norom_view_dwords == 1:
          if norom_view_bytes == 1:
            entity_size = 8;
          elif norom_view_words == 1:
            entity_size = 16;
          elif norom_view_dwords == 1:
            entity_size = 32;
          bits_remaining = pod_num_data_bits;
          start_index = 0;
          rip_list = [];
          while ( bits_remaining > 0 ):
            if ( bits_remaining < entity_size ):
              stop_index = start_index + bits_remaining -1;
            else:
              stop_index = start_index + entity_size -1;
            if start_index == stop_index:
              sig_name = view_name.replace(".","_") + "[%d]" % ( stop_index );
              rip_list += [ "create_signal %s -source %s[%d]" % ( sig_name, view_name, stop_index )];
            else:
              sig_name = view_name.replace(".","_") + "[%d:%d]" % ( stop_index, start_index );
              rip_list += [ "create_signal %s -source %s[%d:%d]" % ( sig_name, view_name, stop_index, start_index )];
            bits_remaining -= entity_size;
            start_index += entity_size;
#         print( rip_list );
          rip_list.reverse();# Place top numbers on top
          self.no_view_rom_list += rip_list;
        # Default to bits
        else:
          for k in range(0, pod_num_data_bits ):
            sig_name = view_name.replace(".","_") + "_" + "%d" % k;
            self.no_view_rom_list += [ "create_signal %s -source %s[%d]" % ( sig_name, view_name, k) ];
        self.no_view_rom_list += [ "end_group", "end_view", "add_view" ];

      hub_list += [ pod_list ];

    self.rle_hub_pod_dict = {};
    for (i,each_pod_list) in enumerate( hub_list ):
      for (j,each_pod) in enumerate( each_pod_list ):
        # 1,0 1.0.clk_100.0.0.u2_pod
#       print("%d,%d %s" % ( i,j,each_pod) );
        # Make a name only dictionary like this foo["clk_100.u2_pod"] = (1,0)
        words = each_pod.split(".") + [None] * 8; # Avoid IndexError
        self.rle_hub_pod_dict[ words[2]+"."+words[5] ] = (i,j);

        # For generates with instances, add "clk_100.u2_pod.0]
        self.rle_hub_pod_dict[ words[2]+"."+words[5]+"."+words[4] ] = (i,j);
    self.rle_hub_pod_list = hub_list;

    file_path = self.parent.vars["sump_path_dbg"];
    file_name = os.path.join( file_path,"viewrom_parsed.txt" );
    list2file( file_name, self.view_rom_list );
    file_name = os.path.join( file_path,"viewrom_synthetic.txt" );
    list2file( file_name, self.no_view_rom_list );

    if len( self.view_rom_list ) == 0:
      self.view_rom_list = self.no_view_rom_list[:];
    else:
      self.merge_view_rom_no_view_rom();

#   dump_list = [];
#   for each in self.rle_hub_pod_list:
#     dump_list += [str(each)];
#   list2file("rle_hub_pod_list.txt", dump_list );

    self.expand_view_rom_generates();

    return True;

# expand_view_rom_generates(): If generates are used for multiple pod 
# instances, support placing a "*" in the View ROM that gets expanded
# out to each generate instance
#
# self.rle_hub_pod_list
#    __ Index      ___ Index
#   / _ Generate  / __ Generate Instance
#  / /           / /
# '0.0.ck100_hub.0.0.u0_pod',
# '0.0.ck100_hub.1.0.u1_pod', 
# '0.0.ck100_hub.2.1.u1_pod', 
# '0.0.ck100_hub.3.2.u1_pod', 
# '0.0.ck100_hub.4.3.u1_pod'
# WARNING: This doesn't handle generate instanced on hubs, only pods!!
# When generates are used, the view ROM can specify ".*" for the instance
# and this routine will replace all ".*" with mu
  def expand_view_rom_generates( self ):
    parsing_jk = False;
    org_list = self.view_rom_list[:];
    new_list = [];
    top_type = "";
    group_cnt = 0;
    for each in org_list:
#     if ( "*" in each and "create_view" in each ):
#     if ( not parsing_jk and "*" in each and "create_signal" in each ):
#     if ( not parsing_jk and "*" in each and "create_group" in each ):
#     if ( not parsing_jk and "*" in each ):
      if ( not parsing_jk and "*" in each and
           ( "create_view" in each or "create_group" in each ) ):
        top_type = "";
        parsing_jk = True;
        parse_list = []; 
        if ( "create_view" in each ):
          top_type = "end_view";
        elif ( "create_group" in each ):
          top_type = "end_group";
          group_cnt = 0;
#       else:
#         self.parent.log( ["ERROR-5552368 : Invalid '*' in: %s" % ( each ) ]);
#         print( "ERROR-5552368 : Invalid '*' in: %s" % ( each ) );
#         new_list += [ each ];
#       print("top_type == %s" % top_type );
      if not parsing_jk:
        new_list += [ each ];
      else:
        parse_list += [each ];
#       if ( "end_view" in each ):
#       if ( "end_source" in each ):
#       if ( "end_source" in each or "end_view" in each ):
        if ( "create_group" in each and top_type == "end_group" ):
          group_cnt += 1;# Keep track of group hierarchy
#         print("group_cnt = %d" % group_cnt );

        if ( top_type in each and top_type == "end_group" ):
          group_cnt -= 1;# Keep track of group hierarchy
#         print("group_cnt = %d" % group_cnt );

        if ( top_type in each and top_type != "" and group_cnt == 0 ):
          parsing_jk = False;
          # Iterate the view and look for:
          # create_signal u1_pod_e[0] -source ck100_hub.u1_pod.*[0]
          # If found, iterate the self.rle_hub_pod_list and find any 
          # matches. For each instance match, create a unique new view
          # that replaces any ".*" with ".n" where n is the instance
          # numbers.
          found_jk = False;
          match_list = [];
          for each_line in parse_list:
            if "create_signal" in each_line and ".*" in each_line and found_jk == False:
              words = each_line.split(" ") + [None]*8;# Avoid IndexError
              if words[2] == "-source":
                hub_pod_rip = words[3];
                words_hier = hub_pod_rip.split(".");
                if "*" in words_hier[2]:
                  hub_name = words_hier[0];
                  pod_name = words_hier[1];
                  found_jk = True; 
          if found_jk:
            generate_instance_list = [];
#           print("----");
            for each_hub_pod in self.rle_hub_pod_list:
#             print("----:");
#             print( each_hub_pod );
              for each_each in each_hub_pod:
#               print("----::");
#               print( each_each );
                words = each_each.split(".") + [None]*8;# Avoid IndexError
                if words[2] == hub_name and words[5] == pod_name:
                  generate_instance_list += [ words[4] ];
            for each_generate_instance in generate_instance_list:
              for each_line in parse_list:
                new_line = each_line.replace("*", each_generate_instance );
                new_list += [ new_line ];
    
#   list2file("new_list.txt", new_list );
#   list2file("parse_list.txt", parse_list );
    self.view_rom_list = new_list[:];
    return;

  # It's possible for a design to have a view rom, but also have some pods that
  # aren't specified in that view rom. Search for these pods and merge
  def merge_view_rom_no_view_rom( self ):
    log( self.parent , ["merge_view_rom_no_view()"] );
#   print("merge_view_rom_no_view_rom()");
    no_view_list = [];
    for each in self.no_view_rom_list:
      words = each.strip().split() + [None] * 4;# Avoid IndexError
      if words[0] == "create_view":
        no_view_list += [ words[1] ];# ie "ck100_hub.u0_pod"
    for each_view in no_view_list:
      found = False;
      for each in self.view_rom_list:
#       print("%s : %s" % ( each_view, each ) );
        words = each.strip().split() + [None] * 4;# Avoid IndexError
#       if words[0] == "create_signal" and words[2] == "-source":
        if words[2] == "-source":
          if each_view in words[3]:
            found = True; break;
      if not found:
#       print("appending synthetic view for %s" % each_view);
        log( self.parent , ["appending synthetic view for %s" % each_view] );
        parse_jk = False;
        for each in self.no_view_rom_list:
          words = each.strip().split() + [None] * 4;# Avoid IndexError
          if words[0] == "create_view" and words[1] == each_view:
            parse_jk = True;
          if parse_jk:
            self.view_rom_list += [ each ];
#           print( each );
          if words[0] == "add_view":
            parse_jk = False;
    return;



  # A View ROM starts with a 0xF0 "ROM Start" byte and ends with 0xE0 "ROM End" byte 
  # The way Verilog assign works, the ROM contents are actually reversed. The 1st
  # DWORD read will be 0xXXXXXXE0. For reading the ROM content, read the 1st DWORD
  # and make sure 0xE0 is at D[7:0] location. Then keep on reading DWORDs until two
  # DWORDs of 0x00000000. The 0xF0 "ROM Start" will be just before that on some
  # unpredictable 1 of 4 byte position within a DWORD. The Verilog must have a 
  # 64'd0 postamble before the 0xF0 "ROM Start" so that software knows when to stop
  # reading.
  # Example:
  #  e5e5e1e0
  #  ...
  #  00f0f168
  #  00000000
  #  00000000
  # ROMs will always end with a string of 8 0x00 bytes. The only 4 byte binary params 
  # are for vectors with 16 bits each for bottom and top rip points. 
  # A vector like foo[0:0] is not possible. Regardless of byte alignment, any DWORD 
  # of 0x00000000 will safely indicate that the ROM has ended. Just searching for 0xF0
  # start is not possible since that value could be a binary bit index for a signal.
  def rd_core_view_rom(self):
    rts = [];
#   print("Core View ROM Contents");
    data_list = [];
    view_rom_kb = self.rd( self.cmd_rd_view_rom_kb )[0];
    rom_length = int( view_rom_kb*1024/32 );
    rts = self.rd_any_rom( rom_type = "core", rom_addr = None, rom_length = rom_length );
    return rts;

  def rd_pod_view_rom(self, hub, pod, size_kb ):
    rts = [];
    self.wr_pod(hub=hub,pod=pod,reg=self.rle_pod_addr_ram_page_ptr,data=0x80000000);
    rom_length = int( size_kb * 1024 / 32 );
    rts = self.rd_any_rom( rom_type = "pod", rom_addr = (hub,pod), rom_length = rom_length );
    return rts;

  def rd_any_rom( self, rom_type, rom_addr, rom_length ):
    rts = [];
    if rom_type == "core":
      self.wr( self.cmd_wr_ram_rd_page, 0x200 );# ROM
      self.wr( self.cmd_wr_ram_rd_ptr,  0x0000 );
      data_list = self.rd( self.cmd_rd_ram_data, num_dwords=1);
    else:
      (hub,pod) = rom_addr;
      data_list = self.rd_pod(hub=hub,pod=pod,reg=self.rle_pod_addr_ram_data);

    if ( ( data_list[0] & 0x000000FF ) == self.vrbyte_rom_end ):
      remaining_dwords = int( rom_length )-1;
      while remaining_dwords > 0:
        if remaining_dwords > 64:
          dwords_to_read = 64;
        else:
          dwords_to_read = remaining_dwords;
        if rom_type == "pod":
          dwords_to_read = 1;

        if rom_type == "core":
          data_list += self.rd( self.cmd_rd_ram_data, num_dwords=dwords_to_read);
        else:
          data_list += self.rd_pod(hub=None,pod=None,reg=None);# Note the burst read
        remaining_dwords -= dwords_to_read;

      found_rom_end = False;
      for i in range( 0, len( data_list )-1 ):
#       print("%d %08x" % ( i, data_list[i] ));
        if ( data_list[i]   == 0x00000000 and
             data_list[i+1] == 0x00000000     ):
          data_list = data_list[0:i+2];
          found_rom_end = True;
          break;
        
      if found_rom_end:
        rom_dword_cnt = len(data_list);
        a = 100 * float( rom_dword_cnt / rom_length );
        b = rom_length * 32 / 1024;
#       print("ROM Size is %02.0f%% full of %d Kbits" % ( a, b) );
        log( self.parent , [ "ROM Size is %02.0f%% full of %d Kbits" % ( a, b) ] );

        for each_dword in data_list:
          byte_list = self.dword2bytes( each_dword );
          rts += byte_list;
        rts = list(reversed(rts));# Put ROM in proper order for byte parsing

        # Dump hex bytes to files for debugging 
        if rom_type == "core":
          file_name = "viewrom_core";
        else:
          file_name = "viewrom_pod_%d_%d" % ( hub, pod );
        file_path = self.parent.vars["sump_path_dbg"];
        file_name = os.path.join( file_path, file_name );

        dump_list = [ "%02x" % each for each in rts ];# list comprehension
        list2file( (file_name + "_hex.txt") , dump_list );
        dbg_list = self.viewrom_debugger( byte_list = rts );
        list2file( (file_name + "_txt.txt") , dbg_list );
    return rts;

  def viewrom_debugger( self, byte_list ):
    rts = [];
    code_dict = {};
    code_dict[0xF0] = ("ROM_Start"              , 0, False );
    code_dict[0xF1] = ("View_Name"              , 0, True  );
    code_dict[0xF2] = ("Signal_Source_This_Pod" , 0, False );
    code_dict[0xF3] = ("Signal_Source_Hub_Pod"  , 2, False );
    code_dict[0xF4] = ("Signal_Source_Name"     , 0, True  );
    code_dict[0xF5] = ("Group_Name"             , 0, True  );
    code_dict[0xF6] = ("Signal_Bit"             , 2, True  );
    code_dict[0xF7] = ("Signal_Vector"          , 4, True  );
    code_dict[0xF8] = ("FSM_State"              , 1, True  );
    code_dict[0xF9] = ("Signal_Vector_Group"    , 4, True  );
    code_dict[0xFD] = ("bd_shell"               , 0, True  );
    code_dict[0xFE] = ("attribute"              , 0, True  );
    code_dict[0xE0] = ("ROM_End"                , 0, False );
    code_dict[0xE1] = ("View_End"               , 0, False );
    code_dict[0xE2] = ("Source_End"             , 0, False );
    code_dict[0xE3] = ("Source_End"             , 0, False );
    code_dict[0xE4] = ("Source_End"             , 0, False );
    code_dict[0xE5] = ("Group_End"              , 0, False );

    # Ignore the 1st 8 bytes of 0x00
    parsing_ascii = False;
    ascii_bool = False;
    parm_cnt = 0;
    txt = "";
    line = "";
    for each_byte in byte_list[8:]:
      if parsing_ascii:
        if each_byte >= 0xE0:
          parsing_ascii = False;
        else:
          txt = txt + "%c" % each_byte;
      if not parsing_ascii:
        if parm_cnt != 0:
          line = line + "%02x " % each_byte;
          parm_cnt = parm_cnt - 1;
        else:
          if ( code_dict.get( each_byte ) == None ): 
            line = line + "E! %02x " % each_byte;
          else:
            ( name, parm_cnt, ascii_bool ) = code_dict[ each_byte ];
            # Dump any queued info
            if line != "" or txt != "":
              rts += ["%s : %s" % ( line, txt ) ];
            line = ""; txt = "";

            # Start new line
            line = "%02x : %s :" % ( each_byte, name );
            if parm_cnt == 0 and not ascii_bool:
              rts += ["%s : %s" % ( line, txt ) ];
              line = ""; txt = "";
        if parm_cnt == 0 and ascii_bool:
          parsing_ascii = True;
    return rts;


  #########################################
  # Code ParmBytes ASCII   Definition
  # F0   0                 ROM Start
  # F1   0         Yes     View Name
  # F2   0                 Signal Source - This Pod
  # F3   2                 Signal Source Hub-N,Pod-N
  # F4   0         Yes     Signal Source Hub-Name.Pod-Name or "analog_ls","digital_ls","digital_hs"
  # F5   0         Yes     Group Name
  # F6   2         Yes     Signal Bit source, Name
  # F7   4         Yes     Signal Vector Rip, Name
  # F8   1         Yes     FSM Binary State, Name
  # F9   4         Yes     Signal Vector Group, Name
  # FD   0         Yes     Reserved for possible bd_shell use   
  # FE   0         Yes     Attribute for last signal declaration
  #
  # E0   0                 ROM End
  # E1   0                 View End
  # E2   0                 Source End
  # E3   0                 Source End
  # E4   0                 Source End
  # E5   0                 Group End

# self.rom_signal_source = None;

# def view_rom_line( self, txt_line, hub, pod ):
  def view_rom_line( self, txt_line, hub, pod, inst ):
    words = txt_line.strip().split() + [None] * 8; # Avoid IndexError
    txt = "";
    src_name = self.rom_signal_source;# ie "digital_rle[0][0]"

    if words[0] == "f0":
      txt = "create_rom";
    elif words[0] == "f1":
      # For generates that with multiple instances, modify the name to "foo", "foo.1", "foo.2"
      if inst != 0:
        words[1] = words[1] + "." + ( "%d" % inst );
      txt = "create_view " + words[1];
      self.rom_view_name = words[1];
    elif words[0] == "f5" and words[1] != None:
      txt = "create_group " + words[1];
#   elif words[0] == "f5" and words[1] == None:
#     txt = "end_group";# HACK!         

    elif words[0] == "e0":
      txt = "end_rom";
    elif words[0] == "e1":
      txt = "end_view";
    elif words[0] == "e2" or \
         words[0] == "e3" or \
         words[0] == "e4"     :
      txt = "end_source";
    elif words[0] == "e5":
      txt = "end_group";

    elif words[0] == "f2":
      self.rom_signal_source = "digital_rle[%d][%d]" % ( hub, pod );
    elif words[0] == "f3":
      hub = int( words[1], 16 );
      pod = int( words[2], 16 );
      self.rom_signal_source = "digital_rle[%d][%d]" % ( hub, pod );
    elif words[0] == "f4":
      self.rom_signal_source = words[1];# Must be "analog_ls","digital_ls","digital_hs", or "u_hub.u_pod"
#     if "." in words[1]:
#       # self.rle_hub_pod_dict = {};# Lookup where key is "hub_name.pod_name" and returns (hub_i,pod_j)
#       if ( self.sump.rle_hub_pod_dict.get( words[1] ) == None ):
#         print("WARNING: Strange source key %s" % words[1] );
#         self.rom_signal_source = words[1];# Unknown
#       else:
#         (hub,pod) = self.sump.rle_hub_pod_dict[ words[1] ];
#         self.rom_signal_source = "digital_rle[%d][%d]" % ( hub, pod );
#     else:
#       self.rom_signal_source = words[1];# Must be "analog_ls","digital_ls","digital_hs"
    elif words[0] == "fd":
      txt = txt_line.replace("fd ","");# bd_shell command

    elif words[0] == "fe":
#     txt = "apply_attribute " + words[1];
      attrib_list = words[1].split(',');
      txt = "";
      for each_attrib in attrib_list:
        txt += "apply_attribute " + each_attrib + " ";
       
    elif words[0] == "f6":
      i = int(words[1]+words[2],16);
      txt = "create_signal " + words[3] + " -source " + src_name + ("[%d]" % i);
    elif words[0] == "f7":
      i = int(words[1]+words[2],16);
      j = int(words[3]+words[4],16);
      if i < j:
        (i,j) = (j,i); # Make sure bit-rip is 7:0 and NOT 0:7 ( swap )
      txt = "create_signal " + words[5] + " -source " + src_name + ("[%d:%d]" % (i,j));
    elif words[0] == "f9":
      i = int(words[1]+words[2],16);
      j = int(words[3]+words[4],16);
      if i < j:
        (i,j) = (j,i); # Make sure bit-rip is 7:0 and NOT 0:7 ( swap )
      txt = "create_bit_group " + words[5] + " -source " + src_name + ("[%d:%d]" % (i,j));
    elif words[0] == "f8":
      txt = "create_fsm_state " + words[1]+" " + words[2];
    else:
      txt = txt_line;
    return txt;

  # Given a ROM byte list, parse one or more views from it
# def parse_view_rom(self, rom_byte_list, hub, pod ):
  def parse_view_rom(self, rom_byte_list, hub, pod, inst ):
    rts = [];
    cmd_en   = True;
    ascii_en = False;
    byte_cnt = 0;# Number of Parm Bytes to parse next
    ascii_txt = "";
    cmd_txt = "";
    for byte in rom_byte_list:
      if byte_cnt != 0:
        cmd_txt += "%02x " % byte;
        byte_cnt = byte_cnt - 1;
      else:
        # ROM supports 7bit ASCII only.
        if ascii_en and byte >= 0x20 and byte <= 0x7F:
          ascii_txt += chr( byte );
        # End Line since non-ASCII
        else:  
#         # rom supports short cuts of "user_ctrl" for "sump_user_ctrl", etc.
#         shorthand_list = [ ("user_ctrl","sump_user_ctrl" ),
#                            ("user_stim","sump_user_stim" ),  ];
#         for (a,b) in shorthand_list: 
#           if a in ascii_txt and b not in ascii_txt:
#             ascii_txt = ascii_txt.replace(a,b);

#         txt = self.view_rom_line( cmd_txt + " " + ascii_txt, hub, pod );
#         txt = self.view_rom_line( cmd_txt + " " + ascii_txt, hub, pod, inst );
          txt = self.view_rom_line( cmd_txt + ascii_txt, hub, pod, inst );
#         rts += [ txt ];
          # if "apply_attribute" in txt, we need to apply it to last "create_*" line
          if "apply_attribute" in txt:
            txt = txt.replace("apply_attribute ","-");
            txt = txt.replace("uc[", "user_ctrl[");
            txt = txt.replace("=", " ");
            rts[-1] = rts[-1] + " " + txt;
          elif txt != "":
            rts += [ txt ];
#         else:
#           rts += [ txt ];


          cmd_txt = "";
          ascii_txt = "";
          ascii_en = False;# String was terminated with new command byte
          cmd_en = True;# This command byte will be processed next
      if cmd_en:
        cmd_txt = "%02x " % byte;
        if byte == 0xF0 : cmd_en = True;  byte_cnt = 0; ascii_en = False;
        if byte == 0xF1 : cmd_en = False; byte_cnt = 0; ascii_en = True;
        if byte == 0xF2 : cmd_en = True;  byte_cnt = 0; ascii_en = False;
        if byte == 0xF3 : cmd_en = False; byte_cnt = 2; ascii_en = False;
        if byte == 0xF4 : cmd_en = False; byte_cnt = 0; ascii_en = True;
        if byte == 0xF5 : cmd_en = False; byte_cnt = 0; ascii_en = True;
        if byte == 0xF6 : cmd_en = False; byte_cnt = 2; ascii_en = True;
        if byte == 0xF7 : cmd_en = False; byte_cnt = 4; ascii_en = True;
        if byte == 0xF8 : cmd_en = False; byte_cnt = 1; ascii_en = True;
        if byte == 0xF9 : cmd_en = False; byte_cnt = 4; ascii_en = True;
        if byte == 0xFD : cmd_en = False; byte_cnt = 0; ascii_en = True;
        if byte == 0xFE : cmd_en = False; byte_cnt = 0; ascii_en = True;
        if byte >= 0xE0 and byte <= 0xEF:
                          cmd_en = True;  byte_cnt = 0; ascii_en = False;
    return rts;


  # Given 0x04030201 return [ 0x01, 0x02, 0x03, 0x4 ]
  def dword2bytes(self, dword ):
    rts = [];
    rts += [( dword & 0x000000FF ) >> 0];
    rts += [( dword & 0x0000FF00 ) >> 8];
    rts += [( dword & 0x00FF0000 ) >> 16];
    rts += [( dword & 0xFF000000 ) >> 24];
    return rts;

  def rd_status( self ):
    # New status method doesn't care what the ctrl reg is set to.
    # The status bits show up on a read at the very top 8 bits.
    # This is better than old method that was reading status from data_reg
    # but required ctrl_reg to be set to armed or idle.
    # New method supports multiple software threads.
    if not self.parent.rd_status_legacy_en:
      status = self.bd.rd( self.addr_ctrl )[0];
      status = ( 0x1F000000 & status ) >> 24;
    else:
      status = self.rd( None )[0];
      status = status & 0x000000FF;
    if ( status == 0x00 ):
      str = "idle";
    elif ( ( status & self.status_acquired  ) != 0x00 ):
      str = "acquired";
    elif ( ( status & self.status_triggered ) != 0x00 ):
      str = "triggered";
    elif ( ( status & self.status_armed     ) != 0x00 and
           ( status & self.status_pre_trig  ) == 0x00     ):
      str = "pre-trig_fill";
    elif ( ( status & self.status_armed     ) != 0x00 ):
      str = "armed";
    else:
      str = "unknown %02x" % status ;
    self.status = ( str, status );
    return;

  def close ( self ):
    return;


##############################################################################
# functions to send Backdoor commands to BD_SERVER.PY over TCP Sockets
class Backdoor:
  def __init__ ( self, parent, ip, port, aes_key, aes_authentication ):
    self.aes     = None;
    self.aes_e2e = False;
    self.parent  = parent;
    try:
      import socket;
    except:
      raise RuntimeError("ERROR: socket is required");
    try:
      self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
      self.sock.connect( ( ip, port ) );# "localhost", 21567
      self.sock.settimeout(5); # Dont wait forever

      # Authentication Encryption only when Client and Server are different machines
      # End-2-End Encryption only when Server requests it
      laddr = self.sock.getsockname();# Server ("IP",port)
      raddr = self.sock.getpeername();# Client ("IP",port)
#     if laddr[0] != raddr[0] and aes_authentication == 1:
      if raddr[0] != "127.0.0.1" and aes_authentication == 1:
        try:
          from aes import AES;
          self.aes = AES( aes_key );
          self.aes_e2e = True;# Turn on Encryption for Authentication
          self.tx_tcp_packet("opensesame\n");  # Request for Authentication
          challenge = self.rx_tcp_packet();    # Wait for Challenge Question
          words = " ".join(challenge.split()).split(' ') + [None] * 2;
          if words[0] == "challenge":
            force_rej = 0;# Make this 1 to force a rejection
            self.tx_tcp_packet("response %08x\n" % (int(words[1],10)+force_rej));# Hex resp
            greetings = self.rx_tcp_packet();# Wait for "Greetings, ..." ACK back
            if "Greetings," in greetings:
              print( greetings );
              if "e2e" in greetings:
#               print("AES-256 End-2-End Encryption is required by bd_server.py.");
                log( self.parent , [ "AES-256 End-2-End Encryption is required by bd_server.py." ] );
                self.aes_e2e = True;
              else:
                self.aes_e2e = False;
            else:
#             print("ERROR: Authentication failed with %s" % greetings );
              log( self.parent , [ "ERROR: Authentication failed with %s" % greetings ] );
              self.sock = None;
          else:
#           print("ERROR: %s was not a challenge" % words[0] );
            log( self.parent , [ "ERROR: %s was not a challenge" % words[0] ] );
            self.sock = None;
        except:
#         print("ERROR: Unknown AES Install Failure. Missing aes.py perhaps?" );
          log( self.parent , [ "ERROR: Unknown AES Failure. Missing aes.py perhaps or invalid authentication key?" ] );
          self.sock = None;
      else:
#       print("AES Authentication not required.");
        log( self.parent , [ "AES Authentication not required." ] );
    except:
#     print("ERROR: Unable to open Socket %d on %s" % ( port, ip ) );
      log( self.parent , [ "ERROR: Unable to open Socket %d on %s" % ( port, ip ) ] );
      self.sock = None;
      try:
        (ip_name, ip_null, ip_num ) = socket.gethostbyaddr( ip );
#       print("ERROR: Computer %s at %s located but connection to Port %d refused!!" % ( ip_name, ip_num,port ) );
#       print("Either bd_server.py has not been started or a firewall is blocking the port.");
        log( self.parent , [ "ERROR: Computer %s at %s located but connection to Port %d refused!!" % ( ip_name, ip_num,port ) ] );
        log( self.parent , [ "Either bd_server.py has not been started or a firewall is blocking the port." ] );
      except:
#       print("ERROR: Server at %s not found!" % ( ip ) );
        log( self.parent , [ "ERROR: Server at %s not found!" % ( ip ) ] );
      return;
  def close ( self ):
    self.sock.close();

  def bs(self, addr, bitfield ):
    rts = self.rd( addr, 1 );
    data_new = rts[0] | bitfield[0];  # OR in some bits
    self.wr( addr, [data_new] );

  def bc(self, addr, bitfield ):
    rts = self.rd( addr, 1 );
    data_new = rts[0] & ~ bitfield[0];# CLR some bits
    self.wr( addr, [data_new] );

  def wr(self, addr, data, repeat = False ):
    if ( repeat == False ):
      cmd = "w";# Normal Write : Single or Burst with incrementing address
    else:
      cmd = "W";# Write Multiple DWORDs to same address
    payload = "".join( [cmd + " %08x" % addr] +
                       [" %08x" % int(d) for d in data] +
                       ["\n"] );
    self.tx_tcp_packet( payload );
    self.rx_tcp_packet();

  def quit(self):
    cmd = "q";
    payload = cmd+"\n";
    self.tx_tcp_packet( payload );
#   self.rx_tcp_packet();

  def rd( self, addr, num_dwords=1, repeat = False ):
    if ( repeat == False ):
      cmd = "r";# Normal Read : Single or Burst with incrementing address
    else:
      cmd = "k";# Read Multiple DWORDs from single address
#   payload = cmd + " %08x %08x\n" % (addr,(num_dwords-1));# 0=1DWORD,1=2DWORDs
    if num_dwords == 1:
      payload = cmd + " %08x\n" % (addr);# 0=1DWORD,1=2DWORDs
    else:
      payload = cmd + " %08x %08x\n" % (addr,(num_dwords-1));# 0=1DWORD,1=2DWORDs
    self.tx_tcp_packet( payload );
    payload = self.rx_tcp_packet().rstrip();
    dwords = payload.split(' ');
    rts = [];
    for dword in dwords:
      rts += [int( dword, 16 )];
    return rts;

  def tx_tcp_packet( self, payload ):
    # A Packet is a 8char hexadecimal header followed by the payload.
    # The header is the number of bytes in the payload.
    if self.aes_e2e == True:
      payload = self.aes.encrypt(payload);
    header = "%08x" % len(payload);
    bin_data = (header+payload).encode("utf-8");# String to ByteArray
    self.sock.send( bin_data );

  def rx_tcp_packet( self ):
    # Receive 1+ Packets of response. 1st Packet will start with header that
    # indicates how big the entire Backdoor payload is. Sit in a loop
    # receiving 1+ TCP packets until the entire payload is received.
    bin_data = self.sock.recv(1024);
    rts = bin_data.decode("utf-8");# ByteArray to String
    header      = rts[0:8];      # Remove the header, Example "00000004"
    payload_len = int(header,16);# The Payload Length in Bytes, Example 0x4
    payload     = rts[8:];       # Start of Payload is everything after header
    # 1st packet may not be entire payload so loop until we have it all
    while ( len(payload) < payload_len ):
      bin_data = self.sock.recv(1024);
      payload += bin_data.decode("utf-8");# ByteArray to String
    if self.aes_e2e == True:
      payload = self.aes.decrypt(payload);
    return payload;


###############################################################################
def init_globals( self ):

  import platform,os;
  try:
    import RPi.GPIO as gpio;
    self.os_platform ="rpi";# This must be a RaspberryPi
  except ImportError:
    self.os_platform ="pc";# Assume a PC
  self.os_sys = platform.system();  # Windows vs Linux
  if ( self.os_sys == "Darwin" ):
    self.os_sys = "Linux";# Mac Support
    self.os_platform ="mac";
  if ( self.os_sys == "Windows" ):
    title = "sump3.py "+self.vers+" "+self.copyright;
    os.system("title "+title );# Give DOS-Box a snazzy title

  
  self.name = "SUMP3 Mixed-Signal Logic Analyzer"; 
  self.background_surface = None;
  self.cmd_history = [];
  self.sump_manual = "sump3_manual.txt";
  self.display_console = True;
# self.view_list = [];# List of all the views - not necessarily assigned to a window
  self.view_applied_list = [];# List of all the views that have been created
  self.view_ontap_list = [];# List of all the views that are defined in files under sump_views
  self.sump_connected = False;
  self.mode_acquire = False;
  self.thread_id = None;
  self.thread_id_en = False;
# self.screen_shot = False;
  self.file_dialog = None;# "load_pizza", "save_pizza", "source_script", "load_uut"
  self.tool_tip_obj = None;# object_id of hovered button
  self.tool_top_tick_time = None;# PyGame tick_time in mS that hover event happened
  self.path_to_uut = None;# Note, this is selected UUTs file path, not the env var sump_path_uut
  self.signal_list = [];
  self.measurement_list = [];
  self.triggerable_list = [];
  self.maskable_list = [];
  self.user_ctrl_assigned_list = [];
  self.last_scroll_wheel_tick = 0;
  self.has_focus = True;
  self.toggle = False;
  self.sump_remote_in_use = False;
  self.window_selected = None;# 0,1 or 2. When mouse is clicked and border goes yellow
  self.display_button_list = [];# Fixes a bug with resize vs init
  self.color_white = pygame.Color(0xFF,0xFF,0xFF);
  self.color_black = pygame.Color(0x00,0x00,0x00);
  self.color_yellow = pygame.Color(0xFF,0xFF,0x00);
  self.color_red    = pygame.Color(0xFF,0x00,0x00);
  self.color_pink   = pygame.Color(0xFF,0xC0,0xCB);
  self.color_orange = pygame.Color(0xFF,0xA5,0x00);
  self.color_dark_red = pygame.Color(0x80,0x00,0x00);
  self.color_grid   = pygame.Color(0x40,0x40,0x40);
# self.color_trigger = self.color_red;
# self.color_triggerable = self.color_orange;
  self.cursor_list = [];
  self.cursor_list.append( cursor(name="Cursor-1"));
  self.cursor_list.append( cursor(name="Cursor-2"));
# self.cursor_list[0].x = 100;
# self.cursor_list[1].x = 200;
  self.cursor_list[0].x = 0;
  self.cursor_list[1].x = 0;
# self.cursor_list[0].color = self.color_yellow;
# self.cursor_list[1].color = self.color_yellow;
# self.zoom_pan_list = [];
# self.zoom_pan_list += [(1.0,0,0)];# Zoom, Pan (L-R) and Scroll (Up-Down)
# self.zoom_pan_list += [(1.0,0,0)];
# self.zoom_pan_list += [(1.0,0,0)];
  self.select_text_rect = ( 0,0,0,0 );
# self.select_text_i    = -1;
  self.select_text_i    = None;
  self.last_view_created = None;# the name, not the instance
  self.last_view_obj_created = None;# the instance
  self.last_create_type = None;# signal, view, group
  self.group_stack_list  = [];# Hierarchy stack for create_group,end_group

# self.view_preset_list = [ (None,None),(None,None),(None,None),(None,None),
#                           (None,None),(None,None),(None,None),(None,None), ];
  self.mouse_x = 0;
  self.mouse_y = 0;
  self.mouse_btn1_up   = ( None, None );
  self.mouse_btn1_dn   = ( None, None );# (x,y)
  self.mouse_btn2_up   = ( None, None );
  self.mouse_btn2_dn   = ( None, None );
  self.mouse_btn3_up   = ( None, None );
  self.mouse_btn3_dn   = ( None, None );
  self.mouse_pinch_up  = ( None, None );
  self.mouse_pinch_dn  = ( None, None );
  self.mouse_btn1_select = False;# True if last Btn1 Down selected a signal
  self.mouse_btn1_up_time = 0;# Used for double-click detection
  self.mouse_btn1_up_time_last = 0;
  self.mouse_motion      = False;
  self.mouse_motion_prev = False;
  self.mouse_signal_drag_from_window = None;
  self.mouse_signal_drag_to_window = None;
  self.sump = None;
  self.text_stats = None;
  self.text_stats_tick_time = 0;
  self.status_downloading = False;
# self.rom_signal_source = None;
  self.signal_delete_list = [];# Stack of signals deleted for <DEL>,<INS>,<HOME>
  self.signal_copy_list = [];# Stack of signals copied 
  self.time_lock = False;
  self.max_pod_acq_time_ms = 0; # used for acquire wait from trig to download


  # Map the display name to the variable names. Note that these are not in the 
  # Sump class as the Sump instance only exists once the hardware has been 
  # connected. Need to be able to display this prior to a connection.
  self.acq_parm_list = [];
  self.acq_parm_list += [("HS Clock  ",    "sump_hs_clock_freq",    "MHz")];
  self.acq_parm_list += [("HS Window ",    "sump_hs_clock_freq",    "uS")];
  self.acq_parm_list += [("LS Period ",    "sump_ls_clock_div",     "uS")];
  self.acq_parm_list += [("LS Window ",    "sump_ls_sample_window", "uS")];
  self.acq_parm_list += [("Trig Type ",    "sump_trigger_type",     "")];
  self.acq_parm_list += [("Trig Level",    "sump_trigger_analog_level", "mV")];
  self.acq_parm_list += [("Trig Delay",    "sump_trigger_delay",    "uS")];
  self.acq_parm_list += [("Trig Nth  ",    "sump_trigger_nth",      "")];
  self.acq_parm_list += [("Trig Pos  ",    "sump_trigger_location", "%")];
  self.acq_parm_list += [("Num Trigs ",    "sump_trigger_count",    "")];


  self.acq_trig_list = [];
  self.acq_trig_list += ["or_rising"];
  self.acq_trig_list += ["or_falling"];
  self.acq_trig_list += ["and_rising"];
  self.acq_trig_list += ["and_falling"];
  self.acq_trig_list += ["analog_rising"];
  self.acq_trig_list += ["analog_falling"];
  self.acq_trig_list += ["ext_in_rising"];
  self.acq_trig_list += ["ext_in_falling"];
  
  return;


###############################################################################
def init_vars( self, file_ini ):
  # Load App Variables with Defaults.
  vars   = {}; # Variable Dictionary
  vars["font_name"] = "dejavusansmono";
  vars["font_size"] = "16";
  vars["font_size_toolbar"] = "16";
  vars["file_log"]  = "sump3_log.txt";
  vars["debug_mode"                ] = "0";
  vars["dbg_random_adc_none_samples"] = "0";    
  vars["tool_tips_on_hover"        ] = "0";
  vars["tool_tips_text_stats_en"   ] = "1";
  vars["screen_color_background"   ] = "000000";
  vars["screen_color_foreground"   ] = "00FF00";
  vars["screen_color_selected"     ] = "FFFF00";
  vars["screen_color_trigger"      ] = "E00000";
  vars["screen_color_triggerable"  ] = "AA5500";
  vars["screen_color_cursor"       ] = "FFFF55";
  vars["screen_save_position"      ] = "0";
  vars["screen_x"                  ] = "20";
  vars["screen_y"                  ] = "30";
# vars["screen_width"              ] = "800";
# vars["screen_height"             ] = "600";
# vars["screen_height_small"       ] = "600";
# vars["screen_width"              ] = "1024";
# vars["screen_height"             ] = "720";
  vars["screen_width"              ] = "1280";
  vars["screen_height"             ] = "720";
  vars["screen_height_small"       ] = "600";
# vars["screen_windows"            ] = "F";# 4 bits for which windows are visible
  vars["screen_windows"            ] = "9";# 4 bits for visible windows. 9 = Win1 + bd_shell
  vars["screen_window_rle_time"    ] = "1";# Draw RLE Time range in upper right of windows  
  vars["screen_console_height"     ] = "300";# bd_shell console height
  vars["screen_save_image_format"  ] = "png";# png jpg bmp 
  vars["screen_measurements_tall"  ] = "0";# Wide versus Tall cursor measurements           
  vars["screen_adc_sample_points"  ] = "0";# 1 displays dot at each sample point            
  vars["screen_analog_line_width"  ] = "2";# 
  vars["screen_analog_bold_width"  ] = "4";# 
  vars["screen_max_text_stats_width"] = "25";
  vars["sump_remote_file_en"       ] = "1";
  vars["sump_remote_telnet_en"     ] = "0";
  vars["sump_remote_telnet_port"   ] = "23";
  vars["sump_remote_telnet_host"   ] = "127.0.0.1";# vs *.*.*.* or ""
  vars["bd_connection"             ] = "tcp";
  vars["bd_protocol"               ] = "poke";
  vars["bd_server_ip"              ] = "localhost";
  vars["bd_server_socket"          ] = "21567";
  vars["bd_server_quit_on_close"   ] = "1";
  vars["aes_key"                   ] = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f";
  vars["aes_authentication"        ] = "0";
  vars["uut_name"                  ] =  None;
# vars["uut_rev"                   ] = "00_00";
  vars["sump_uut_addr"             ] = "00000098";
  vars["sump_thread_id"            ] = "00000000";
  vars["sump_thread_lock_en"       ] = "0";
  vars["sump_rd_status_legacy_en"  ] = "0";
  vars["sump_script_startup"       ] = "sump_startup.txt";
  vars["sump_script_triggered"     ] = "sump_triggered.txt";
  vars["sump_script_shutdown"      ] = "sump_shutdown.txt";
  vars["sump_script_remote"        ] = "sump_remote.txt";
  vars["sump_trigger_type"         ] = "or_rising";
  vars["sump_trigger_field"        ] = "00000000";
  vars["sump_trigger_delay"        ] = "0.0";# uS
  vars["sump_trigger_nth"          ] = "1";
  vars["sump_trigger_count"        ] = "0";
  vars["sump_trigger_location"     ] = "50.0";
  vars["sump_trigger_analog_level" ] = "100.0";
  vars["sump_trigger_analog_ch"    ] = "0";
  vars["sump_user_ctrl"            ] = "00000000";
# vars["sump_user_stim"            ] = "00000000";
  vars["sump_path_ram"             ] = "sump_ram";
  vars["sump_path_uut"             ] = "sump_uut";
  vars["sump_path_dbg"             ] = "sump_dbg";
# vars["sump_hs_clock_freq"        ] = "80.0";
# vars["sump_ls_clock_freq"        ] = "0.250";
  vars["sump_hs_clock_freq"        ] = "1.0";
  vars["sump_ls_clock_freq"        ] = "2.250";
  vars["sump_ls_clock_div"         ] = "1";
  vars["sump_ls_sample_window"     ] = "1";
  vars["sump_ls_ana_dig_alignment" ] = "4";
# vars["sump_rle_trigger_latency"  ] = "0.0";

  vars["sump_download_disable_ls"  ] = "0";
  vars["sump_download_disable_hs"  ] = "0";
  vars["sump_download_disable_rle" ] = "0";
  vars["sump_download_ondemand"    ] = "1";

  vars["sump_path_vcd"             ] = "sump_vcd";
  vars["sump_path_png"             ] = "sump_png";
  vars["sump_path_pza"             ] = "sump_pza";
  vars["sump_path_jpg"             ] = "sump_jpg";
  vars["sump_path_bmp"             ] = "sump_bmp";
  vars["sump_path_view"            ] = "sump_view";
  vars["sump_path_list"            ] = "sump_list";
# vars["sump_path_scripts"         ] = "sump_scripts";
# vars["sump_path_views"           ] = None;
# vars["sump_path_views"           ] = None;

# vars["vcd_hubpod_names"    ] = "1";
# vars["vcd_group_names"           ] = "1";
# vars["vcd_full_capture_width"    ] = "0";

  vars["list_csv_format"]   = "0";
  vars["vcd_hierarchical"]  = "1";
  vars["vcd_hubpod_names"]  = "0";
  vars["vcd_hubpod_nums"]   = "0";
  vars["vcd_group_names"]   = "0";
# vars["vcd_remove_rips"]   = "1";
# vars["vcd_replace_rips"]  = "0";
  vars["vcd_viewer_en"      ] = "1";
  vars["vcd_viewer_gtkw_en" ] = "1";
  vars["vcd_viewer_path"    ] = "C:\\gtkwave\\bin\\gtkwave.exe";
  vars["vcd_viewer_width"   ] = "1900";
  vars["vcd_viewer_height"  ] = "800";


  vars["scroll_wheel_glitch_lpf_en" ] = "1";
  vars["scroll_wheel_pan_en"        ] = "1";
  vars["scroll_wheel_pan_reversed"  ] = "0";
  vars["scroll_wheel_zoom_en"       ] = "1";
  vars["scroll_wheel_analog_en"     ] = "0";

  self.var_save_list = ["font_name","font_size","font_size_toolbar","file_log","debug_mode","tool_tips_on_hover",
    "tool_tips_text_stats_en",
    "dbg_random_adc_none_samples",
    "screen_color_background","screen_color_foreground","screen_color_selected",
    "screen_color_trigger","screen_color_triggerable","screen_color_cursor",
    "screen_x", "screen_y","screen_save_position",
    "screen_width","screen_height", "screen_windows","screen_window_rle_time",
    "screen_console_height", "screen_measurements_tall", "screen_adc_sample_points", "screen_save_image_format",
    "screen_analog_line_width", "screen_analog_bold_width", "screen_max_text_stats_width",
    "bd_connection","bd_protocol","bd_server_ip","bd_server_socket","bd_server_quit_on_close",
    "aes_key", "aes_authentication",
    "sump_remote_file_en", "sump_remote_telnet_en", "sump_remote_telnet_port", "sump_remote_telnet_host",
    "sump_script_startup","sump_script_triggered","sump_script_shutdown",
    "sump_path_ram","sump_path_uut","sump_path_dbg",
    "sump_path_jpg","sump_path_png","sump_path_bmp","sump_path_pza","sump_path_vcd",
    "sump_path_vcd","sump_path_view",
    "sump_script_remote",
    "sump_thread_id", "sump_thread_lock_en", "sump_rd_status_legacy_en",
    "sump_ls_ana_dig_alignment",
    "vcd_hierarchical", "vcd_hubpod_names", "vcd_hubpod_nums","vcd_group_names", 
#   "vcd_remove_rips", "vcd_replace_rips",
    "vcd_viewer_en", "vcd_viewer_gtkw_en", "vcd_viewer_path","vcd_viewer_height","vcd_viewer_width",
    "list_csv_format",
    "sump_download_disable_ls", "sump_download_disable_hs", "sump_download_disable_rle",
    "sump_download_ondemand",
    "scroll_wheel_glitch_lpf_en",
    "scroll_wheel_pan_en",  
    "scroll_wheel_pan_reversed",
    "scroll_wheel_zoom_en",   
    "scroll_wheel_analog_en",   
 ];
  
  # Now load an existing ini file and overwrite any defaults
  if os.path.exists( file_ini ):
    file_in   = open( file_ini, 'r' );
    file_list = file_in.readlines();
    file_in.close();
    for each in file_list:
      each = each.replace("="," = ");
      words = each.strip().split() + [None] * 4; # Avoid IndexError
      # foo = bar
      if ( words[1] == "=" and words[0][0:1] != "#" ):
        vars[ words[0] ] = words[2];
  else:
    print( "Warning: Unable to open " + file_ini);

  self.color_fg             = rgb2color( int(vars["screen_color_foreground"   ],16));
  self.color_fg_dim         = rgb2color_dim( int(vars["screen_color_foreground"   ],16));
  self.color_bg             = rgb2color( int(vars["screen_color_background"   ],16));
  self.color_selected       = rgb2color( int(vars["screen_color_selected"     ],16));
  self.color_trigger        = rgb2color( int(vars["screen_color_trigger"      ],16));
  self.color_triggerable    = rgb2color( int(vars["screen_color_triggerable"  ],16));
  self.cursor_list[0].color = rgb2color( int(vars["screen_color_cursor"       ],16));
  self.cursor_list[1].color = rgb2color( int(vars["screen_color_cursor"       ],16));

  # Tell SDL to place window at last saved location
  if ( vars["screen_save_position"].lower() in ["true","yes","1"] ):
    screen_x = vars["screen_x"];
    screen_y = vars["screen_y"];
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%s,%s" % (screen_x,screen_y);
  return vars;


###############################################################################
# Dump all the app variables to ini file when application quits.
def var_dump( self, file_ini ):
# log( self, ["var_dump()"] );
  file_out  = open( file_ini, 'w' );
  file_out.write( "# [" + file_ini + "]\n" );
  file_out.write( "# WARNING: \n");
  file_out.write( "#  This file is auto generated on application exit.\n" );
  file_out.write( "#  Safe to change values, but comments will be lost.\n" );
  txt_list = [];
# for key in self.vars:
  for key in self.var_save_list:
    val = self.vars[ key ];
#   print( key, val );
    txt_list.append( key + " = " + val + "\n" );
  for each in sorted( txt_list ):
    file_out.write( each );
  file_out.close();
  return;

###############################################################################
# Generate all the sump subdirectories if they don't exist already.
def create_dirs( self ):
  for key in self.vars:
    if "sump_path_" in key:
      sump_path = self.vars[key];
      if sump_path != None and not os.path.exists( sump_path ):
#     if not os.path.exists( self.vars[key] ):
        try:
          print( "Creating %s" % sump_path );
          os.mkdir( sump_path );
#         print( "Creating %s" % self.vars[key] );
#         os.mkdir( self.vars[key] );
        except:
          print( "ERROR: unable to mkdir %s" % self.vars[key] );
  return;

def rgb2color( rgb ):
  r = ( rgb & 0xFF0000 ) >> 16;
  g = ( rgb & 0x00FF00 ) >> 8 ;
  b = ( rgb & 0x0000FF ) >> 0 ;
  return pygame.Color(r,g,b);

def rgb2color_dim( rgb ):
  r = ( rgb & 0xFF0000 ) >> 16+2;
  g = ( rgb & 0x00FF00 ) >> 8+2 ;
  b = ( rgb & 0x0000FF ) >> 0+2 ;
  return pygame.Color(r,g,b);


# Given "foo*bar" and ["foo2bar", "fobar"] return ["foo2bar"]
def star_match( search_str, search_list ):
  import re;
  esc_list = ["[","]",".","+","^","?"];# Escape out the RegEx chars
  c = "";
  for each_ch in search_str:
    for each_esc in esc_list:
      each_ch = each_ch.replace(each_esc,"\\"+each_esc);
    c = c + each_ch;
  c = c.replace("*",".*");
  d = [];
  for each in search_list:
    if re.match(c,each):
      d += [ each ];
  return d;

def hexlist2file( file_name, my_list ):
  file_out  = open( file_name, 'w' );
  for each_sample in my_list:
    hex_str = "";
    for each_dword in each_sample:
      hex_str = hex_str + "%08x " % each_dword;
    hex_str = hex_str[:-1] + "\n";
    file_out.write( hex_str );
  file_out.close();
  return;


def list2file( file_name, my_list, concat = False ):
  if ( concat ):
    type = 'a';
  else:
    type = 'w';
# print( file_name, type );
  file_out  = open( file_name, type );
  for each in my_list:
    file_out.write( each + "\n" );
  file_out.flush();# Forces write to disk prior to close. Useful for log files, etc
  file_out.close();
  return;


def file2list( file_name, binary = False ):
  if ( binary == False ):
    try:
      file_in   = open ( file_name, 'r' );
      file_list = file_in.readlines();
      file_list = [ each.strip('\n') for each in file_list ];# list comprehension
    except:
      print("ERROR: Unable to open file %s" % file_name );
      file_list = [];
    return file_list;
  else:
    # See https://stackoverflow.com/questions/1035340/
    #           reading-binary-file-and-looping-over-each-byte
    byte_list = [];
    file_in = open ( file_name, 'rb' );
    try:
      byte = file_in.read(1);
      while ( byte ):
        byte_list += [ord(byte)];
        byte = file_in.read(1);
    finally:
      file_in.close();
    return byte_list;

def filegz2list( file_name ):
  import gzip;
  list_out = [];
  with gzip.open( file_name, "rt" ) as file_in_gz:
    list_out = [ each.strip('\n').strip('\r') for each in file_in_gz ];
  return list_out;
    
def list2filegz( file_name, list ):
  import gzip;
  with gzip.open( file_name, "wt" ) as file_out_gz:
    for each in list:
      file_out_gz.write( each+'\n' )
    file_out_gz.close();
  return;


###############################################################################
#  0123456
#0   /|\
#1  / | \
#2  _ | _
#3 |_  |_A
#   __          
#  |  \  | \ / |  |
#  |--   |  |  |  |
#  |  /  |     |  |
#   --             ----
#########################
def create_icon( self ):
  self.icon_surface = self.pygame.Surface( ( 32,32 ) );
  self.icon_surface = self.icon_surface.convert();# Makes blitting faster
  self.icon_surface.fill( self.color_bg );
  arrow_list = [(9,16),(9,0),(0,8),(9,0),(18,8) ];
  c1_list    = [(6,16),(0,16),(0,32),(6,32)];
  c2_list    = [(18,16),(12,16),(12,32),(18,32)];
  self.pygame.draw.lines(self.icon_surface,self.color_fg,False,arrow_list,2);
  self.pygame.draw.lines(self.icon_surface,self.color_fg,False,c1_list,2);
  self.pygame.draw.lines(self.icon_surface,self.color_fg,False,c2_list,2);
  return self.icon_surface;


#####################################
# create_preset 1 -button_label FooBar -file foo.txt
#def cmd_create_preset( self, words ):
#  rts = [];
#  # create_signal my_net -source digital[0]
#  preset_i = int( words[1] )-1;# 0-7 internally
#  button_label = None;
#  file = None;
#  for ( i, each_word ) in enumerate( words[2:] ):
#    if ( each_word != None and each_word[0:1] == "-" ):
#      if each_word == "-button_label":
#        button_label = words[2+i+1];
#      if each_word == "-file":
#        file = words[2+i+1];
#  if button_label != None and file != None:
#    self.container_view_list[1+preset_i].set_text( text = button_label );
#    self.view_preset_list[preset_i] = ( button_label, file );
#  return rts;

#####################################
# remove_preset 1 or *
#def cmd_remove_preset( self, words ):
#  rts = [];
#  if words[1] == "*":
#    count = range(0,8);
#  else:
#    count = [ int( words[1] ) - 1 ];
#  for i in count:
#    self.view_preset_list[i] = ( None, None );
#    self.container_view_list[1+i].set_text( text = "" );
#  return rts;

#####################################
# "create_fsm_state 0a foo" for last signal created, 0x0A is state "foo"
def cmd_create_fsm_state( self, words ):
  rts = [];
  self.last_create_type = "fsm_state";
  try:
    state_num  = int( words[1], 16 );
    state_name = words[2];
    if len( self.signal_list ) != 0:
      each_sig = self.signal_list[-1];# Last signal created
      each_sig.fsm_state_dict[state_num] = state_name;
#     print("%s %s %s" % ( each_sig.name, state_num, state_name ) );
  except:
    print("ERROR: Invalid create_fsm_state hex value of %s" % words[1] );
# for key in each_sig.fsm_state_dict:
#   print("%s : %s = %s" % ( each_sig.name, key, each_sig.fsm_state_dict[key] )  );
  return rts;


#####################################
# "create_bit_group foo" 
def cmd_create_bit_group( self, words ):
  self.last_create_type = "group";
  rts = cmd_create_signal(self, words +["-type","group"], defer_update = True );
  group_name = words[1];
  a = group_name.replace("["," [");
  b = " ".join(a.split()).split(' ') + [None] * 5;
  group_name_short = b[0];# Removed "[7:0]" from name if exists

  found_rip = False;
  prev_word = None;
  for each_word in words + [None]:
    if prev_word == "-source" and not found_rip:
      if ":" in each_word:
        try:
#       if True:
          found_rip = True;
          # -source hub.pod[3:0]
          rip_word  = each_word;
          rip_word  = rip_word.replace("[", " [ ");
          rip_word  = rip_word.replace("]", " ] ");
          rip_word  = rip_word.replace(":", " : ");
          #             0   1 2 3 4 5
          # -source hub.pod [ 3 : 0 ]
          rip_words = " ".join(rip_word.split()).split(' ') + [None] * 5;
          source_name_short = rip_words[0];# Brackets removed
          bit_top = int( rip_words[2],10 );
          bit_bot = int( rip_words[4],10 );
          bit_offset = bit_bot;# The rip will always be 7:0 even if source is 9:2
          for i in range( bit_top, bit_bot-1, -1 ):
            signal_name = group_name_short + "[%d]" % (i-bit_offset);
            source_name = source_name_short + "[%d]" % (i);

            # Punt and enable triggerable and maskable for bits 0-31
            if i <= 31:
              triggerable = "True";
              maskable    = "True";
            else:
              triggerable = "False";
              maskable    = "False";

#           # This doesnt work, why?
#           # triggerable_list is "digital_rle[0][0][6]"
#           # source_name      is "ck100_hub.u1_pod.3[6]" ( for generate )
#           triggerable = "False";
#           maskable    = "False";
#           for each_triggerable in self.triggerable_list:
#             print( each_triggerable, source_name );
#             if each_triggerable in source_name:
#               triggerable = "True";
#           for each_maskable in self.maskable_list:
#             if each_maskable in source_name:
#               maskable = "True";

            txt = "create_signal %s -source %s -triggerable %s -maskable %s" % \
              ( signal_name, source_name, triggerable, maskable );
#           print( txt );
            proc_cmd( self, txt, quiet = True );
        except:
          log( self, ["ERROR: cmd_create_bit_group()"] );
    prev_word = each_word;
  if len( self.group_stack_list ) != 0:
    self.group_stack_list = self.group_stack_list[:-1];# Remove last element
  return rts;

#####################################
# "create_group foo" is a shorcut for "create_signal foo -type group"
def cmd_create_group( self, words ):
  self.last_create_type = "group";
  rts = cmd_create_signal(self, words +["-type","group"], defer_update = True );
  return rts;

#####################################
# "end_group" just pops the last "create_group" off of the group hierachy stack
def cmd_end_group( self, words ):
  rts = [];
  if len( self.group_stack_list ) != 0:
    self.group_stack_list = self.group_stack_list[:-1];# Remove last element
  return rts;

#####################################
def cmd_create_signal( self, words, defer_update = False ):
# log( self, ["create_signal() %s" % words[1] ] );
  rts = [];
  self.last_create_type = "signal";

# self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" create_signal "+words[1]);
# self.pygame.event.pump();
# start_time = self.pygame.time.get_ticks();

# pygame.time.wait(1);# time in mS. 
# pygame.display.update();# Now off to the GPU
# rts += [ str( words ) ];
  # create_signal my_net -source digital[0]
  my_sig = signal( name = words[1] );
  self.signal_list += [ my_sig ];

  if len( self.group_stack_list ) != 0:
    my_sig.member_of = self.group_stack_list[-1];# Automatically member of last group
#   print("%s is now member_of %s" % ( my_sig.name, my_sig.member_of.name ) );

  for ( i, each_word ) in enumerate( words[2:] ):
    if ( each_word != None and each_word[0:1] == "-" ):
      assign_signal_attribute_by_name( self, new_signal = my_sig, 
                                       attribute = each_word[1:], value = words[2+i+1] );
  if my_sig.type == "group" :
    my_sig.collapsable = True;
    self.group_stack_list += [ my_sig ];

  # digital_rle source may be specified as either "digital_rle[0][1][2]" or 
  #  "hub_name.pod_name[2] or "hub_name.pod_name.0[2]" with generate instance
  # If specified by name, do a lookup and convert to number
  if my_sig.source != None:
    if "." in my_sig.source:
      # self.rle_hub_pod_dict = {};# Lookup where key is "hub_name.pod_name" and returns (hub_i,pod_j)
      (hubpod_name, rip_num ) = my_sig.source.split("[");

      if ( self.sump.rle_hub_pod_dict.get( hubpod_name  ) != None ):
        (hub,pod) = self.sump.rle_hub_pod_dict[ hubpod_name ];
        my_sig.source = "digital_rle[%d][%d][%s" % ( hub, pod, rip_num );
#     else:
#       print("WARNING: Strange source key %s" % my_sig.source );
#       for key in self.sump.rle_hub_pod_dict:
#         print("%s = %s" % ( key, self.sump.rle_hub_pod_dict[key] ) );

  # Count the number of bits for the digital signals
  if my_sig.source != None:
    if "digital_" in my_sig.source:
      words_tmp = my_sig.source.split("[");
      rip_num = words_tmp[-1];
      rip_num = rip_num.replace("]","");
      if ":" in rip_num:
        (bit_top, bit_bot ) = rip_num.split(":");
        bits_total = int(bit_top) - int(bit_bot) + 1;
      else:
        bits_total = 1;
      my_sig.bits_total = bits_total;

  # TODO: This might need to be applied when an existing signal attribute is 
  # changed - TBD. For now, it assumes a single line with -view and -member_of on creation.
  signal_attribute_inheritance(self, my_sig);

  # If a digital_rle signal and it has a view assigned to it, add this (hub,pod) tuple of the
  # signal to class view's self.rle_hub_pod_list so the view object knows which (hub,pod)s 
  # exist in it.
  if my_sig.source != None:
    if "digital_rle" in my_sig.source and my_sig.view_obj != None:
      # "digital_rle[0][1][1:0]"
      source_name = my_sig.source.replace("["," ");
      source_name = source_name.replace("]"," ");
      words_tmp = " ".join(source_name.split()).split(" ");
      hub = int( words_tmp[1] );
      pod = int( words_tmp[2] );
      if (hub,pod) not in my_sig.view_obj.rle_hub_pod_list:
        log( self, ["Adding Hub-Pod (%d,%d) to View %s" % (hub,pod,my_sig.view_obj.name) ] );
        my_sig.view_obj.rle_hub_pod_list += [ (hub,pod) ];
#     my_sig.view_obj.rle_hub_pod_user_ctrl_list += [ (hub,pod,my_sig.user_ctrl_list[:]) ];
      if len( my_sig.user_ctrl_list ) != 0:
        my_sig.view_obj.rle_hub_pod_user_ctrl_list += [ (hub,pod,my_sig.user_ctrl_list[:]) ];

  if my_sig.source != None:
    if "analog_ls" in my_sig.source:
      my_sig.type = "analog";# New 2024.12.12
 
  # signal_list_modified becomes really slow as number of signals increases 
# if not defer_update:
  if True:
#   signal_list_modified(self);
    signal_list_modified(self, my_signal = my_sig );

# stop_time = self.pygame.time.get_ticks();
# render_time = stop_time - start_time;
# sig_type = my_sig.type;
# log( self, ["create_signal() %s : Time = %d mS %s %s " % ( my_sig.name, render_time, defer_update, sig_type )] );
  return rts;


#####################################
# When a signal is first created it automatically inherits 
# common attributes from parent groups and a parent view.
# WARNING: views and groups need to be created in hierarchical 
# order for this to work properly as this will only traverse
# one level up.
# Inherit the following attributes:
#   view_name
#   timezone
#   user_ctrl_list
def signal_attribute_inheritance( self, my_sig ):
  #1 : If this signal has a source and no timezone defined, it automatically gets
  #    assigned a timezone of "ls", "hs" or "rle" based on the source description
  if my_sig.timezone == None and my_sig.source != None :  
    if "digital_ls" in my_sig.source:
      my_sig.timezone = "ls";
    elif "analog_ls" in my_sig.source:
      my_sig.timezone = "ls";
    elif "digital_hs" in my_sig.source:
      my_sig.timezone = "hs";
    elif "digital_rle" in my_sig.source:
      my_sig.timezone = "rle";

  #2 : If signal has no view, assign it the last created view name.
  # Note that every "create_view" should terminate with a "end_view"
  if my_sig.view_name == None and self.last_view_created != None :  
    my_sig.view_name = self.last_view_created;
    my_sig.view_obj  = self.last_view_obj_created;

  # If a signal is a member of a group, inherit things like view,timezone,user_ctrl_list
  if my_sig.member_of != None:
#   for each_group in self.signal_list:
#     if each_group.type == "group":
#       if each_group      == my_sig.member_of :
    if True:
      if True:
        if True:
          each_group = my_sig.member_of;
          if each_group.view_name != None:
            my_sig.view_name = each_group.view_name;
            my_sig.view_obj  = each_group.view_obj;
          if each_group.timezone != None:
            my_sig.timezone = each_group.timezone;
          if each_group.rle_masked == True:
            my_sig.rle_masked = each_group.rle_masked;
          if each_group.hidden     == True:
            my_sig.hidden     = each_group.hidden;
          if each_group.visible    == False:
            my_sig.visible    = each_group.visible;

          if len( each_group.user_ctrl_list ) != 0:
            for each_user_ctrl in each_group.user_ctrl_list:
              if each_user_ctrl not in my_sig.user_ctrl_list:
                my_sig.user_ctrl_list += [ each_user_ctrl ];


  # If a signal has a view, inherit a user_ctrl_list from it
  if my_sig.view_name != None:
#   for each_view in self.view_applied_list:
#     if each_view      == my_sig.view_obj:
    if True:
      if True:
        each_view = my_sig.view_obj;
        if len( each_view.user_ctrl_list ) != 0:
          for each_user_ctrl in each_view.user_ctrl_list:
            if each_user_ctrl not in my_sig.user_ctrl_list:
              my_sig.user_ctrl_list += [ each_user_ctrl ];
    

  # If a signal has no color, inherit one from group, view or use default foreground
  if my_sig.color == None and my_sig.member_of != None:
#   for each_group in self.signal_list:
#     if each_group.type == "group":
#       if each_group      == my_sig.member_of:
    if True:
      if True:
        if True:
          each_group = my_sig.member_of;
          if each_group.color != None:
            my_sig.color = each_group.color;
  if my_sig.color == None:
#   for each_view in self.view_applied_list:
#     if each_view      == my_sig.view_obj:
    if True:
      if True:
        each_view = my_sig.view_obj;
        if each_view.color != None:
          my_sig.color = each_view.color;
  if my_sig.color == None:
    my_sig.color = int( self.vars["screen_color_foreground"], 16 );
#   my_sig.color = self.color_fg;
  return;


#####################################
# Do some one-time house keeping whenever the signal list has changed
# First up is calculating the hierarchy level of each signal
def signal_list_modified( self, my_signal = None ):
# start_time = self.pygame.time.get_ticks();
  # Calculate the hierarchy level for each signal. We do this by counting the number
  # of parents, grandparents, etc.

  if my_signal == None:
    sig_list = self.signal_list;
  else:
    sig_list = [ my_signal ];

# for each_sig in self.signal_list:
  for each_sig in sig_list:
    each_sig.hier_level = recursive_parent_count( self, each_sig, 0 );
# stop_time = self.pygame.time.get_ticks();
# render_time = stop_time - start_time;
# log( self, ["signal_list_modified() Time = %d mS " % (render_time)] );
  return;

# WARNING: This won't work with multiple groups of the same name
def recursive_parent_count( self, my_sig, count ):
  if my_sig.member_of != None:
    # Find the parent
    for each_sig in self.signal_list:
      if ( each_sig.type == "group" and each_sig      == my_sig.member_of ):
#     if ( each_sig.type == "group" and each_sig.name == my_sig.member_of ):
# This Step-1 is now handled by signal_attribute_inheritance()   
#       # Step-1 : Automatically assign the same view as parent ( saves typing )
#       my_sig.view_name = each_sig.view_name;  
        # Step-2 : Go down the rabbit hole of finding all the parents
        count = recursive_parent_count( self, each_sig, count+1 );# Go down the rabbit hole
  return count;

#####################################
def cmd_debug( self, words ):
# print( self.window_list );
# for (i,each_win) in enumerate( self.window_list ):
#   print("---------");
#   print("Window-%d" % i );
#   print(each_win.name);
#   print(each_win.timezone);
#   print(each_win.view_list);
#   print(each_win.zoom_pan_list);
#   print(each_win.sample_period);
#   print(each_win.sample_unit);
#   print(each_win.trigger_index);
#   print(each_win.samples_total);
#   print(each_win.samples_shown);
#   print(each_win.samples_start_offset);
#   print(each_win.x_space);
#   print(each_win.cursor_x_list);
#   print(each_win.panel.visible);
#   print(each_win.panel.relative_rect);# ( x,y,w,h )
  for each_applied_view in self.view_applied_list:
    print( each_applied_view.name );
  return;


#####################################
def cmd_list_signal( self, words ):
  rts = [];
  for each_sig in self.signal_list:
    if ( each_sig.name == words[1] or words[1] == "*" or each_sig.selected ):
      rts += ["----------------------------------"];
      rts += ["-name     %s" % each_sig.name      ];
      rts += ["-source   %s" % each_sig.source    ];
      rts += ["-type     %s" % each_sig.type      ];
      rts += ["-format   %s" % each_sig.format    ];
      rts += ["-window   %s" % each_sig.window    ];
      rts += ["-view     %s" % each_sig.view_name ];
      rts += ["-timezone %s" % each_sig.timezone  ];
      rts += ["-visible  %s" % each_sig.visible   ];
      rts += ["-rle_masked %s" % each_sig.rle_masked];
      rts += ["-hidden   %s" % each_sig.hidden    ];
      rts += ["-selected %s" % each_sig.selected  ];
      rts += ["-color   %06x" % each_sig.color    ];
      rts += ["-user_ctrl %s" % each_sig.user_ctrl_list ];
      rts += ["-sample_period  %s" % each_sig.sample_period   ];
      rts += ["-sample_unit    %s" % each_sig.sample_unit     ];
      rts += ["-maskable       %s" % each_sig.maskable        ];
      rts += ["-triggerable    %s" % each_sig.triggerable     ];
      rts += ["-trigger        %s" % each_sig.trigger         ];
      rts += ["-trigger_field %08x" % each_sig.trigger_field   ];
      if each_sig.member_of != None:
        rts += ["-group          %s" % each_sig.member_of.name  ];
        rts += ["-hier_level     %d" % each_sig.hier_level      ];
#     rts += ["-group          %s" % each_sig.member_of       ];
      if each_sig.type == "analog":
        rts += ["-range          %s" % each_sig.range           ];
        rts += ["-units          %s" % each_sig.units           ];
        rts += ["-units_per_code %s" % each_sig.units_per_code  ];
#       rts += ["-units_per_division %s" % each_sig.units_per_division  ];
#       rts += ["-vertical_scale %s" % each_sig.vertical_scale  ];
#       rts += ["-vertical_scale %s" % each_sig.units_per_division  ];
        rts += ["-vertical_offset %s" % each_sig.vertical_offset     ];
        rts += ["-units_per_division %s" % each_sig.units_per_division  ];
        rts += ["-divisions_per_range %s" % each_sig.divisions_per_range ];
        rts += ["-offset_units   %s" % each_sig.offset_units    ];
        rts += ["-offset_codes   %s" % each_sig.offset_codes    ];

#     txt_str = "%s -source %s -type %s -view %s -units %s -color %06x -visible %s -window %s" % ( each_sig.name, 
#       each_sig.source, each_sig.type, each_sig.view_name, each_sig.units, each_sig.color, each_sig.visible, each_sig.window );
#     rts += [ txt_str ];
  return rts;


#####################################
# apply a specified attribute to any selected signals OR the last signal created if none selected
# Note that the last signal created is about View ROM
def cmd_apply_attribute( self, words ):
  rts = [];
  rts += ["apply_attribute() %s" % str( words ) ];
  apply_signal_list = [];
  for each_sig in self.signal_list:
    if each_sig.selected:
      apply_signal_list += [ each_sig ];
  if len( apply_signal_list ) == 0 and len( self.signal_list ) != 0:
    if self.last_create_type != "view":
      apply_signal_list += [ self.signal_list[-1] ];# Last created signal

  # words can either be "attribute = value" or "attribute=value" so separate
  txt_line = "";
  for each in words:
    if each != None:
      each = each.replace("="," = ");
      txt_line += " "+each;
  new_words = " ".join(txt_line.split()).split(' ') + [None] * 4;

  if len( new_words ) >= 4:
    if new_words[2] == "=":
      for each_sig in apply_signal_list:
#       rts += [ "%s : %s = %s" % ( each_sig.name, new_words[1], new_words[3] ) ];
        assign_signal_attribute_by_name( self, new_signal = each_sig, 
                                       attribute = new_words[1], value = new_words[3] );
      if len(apply_signal_list) == 0 and self.last_create_type == "view" and len(self.view_applied_list) != 0:
        my_view = self.view_applied_list[-1];# Last view created
        assign_view_attribute_by_name( self, new_view = my_view, attribute = new_words[1], value = new_words[3] );
#       print("Oy %s %s %s" % ( my_view.name, new_words[1], new_words[3] ) );
  return rts;


#####################################
# Given a signal name, apply False to visible attribute
def cmd_remove_signal( self, words ):
  rts = [];
  if words[1] == None:
    signal_list_names = [];
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
        signal_list_names += [ each_sig.name ];
  else:
#   signal_list_names = [ each.name for each in self.signal_list ];# all the names
#   signal_list_names = fnmatch.filter(signal_list_names,words[1] );# filtered names
    signal_list_names = [ words[1] ];
  for each_name in signal_list_names:
    for each_sig in self.signal_list:
      if each_name == each_sig.name:
        each_sig.visible = False;
        each_sig.rle_masked = True;
        rts += ["remove_signal() %s" % each_sig.name ];
  self.refresh_waveforms = True;
  return rts;


#####################################
# Given a signal name, apply True to hidden attribute
def cmd_hide_signal( self, words ):
  rts = [];
  if words[1] == None:
    signal_list_names = [];
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
        signal_list_names += [ each_sig.name ];
  else:
#   signal_list_names = [ each.name for each in self.signal_list ];# all the names
#   signal_list_names = fnmatch.filter(signal_list_names,words[1] );# filtered names
#   signal_list_names = [ words[1] ];
    signal_list_names = [ each.name for each in self.signal_list ];# all the names
    signal_list_names = star_match( words[1], signal_list_names );
  for each_name in signal_list_names:
    for each_sig in self.signal_list:
      if each_name == each_sig.name:
        each_sig.hidden = True;
        rts += ["hide_signal() %s" % each_sig.name ];
  self.refresh_waveforms = True;
  return rts;


#####################################
# Given a signal name, apply False to hidden attribute
def cmd_show_signal( self, words ):
  rts = [];
  if words[1] == None:
    signal_list_names = [];
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
        signal_list_names += [ each_sig.name ];
  else:
#   signal_list_names = [ each.name for each in self.signal_list ];# all the names
#   signal_list_names = fnmatch.filter(signal_list_names,words[1] );# filtered names
#   signal_list_names = [ words[1] ];
    signal_list_names = [ each.name for each in self.signal_list ];# all the names
    signal_list_names = star_match( words[1], signal_list_names );
  for each_name in signal_list_names:
    for each_sig in self.signal_list:
      if each_name == each_sig.name:
        each_sig.hidden = False;
        rts += ["show_signal() %s" % each_sig.name ];
  self.refresh_waveforms = True;
  return rts;


#####################################
# Given a signal name, toggle the hidden attribute <END>
def cmd_hide_toggle_signal( self, words ):
  rts = [];
  if words[1] == None:
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
        each_sig.hidden = not each_sig.hidden;
        self.refresh_waveforms = True;
  return rts;


#####################################
# Given a signal name, toggle the masked attribute <END>
def cmd_mask_toggle_signal( self, words ):
  rts = [];
  if words[1] == None:
    for each_sig in self.signal_list:
#     if each_sig.selected:
      if each_sig.selected and each_sig.maskable:
        each_sig.selected = False;
        each_sig.rle_masked = not each_sig.rle_masked;
        self.refresh_waveforms = True;
  return rts;


#####################################
# Given a signal name, apply True to visible attribute
def cmd_add_signal( self, words ):
  rts = [];
# signal_list_names = [ each.name for each in self.signal_list ];# all the names
# signal_list_names = fnmatch.filter(signal_list_names,words[1] );# filtered names
# signal_list_names = [ words[1] ];
  signal_list_names = [ each.name for each in self.signal_list ];# all the names
  signal_list_names = star_match( words[1], signal_list_names );
  for each_name in signal_list_names:
    for each_sig in self.signal_list:
      if each_name == each_sig.name:
        each_sig.visible = True;
        each_sig.rle_masked = False;
        rts += ["add_signal() %s" % each_sig.name ];
  return rts;


#####################################
# Given a group name, find the signal object that matches and expand it
def cmd_expand_group( self, words ):
  rts = [];
  if words[1] == None:
    signal_list_names = [];
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
        signal_list_names += [ each_sig.name ];
  else:
#   signal_list_names = [ each.name for each in self.signal_list ];# all the names
#   signal_list_names = fnmatch.filter(signal_list_names,words[1] );# filtered names
#   signal_list_names = [ words[1] ];
    signal_list_names = [ each.name for each in self.signal_list ];# all the names
    signal_list_names = star_match( words[1], signal_list_names );
  for each_name in signal_list_names:
    for each_sig in self.signal_list:
      if each_name == each_sig.name:
#       each_sig.collapsed = False;
        proc_expand_group( self, each_sig );
  return rts;

#####################################
# Given a group name, find the signal object that matches and collapse it
def cmd_collapse_group( self, words ):
  print("cmd_collapse_group() %s" % words );
  rts = [];
  if words[1] == None:
    signal_list_names = [];
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
        signal_list_names += [ each_sig.name ];
  else:
#   signal_list_names = [ each.name for each in self.signal_list ];# all the names
#   signal_list_names = fnmatch.filter(signal_list_names,words[1] );# filtered names
# fnmatch.filter is only for files and doesnt support names like foo[1:0]
#   signal_list_names = [ words[1] ];
    signal_list_names = [ each.name for each in self.signal_list ];# all the names
    signal_list_names = star_match( words[1], signal_list_names );
  for each_name in signal_list_names:
#   print(each_name);
    for each_sig in self.signal_list:
      if each_name == each_sig.name:
#       each_sig.collapsed = True;
        proc_collapse_group( self, each_sig );
  return rts;


#####################################
# Copy a signal into the clipboard ( delete buffer ) 
#def cmd_copy_signal( self, words ):
#  print("cmd_copy_signal()");
## import copy;
#  rts = [];
#  if words[1] == None:
#    for each_sig in self.signal_list:
#      if each_sig.selected:
#        each_sig.selected = False;
##       self.signal_delete_list += [ copy.copy( each_sig ) ];
##       self.signal_delete_list += [ copy.deepcopy( each_sig ) ];
##       self.signal_delete_list += [ copy_signal_obj( self, each_sig ) ];
#        self.signal_copy_list += [ copy_signal_obj( self, each_sig ) ];
#        print("Copying %s" % each_sig.name );
#  elif words[1] == "*":
#    pass;
#  else:
#    for ( i, each_sig ) in enumerate( self.signal_list ):
#      if ( each_sig.name == words[1] ):
##       self.signal_delete_list += [ copy.copy( each_sig ) ];
##       self.signal_delete_list += [ copy.deepcopy( each_sig ) ];
##       self.signal_delete_list += [ copy_signal_obj( self, each_sig ) ];
#        self.signal_copy_list += [ copy_signal_obj( self, each_sig ) ];
#  return rts;


#####################################
# Copy a signal into the clipboard ( delete buffer ) 
def cmd_copy_signal( self, words ):
  print("cmd_copy_signal()");
# print(len(self.signal_copy_list));
  rts = [];
  if words[1] == None:
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
#       A 0xF9 "Binary Group" isn't type group, but type digital
#       group_copy = each_sig.type == "group";
        group_copy = each_sig.collapsable;
        hier_offset = each_sig.hier_level;
        recursive_signal_copy(self, each_sig, None, group_copy, hier_offset );
  elif words[1] == "*":
    pass;
  else:
    for ( i, each_sig ) in enumerate( self.signal_list ):
      if ( each_sig.name == words[1] ):
#       group_copy = each_sig.type == "group";
        group_copy = each_sig.collapsable;
        hier_offset = each_sig.hier_level;
        recursive_signal_copy(self, each_sig, None, group_copy, hier_offset );
  self.signal_copy_list.reverse();# Not sure why
  return rts;

def recursive_signal_copy( self, parent, copy_parent, group_copy, hier_offset ):
  self.signal_copy_list += [ copy_signal_obj( self, parent ) ];
  self.signal_copy_list[-1].hier_level -= hier_offset;

  # Note: there's a strange bug if same group is copied twice. 

  if group_copy:
    if copy_parent != None:
      self.signal_copy_list[-1].member_of = copy_parent;
    parent_copy = self.signal_copy_list[-1];# New parent, not the original
    for each_sig in self.signal_list:
      if each_sig.member_of == parent:
        recursive_signal_copy( self, parent = each_sig, copy_parent = parent_copy, 
                               group_copy = group_copy, hier_offset = hier_offset );
  else:
    self.signal_copy_list[-1].visible    = True;
    self.signal_copy_list[-1].parent     = None;
    self.signal_copy_list[-1].member_of  = None;
    self.signal_copy_list[-1].hier_level = 0;

  return;

#####################################
# For some reason copy.deepcopy() is crashing, so do it manually
def copy_signal_obj( self, src_sig ):
  dst_sig = signal( name = src_sig.name );
  dst_sig.__dict__ = src_sig.__dict__.copy();
  dst_sig.window = None;
  dst_sig.selected = False;
  return dst_sig; 

# dst_sig.name = "new_name";
# print( dst_sig );
# print( dst_sig.name );
# print( dst_sig.parent );
# print( dst_sig.window );
# print( dst_sig.view_name );
# dst_sig.visible = False;
# dst_sig.rle_masked = True;
# print("2");
# self.signal_list += [ dst_sig ];
# print("3");


#####################################
# Delete a signal from being shown <DEL> and also set rle_masked to True if maskable
#def cmd_delete_signal( self, words ):
#  rts = [];
#  if words[1] == None:
#    for each_sig in self.signal_list:
#      if each_sig.selected:
#        each_sig.visible = False;
#        each_sig.selected = False;
#        if each_sig.maskable:
#          each_sig.rle_masked = True;
#        self.signal_delete_list += [ each_sig ];
#  elif words[1] == "*":
#    pass;
#  else:
#    for ( i, each_sig ) in enumerate( self.signal_list ):
#      if ( each_sig.name == words[1] ):
#        each_sig.visible = False;
#        if each_sig.maskable:
#          each_sig.rle_masked = True;
#        self.signal_delete_list += [ each_sig ];
#  self.refresh_waveforms = True;
#  return rts;


#####################################
# Select a signal
def cmd_select_signal( self, words ):
  rts = [];
  if words[1] != None:
    for ( i, each_sig ) in enumerate( self.signal_list ):
      if ( each_sig.name == words[1] or words[1] == "*" ):
        each_sig.selected = True;
  self.refresh_waveforms = True;
  return rts;


#####################################
# DeSelect a signal
def cmd_deselect_signal( self, words ):
  rts = [];
  if words[1] != None:
    for ( i, each_sig ) in enumerate( self.signal_list ):
      if ( each_sig.name == words[1] or words[1] == "*" ):
        each_sig.selected = False;
  self.refresh_waveforms = True;
  return rts;



#####################################
# Delete a signal from being shown <DEL> and also set rle_masked to True if maskable
def cmd_delete_signal( self, words ):
  rts = [];
  if words[1] == None:
    for each_sig in self.signal_list:
      if each_sig.selected:
        recursive_signal_delete( self, parent = each_sig );
#       self.signal_delete_list += [ each_sig ];
  elif words[1] == "*":
    pass;
  else:
    for ( i, each_sig ) in enumerate( self.signal_list ):
      if ( each_sig.name == words[1] ):
        each_sig.visible = False;
        recursive_signal_delete( self, parent = each_sig );
#       self.signal_delete_list += [ each_sig ];
  self.refresh_waveforms = True;
  return rts;


def recursive_signal_delete( self, parent ):
  parent.visible = False;
  if parent.maskable:
    parent.rle_masked = True;
  for each_sig in self.signal_list:
    if each_sig.member_of == parent:
      recursive_signal_delete( self, parent = each_sig );
  return;


#####################################
# Cut a signal. Delete it from being show and copy to the copy buffer.
#def cmd_cut_signal( self, words ):
#  rts = [];
#  if words[1] == None:
#    for each_sig in self.signal_list:
#      if each_sig.selected:
#        each_sig.selected = False;
#        self.signal_copy_list += [ copy_signal_obj( self, each_sig ) ];
#        each_sig.visible = False;
#  elif words[1] == "*":
#    pass;
#  else:
#    for ( i, each_sig ) in enumerate( self.signal_list ):
#      if ( each_sig.name == words[1] ):
#        self.signal_copy_list += [ copy_signal_obj( self, each_sig ) ];
#        each_sig.visible = False;
#  self.refresh_waveforms = True;
#  return rts;


#####################################
# Cut a signal. Delete it from being shown and copy to the copy buffer.
def cmd_cut_signal( self, words ):
  print("cmd_cut_signal()");
  rts = [];
  if words[1] == None:
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
#       group_copy = each_sig.type == "group";
        group_copy = each_sig.collapsable;
        hier_offset = each_sig.hier_level;
        recursive_signal_cut(self, each_sig, None, group_copy, hier_offset );
#       each_sig.visible = False;
  elif words[1] == "*":
    pass;
  else:
    for ( i, each_sig ) in enumerate( self.signal_list ):
      if ( each_sig.name == words[1] ):
#       group_copy = each_sig.type == "group";
        group_copy = each_sig.collapsable;
        hier_offset = each_sig.hier_level;
        recursive_signal_cut(self, each_sig, None, group_copy, hier_offset );
#       each_sig.visible = False;
  self.signal_copy_list.reverse();# Not sure why
  self.refresh_waveforms = True;
  return rts;

def recursive_signal_cut( self, parent, copy_parent, group_copy, hier_offset ):
  self.signal_copy_list += [ copy_signal_obj( self, parent ) ];
  self.signal_copy_list[-1].hier_level -= hier_offset;
  parent.visible = False;

  # Note: there's a strange bug if same group is copied twice. 

  if group_copy:
    if copy_parent != None:
      self.signal_copy_list[-1].member_of = copy_parent;
    parent_copy = self.signal_copy_list[-1];# New parent, not the original
    for each_sig in self.signal_list:
      if each_sig.member_of == parent:
        recursive_signal_cut( self, parent = each_sig, copy_parent = parent_copy, 
                               group_copy = group_copy, hier_offset = hier_offset );
  else:
    self.signal_copy_list[-1].visible    = True;
    self.signal_copy_list[-1].parent     = None;
    self.signal_copy_list[-1].member_of  = None;
    self.signal_copy_list[-1].hier_level = 0;

  return;


#####################################
# rename a signal. Either "rename_signal foo bar" or "rename_signal bar" on selected
def cmd_rename_signal( self, words ):
  rts = [];
  if words[2] == None:
    for each_sig in self.signal_list:
      if each_sig.selected:
        each_sig.selected = False;
        each_sig.name = words[1];
  else:
    for ( i, each_sig ) in enumerate( self.signal_list ):
      if ( each_sig.name == words[1] ):
        each_sig.name = words[2];
  self.refresh_waveforms = True;
  return rts;

#####################################
# Clone a selected signal from selected window to another window
#def cmd_clone_signal( self, words ):
#  rts = [];
#  print("cmd_clone_signal()");
#  if words[1] == None:
#    for each_sig in self.signal_list:
#      if each_sig.selected:
#        each_sig.selected = False;
#        self.signal_copy_list += [ copy_signal_obj( self, each_sig ) ];
#        print("Copying %s" % each_sig.name );
#  elif words[1] == "*":
#    pass;
#  else:
#    for ( i, each_sig ) in enumerate( self.signal_list ):
#      if ( each_sig.name == words[1] ):
#        self.signal_copy_list += [ copy_signal_obj( self, each_sig ) ];
#  # Note that user will have to select the destination window
#  cmd_paste_signal( self, [ None,None,None] );
#  return rts;


#####################################
# Paste a signal. Identical to insert_signal ( for now anyways )
#def cmd_paste_signal( self, words ):
# print("cmd_paste_signal()");
# print("self.signal_list length is %d" % len( self.signal_list ) );
# rts = cmd_insert_signal( self, words );
# print("self.signal_list length is %d" % len( self.signal_list ) );
# return rts;

#####################################
# Paste a signal. Identical to insert_signal ( for now anyways )
def cmd_paste_signal( self, words ):
  rts = [];
  while len( self.signal_copy_list ) != 0:
    each_sig = self.signal_copy_list.pop();
#   print("cmd_paste_signal() %s" % ( each_sig.name ) );

    # A copied signal has no window
    test_flag = False;
    if each_sig.window == None:
      if self.window_selected != None:
        my_window = self.window_list[ self.window_selected ];
        my_window.signal_list += [ each_sig ];
        test_flag = True;
        each_sig.window     = my_window;
#       each_sig.visible    = True;
#       each_sig.parent     = None;
#       each_sig.member_of  = None;
#       each_sig.hier_level = 0;
        each_sig.view_obj   = None;
        each_sig.view_name  = None;

        # Create a new blank view for the paste if none exists on selected window
        if len( my_window.view_list ) == 0:
          my_view = view( name = "custom_view");
          my_view.timezone = each_sig.timezone;
          my_window.timezone  = my_view.timezone;
          my_window.view_list += [ my_view ];
          my_view.sample_period = each_sig.sample_period;
          my_window.sample_period = my_view.sample_period;
          my_view.sample_unit   = each_sig.sample_unit;
          my_window.sample_unit = my_view.sample_unit;
          my_view.trigger_index = each_sig.trigger_index;
          my_window.trigger_index = my_view.trigger_index;
        for (i, each_view) in enumerate( my_window.view_list ):
          if i == 0:
            each_sig.view_obj   = my_window.view_list[i];
            each_sig.view_name  = each_sig.view_obj.name;

        # Only insert if pasting into window with same timezone
        if each_sig.timezone == my_window.timezone:
          self.signal_list += [ each_sig ];
        else:
          print("cmd_paste_signal() : ERROR incompatible timezone");

#   if to_i != None and from_i != None:
#     # If the timezones are the same, inherit these attributes from destination
#     # group,hier_level,window,parent and then move the signal to destination
#     # For now, don't allow groups to be moved as it's super complicated
#     if self.signal_list[from_i].timezone == self.signal_list[to_i].timezone and \
#        self.signal_list[from_i].type != "group":
#       if test_flag == False:
#         self.signal_list[from_i].member_of  = self.signal_list[to_i].member_of;
#         self.signal_list[from_i].hier_level = self.signal_list[to_i].hier_level;
#         self.signal_list[from_i].window     = self.signal_list[to_i].window;
#         self.signal_list[from_i].parent     = self.signal_list[to_i].parent;
#         self.signal_list[from_i].view_name  = self.signal_list[to_i].view_name;
#         self.signal_list[from_i].view_obj   = self.signal_list[to_i].view_obj;
#       
#       # Now move from_i to just below to_i
#       if from_i > to_i : delta = 1;
#       else             : delta = 0;
#       self.signal_list.insert( to_i+delta, self.signal_list.pop(from_i));
  self.refresh_waveforms = True;
  return rts;


#####################################
# Undelete a signal from being shown <INS> and also clear rle_masked to False
def cmd_insert_signal( self, words ):
  rts = [];
  if words[1] == "*":
    while len( self.signal_delete_list ) != 0:
      each_sig = self.signal_delete_list.pop();
      if not each_sig.visible:
        each_sig.rle_masked = False;
      each_sig.visible = True;
      each_sig.hidden  = False;
  elif len( self.signal_delete_list ) != 0:
    each_sig = self.signal_delete_list.pop();
    if not each_sig.visible:
      each_sig.rle_masked = False;
    each_sig.visible = True;
    each_sig.hidden  = False;

    # If there isn't a signal selected, deleted signal(s) goes back to original spot.
    # If there IS a signal selected, move the deleted signal to just below the
    # selected signals spot AND inherit properties (Window,View,Group,etc)
    selected_signal = None;
    from_i = None;
    to_i = None;
    for (i, my_sig) in enumerate( self.signal_list ):
      if my_sig.selected:
        selected_signal = my_sig;
        to_i = i;
      if my_sig == each_sig:
        from_i = i;

#   # A copied signal has no window
    test_flag = False;
    if each_sig.window == None:
      if self.window_selected != None:
        my_window = self.window_list[ self.window_selected ];
        my_window.signal_list += [ each_sig ];
        test_flag = True;
        each_sig.window     = my_window;
        each_sig.visible    = True;
        each_sig.parent     = None;
        each_sig.member_of  = None;
        each_sig.hier_level = 0;
        each_sig.view_obj   = None;
        each_sig.view_name  = None;
        # Create a new blank view for the paste if none exists on selected window
        if len( my_window.view_list ) == 0:
          my_view = view( name = "custom_view");
          my_view.timezone = each_sig.timezone;
          my_window.timezone  = my_view.timezone;
          my_window.view_list += [ my_view ];
          my_view.sample_period = each_sig.sample_period;
          my_window.sample_period = my_view.sample_period;
          my_view.sample_unit   = each_sig.sample_unit;
          my_window.sample_unit = my_view.sample_unit;
          my_view.trigger_index = each_sig.trigger_index;
          my_window.trigger_index = my_view.trigger_index;
        for (i, each_view) in enumerate( my_window.view_list ):
          if i == 0:
            each_sig.view_obj   = my_window.view_list[i];
            each_sig.view_name  = each_sig.view_obj.name;

    if to_i != None and from_i != None:
      # If the timezones are the same, inherit these attributes from destination
      # group,hier_level,window,parent and then move the signal to destination
      # For now, don't allow groups to be moved as it's super complicated
      if self.signal_list[from_i].timezone == self.signal_list[to_i].timezone and \
         self.signal_list[from_i].type != "group":
        if test_flag == False:
          self.signal_list[from_i].member_of  = self.signal_list[to_i].member_of;
          self.signal_list[from_i].hier_level = self.signal_list[to_i].hier_level;
          self.signal_list[from_i].window     = self.signal_list[to_i].window;
          self.signal_list[from_i].parent     = self.signal_list[to_i].parent;
          self.signal_list[from_i].view_name  = self.signal_list[to_i].view_name;
          self.signal_list[from_i].view_obj   = self.signal_list[to_i].view_obj;
        
        # Now move from_i to just below to_i
        if from_i > to_i : delta = 1;
        else             : delta = 0;
        self.signal_list.insert( to_i+delta, self.signal_list.pop(from_i));
  self.refresh_waveforms = True;
  return rts;


#####################################
#def cmd_delete_signal( self, words ):
#  rts = [];
#  if words[1] == "*":
#    self.signal_list.clear();
#  else:
#    for ( i, each_sig ) in enumerate( self.signal_list ):
#      if ( each_sig.name == words[1] ):
#        del self.signal_list[i];
#  return rts;


#####################################
# When the view_name wasn't specified, inherit it from the file_name
def view_name_from_file_name( file_name ):
  fn = os.path.basename( file_name );# Remove the path
  ( fn,fext ) = os.path.splitext( fn );# ("foo",".txt");
  view_name = fn;
# print("view_name_from_file_name() %s => %s" % ( file_name, view_name ));
  return view_name;
  

#####################################
# Search the ./sump_view directory for any and all views.
# Don't execute the scripts, but parse them for view information like
# view name, timezone and sump_user_ctrl settings.
# This list of views is used for the selection boxes under "Views"
# include_view foo.txt
# include_view *.txt
def cmd_add_view_ontap( self, words, defer_gui_update = False ):
# print("add_view_ontap() %s" % words );
  rts = [];
  # Find any text files containing "create_view" as a word[0] keyword
  import glob,os;
# cwd = os.getcwd();
  cwd = self.path_to_uut;# New 2023.05.30
# file_list = glob.glob( words[1] );
  if cwd != None:
    file_list = glob.glob(os.path.join(cwd, words[1]) );# New 2023.05.30
  else:
    file_list = [];

  # New 2023.12.13
  if len(words) >=2 :
    if words[1] == None:
      words[1] = "*.txt";

  if len(words) >=3 :
    if words[2] != None:
      if words[2] == "defer_gui_update":
        defer_gui_update = True;

  # look for saved view files
  file_path = self.vars["sump_path_view"];
  file_list += glob.glob(os.path.join(file_path, words[1] ) );# New 2023.12.13

  # Also look for rom view files
  file_path = self.vars["sump_path_ram"];
# file_name = "rom_*.txt";
# print( file_path, words[1] );
  file_list += glob.glob(os.path.join(file_path, words[1] ) );# New 2023.08.10

  if len( file_list ) == 0:
    print("WARNING: len(file_list) == 0" );
  for each_file in file_list:
#   print("Importing each_file ", each_file );
    update_file_vars( self, each_file );
    file_lines = file2list( each_file );
    if any( "create_view" in each for each in file_lines ):
      for each in file_lines:
#       print(each);
        words = " ".join(each.split()).split(' ') + [None] * 4;
        if words[0] == "create_view":
          if words[1] != None:
            view_name = words[1];
          else:
            view_name = view_name_from_file_name( each_file );

# This doesn't work quite right - removed
#         # Look for any variables ( like $file_name ) and replace if found.
#         if view_name != None:
#           if "$" in view_name:
#             for key in self.vars:
#               target = "$"+key;
#               if target in view_name and len(target) == len(view_name):
#                 view_name = view_name.replace(target,self.vars[key]);
          my_view = view( name = view_name);
#         file_name = os.path.join( cwd, each_file );
          file_name = each_file;# New 2023.05.30
          my_view.filename = file_name;
          for ( i, each_word ) in enumerate( words[2:] ):
            if ( each_word != None and each_word[0:1] == "-" ):
              assign_view_attribute_by_name( self, new_view = my_view, attribute = each_word[1:], value = words[2+i+1] );
          # Don't allow multiple views of same name. Search the existing list and remove duplicates
          for ( i, each_view ) in enumerate( self.view_ontap_list ):
            if each_view.name == my_view.name:
              log(self,["WARNING: duplicate of %s - remove_view_ontap()" % my_view.name]);
              del self.view_ontap_list[i];
          # If -timezone was not specified, attempt to infer via signal source
          if my_view.timezone == None:
            # WARNING: This won't accept two or more spaces between -source and name
            if any( "-source analog_ls" in each2 for each2 in file_lines ):
              my_view.timezone = "ls";
            if any( "-source digital_ls" in each2 for each2 in file_lines ):
              my_view.timezone = "ls";
            if any( "-source analog_hs" in each2 for each2 in file_lines ):
              my_view.timezone = "hs";
            if any( "-source digital_hs" in each2 for each2 in file_lines ):
              my_view.timezone = "hs";
            if any( "-source digital_rle" in each2 for each2 in file_lines ):
              my_view.timezone = "rle";
            if my_view.timezone == None:
#             log(self,["WARNING: Inferring rle timezone even though '-source digital_rle' not found"]);
              my_view.timezone = "rle";
              # NOTE: This happens if instead of "-source digital_rle[0][1][2]" it's -"source hub0.pod1[2]"

          # If rle, we need to make a (hub,pod) list so that we know what any user_ctrl is being
          # applied to and may conflict with
          if my_view.timezone == "rle":
            for each2 in file_lines:
              if "-user_ctrl" in each2:
#               print("1");
                words = " ".join(each2.split()).split(' ');
                for (i,each_word) in enumerate( words ):
                  if "-user_ctrl" in each_word:
#                   print("2");
                    bit_rip = each_word.replace("-user_ctrl","");# "-user_ctrl[2:1]" becomes "[2:1]"
                    bit_val = words[i+1];
#                   print("--> %s : %s %s" % ( my_view.name, bit_rip, bit_val ) );
                    if ( (bit_rip,bit_val) not in my_view.user_ctrl_list ):
                      my_view.user_ctrl_list += [ (bit_rip,bit_val) ];

              if "-source " in each2:
#             if "-source digital_rle" in each2:
#               print("-->", each2 );
                # -source can either be "digital_rle[0][1][2]" or "hub0.pod1[2]"
                # look for hub0.pod1[2] and if found replace with digital_rle[0][1][2] 
                hub_num = None; pod_num = None;
                if self.sump != None:
                  for key in self.sump.rle_hub_pod_dict:
                    search_str = "-source " + key;
                    if search_str in each2:
                      (hub_num,pod_num) = self.sump.rle_hub_pod_dict[key];
                if hub_num == None:
                  each2 = each2.replace("["," ");
                  each2 = each2.replace("]"," ");
                  words = " ".join(each2.split()).split(' ');
                  for (i,each_word) in enumerate( words ):
                    if each_word == "-source":
                      try:
                        hub_num = int( words[i+2] );
                        pod_num = int( words[i+3] );
                      except:
                        if self.sump_connected:
                          log(self,["ERROR-9680 : Invalid source reference : %s" % each2]);
#                 print("Oy %s %d %d" % ( my_view.name, hub_num, pod_num ) );
                if (hub_num,pod_num) not in my_view.rle_hub_pod_list:
                  my_view.rle_hub_pod_list += [ (hub_num,pod_num ) ];
                  my_view.rle_hub_pod_user_ctrl_list += [ (hub_num,pod_num,my_view.user_ctrl_list[:] ) ];
#                   print( my_view.rle_hub_pod_list, my_view.rle_hub_pod_user_ctrl_list );
                  
#   self.rle_hub_pod_list = [];# (hub,pod) tuples assigned to this view
#   self.rle_hub_pod_user_ctrl_list = [];# (hub,pod,user_ctrl_list) tuples assigned to this view

          log(self,["View %s rle_hub_pod_list = %s" % ( my_view.name, my_view.rle_hub_pod_list )]);
          log(self,["add_view_ontap() %s at %s" % ( my_view.name, my_view.filename )]);
          self.view_ontap_list += [ my_view ];
  if defer_gui_update == False:
    create_view_selections( self );
  return rts;
# from class view
#   self.rle_hub_pod_list = [];# (hub,pod) tuples assigned to this view
#   self.rle_hub_pod_user_ctrl_list = [];# (hub,pod,user_ctrl_list) tuples assigned to this view


#####################################
# Remove an ontap view by name or wildcard search
# also accept removing by file it name ends in .txt
def cmd_remove_view_ontap( self, words ):
  rts = [];
  if words[1].endswith(".txt"):
    for each_file in file_list:
      update_file_vars( self, each_file );
      file_lines = file2list( each_file );
      # Look for create_view as it will be followed by the view name
      if any( "create_view" in each for each in file_lines ):
        for each in file_lines:
          words = " ".join(each.split()).split(' ') + [None] * 4;
          if words[0] == "create_view":
#           view_name = words[1];
            if words[1] != None:
              view_name = words[1];
            else:
              view_name = view_name_from_file_name( each_file );
            # Search the existing list and remove this view
            for ( i, each_view ) in enumerate( self.view_ontap_list ):
              if each_view.name == my_view.name:
                rts += ["remove_view_ontap() %s" % my_view.name];
                del self.view_ontap_list[i];
  else:
    # Search the existing list and remove this view
#   view_ontap_name_list = [ each.name for each in self.view_ontap_list ];# list comprehension
#   view_name_list = fnmatch.filter(view_ontap_name_list,words[1] );
#   view_name_list = [ words[1] ];
    view_ontap_name_list = [ each.name for each in self.view_ontap_list ];# list comprehension
    view_name_list = star_match( words[1], view_ontap_name_list );
    for each_name in view_name_list:
      for ( i, each_view ) in enumerate( self.view_ontap_list ):
        if each_view.name == each_name:
          rts += ["remove_view_ontap() %s" % each_name];
          del self.view_ontap_list[i];
  return rts;


#####################################
# List ontap view by name or wildcard search
# also accept removing by file it name ends in .txt
def cmd_list_view_ontap( self, words ):
  rts = [];
  if words[1].endswith(".txt"):
    for each_file in file_list:
      update_file_vars( self, each_file );
      file_lines = file2list( each_file );
      # Look for create_view as it will be followed by the view name
      if any( "create_view" in each for each in file_lines ):
        for each in file_lines:
          words = " ".join(each.split()).split(' ') + [None] * 4;
          if words[0] == "create_view":
#           view_name = words[1];
            if words[1] != None:
              view_name = words[1];
            else:
              view_name = view_name_from_file_name( each_file );
            # Search the existing list and remove this view
            for ( i, each_view ) in enumerate( self.view_ontap_list ):
              if each_view.name == my_view.name:
#               log(self,["list_view_ontap() %s %s" % ( my_view.name, my_view.filename) ]);
                rts += ["list_view_ontap() %s %s" % ( my_view.name, my_view.filename) ];
  else:
    # Search the existing list and remove this view
#   view_ontap_name_list = [ each.name for each in self.view_ontap_list ];# list comprehension
#   view_name_list = fnmatch.filter(view_ontap_name_list,words[1] );
#   view_name_list = [ words[1] ];
    view_ontap_name_list = [ each.name for each in self.view_ontap_list ];# list comprehension
    view_name_list = star_match( words[1], view_ontap_name_list );
    for each_name in view_name_list:
      for ( i, each_view ) in enumerate( self.view_ontap_list ):
        if each_view.name == each_name:
#         log(self,["list_view_ontap() %s %s" % (each_view.name, each_view.filename) ]);
          rts += ["list_view_ontap() %s %s" % (each_view.name, each_view.filename) ];
  return rts;

#####################################
# Search the ./sump_views directory for any and all views.
# Don't execute the scripts, but parse them for view information like
# view name, timezone and sump_user_ctrl settings.
# This list of views is used for the selection boxes under "Views"
#def create_view_ontap_list(self):
#  # Find any text files containing "create_view" as a word[0] keyword
#  import glob,os;
#  self.view_ontap_list = [];
#  search_path = self.vars["sump_path_views"];
#  if search_path == None or search_path == "":
#    return;
#  paths = search_path.split(',');# Multiple dirs are supported with "," separator
#  for each_path in paths:
#    file_list = glob.glob( each_path + "/*.txt");
#    for each_file in file_list:
#      file_lines = file2list( each_file );
#      if any( "create_view" in each for each in file_lines ):
#        for each in file_lines:
#          words = " ".join(each.split()).split(' ') + [None] * 4;
#          if words[0] == "create_view":
#            view_name = words[1];
#            my_view = view( name = view_name);
#            my_view.filename = each_file;
#            print("Oy", each_file );
#            for ( i, each_word ) in enumerate( words[2:] ):
#              if ( each_word != None and each_word[0:1] == "-" ):
#                assign_view_attribute_by_name( self, new_view = my_view, attribute = each_word[1:], value = words[2+i+1] );
#            self.view_ontap_list += [ my_view ];
#  return;


#####################################
def cmd_create_view( self, words ):
  self.last_create_type = "view";
  rts = [];
  rts += ["cmd_create_view()"];
  view_name = words[1];

  # If a view by this name already exists, delete it and then recreate it
# for each_view in self.view_applied_list:
#   if each_view.name == view_name:
# New 2023.12.06
#     del each_view;
#     print("Warning: View of name %s already exists!" % each_view.name );

  if view_name == None:
    try:
#   if True:
      file_name = self.vars["file_name"];# Last opened file
      view_name = view_name_from_file_name( file_name );
#   if False:
    except:
      rts += ["ERROR-7652"];
      view_name = "UNKNOWN-7652";

  print("Creating view %s" % view_name );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Creating view %s" % view_name );
  # create_view my_view -timezone slow_clock
  my_view = view( name = view_name);
  self.last_view_created = view_name;
  self.last_view_obj_created = my_view;
  self.view_applied_list += [ my_view ];
  self.group_stack_list = [];

  for ( i, each_word ) in enumerate( words[2:] ):
    if ( each_word != None and each_word[0:1] == "-" ):
      assign_view_attribute_by_name( self, new_view = my_view, attribute = each_word[1:], value = words[2+i+1] );
  self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright);
  self.pygame.event.pump();
# pygame.time.wait(10);# time in mS. GUI is out of focus
# pygame.display.update();# Now off to the GPU

# # Since new signals were added, go out and re-read the sump capture samples 
# # and populate new signal values
# populate_signal_values_from_samples( self );

# for each_sig in self.signal_list:
#   print( each_sig.name, each_sig.view_name, each_sig.visible );
#   self.name            = name;
#   self.name_rect       = None;# (x,y,w,h) of drawn text
#   self.type            = type;# "analog", "digital" "group" "spacer"
#   self.window          = None;# "analog_ls", "digital_ls", "digital_hs"
#   self.parent          = None;# parent window
#   self.view_name       = None;# like a group, but different
#   self.member_of       = None;# Signals can have a group as a parent
#   self.hier_level      = 0;
#   self.source          = "";  # "digital[0]"
#   self.nickname        = "";
    
# self.refresh_waveforms = True;
  return rts;

#####################################
def cmd_end_view( self, words ):
  rts = [];
  # When the end_view statement is encountered we need to see if the view has a timezone specified.
  # If it does not, it should inherit a timezone from 1st signal in it.
  for each_sig in self.signal_list:
    for each_view in self.view_applied_list:
      if each_view.name == each_sig.view_name and each_view.timezone == None:
        if each_sig.timezone != None:
          each_view.timezone = each_sig.timezone;

  # It's possible a view has signals ( such as type group ) that don't have a defined timezone. Inherit from view.
  for each_sig in self.signal_list:
    for each_view in self.view_applied_list:
      if each_view.name == each_sig.view_name and each_sig.timezone == None:
        if each_view.timezone != None:
          each_sig.timezone = each_view.timezone;

  # Now check for incompatible signal timezones in this view due to user error
  for each_sig in self.signal_list:
    for each_view in self.view_applied_list:
      if each_view.name == each_sig.view_name and each_view.timezone != None:
        if each_sig.timezone != None:
          if each_sig.timezone != each_view.timezone:
            log(self,["ERROR: Signal %s of timezone %s can not be in View %s of timezone %s" % \
                (each_sig.name, each_sig.timezone, each_view.name, each_view.timezone )]);
# Keep open so that add_view can be used without explicitly specifying the view name
# self.last_view_created = None;# Close this out so any new signals don't inherit this view name
  return rts;


#####################################
# List all the views
def cmd_list_view( self, words ):
  rts = [];
# for each_view in self.view_list:
  for each_view in self.view_applied_list:
    if ( each_view.name == words[1] or words[1] == "*" ):
      txt_str = "-name %s -timezone %s" % ( each_view.name, each_view.timezone );
      rts += [ txt_str ];
  return rts;


#####################################
# List all the views that a window has
def cmd_list_window_views( self, words ):
  rts = [];
  view_name = words[1];
  if words[2] == "-window":
    win_num = int(words[3],10) -1;
  elif self.window_selected != None:
    win_num = self.window_selected;
# else:
#   return ["WARNING: no window specified"];

  # Show the views of the specified window
  for (i,each_view) in enumerate( self.window_list[win_num].view_list ):
    rts += [ each_view.name ];
# for (i,each_name) in enumerate( self.window_list[win_num].view_list ):
#   rts += [ each_name ];
  return rts;


#####################################
# delete_view permanently removes the view object from the list of views.
# Don't confuse delete_view with remove_view.
# remove_view removes a view object from being displayed on a window it was on.
# add_view is the inverse of remove_view.
#def cmd_delete_view( self, words ):
#  rts = [];
#  view_name = words[1];
#  if view_name == "*":
#    self.view_list.clear();
#  else:
#    for ( i, each_view ) in enumerate( self.view_list ):
#      if ( each_view.name == view_name ):
#        del self.view_list[i];
#
#  # Just deleting the object isn't enough. Need to iterate the view_list
#  # for all three windows and delete the deleted view's name.
#  for each_win in self.window_list:
#    for (i,each_name) in enumerate( each_win.view_list ):
#      if ( each_name == view_name ):
#        del each_win.view_list[i];
#
#  return rts;


# remove_view removes a view object from being displayed on a window it was on.
def cmd_remove_view( self, words ):
  rts = [];
  view_name = words[1];
  win_num = None;
  if view_name == None:
    return rts;
  if words[2] == "-window":
    win_num = int(words[3],10)-1;
  elif self.window_selected != None:
    win_num = self.window_selected;
  else:
    select_window( self, None );
    win_num = self.window_selected;

# else:
#   return ["ERROR: no window specified"];

  if ( win_num == None ):
    print("ERROR-49 : win_num == None ");
    return rts;

  # Apply wildcard search and remove one or more views
# win_view_name_list = [ each.name for each in self.window_list[win_num].view_list ];
# view_name_list = fnmatch.filter( win_view_name_list, view_name);
# view_name_list = [ view_name ];
  win_view_name_list = [ each.name for each in self.window_list[win_num].view_list ];
  view_name_list = star_match( view_name, win_view_name_list );

  for view_name in view_name_list:
    # Remove the view from the specified window
    view_obj_list = [];
    for (i,each_view) in enumerate( self.window_list[win_num].view_list ):
      if each_view.name == view_name:
        view_obj_list += [ each_view ];
        del self.window_list[win_num].view_list[i];
        rts += ["remove_view() %s" % view_name];
 
        # Remove that view from the view_applied_list 
        for (j,each_applied_view) in enumerate( self.view_applied_list ):
          if each_applied_view == each_view:
            del self.view_applied_list[j];
          

    # Also need to remove any signal associated with that view from the signal list
    # Note the you can't "del " multiple items, so build a new list
    lst_list = [];
    for each_sig in self.signal_list:
      if each_sig.view_obj not in view_obj_list:
        lst_list += [ each_sig ];
    self.signal_list = lst_list;

  # If we just removed the last view, need to set timezone to None
  if len( self.window_list[win_num].view_list ) == 0:
    self.window_list[win_num].timezone = None;
    self.window_list[win_num].sample_period = None;
    self.window_list[win_num].sample_unit  = None;

  create_view_selections( self );
  self.refresh_waveforms = True;
  return rts;


#####################################
# unselect an object on <ESC> or right-mouse click.
def proc_unselect( self ):
  any_selected = False;
  if self.select_text_i != None:
    self.select_text_i = None;
    any_selected = True;
  else:
    for each_sig in self.signal_list:
      if each_sig.selected:
        any_selected = True;
      each_sig.selected = False;

# 2023.11.29
  if not any_selected:
    select_window( self, None );

  # 2024.01.12 : Call create_view_selections to unselect any selected view
  # There should be a better way to unselect, but I don't know what is is.
  assigned  = len( self.container_view_list )-2;
  available = assigned + 1;
  available_selected = [ self.container_view_list[available].get_single_selection() ];
  assigned_selected  = [ self.container_view_list[assigned].get_single_selection() ];
  if None not in available_selected or None not in assigned_selected:
    create_view_selections( self );
  
  rts = True;# Force a refresh
  return rts;


#####################################
# The "Apply" button was pressed, so source the selected view file
# This creates the view in the self.view_applied_list
def proc_apply_view( self ):
  print("proc_apply_view()");
  assigned  = len( self.container_view_list )-2;
  available = assigned + 1;
# for each_view_name in self.container_view_list[available].get_multi_selection():
  for each_view_name in [ self.container_view_list[available].get_single_selection() ]:
    words = ["apply_view", each_view_name ];
    cmd_apply_view(self, words );
  return;


#####################################
# The "Remove" button was pressed, so remove the selected view from the window
def proc_remove_view( self ):
  assigned  = len( self.container_view_list )-2;
  available = assigned + 1;
# for each_view_name in self.container_view_list[assigned].get_multi_selection():
  for each_view_name in [ self.container_view_list[assigned].get_single_selection() ]: 
    cmd_remove_view( self, ["remove_view",each_view_name,None,None] );
  return;


#####################################
# Take a view in the ontap list and apply it to a window
def cmd_apply_view( self, words ):
  rts = [];
  view_name = words[1];
  start_time = self.pygame.time.get_ticks();

  if view_name == "*":
#   rts +=["WARNING: Wildcard apply_view not yet implemented."]
#   return rts;
    view_name_list = [ each_view.name for each_view in self.view_ontap_list ];# all the names
    view_name_list = star_match( words[1], view_name_list );
  else:
    view_name_list = [ view_name ];

  # 2024.01.11 Strange bug where having a signal selected before a cmd_apply_view results
  # in ALL of the user_ctrl arbitration not working. Can't explain it. 
  # Unselecting seems to prevent the issue from happening though.
  for each_sig in self.signal_list:
    if each_sig.selected:
      each_sig.selected = False;

# if self.window_selected != None:
#   for each_view in self.view_ontap_list:
#     if each_view.name == view_name or view_name == "*":
  for view_name in view_name_list:
    pygame.time.wait(10);# time in mS
    start_time = self.pygame.time.get_ticks();
    for each_view in self.view_ontap_list:
      if each_view.name == view_name and self.window_selected != None:

        update_file_vars( self, each_view.filename );
        cmd_list = file2list( each_view.filename );
        for cmd_str in cmd_list:
          proc_cmd( self, cmd_str, quiet = True );
        my_new_view_name = each_view.name;
        # Now that the view has been created, find the object in the window list
        for each_window in self.window_list:
          for each_applied_view in each_window.view_list:
            if each_applied_view.name == my_new_view_name:
              # This new view might have a user_ctrl_list, if so - rip through it and
              # remove ANY conflicting views from any window.
              new_user_ctrl_list = each_applied_view.user_ctrl_list
              for ( target_i, each_target_window ) in enumerate( self.window_list ):
                for each_target_view in each_target_window.view_list:
                  user_ctrl_clash = False;
                  hub_pod_clash = False;
                  for each_new_tuple in new_user_ctrl_list:
                    for each_old_tuple in each_target_view.user_ctrl_list:
                      # TODO: This needs to check for same hub+pod too
                      (a,b) = each_new_tuple;
                      (c,d) = each_old_tuple;
                      if ( a == c and b != d ):
                        user_ctrl_clash = True;
                  for each_new_tuple in each_applied_view.rle_hub_pod_list:
                    for each_old_tuple in each_target_view.rle_hub_pod_list:
                      (a,b) = each_new_tuple;
                      (c,d) = each_old_tuple;
                      if ( a == c and b == d ):
                        hub_pod_clash = True;# (hub,pod) combo exists in both
                  if user_ctrl_clash and hub_pod_clash:
                    org_i = self.window_selected;
                    self.window_selected = target_i;
                    cmd_remove_view( self, ["remove_view",each_target_view.name,None,None] );
                    self.window_selected = org_i;
                    rts += ["Removing view %s due to user_ctrl conflict with view %s" \
                             % ( each_target_view.name, my_new_view_name )];
    stop_time = self.pygame.time.get_ticks();
    render_time = stop_time - start_time;
    log( self, ["cmd_apply_view() %s : Time = %d mS " % ( view_name, render_time)] );
    # Locate any groups that are collapsed and recursively collapse on down
    for each_sig in self.signal_list:
      if each_sig.type == "group" and each_sig.collapsed == True:
        recursive_signal_collapse( self, parent = each_sig );
# else:
#   rts += ["ERROR: no window specified"];
  stop_time = self.pygame.time.get_ticks();
  render_time = stop_time - start_time;
  log( self, ["cmd_apply_view() Time = %d Seconds" % (render_time/1000)] );
  return rts;


#####################################
# select specified window
def cmd_select_window( self, words ):
  print("select_window()");
  rts = [];
  try:
    wave_i = int( words[1] ) -1;
    select_window( self, wave_i );
  except:
    if words[1] == "*":
      for i in range(0,3):
        select_window( self, i );
  return rts;


#####################################
# close specified window
def cmd_close_window( self, words ):
  print("close_window()");
  rts = [];
  try:
    wave_i = int( words[1] ) -1;
    close_window( self, wave_i );
  except:
    if words[1] == "*":
      for i in range(0,3):
        close_window( self, i );
  return rts;


#####################################
# close bd_shell window
def cmd_close_bd_shell( self ):
  print("close_bd_shell()");
  rts = [];
  close_bd_shell( self );
  return rts;

#####################################
# open  bd_shell window
def cmd_open_bd_shell( self ):
  print("open_bd_shell()");
  rts = [];
  open_bd_shell( self );
  return rts;


#####################################
# add_grid view_name -window N
# note if -window is omitted use the current selected window number.
def cmd_add_grid( self, words ):
  print("add_grid()", words );
  rts = [];
  if words[1] == "-window":
    win_num = int(words[2],10)-1;
  elif self.window_selected != None:
    win_num = self.window_selected;
  else:
    return ["ERROR: no window specified"];
  self.window_list[win_num].grid_enable = True;
  return rts;


#####################################
# remove_grid view_name -window N
# note if -window is omitted use the current selected window number.
def cmd_remove_grid( self, words ):
  print("remove_grid()", words );
  rts = [];
  if words[1] == "-window":
    win_num = int(words[2],10)-1;
  elif self.window_selected != None:
    win_num = self.window_selected;
  else:
    return ["ERROR: no window specified"];
  self.window_list[win_num].grid_enable = False;
  return rts;


#####################################
# add_view view_name -window N
# note if -window is omitted use the current selected window number.
# note if view_name isn't specified, use last_view_created name
def cmd_add_view( self, words, defer_gui_update = False ):
  print("add_view()", words );
  rts = [];
  if words[1] == None:
    view_name = self.last_view_created;
    view_obj  = self.last_view_obj_created;
  elif words[1] == "-window":
    view_name = self.last_view_created;
    view_obj  = self.last_view_obj_created;
    words[3] = words[2];
    words[2] = words[1];
  else:
    view_name = words[1];

  if words[2] == "-window":
    win_num = int(words[3],10)-1;
  elif self.window_selected != None:
    win_num = self.window_selected;
  else:
    return ["ERROR: no window specified"];

  # If this view already exists in self.window[n].view_list, do nothing.
  for each_view in self.window_list[win_num].view_list:
    if each_view.name == view_name:
      return ["WARNING: View is already applied to Window"];

  # Find the view object that has the same name of added view
  my_view = None;
  for each_view in self.view_applied_list:
#   if each_view.name == view_name:
    if each_view.name == view_name and each_view.window == None:
      my_view = each_view;
# New 2023.12.06
#     my_view = copy.deepcopy( each_view );
#     print("Oy1");

  # Abort if view not found
  if my_view == None:
    return ["ERROR: View %s not found!" % ( view_name )];

  # A window may only have a single timezone associated with it.
  # when view_list is empty and a view is added, inherit that timezone
  if len( self.window_list[win_num].view_list ) == 0:
    self.window_list[win_num].timezone = my_view.timezone;

  timezone = self.window_list[win_num].timezone;

  # Refuse to add another view that has a different timezone
# if my_view.timezone != timezone:
#   return ["ERROR: incompatible timezone %s != %s" % ( each_view.timezone, timezone )];

  # Add this new view object to the window.view_list for the selected window.
  self.window_list[win_num].view_list += [ my_view ];
  # New 2023.12.06
  my_view.window = self.window_list[win_num];
# print("View %s belongs to Window %d" % ( my_view.name, win_num ));


  # Since new views were added, go out and re-read the sump capture samples 
  # and populate new signal values with samples if sump is connected
# if self.sump != None:
  # This crashes if we haven't done a download yet, so this hack checks
  # for any values to determine if it's safe to call.
# print("Oy");
# if any ( len(each_sig.values) != 0 for each_sig in self.signal_list ):
#   print("Vey");
# if True:
  populate_signal_values_from_samples( self );
  if defer_gui_update == False:
    create_view_selections( self );
  return rts;

# Reduce a floating point number to three decimal places max
def three_decimal_places( num ):
# num = num * 1000;
# num = float( int( num ) );# Truncate
# num = num / 1000.0;
  num = round( num, 3 );
  return num;

# Convert a float to a comma separated string. This is a new Python method so
# make a function so that users with older python can bypass rather than crash
def comma_separated( num ):
  try:
    txt = f"{num:,}"; # Comma thousand separator
  except:
    txt = "%f" % float(num);
  return txt;


#####################################
# Save selected signals to a list text file. Lots of copy+past from save_vcd() 
def cmd_save_list( self, words ):
  rts = [];
  rts += ["save_list()"];
  cmd = words[0];
  filename = words[1];
  lst_list = [];

  list_csv_format = ( self.vars["list_csv_format"].lower() in ["true","yes","1"] );

  signal_names = [];   # [ (name,bits),(name,bits) ]
  signal_names_and_groups = [];   # [ (name,bits,bool True if group) ]
  signal_samples = []; # [ [(val,time),(val,time)], [(val,time),(val,time)]]
  time_list = [];

  # If both C1 and C2 cursors are visible, crop the list based on their distance to Trigger
  if self.cursor_list[0].visible and self.cursor_list[1].visible:
    c1 = self.cursor_list[0].trig_delta_t;# Distance from cursor to trigger
    c2 = self.cursor_list[1].trig_delta_t;# Distance from cursor to trigger
    if ( c1 > c2 ):
      c_start = c2;
      c_stop  = c1;
    else:
      c_start = c1;
      c_stop  = c2;
  else:
    c_start = None;
    c_stop  = None;

# Only the selected
# if self.window_selected != None:
#   win_num = self.window_selected;
#   signal_list = self.window_list[win_num].signal_list;

# All Windows - List will save only selected Signals 
  signal_list = [];
  for each_window in self.window_list:
    signal_list += each_window.signal_list;

  list_group_names  = True;
  list_hubpod_nums  = False;
  list_hubpod_names = True;

  none_selected = not any ( each_sig.selected for each_sig in signal_list );

  if True:
    min_time = 0;
    max_time = 0;
    for each_sig in signal_list:
#     if each_sig.hidden == False and each_sig.visible == True:
#     if each_sig.hidden == False and each_sig.visible == True and each_sig.values != None and len( each_sig.values ) != 0:
# Note : It's important to make VCDs from signals not visible as they may be in collapsed groups
      if each_sig.values != None and len( each_sig.values ) != 0:
        if each_sig.source != None and ( each_sig.selected == True or none_selected == True ) :
          if "digital_rle" in each_sig.source:
            sig_name = each_sig.name;
            # Convert group hiearachies to signal name of group.group.sig_name
            if list_group_names == True:
              sig_name = recurs_group_name( self, signal_list, each_sig, sig_name );

            words = each_sig.source.split('[');
            hub_num = int(words[1].replace("]",""));
            pod_num = int(words[2].replace("]",""));

            if list_hubpod_nums  == True:
              hub_str  = "hub(%d)" % hub_num;
              pod_str  = "pod(%d)" % pod_num;
              sig_name = hub_str+"."+pod_str+"."+sig_name;
            if list_hubpod_names  == True:
              key_name = "";
              for key in self.sump.rle_hub_pod_dict:
                if self.sump.rle_hub_pod_dict[key] == (hub_num,pod_num):
                  key_name = key;
              words = key_name.split(".");
              if len(words) == 2:
                hub_str = words[0];
                pod_str = words[1];
              else:
                hub_str  = "hub(%d)" % hub_num;# Fallback to nums if names failed
                pod_str  = "pod(%d)" % pod_num;
              sig_name = hub_str+"."+pod_str+"."+sig_name;
 
            signal_names            += [ ( sig_name, each_sig.bits_total) ];
            signal_names_and_groups += [ ( sig_name, each_sig.bits_total, False) ];
            sig_values = list(each_sig.values[0:-1]);
            sig_values += [ -1 ];# Make last sample X unknown
            this_signal_samples = list(zip( sig_values, each_sig.rle_time ));
            signal_samples += [ this_signal_samples ];
            time_list      += each_sig.rle_time;

    if len(time_list) == 0:
      rts = [ "ERROR No time_list. Did you forget to select signals?" ];
      return rts;

    min_time = min( time_list );
    max_time = max( time_list );
    time_list += [ min_time - 1 ];# Starting point of 1ps before 1st valid RLE sample

    # casting list to a set removes redundant time entries. ie, [0,1,1,2,3] becomes [0,1,2,3]
    time_set = sorted( set( time_list ) );# uniquify

    # top of file is key for signal name order
    if list_csv_format == True:
      lst_list += ["time_ps"];
    for (sig_nam,sig_bits) in signal_names:
      sig_full_name = "%s" % sig_nam;
      if list_csv_format == False:
        lst_list += [ "# %s" % sig_full_name ];
      else:
        lst_list[-1] += ",%s" % sig_full_name;

    signal_cache = {}; # Hash dictionary of last known value and when next timestamp is
    for ( i, each_signal_sample ) in enumerate( signal_samples ):
      (sig_nam,sig_bits) = signal_names[i];
      sample_i = 0;
      rle_value = -1;# Unknown
      ( null, rle_time ) = each_signal_sample[sample_i];# 1st RLE time for this signal
      signal_cache[ sig_nam ] = ( rle_value, rle_time, sample_i );# Until this RLE time, value is X

#   dump_list = [];
#   for (rle_value, rle_time ) in signal_samples[0]:
#     dump_list += [ "%d %d" % ( rle_time, rle_value ) ];
#   list2file("dump2.txt", dump_list );

    # Walk thru the uniquified set of RLE time
    for each_time in time_set:
      for (i,(sig_nam,sig_bits)) in enumerate( signal_names ):
        (last_val, next_rle_time, last_rle_index ) = signal_cache[ sig_nam ];
        if each_time == next_rle_time:
          each_signal_sample = signal_samples[i];

          # Advance next RLE time for this signal if there are samples left
          if ( last_rle_index+1 < len( each_signal_sample ) ):
            ( rle_value, null          ) = each_signal_sample[last_rle_index  ];# RLE Value for this time
            ( null     , next_rle_time ) = each_signal_sample[last_rle_index+1];# Next RLE time
            signal_cache[ sig_nam ] = ( rle_value, next_rle_time,last_rle_index+1 );
          else:
            signal_cache[ sig_nam ] = ( -1, max_time, last_rle_index );# No more so go X unknown

      # Either Crop to C1,C2 cursors or else dump the entire capture
      if c_start == None or ( each_time >= c_start and each_time <= c_stop ):
        if list_csv_format == True:
          txt = "%d" % int(each_time); # Note no comma thousand separators since this is a CSV file
        else:
          txt = "";
        for (i,(sig_nam,sig_bits)) in enumerate( signal_names ):
          (rle_value, rle_time, rle_index ) = signal_cache[ sig_nam ];
          if ( sig_bits  == 1 ):
            if   ( rle_value == -1 ): val = "x";
            elif ( rle_value == 0  ): val = "0";
            elif ( rle_value == 1  ): val = "1";
            else                    : val = "x";
          else:
            num_nibbles = sig_bits // 4;
            if sig_bits % 4 != 0: num_nibbles += 1;
            if ( rle_value == -1 ):
              val = (" "*(num_nibbles-1)) + "x";
            else:
              # 8192 is max signal width in bits
              val = "%02048x" % rle_value;
              val = val[-num_nibbles:];
          if list_csv_format == True:
            txt += ",%s" % val.replace(" ",""); 
          else:
            txt += "%s " % val; 
        if list_csv_format == False:
          txt += ": " + comma_separated(int(each_time)) + " ps"; # Comma thousand separator
        lst_list += [ txt ];

  if len( lst_list ) != 0:  
    if filename == None:
      filename_path = self.vars["sump_path_list"];
      filename_base = os.path.join( filename_path, "sump3_" );
      if list_csv_format == True: 
        file_ext = ".csv";
      else:
        file_ext = ".txt";
      filename = make_unique_filename( self, filename_base, file_ext );
    else:
      filename_path = self.vars["sump_path_list"];
      filename = os.path.join( filename_path, filename );

    if ( not os.path.exists( filename_path ) ):
      try:
        os.mkdir(filename_path);
      except:
        log(self,["ERROR: unable to mkdir %s" % filename_path]);
    rts += [ "Saving %s" % filename ];
    try:
      list2file( filename, lst_list );
      self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Saved %s" % filename);
    except:
      rts += [ "ERROR Saving %s" % filename ];


  return rts;


#####################################
# Convert RLE dataset to Verilog VCD
def cmd_save_vcd( self, words ):
  if not self.has_focus:
    print("I don't have focus. I shouldn't be here. I don't belong.");
    return ["No Focus"];
  rts = [];
  rts += ["save_vcd()"];
  cmd = words[0];
  filename = words[1];
  vcd_list = None;
  gtkw_list = [];

  # These options make the VCD signal names really long but preserve hierarchical names
  vcd_hierarchical = ( self.vars["vcd_hierarchical"].lower() in ["true","yes","1"] );
  vcd_hubpod_names = ( self.vars["vcd_hubpod_names"].lower() in ["true","yes","1"] );
  vcd_hubpod_nums  = ( self.vars["vcd_hubpod_nums"].lower() in ["true","yes","1"] );
  vcd_group_names  = ( self.vars["vcd_group_names"].lower()  in ["true","yes","1"] );
# vcd_remove_rips  = ( self.vars["vcd_remove_rips"].lower() in ["true","yes","1"] );
# vcd_replace_rips = ( self.vars["vcd_replace_rips"].lower() in ["true","yes","1"] );

  if ( vcd_hubpod_names and vcd_hubpod_nums ):
    vcd_hubpod_nums = False;# There can be only one

  vcd_remove_rips = True;
  vcd_replace_rips = False;

  # See class_rl2vcd.py from Sump2 project
  signal_names = [];   # [ (name,bits),(name,bits) ]
  signal_names_and_groups = [];   # [ (name,bits,bool True if group) ]
  signal_samples = []; # [ [(val,time),(val,time)], [(val,time),(val,time)]]
  time_list = [];

  if self.cursor_list[0].visible and self.cursor_list[1].visible:
    c1 = self.cursor_list[0].trig_delta_t;# Distance from cursor to trigger
    c2 = self.cursor_list[1].trig_delta_t;# Distance from cursor to trigger
    if ( c1 > c2 ):
      c_start = c2;
      c_stop  = c1;
    else:
      c_start = c1;
      c_stop  = c2;
  else:
    c_start = None;
    c_stop  = None;
      

# Only the selected
# if self.window_selected != None:
#   win_num = self.window_selected;
#   signal_list = self.window_list[win_num].signal_list;
# All Windows
  signal_list = [];
  for each_window in self.window_list:
    signal_list += each_window.signal_list;

  none_selected = not any ( each_sig.selected for each_sig in signal_list );

  hub_stack = [];
  pod_stack = [];
  group_stack = [];
  current_group = None;
  current_hub = None;
  current_pod = None;
  hub_str = None;
  pod_str = None;
  if True:
    min_time = 0;
    max_time = 0;
    for each_sig in signal_list:
#     if each_sig.hidden == False and each_sig.visible == True:
#     if each_sig.hidden == False and each_sig.visible == True and each_sig.values != None and len( each_sig.values ) != 0:
# Note : It's important to make VCDs from signals not visible as they may be in collapsed groups
      if each_sig.values != None and len( each_sig.values ) != 0:
        sig_rip = "";
        # If signals are selected, only export those. Otherwise export all signals
        if each_sig.source != None and ( each_sig.selected == True or none_selected == True ) :
          if "digital_rle" in each_sig.source:
            sig_name = each_sig.name;
            # Remove "[7:0]" from "foo[7:0]" since GTKwave displays bitwidths 
            if vcd_remove_rips == True:
              words = sig_name.split('[');
              sig_name = words[0];# "foo" and "7:0]" is tossed
              if len(words) == 2:
                sig_rip = "[" + words[1];

            # Replace "[7:0]" from "foo[7:0]" with "foo_7_0"
            if vcd_replace_rips == True:
              sig_name = sig_name.replace("[","_");
              sig_name = sig_name.replace(":","_");
              sig_name = sig_name.replace("]","");

            # Convert group hiearachies to signal name of group.group.sig_name
            if vcd_group_names == True:
              sig_name = recurs_group_name( self, signal_list, each_sig, sig_name );

            words = each_sig.source.split('[');
            hub_num = int(words[1].replace("]",""));
            pod_num = int(words[2].replace("]",""));

            if vcd_hubpod_nums  == True:
              hub_str  = "hub(%d)" % hub_num;
              pod_str  = "pod(%d)" % pod_num;
              sig_name = hub_str+"."+pod_str+"."+sig_name;
            if vcd_hubpod_names  == True:
              key_name = "";
              for key in self.sump.rle_hub_pod_dict:
                if self.sump.rle_hub_pod_dict[key] == (hub_num,pod_num):
                  key_name = key;
              words = key_name.split(".");
              if len(words) == 2:
                hub_str = words[0];
                pod_str = words[1];
              else:
                hub_str  = "hub(%d)" % hub_num;# Fallback to nums if names failed
                pod_str  = "pod(%d)" % pod_num;
              sig_name = hub_str+"."+pod_str+"."+sig_name;

 
            if vcd_hierarchical == True:
              # This is confusing. We have to close hierarchy in the order group,pod,hub
              # and create new hierarchy in the order hub,pod,group
              need_group_start = False;
              need_pod_start   = False;
              need_hub_start   = False;
              need_group_stop  = False;
              need_pod_stop    = False;
              need_hub_stop    = False;

              if len(pod_stack) != 0:
                if pod_stack[-1] != pod_num:
                  pod_stack = [ pod_num ];
                  need_pod_stop  = True; 
                  need_pod_start = True; 
              else:
                pod_stack = [ pod_num ];
                need_pod_start = True; 

              if len(hub_stack) != 0:
                if hub_stack[-1] != hub_num:
                  pod_stack = [ pod_num ];
                  hub_stack = [ hub_num ];
                  need_pod_stop  = True; 
                  need_hub_stop  = True;
                  need_pod_start = True; 
                  need_hub_start = True;
              else:
                pod_stack = [ pod_num ];
                hub_stack = [ hub_num ];
                need_pod_start = True; 
                need_hub_start = True;

              if ( vcd_hubpod_names or vcd_hubpod_nums ):
                if need_hub_stop  == True:
                  signal_names_and_groups += [ ( "", 0,True ) ];# End current 
                if need_pod_stop  == True:
                  signal_names_and_groups += [ ( "", 0,True ) ];# End current 

              # Close out all groups
              if need_hub_stop == True or need_pod_stop == True:
                while len( group_stack ) != 0 :
                  current_group = group_stack.pop();
                  signal_names_and_groups += [ ( "", 0,True ) ];
                current_group = None;

              # If this signals group isn't current_group then either
              # 1) We've pushed down into a new group
              # 2) We've popped up and left a group
              if each_sig.member_of != None and current_group == None:
                need_group_start = True;# Pushed down

              elif each_sig.member_of != None and each_sig.member_of != current_group:
                # Check to see if it's a member of one up from current group
                need_group_start = True;# Pushed down until determine otherwise
                if len(group_stack) >= 2:
                  if each_sig.member_of == group_stack[-2]:
                    need_group_stop = True;# Popped up
                    need_group_start = False;

              if need_hub_start == True and hub_str != None:
                signal_names_and_groups += [ ( hub_str               , 0,True ) ];# Start new hub
              if need_pod_start == True and pod_str != None:
                signal_names_and_groups += [ ( pod_str               , 0,True ) ];# Start new pod
              if need_group_start == True:
                signal_names_and_groups += [ ( each_sig.member_of.name,0,True ) ];
                group_stack += [ each_sig.member_of ];
                current_group = each_sig.member_of;

            signal_names            += [ ( sig_name, each_sig.bits_total) ];
#           print( sig_name, sig_rip );
#           gtkw_list               += [   sig_name                       ];
            gtkw_list               += [   sig_name + sig_rip             ];
            signal_names_and_groups += [ ( sig_name, each_sig.bits_total, False) ];
            sig_values = list(each_sig.values[0:-1]);
            sig_values += [ -1 ];# Make last sample X unknown

            this_signal_samples = list(zip( sig_values, each_sig.rle_time ));
            signal_samples += [ this_signal_samples ];
            time_list      += each_sig.rle_time;


    if vcd_hierarchical == True:
      while len( group_stack ) != 0 and each_sig.member_of != current_group:
        current_group = group_stack.pop();
        signal_names_and_groups += [ ( "", 0,True ) ];# End current
      if ( vcd_hubpod_names or vcd_hubpod_nums ):
        signal_names_and_groups += [ ( "", 0,True ) ];# End current Pod
        signal_names_and_groups += [ ( "", 0,True ) ];# End current Hub

    if len(time_list) == 0:
      rts = [ "ERROR No time_list" ];
      return rts;
    min_time = min( time_list );
    max_time = max( time_list );

    # Adjust so that 1st sample is at time 0 instead of trigger being at T=0
    time_list = [ each + abs(min_time) for each in time_list ];
    # Also adjust the cursors for culling samples outside cursor region
    if c_start != None:
      c_start += abs(min_time);
      c_stop  += abs(min_time);


    # casting list to a set removes redundant time entries. ie, [0,1,1,2,3] becomes [0,1,2,3]
    # this is useful for VCD creation.
    time_set = sorted( set( time_list ) );

    # VCD files map long signal names to short uniquified characters
    char_code = []; # This will be ['AAAA','AAAB',..,'ZZZZ']
    for ch1 in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
      for ch2 in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        for ch3 in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
          for ch4 in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            char_code += [ ch1+ch2+ch3+ch4 ];

    # Create boilerplate VCD header and footer
    now = time.time();
    means = time.ctime( now );
    if self.vars["uut_name"] == None:
      module_name = "UUT";
    else:
      module_name = self.vars["uut_name"];

    rts  = [];
    rts += [ "$date " + means + " $end" ];
    rts += [ "$version sump3.py " + self.vers + " cmd_save_vcd() by BlackMesaLabs $end" ];
    rts += [ "$timescale 1ps $end" ];
    rts += [ "$scope module " + module_name + " $end" ];
    header = rts[:];

    rts  = [];
    rts += [ "$upscope $end"];
    rts += [ "$enddefinitions $end"];
    rts += [ "#0" ];
    rts += [ "$dumpvars"];
#   rts += [ "$end"];
    footer = rts[:];

    rts = header[:];

    # Assign a unique VCD symbol ( "AAAA" ) to each signal and make the name_map
    ch_ptr = 0;
    signal_ch_code = [];
#   dump_list = [];
    for (sig_name,sig_width,is_group) in signal_names_and_groups:
#     dump_list += [ "%s %s %s" % ( sig_name, sig_width, is_group ) ];
      if is_group == True:
        if sig_name == "":
          rts += [ "$upscope $end" ];
        else:
          rts += [ "$scope module "+sig_name+" $end" ];
      else:
        if ( sig_width == 1 ):
          ch_code = char_code[ ch_ptr ];
          signal_ch_code += [ ch_ptr ]; ch_ptr +=1;
          rts += [ "$var wire 1 " + ch_code + " " + sig_name + " $end" ];
        else:
# 2024.02.09
#         signal_ch_code += [ ch_ptr ];
#         for i in range(0,sig_width):
#           ch_code = char_code[ ch_ptr ]; ch_ptr +=1;
#           bit = sig_width-1-i;
#           rts += [ "$var wire 1 "+ch_code+" "+sig_name+" [%d] $end" % bit ];
          signal_ch_code += [ ch_ptr ];
          ch_code = char_code[ ch_ptr ]; ch_ptr +=1;
          txt = "$var wire %d " % sig_width;
          txt += ch_code + " ";
          txt += sig_name+" [%d:0] $end" % ( sig_width-1 );
          rts += [ txt ];
#         rts += [ "$var wire %d " % sig_width +ch_code+" "+sig_name+" [%d:0] $end" % sig_width-1];

#   list2file("dump2.txt", dump_list );
    rts +=  footer;

    # Create a list that has next RLE timestamp and index for each signal
    # signal_samples looks like this [ [(val,time),(val_time),..], [(val,time),... ] ];
    signal_rle_time = [];
    for each_signal_sample in signal_samples:
      ( rle_value, rle_time ) = each_signal_sample[0];# Should be 0 always
      signal_rle_time += [ ( rle_time+abs(min_time), 0 ) ];# Time,Index

    if c_start != None:
      c_start_located = False;
    else:
      c_start_located = True;

    # Sweep a tick count from min_time to max_time and add samples as they "expire"
    time_i = 0;
    last_vcd_time = -1;
    for each_time in time_set:
      vcd_ps_time = -1;
      for ( i, (rle_time,rle_index) ) in enumerate( signal_rle_time ):
        # Cursor cropping of VCD signals
        if c_start != None:
          if ( each_time >= c_start and each_time < c_stop ):
            if c_start_located == False:
              c_start_located = True;
          if ( each_time >= c_stop ):
            if c_start_located == True:
              c_start_located = False;

        if ( each_time == rle_time ):
          # this will be true only on i == 0
          # VCD format is one timestamp followed by all the signals that change at that time.
          if ( rle_time > last_vcd_time ):
            if c_start == None:
              vcd_ps_time = rle_time;
            else:
              vcd_ps_time = rle_time - c_start;
            if c_start_located == True:
              rts += [ "#" + "%d" % vcd_ps_time ];
            last_vcd_time = rle_time;

          if c_start_located == True:
            ( rle_value, rle_time ) = signal_samples[i][rle_index];
            (sig_name,sig_width) = signal_names[i];
            if ( sig_width == 1 ):
              ch_code = char_code[ signal_ch_code[ i ] ];
              if   ( rle_value == -1 ): val = "x";
              elif ( rle_value == 0  ): val = "0";
              elif ( rle_value == 1  ): val = "1";
              else                    : val = "x";
              rts += [ val + ch_code ];
            else:
              bit = 1;
              val = "";
              for j in range(0,sig_width):
# 2024.02.09
#               if ( rle_value == -1 ): val = "x";
#               else:
#                 if ( ( rle_value & bit ) == 0 ): val = "0";
#                 else                           : val = "1";
#               bit = bit << 1;
#               ch_code = char_code[ signal_ch_code[ i ]+sig_width-1-j ];
#               rts += [ val + ch_code ];
                if ( rle_value == -1 ): val += "x";
                else:
                  if ( ( rle_value & bit ) == 0 ): val += "0";
                  else                           : val += "1";
                bit = bit << 1;
              ch_code = char_code[ signal_ch_code[ i ] ];
              val = "b" + val[::-1];# Reverse bit ordering and add the "b" for binary
              rts += [ val + " " + ch_code ];

          # Advance next RLE time for this signal if there are samples left
          if ( rle_index+1 < len( signal_samples[i] ) ):
            ( rle_value, rle_time ) = signal_samples[i][rle_index+1];
            signal_rle_time[i] = ( rle_time+abs(min_time), rle_index+1 );
          else:
            signal_rle_time[i] = ( max_time+abs(min_time)+1, rle_index+1 );# Done
         
    vcd_list = rts[:];

  rts = [];
  if vcd_list != None:
    if filename == None:
      filename_path = self.vars["sump_path_vcd"];
      filename_base = os.path.join( filename_path, "sump3_" );
      filename = make_unique_filename( self, filename_base, ".vcd" );
    else:
      filename_path = self.vars["sump_path_vcd"];
      filename = os.path.join( filename_path, filename );

    if ( not os.path.exists( filename_path ) ):
      try:
        os.mkdir(filename_path);
      except:
        log(self,["ERROR: unable to mkdir %s" % filename_path]);
    rts = [ "Saving %s" % filename ];
    try:
      list2file( filename, vcd_list );
      self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Saved %s" % filename);
    except:
      rts = [ "ERROR Saving %s" % filename ];

    vcd_viewer_en      = ( self.vars["vcd_viewer_en"].lower() in ["true","yes","1"] );
    vcd_viewer_gtkw_en = ( self.vars["vcd_viewer_gtkw_en"].lower() in ["true","yes","1"] );
    vcd_viewer_path    = self.vars[ "vcd_viewer_path"  ];
    vcd_viewer_width   = self.vars[ "vcd_viewer_width"  ];
    vcd_viewer_height  = self.vars[ "vcd_viewer_height"  ];
    if ( vcd_viewer_en == True ):
      vcd_file = filename;
      if not vcd_viewer_gtkw_en:
        gtkw_file = "";
      else:
        (path,fnl) = os.path.split( vcd_file );
        (fn,fext)  = os.path.splitext( fnl );
        fn     = fn + ".gtkw";
        gtkw_file = os.path.join( path, fn );
        rts += generate_gtkw( self, module_name, vcd_hierarchical, vcd_file, gtkw_file, gtkw_list,
                              vcd_viewer_width, vcd_viewer_height );

      if ( os.path.exists( vcd_viewer_path ) and os.path.exists( vcd_file ) ):
#       python_env = os.environ.copy();
        try:
          rts += ["( vcd_viewer_path, vcd_file ) %s %s" % ( vcd_viewer_path, vcd_file )];

# This had issues with not terminating the PyGame-GUI event and looping forever
# launching GTKwave over and over and over again.
#         # using pipe causes the process to wait until it is done communicating
#         # causing several processes coverage to be missed during the combine step
#         import subprocess;
#         startupinfo = subprocess.STARTUPINFO();
#         startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW;
#         startupinfo.wShowWindow = subprocess.SW_HIDE;
#         process = subprocess.Popen(args=[ vcd_viewer_path,
#                                            vcd_file, gtkw_file      ],
#                                            shell = True,
#                                            startupinfo=startupinfo, );
          os.system("%s %s %s" % ( vcd_viewer_path, vcd_file, gtkw_file ));
        except:
          rts += ["ERROR: ( vcd_viewer_path, vcd_file ) %s %s" % ( vcd_viewer_path, vcd_file )];
# print("3");
  return rts;


#####################################
# Generate a GTKW list 
# [*] sump3.py generated
# [dumpfile] "./sump2_vcd/sump2_0008.vcd"
# [savefile] "./sump2_vcd/sump2_0008.gtkw"
# [size] 1816 920
# TOP.foo[2:0]
def generate_gtkw( self, module_name, hierarchical, vcd_file, gtkw_file, gtkw_list, w, h ):
  rts = [];
  gtkw_flist = [];
  gtkw_flist += ["[*]"];
  gtkw_flist += ['[dumpfile] "./%s"' % vcd_file ];
  gtkw_flist += ['[savefile] "./%s"' % gtkw_file];
  gtkw_flist += ["[size] %s %s" % ( w, h )];
  for sig_name in gtkw_list:
    # Spartan7mini.clk_80.u0_pod.u0_group_name.\clk_80.u0_pod.u0_group_name.psu_fault
    if hierarchical:
      b = sig_name.split(".");
      c = len(b[-1]) + 1;
      hier_name = sig_name[:-c];# Remove the signal short name from the full hier name
      gtkw_flist += ["%s.%s.\\%s" % (module_name, hier_name, sig_name ) ];
#     gtkw_flist += [   "%s.\\%s" % (             hier_name, sig_name ) ];
    else:
      gtkw_flist += ["%s.\\%s" % (module_name, sig_name ) ];
#     gtkw_flist += [   "%s" % (             sig_name ) ];
  try:
    list2file( gtkw_file, gtkw_flist );
  except:
    rts = [ "ERROR Saving %s" % gtkw_file ];
  return rts;


#####################################
# Convert Verilog VCD to RLE dataset
def cmd_load_vcd( self, words ):
  rts = [];
  rts += ["load_vcd() : THIS FEATURE IS NOT YET IMPLEMENTED"];
  cmd = words[0];
  filename = words[1];
  return rts;


#####################################
# Recursively find any group name(s) for a signal
def recurs_group_name( self, signal_list, my_signal, name ):
  if my_signal.member_of != None:
    parent = my_signal.member_of;
    name = parent.name + "." + name;
    name = recurs_group_name(self, signal_list, parent, name );
  return name;


#####################################
def cmd_add_measurement( self, words ):
  log(self,["cmd_add_measurement()"]);
  rts = [];
  for each_sig in self.signal_list:
    if ( each_sig.name == words[1] or words[1] == "*" or each_sig.selected ):
      rts += ["Adding %s" % each_sig.name ];
      self.measurement_list += [ each_sig ];

  # Deselect so isn't displayed as selected signal cursor info
  for each_sig in self.signal_list:
    if each_sig.selected:
      each_sig.selected = False;
      self.refresh_waveforms = True;
      self.refresh_sig_names = True;
  return rts;


#####################################
def cmd_remove_measurement( self, words ):
  log(self,["cmd_remove_measurement()"]);
  rts = [];
  # Note you can't "del" multiple items, so just build a new list instead
  new_list = [];
  for each_sig in self.measurement_list:
    if ( each_sig.name == words[1] or words[1] == "*" or each_sig.selected ):
      rts += ["Removing %s" % each_sig.name ];
    else:
      new_list += [ each_sig ];
  self.measurement_list = new_list;

  # Deselect so isn't displayed as selected signal cursor info
  for each_sig in self.signal_list:
    if each_sig.selected:
      each_sig.selected = False;
      self.refresh_waveforms = True;
      self.refresh_sig_names = True;
  return rts;


#####################################
def cmd_save_window( self, words ):
  log(self,["cmd_save_window()"]);
  rts = image_save( self, words );
  return rts;


#####################################
def cmd_save_screen( self, words ):
  log(self,["cmd_save_screen()"]);
  rts = image_save( self, words );
  return rts;


#####################################
# Called by cmd_save_window, _screen
def image_save( self, words ):
  rts = [];
  cmd = words[0];
  ext = self.vars["screen_save_image_format"];# png jpg bmp
# self.screen_shot = True;
# draw_surfaces(self);
# self.screen_shot = False;

  if ext not in ["png","jpg","bmp"]:
    ext = "png";
  if words[1] == None:
    filename_path = self.vars["sump_path_"+ext];
    filename_base = os.path.join( filename_path, "sump3_" );
    filename = make_unique_filename( self, filename_base, "."+ext );
  else:
    (file_name, file_ext ) = os.path.splitext( words[1] );
    file_ext = file_ext.lower();
    filename_path = self.vars["sump_path_"+file_ext[-3:]];
    filename = os.path.join( filename_path, words[1] );

  if ( not os.path.exists( filename_path ) ):
    try:
      os.mkdir(filename_path);
    except:
      log(self,["ERROR: unable to mkdir %s" % filename_path]);

  if cmd == "save_window":
    my_window  = self.window_list[ self.window_selected ];
    my_image   = my_window.image;
    my_surface = my_window.surface;
  else:
    my_surface = self.screen;

  txt = "Saving %s" % filename;
  rts += [ txt ];
  try:
    self.pygame.image.save( my_surface, filename );
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Saved %s" % filename);
  except:
    txt = "ERROR Saving %s" % filename;
    rts += [ txt ];
# draw_surfaces(self);
  return rts; 


#####################################
#def cmd_save_pic( self, words ):
#  rts = [];
#  cmd = words[0];
#  ext = None;
#  if   ( cmd == "save_jpg" ):
#    ext = "jpg";
#  elif ( cmd == "save_bmp" ):
#    ext = "bmp";
#  else:
#    ext = "png";
#
#  if ext == None and words[1] == None:
#    ext = "png";
#
#
#  if words[1] == None:
#    filename_path = self.vars["sump_path_"+ext];
#    filename_base = os.path.join( filename_path, "sump3_" );
#    filename = make_unique_filename( self, filename_base, "."+ext );
#  else:
#    (file_name, file_ext ) = os.path.splitext( words[1] );
#    file_ext = file_ext.lower();
#    filename_path = self.vars["sump_path_"+file_ext[-3:]];
#    filename = os.path.join( filename_path, words[1] );
#
#  if ( not os.path.exists( filename_path ) ):
#    try:
#      os.mkdir(filename_path);
#    except:
#      log(self,["ERROR: unable to mkdir %s" % filename_path]);
#
#  if self.window_selected == None:
#    self.pygame.image.save( self.screen, filename );
#  else:
#    my_window  = self.window_list[ self.window_selected ];
#    my_image   = my_window.image;
#    my_surface = my_window.surface;
#    txt = "Saving %s" % filename;
#    rts += [ txt ];
#    try:
#      self.pygame.image.save( my_surface, filename );
#    except:
#      txt = "ERROR Saving %s" % filename;
#      rts += [ txt ];
#  return rts; 

###############################################################################
# Given a file_header ( like foo_ ), check for foo_0000, then foo_0001, etc
# and return 1st available name.
def make_unique_filename( self, file_header, file_ext ):
  num = 0;
  while ( True ):
    file_name = file_header + ( "%04d" % num ) + file_ext;
    if ( os.path.exists( file_name ) == False ):
      return file_name;
    else:
      num +=1;
  return None;


#####################################
# save_view view_name -window N
# note if -window is omitted use the current selected window number.
def cmd_save_view( self, words ):
  print("save_view()", words );
  rts = [];
  rts += [ "save_view()" ];
  view_name = words[1];
  if view_name == None:
    filename_path = self.vars["sump_path_view"];
    filename_base = os.path.join( filename_path, "view_" );
    filename = make_unique_filename( self, filename_base, ".txt" );
    (path_dir, fn_w_ext ) = os.path.split( filename );
    (fn_no_ext, ext )     = os.path.splitext( fn_w_ext );
    view_name = fn_no_ext;
  else:
    filename_path = self.vars["sump_path_view"];
    filename = view_name + ".txt";
    filename = os.path.join( filename_path, filename );

  if words[2] == "-window":
    win_num = int(words[3],10)-1;
  elif self.window_selected != None:
    win_num = self.window_selected;
  txt_list = [];
  
  txt_list += ["create_view %s" % view_name];

  group_stack = [];

  # Note: This attempts to save a view file in an order format that a human might write one.
  signal_list = self.window_list[win_num].signal_list;
  for each_sig in signal_list:
#   print( each_sig.name, each_sig.type );
    # If there is a group open, close it if the next item isn't a member of it
    if len(group_stack) != 0:
      if each_sig.member_of != group_stack[-1]:
        txt_list += [ "end_group" ];
        del group_stack[-1];
#       print("end_group")

    if each_sig.type == "group":
      group_stack += [ each_sig ];
#     print("Pushing")

#     # Determine if we're pushing down a group level or closing the previous group
#     close_group = True;
#     1yyif each_sig.member_of != None:
#       # Push down to a new hiearachy level?
#       if len( group_stack ) != 0:
#         if each_sig.member_of == group_stack[-1]:
#           group_stack += [ each_sig ];
#           close_group = False;
#         else:
#           txt_list += [ "end_group" ];
#           del group_stack[-1];
#           close_group = False;
#     else:
#       group_stack += [ each_sig ];
#
#     if close_group and len(group_stack) != 0:
#       txt_list += [ "end_group" ];
#       del group_stack[-1];

    txt = "create_signal %s " % each_sig.name;
    if each_sig.source != None:
      txt += "-source %s " % each_sig.source;
    if each_sig.type != "digital" and each_sig.type != "analog":
      txt += "-type %s " % each_sig.type;# -type group, etc

    # Don't bother saving attributes that have default values like visible, color, etc
    if each_sig.visible == False:
      txt += "-visible %s " % each_sig.visible;
    fg_color = color_lookup(self.vars["screen_color_foreground"]);
    if each_sig.color != fg_color:
      txt += "-color %06x " % each_sig.color;

    if each_sig.source != None:
      txt += "-triggerable %s " % each_sig.triggerable;
      if "digital_rle" not in each_sig.source:
        txt += "-trigger_field %08x " % each_sig.trigger_field;

    if each_sig.source != None:
      if "analog" in each_sig.source:
        txt += "-vertical_offset %s " % each_sig.vertical_offset;
        txt += "-units_per_division %s " % each_sig.units_per_division;
        txt += "-divisions_per_range %s " % each_sig.divisions_per_range;
        txt += "-range %s " % each_sig.range;
        txt += "-units %s " % each_sig.units;
        txt += "-offset_units %s " % each_sig.offset_units;
        txt += "-units_per_code %s " % each_sig.units_per_code;
      else:
        if each_sig.rle_masked == True and each_sig.maskable:
          txt += "-rle_masked %s " % each_sig.rle_masked;

    if each_sig.member_of != None:
      if each_sig.member_of.name != None:
        txt += "-group %s " % each_sig.member_of.name;


#     txt += "-format " % each_sig.format;
#     txt += "-timezone " % each_sig.timezone;
#     txt += "-window %s " % each_sig.window;
#     txt += "-parent %s " % each_sig.parent;
    txt_list += [ txt ];

  while len( group_stack ) != 0:
    txt_list += [ "end_group" ];
    del group_stack[-1];

  txt_list += ["end_view"];
  txt_list += ["add_view"];
# txt_list += ["add_view %s" % view_name];
# file_name = view_name + ".txt";
# file_name = os.path.join( self.path_to_uut, file_name );

  if ( not os.path.exists( filename_path ) ):
    try:
      os.mkdir(filename_path);
    except:
      log(self,["ERROR: unable to mkdir %s" % filename_path]);
  rts += [ "Saving %s" % filename ];
  try:
    list2file( filename, txt_list );
    ( file_path, file_no_path ) = os.path.split( filename );
    cmd_add_view_ontap(self, ["add_view_ontap", file_no_path ] );
    self.pygame.display.set_caption(self.name+" "+self.vers+" "+self.copyright+" Saved %s" % file_no_path);
  except:
    rts += [ "ERROR Saving %s" % filename ];
  return rts;


#####################################
def assign_view_attribute_by_name( self, new_view, attribute, value ):
  if   attribute == "name"            : new_view.name              = value;
  elif attribute == "timezone"        : new_view.timezone          = value;
  elif attribute == "color"           : new_view.color = color_lookup(value);
# elif attribute == "uut_rev":
#   words = value.split(',');# ie "00_00,00_01,00_02"
#   new_view.uut_rev_list = words;
  elif attribute[0:9] == "user_ctrl":
    new_view.user_ctrl_list += [(attribute[9:],value)];
  return;


#####################################
# TODO: There is probably a better way to do this using vars() method.
# Below is brute force.
def assign_signal_attribute_by_name( self, new_signal, attribute, value ):
# print( new_signal.name, attribute, value );
  if value == "None":
    return;

  # Shorthand subs to keep ViewROMs small
  if   attribute == "mask"            : attribute = "rle_masked";
  elif attribute == "m"               : attribute = "rle_masked";
  elif attribute == "vis"             : attribute = "visible";
  elif attribute == "v"               : attribute = "visible";
  elif attribute == "hid"             : attribute = "hidden";
  elif attribute == "h"               : attribute = "hidden";
  elif attribute == "col"             : attribute = "collapsed";
  elif attribute == "clp"             : attribute = "collapsed";
  elif attribute == "clr"             : attribute = "color";
  elif attribute == "rng"             : attribute = "range";
  elif attribute == "u"               : attribute = "units";
  elif attribute == "upc"             : attribute = "units_per_code";
  elif attribute == "upd"             : attribute = "units_per_division";
  elif attribute == "dpr"             : attribute = "divisions_per_range";
  elif attribute == "ou"              : attribute = "offset_units";
  elif attribute == "oc"              : attribute = "offset_codes";
  elif attribute == "ta"              : attribute = "triggerable";
  elif attribute == "trg"             : attribute = "trigger";
  elif attribute == "tf"              : attribute = "trigger_field";
  elif attribute == "vo"              : attribute = "vertical_offset";

# if   attribute == "nickname"        : new_signal.nickname        = value;
  if   attribute == "name"            : new_signal.name            = value;
  elif attribute == "source"          : new_signal.source          = value;
  elif attribute == "timezone"        : new_signal.timezone        = value;
  elif attribute == "parent"          : new_signal.parent          = value;
# elif attribute == "member_of"       : new_signal.member_of       = value;
# elif attribute == "group"           : new_signal.member_of       = value;
  elif attribute == "window"          : new_signal.window          = value;
# elif attribute == "view"            : new_signal.view            = value;
  elif attribute == "view"            : new_signal.view_name       = value;
  elif attribute == "type"            : new_signal.type            = value;
  elif attribute == "format"          : new_signal.format          = value;
  elif attribute == "units"           : new_signal.units           = value;
  elif attribute == "units_per_code"  : new_signal.units_per_code  = float(value);
  elif attribute == "offset_units"    : new_signal.offset_units    = float(value);
  elif attribute == "offset_codes"    : new_signal.offset_codes    = int(value);
  elif attribute == "range"           : new_signal.range           = int(value);
# elif attribute == "vertical_scale"  : new_signal.vertical_scale  = float(value);
# elif attribute == "vertical_scale"  : new_signal.units_per_division = float(value);
  elif attribute == "units_per_division" : new_signal.units_per_division = float(value);
  elif attribute == "divisions_per_range" : new_signal.divisions_per_range = float(value);
  elif attribute == "vertical_offset" : new_signal.vertical_offset = float(value);
  elif attribute == "rle_masked"      :
    new_signal.rle_masked = ( value.lower() in ["true","yes","1"]);
  elif attribute == "selected"        :
    new_signal.selected = ( value.lower() in ["true","yes","1"]);
  elif attribute == "collapsed"       :
    new_signal.collapsed = ( value.lower() in ["true","yes","1"]);
  elif attribute == "visible"         :
    new_signal.visible = ( value.lower() in ["true","yes","1"]);
  elif attribute == "hidden"          :
    new_signal.hidden = ( value.lower() in ["true","yes","1"]);
  elif attribute == "triggerable"     :
    new_signal.triggerable = ( value.lower() in ["true","yes","1"]);
  elif attribute == "maskable"     :
    new_signal.maskable = ( value.lower() in ["true","yes","1"]);
  elif attribute == "color"           : new_signal.color = color_lookup(value);
  elif attribute[0:9] == "user_ctrl":
    new_signal.user_ctrl_list += [(attribute[9:],value)];
  elif attribute[0:2] == "uc":
    new_signal.user_ctrl_list += [(attribute[2:],value)];
# elif attribute == "trigger_field"   : new_signal.trigger_field   = int(value,16);
# New 2023.08.22
  elif attribute == "trigger_field"   :
    if len(value) == 8:
      new_signal.trigger_field   = int(value,16);# Hex value like "00000008"
    else:
      new_signal.trigger_field   = 2**(int(value));# Int value like 0 for D(0)
  # Warning that the variable is called "sump_user_ctrl" and the signal attribute "user_ctrl"


  if attribute == "member_of" or attribute == "group":
    new_signal.member_of = None; 
    for each_sig in self.signal_list:
      if each_sig.type == "group" and each_sig.name == value:
        if new_signal.member_of == None:
          new_signal.member_of = each_sig;
        else:
          print("WARNING: Multiple groups of same name : %s" % value );
    if new_signal.member_of == None:
      print("WARNING: Found no group of name : %s" % value );
      

  # Source name can be used to infer timezone so that user doesn't have to specify
  # doesn't have to explicitly specify it.
# if attribute == "source" and new_signal.timezone == None:
#   if "analog_ls" in new_signal.source:
#     new_signal.timezone == "ls";# Low Speed
#   elif "digital_ls" in new_signal.source:
#     new_signal.timezone == "ls";# Low Speed
#   elif "digital_hs" in new_signal.source:
#     new_signal.timezone == "hs";# High Speed
#   elif "analog_hs" in new_signal.source:
#     new_signal.timezone == "hs";# High Speed
#   elif "digital_rle" in new_signal.source:
#     new_signal.timezone == "rle";# Run Length Encoded

  # infer that a signal with a trigger field being defined is also triggerable
# if attribute == "trigger_field" and int(value,16) != 0x00000000:
  if attribute == "trigger_field":
    new_signal.triggerable = True;

  return;


#####################################
def get_signal_attribute_by_name( signal, attribute ):
  rts = "";
# if   attribute == "nickname"        : rts = signal.nickname;
  if   attribute == "name"            : rts = signal.name;
  elif attribute == "source"          : rts = signal.source;
  elif attribute == "member_of"       : rts = signal.member_of.name;
  elif attribute == "group"           : rts = signal.member_of.name;
# elif attribute == "member_of"       : rts = signal.member_of;
# elif attribute == "group"           : rts = signal.member_of;

  elif attribute == "window"          : rts = signal.window;
# elif attribute == "view"            : rts = signal.view;
  elif attribute == "view"            : rts = signal.view_name;
  elif attribute == "type"            : rts = signal.type;
  elif attribute == "format"          : rts = signal.format;
  elif attribute == "range"           : rts = signal.range;
  elif attribute == "units"           : rts = signal.units;
  elif attribute == "units_per_code"  : rts = signal.units_per_code;
  elif attribute == "offset_units"    : rts = signal.offset_units;
  elif attribute == "offset_codes"    : rts = signal.offset_codes;
# elif attribute == "vertical_scale"  : rts = signal.vertical_scale;
# elif attribute == "vertical_scale"  : rts = signal.units_per_division;
  elif attribute == "units_per_division"  : rts = signal.units_per_division;
  elif attribute == "divisions_per_range" : rts = signal.divisions_per_range;
  elif attribute == "vertical_offset" : rts = signal.vertical_offset;
  elif attribute == "visible"         : rts = signal.visible;
  elif attribute == "triggerable"     : rts = signal.triggerable;
  elif attribute == "trigger_field"   : rts = "%08x" % signal.trigger_field;
  elif attribute == "color"           : rts = "%06x" % signal.color;
  return rts;


#####################################
# See RGB Color table for EGA at https://en.wikipedia.org/wiki/Enhanced_Graphics_Adapter
def color_lookup( txt_str ):
  txt_str = txt_str.lower();
  txt_str = txt_str.replace("_","");# Convert "light_red" to "lightred"
  txt_str = txt_str.replace("-","");# Convert "light-red" to "lightred"
  txt_str = txt_str.replace("bright","light");
  color = None;
  if txt_str == "lightred"      : color = 0xff5555;
  if txt_str == "red"           : color = 0xc00000;
  if txt_str == "pink"          : color = 0xffc0cb;
  if txt_str == "orange"        : color = 0xffa500;
  if txt_str == "brown"         : color = 0xAA5500;
  if txt_str == "darkred"       : color = 0x900000;
  if txt_str == "lightgreen"    : color = 0x55ff55;
  if txt_str == "green"         : color = 0x00c000;
  if txt_str == "darkgreen"     : color = 0x009000;
  if txt_str == "lightblue"     : color = 0x5555FF;
  if txt_str == "blue"          : color = 0x0000c0;
  if txt_str == "darkblue"      : color = 0x000090;
  if txt_str == "cyan"          : color = 0x00AAAA;
  if txt_str == "lightcyan"     : color = 0x00AAAA;
  if txt_str == "aqua"          : color = 0x00FFFF;
  if txt_str == "yellow"        : color = 0xFFFF00;
  if txt_str == "magenta"       : color = 0xAA00AA;
  if txt_str == "lightmagenta"  : color = 0xFF55FF;
  if txt_str == "silver"        : color = 0xC0C0C0;
  if txt_str == "lightgrey"     : color = 0xAAAAAA;
  if txt_str == "darkgrey"      : color = 0x555555;
  if txt_str == "grey"          : color = 0x909090;
  if txt_str == "gray"          : color = 0x909090;
  if txt_str == "olive"         : color = 0x909000;
  if txt_str == "purple"        : color = 0x900090;
  if txt_str == "teal"          : color = 0x009090;
  if txt_str == "white"         : color = 0xFFFFFF;
  if txt_str == "black"         : color = 0x000000;
# print("Color is");
# print( color );
  if color == None:
    try:
      color = int(txt_str,16);
    except:
      color = 0x808080;
# print("Color is");
# print( color );
  return color;


#####################################
def cmd_read( self, words ):
  rts = [];
  addr = int(words[1],16);
  num_dwords = words[2];
  if ( num_dwords == None ):
    num_dwords = 1;
  else:
    num_dwords = int( num_dwords, 16 );
  try:
    rts = self.bd.rd( addr, num_dwords );
    txt_rts = [ "%08x" % each for each in rts ];# list comprehension
  except:
    txt_rts = [ "ERROR cmd_read( %s ) : Read of Hardware failed." % words[1] ];
  return txt_rts;


#####################################
def cmd_write( self, words ):
  rts = [];
  addr = int(words[1],16);
  data_list = [ int( each,16) for each in filter(None,words[2:]) ];
  try:
    rts = self.bd.wr( addr, data_list );
  except:
    rts = [ "ERROR cmd_write( %s %s) : Write to Hardware failed." % ( words[1],words[2] ) ];
  return rts;


#####################################
def cmd_source( self, words ):
  from os import path;
  rts = [];
# search_path = self.vars["sump_path_scripts"];
# paths     = search_path.split(',');
  paths = [];
# paths += [ os.getcwd() ];
# print( words );
  
  # UUT Path is the default path if it exists, otherwise use the CWD
  if self.path_to_uut != None:
    paths += [ self.path_to_uut ];
  else:
    paths += [ os.getcwd() ];

  # Look for the file specified in the usual places.
  # When found, set environment variables $file_name, $file_name_noext, $file_path, $file_name_fullpath
  for each_path in paths:
    file_name = os.path.join( each_path, words[1] );
    if ( path.exists( file_name )):
      rts += ["source() %s" % file_name ];
      update_file_vars( self, file_name );
      cmd_list = file2list( file_name );
      for cmd_str in cmd_list:
        rts1 = proc_cmd( self, cmd_str );
        if ( rts1 != None ):
          rts += rts1;
      break;# Don't source 2nd if file is in two places
    else:
      rts += ["WARNING: %s %s does not exist" % ( each_path, file_name ) ];
  return rts;

def update_file_vars( self, file_name ):
  self.vars["file_name_fullpath"] = file_name;
  ( fp,fn )                       = os.path.split( file_name );
  self.vars["file_name"]          = fn;
  self.vars["file_path"]          = fp;
  self.vars["file_name_noext"]    = os.path.basename( file_name );
  return;


#####################################
# For unix command we remember the actual cwd ( where sump3.py was started ) 
# and temporarily change to the UUTs path. Once we're done with the commands
# we then switch back to the original cwd.
def cmd_unix( self, words ):
  from os import path;
  import os;
  rts = [];
  org_cwd = os.getcwd();
  if self.path_to_uut != None:
    os.chdir( self.path_to_uut );

  if words[0] == "pwd":
    rts += [ os.getcwd() ];
  elif words[0] == "cd":
    try:
      os.chdir( words[1] );
      if self.path_to_uut != None:
        self.path_to_uut = os.getcwd();
    except:
      log(self,["ERROR: Failed to chdir to %s" % words[1] ]);
  elif words[0] == "cp":
    try:
      import shutil
      src = os.path.join( self.path_to_uut, words[1] );
      dst = os.path.join( self.path_to_uut, words[2] );
      shutil.copy2( src, dst );
    except:
      print("cmd_unix(): ERROR cp");
      print( src, dst );

  elif words[0] == "more":
    rts = file2list( words[1] );
  elif words[0] in ["?","help","manual"]:
    try:
      import os;
      if ( self.os_sys == "Linux" ):
        cmd = "vi";
      else:
        cmd = "notepad.exe";
      os.chdir( org_cwd );
      os.system( cmd + " " + self.sump_manual );
    except:
      rts += ["ERROR: "+cmd+" "+self.sump_manual ];
  elif words[0] in ["vi","notepad","edit"]:
    try:
      import os;
      if ( self.os_sys == "Linux" ):
        cmd = "vi";
      else:
        cmd = "notepad.exe";
#     os.chdir( org_cwd );
      if self.path_to_uut != None:
        file_name = os.path.join(self.path_to_uut,words[1] );
      else:
        file_name = words[1];
      os.system( cmd + " " + file_name);
    except:
      rts += ["ERROR: "+cmd+" "+words[1] ];
  elif words[0] == "?" :
    os.system( words[1] );# Note, this is blocking. Works on Windows only
  elif words[0] == "ls":
    if ( words[1] == None ):
      words[1] = "*";
    import glob;
    # Differentiate dirs from files with "/" just like Linux ls does.
    file_list = glob.glob( words[1] );
    for each in file_list:
      if ( os.path.isdir( each ) ):
        each = each + "/";
      rts += [ each ];
  elif words[0] == "sleep_ms":
#   dur = float( words[1] ) / 1000.0;
#   time.sleep(dur); 
#   pygame.time.wait( float(dur) );# time in mS. 
    dur = int( words[1] );
    pygame.time.wait( dur );# time in mS. 
  elif words[0] == "env":
    txt_list = [];
    for key in self.vars:
      val = self.vars[ key ];
      txt_list.append( key + " = " + val);
    for each in sorted( txt_list ):
      rts += [ each ];

  os.chdir( org_cwd );
  return rts;


#####################################
# process "foo = 12" and "bar.color = 00ff00"
# Note that self.vars[key] are always strings
# signal attribute assignments are not always string.
def cmd_assign_var( self, words ):
  rts = []
  if not "." in words[0]:
    # See if words[0] is an attribute for a selected signal, color for example
    found = False;
    for each_sig in self.signal_list:
#     if each_sig.visible:
# 2023.07.10
      if each_sig.visible and each_sig.selected:
        attrib_list = dir( each_sig );
        if words[0] in attrib_list:
          found = True;
          sig_attribute = words[0];
          sig_value = words[2];
          assign_signal_attribute_by_name(self, each_sig, sig_attribute, sig_value );
    if not found:
      self.vars[ words[0] ] = words[2];
  else:
    # Warning - this assumes single "." in the entire words[0]
    ( sig_name, sig_attribute ) = words[0].split('.');
    sig_value = words[2];
    for each_sig in self.signal_list:
      if each_sig.name == sig_name:
        assign_signal_attribute_by_name(self, each_sig, sig_attribute, sig_value );
  if "screen_width" in words[0] or "screen_height" in words[0]:
    self.screen_width = int( self.vars["screen_width"], 10 );
    self.screen_height = int( self.vars["screen_height"], 10 );
    self.options.resolution = ( self.screen_width, self.screen_height );
    screen_set_size(self);
  return rts;


#####################################
# process "sump_user_ctrl[3:0] = a"
# Note that self.vars[key] are always strings
# signal attribute assignments are not always string.
def cmd_assign_user_ctrl_var( self, words ):
  rts = []
  if words[0][0:len("sump_user_ctrl")] == "sump_user_ctrl":
    if "[" in words[0] and "]" in words[0]:
      if words[1] == "=":
        user_ctrl = int(words[2], 16);# new value to assign
        bit_field = words[0].replace("sump_user_ctrl","");
        old_user_ctrl = int( self.vars["sump_user_ctrl"],16);
        (new_field,mask,bot_bit) = gen_bit_rip(bit_field);
        # 123456A8    = ( 12345678 & FFFFFF0F  ) | (         A << 4       );
        new_user_ctrl = ( old_user_ctrl & mask ) | ( user_ctrl << bot_bit );
        self.vars["sump_user_ctrl"] = "%08x" % new_user_ctrl;
  return rts;


#####################################
# process "sump_user_stim[3:0] = a"
# Note that self.vars[key] are always strings
# signal attribute assignments are not always string.
#def cmd_assign_user_stim_var( self, words ):
#  rts = []
#  if words[0][0:len("sump_user_stim")] == "sump_user_stim":
#    if "[" in words[0] and "]" in words[0]:
#      if words[1] == "=":
#        user_stim = int(words[2], 16);# new value to assign
#        bit_field = words[0].replace("sump_user_stim","");
#        old_user_stim = int( self.vars["sump_user_stim"],16);
#        (new_field,mask,bot_bit) = gen_bit_rip(bit_field);
#        # 123456A8    = ( 12345678 & FFFFFF0F  ) | (         A << 4       );
#        new_user_stim = ( old_user_stim & mask ) | ( user_stim << bot_bit );
#        self.vars["sump_user_stim"] = "%08x" % new_user_stim;
#  return rts;

# Given "[7:4]" return the tuple ( 0x000000F0, 0xFFFFFF0F, 4 )
# Given "[4]"   return the tuple ( 0x00000010, 0xFFFFFFEF, 4 )
def gen_bit_rip( txt ):
# print( txt );
  line = txt;
  line = line.replace("["," ");
  line = line.replace("]"," ");
  line = line.replace(":"," ");
# print( line );
  if ":" in txt:
    multiple_bits = True;
  else:
    multiple_bits = False;
  words = " ".join(line.split()).split(' ') + [None] * 4;
  top = int( words[0], 10 );
  if multiple_bits:
    bot = int( words[1], 10 );
  else:
    bot = top; 
  bit = 2**bot;
  val = 0;
  for i in range(bot,top+1):
    val += bit;
    bit = bit << 1;
  val_inv = val ^ 0xFFFFFFFF;
  return ( val, val_inv, bot );


#####################################
# Diplay variable value
def cmd_print_var( self, words ):
  rts = []
# if not "." in words[1]:
#   try:
#     rts = [ self.vars[ words[1] ] ];
#   except:
#     pass;
  if not "." in words[1]:
    # See if words[1] is an attribute for a selected signal, color for example
    found = False;
    for each_sig in self.signal_list:
#     if each_sig.visible:
      if each_sig.visible and each_sig.selected:
        attrib_list = dir( each_sig );
        if words[1] in attrib_list: 
          sig_attribute = words[1];
          val = get_signal_attribute_by_name( each_sig, sig_attribute );
          if val != None:
            rts += [ each_sig.name + "." + sig_attribute + " = " + str(val) ];
          found = True;
    if not found:
      try:
        rts = [ self.vars[ words[1] ] ];
      except:
        pass;
  else:
    # Warning - this assumes single "." in the entire words[1]
    ( sig_name, sig_attribute ) = words[1].split('.');
    sig_value = words[2];
    for each_sig in self.signal_list:
      if each_sig.name == sig_name:
#       rts = get_signal_attribute_by_name( each_sig, sig_attribute );
        val = get_signal_attribute_by_name( each_sig, sig_attribute );
#       print( each_sig.name );
#       print( sig_attribute );
#       print( val );
        if val != None:
          rts += [ each_sig.name + "." + sig_attribute + " = " + str(val) ];
  return rts;


#####################################
def cmd_font_larger( self ):
  rts = [];
  size = int( self.vars["font_size"] );
  size += 2;
  self.vars["font_size"] = str( size );
  self.font = get_font( self, self.vars["font_name"],self.vars["font_size"]);
  self.refresh_waveforms = True;
  return rts;


#####################################
def cmd_font_smaller( self ):
  rts = [];
  size = int( self.vars["font_size"] );
  size -= 2;
  if ( size < 2 ):
    size = 2;
  self.vars["font_size"] = str( size );
  self.font = get_font( self, self.vars["font_name"],self.vars["font_size"]);
  self.refresh_waveforms = True;
  return rts;

#####################################
def adjust_color( color_in, percent ):
  color_in.r = int( color_in.r * (1.0 + percent) );
  color_in.g = int( color_in.g * (1.0 + percent) );
  color_in.b = int( color_in.b * (1.0 + percent) );
  return color_in;

#####################################
def proc_key( self, event ):
  rts = False;

  analog_signals_selected = False;
  for each_signal in self.signal_list:
    if each_signal.selected and each_signal.type == "analog":
      analog_signals_selected = True;
      break;

  # K_ESCAPE : Unselect any selected signal. If none selected, unselect the Window itself
  if event.key == pygame.K_ESCAPE:
    rts = proc_unselect(self);

  # K_TAB : Tab through Windows
# elif event.key == pygame.K_TAB:
#   proc_cmd( self, "win_tab" );
#   rts = True;# Force a refresh

  # K_TAB : Tab through Windows
  elif event.key == pygame.K_TAB:
    if self.file_dialog == None and not self.cmd_console.visible:
      proc_cmd( self, "win_tab" );
      rts = True;# Force a refresh

  elif ( event.key == pygame.K_SLASH ):
    if self.file_dialog == None and not self.cmd_console.visible:
      if ( event.mod & pygame.KMOD_SHIFT ):
        proc_cmd( self, "search_backward" );
      else:
        proc_cmd( self, "search_forward" );
  elif ( event.key == pygame.K_QUESTION ):
    if self.file_dialog == None and not self.cmd_console.visible:
      proc_cmd( self, "search_backward" );

  # K_PAGEDOWN : 
  elif event.key == pygame.K_PAGEDOWN:
    if self.file_dialog == None and not self.cmd_console.visible:
      proc_cmd( self, "page_down" );

  # K_PAGEUP : 
  elif event.key == pygame.K_PAGEUP:
    if self.file_dialog == None and not self.cmd_console.visible:
      proc_cmd( self, "page_up" );

  # K_PAGEUP : Tab through Windows
# elif event.key == pygame.K_PAGEUP:
#   proc_cmd( self, "win_pageup" );
#   self.vars["screen_windows"] = "%01x" % self.screen_windows;
#   screen_erase(self);
#   resize_containers(self);
#   rts = True;# Force a refresh

# # K_PAGEDOWN : Tab through Windows
# elif event.key == pygame.K_PAGEDOWN:
#   proc_cmd( self, "win_pagedown" );
#   self.vars["screen_windows"] = "%01x" % self.screen_windows;
#   screen_erase(self);
#   resize_containers(self);
#   rts = True;# Force a refresh

  elif ( analog_signals_selected and
#   ( ( event.key == pygame.K_LEFT  or event.key == pygame.K_a ) or
#     ( event.key == pygame.K_RIGHT or event.key == pygame.K_d ) or
#   ( ( event.key == pygame.K_UP    or event.key == pygame.K_w ) or
#     ( event.key == pygame.K_DOWN  or event.key == pygame.K_s )    )) :
#   if ( event.key == pygame.K_UP    or event.key == pygame.K_w ):
#     k = "up";
#   elif ( event.key == pygame.K_DOWN  or event.key == pygame.K_s ):
#     k = "down";
#   else:
#     k = "";
    ( ( event.key == pygame.K_UP                               ) or
      ( event.key == pygame.K_DOWN                             )    )) :
    if ( event.key == pygame.K_UP                               ):
      k = "up";
    elif ( event.key == pygame.K_DOWN                             ):
      k = "down";
    else:
      k = "";

    if self.container_display_list[0].visible:
      for each_signal in self.signal_list:
        if each_signal.selected and each_signal.type == "analog":
          if ( self.pygame.key.get_pressed()[self.pygame.K_LSHIFT] or
               self.pygame.key.get_pressed()[self.pygame.K_RSHIFT]   ):
            if ( k == "up" ):
              each_signal.vertical_offset -= .01;
            elif ( k == "down" ):
              each_signal.vertical_offset += .01;
          else:
            if ( self.pygame.key.get_pressed()[self.pygame.K_LCTRL] or
                 self.pygame.key.get_pressed()[self.pygame.K_RCTRL]   ):
              if ( k == "down" ):
                proc_cmd( self, "scale_down_fine" );
              elif ( k == "up" ):
                proc_cmd( self, "scale_up_fine" );
            else:
              if ( k == "down" ):
                proc_cmd( self, "scale_down" );
              elif ( k == "up" ):
                proc_cmd( self, "scale_up" );

      # Only update the windows that have the selected signals in them
      for (i,each_win) in enumerate( self.window_list ):
        for each_signal in self.signal_list:
          if each_signal.selected:
            if each_signal in each_win.signal_list:
              if not i in self.refresh_window_list:
                self.refresh_window_list += [i];

  # K_LEFT : Pan Left
# elif event.key == pygame.K_LEFT or event.key == pygame.K_a :
  elif event.key == pygame.K_LEFT                            :
    if self.file_dialog == None and not self.cmd_console.visible:
      if ( self.pygame.key.get_pressed()[self.pygame.K_LSHIFT] or
           self.pygame.key.get_pressed()[self.pygame.K_RSHIFT]   ):
        iters = 8;
      else:
        iters = 1;
#     if self.window_selected != None:
      if self.window_selected != None and self.select_text_i == None:
        for i in range(0,iters):
          proc_cmd( self, "pan_left" );
      if self.select_text_i != None:
        rate = 8;
        if ( self.pygame.key.get_pressed()[self.pygame.K_LCTRL] or
             self.pygame.key.get_pressed()[self.pygame.K_RCTRL]   ):
          rate = 1;
        proc_acq_adj_dec( self, rate );
      rts = False;# Selected window only refresh

  # K_RIGHT : Pan Right
# elif event.key == pygame.K_RIGHT or event.key == pygame.K_d :
  elif event.key == pygame.K_RIGHT                            :
    if self.file_dialog == None and not self.cmd_console.visible:
      if ( self.pygame.key.get_pressed()[self.pygame.K_LSHIFT] or
           self.pygame.key.get_pressed()[self.pygame.K_RSHIFT]   ):
        iters = 8;
      else:
        iters = 1;
      if self.window_selected != None and self.select_text_i == None:
        for i in range(0,iters):
          proc_cmd( self, "pan_right" );
      if self.select_text_i != None:
        rate = 8;
        if ( self.pygame.key.get_pressed()[self.pygame.K_LCTRL] or
             self.pygame.key.get_pressed()[self.pygame.K_RCTRL]   ):
          rate = 1;
        proc_acq_adj_inc( self, rate );
      rts = False;# Selected window only refresh

  # K_UP : Zoom In  
# elif event.key == pygame.K_UP or event.key == pygame.K_w :
  elif event.key == pygame.K_UP                            :
    if self.file_dialog == None and not self.cmd_console.visible:
      if ( self.pygame.key.get_pressed()[self.pygame.K_LSHIFT] or
           self.pygame.key.get_pressed()[self.pygame.K_RSHIFT]   ):
        iters = 4;
      else:
        iters = 1;
      if self.window_selected != None and self.select_text_i == None:
        for i in range(0,iters):
          proc_cmd( self, "zoom_in" );
      if self.select_text_i != None:
        rate = 8;
        if ( self.pygame.key.get_pressed()[self.pygame.K_LCTRL] or
             self.pygame.key.get_pressed()[self.pygame.K_RCTRL]   ):
          rate = 1;
        proc_acq_adj_inc( self, rate );
    rts = False;# Selected window only refresh

  # K_DOWN : Zoom Out 
# elif event.key == pygame.K_DOWN or event.key == pygame.K_s :
  elif event.key == pygame.K_DOWN                            :
    if self.file_dialog == None and not self.cmd_console.visible:
      if ( self.pygame.key.get_pressed()[self.pygame.K_LSHIFT] or
           self.pygame.key.get_pressed()[self.pygame.K_RSHIFT]   ):
        iters = 4;
      else:
        iters = 1;
      if self.window_selected != None and self.select_text_i == None:
        for i in range(0,iters):
          proc_cmd( self, "zoom_out" );
      if self.select_text_i != None:
        rate = 8;
        if ( self.pygame.key.get_pressed()[self.pygame.K_LCTRL] or
             self.pygame.key.get_pressed()[self.pygame.K_RCTRL]   ):
          rate = 1;
        proc_acq_adj_dec( self, rate );
    rts = False;# Selected window only refresh

  # K_DELETE : Make selected invisible ( remove from display )
  # same as CLI remove_signal 
  elif event.key == pygame.K_DELETE:
    if self.file_dialog == None and not self.cmd_console.visible:
#   if self.file_dialog == None:
      proc_cmd( self, "delete_signal" );
      rts = True;# Force a refresh
#     for each_sig in self.signal_list:
#       if each_sig.selected:
#         each_sig.visible = False;
#         each_sig.rle_masked = True;
#         rts = True;# Force a refresh

  # K_INSERT : Make all signals visible and unhidden
  elif event.key == pygame.K_INSERT:
    if self.file_dialog == None and not self.cmd_console.visible:
#   if self.file_dialog == None:
      proc_cmd( self, "insert_signal" );
      rts = True;# Force a refresh

  # K_HOME : Make all signals visible and unhidden
  elif event.key == pygame.K_HOME:
    if self.file_dialog == None and not self.cmd_console.visible:
#   if self.file_dialog == None:
      proc_cmd( self, "insert_signal *" );
      rts = True;# Force a refresh

  # K_END : Toggle hidden attribute of selected
  elif event.key == pygame.K_END:
    if self.file_dialog == None and not self.cmd_console.visible:
#   if self.file_dialog == None:
      proc_cmd( self, "hide_toggle_signal" );
      rts = True;# Force a refresh
#     for each_sig in self.signal_list:
#       if each_sig.selected:
#         each_sig.hidden = not each_sig.hidden;
#         rts = True;# Force a refresh

  # K_BACKSPACE : Undo previous zoom pan actions     
  elif event.key == pygame.K_BACKSPACE:
#   if self.window_selected != None:
    # K_BACKSPACE is used in bd_shell for typing, so ignore if console is visible
    if ( self.file_dialog == None and self.window_selected != None and
         not self.cmd_console.visible ):
      win_num      = self.window_selected;
      my_win       = self.window_list[win_num];
      if len( my_win.zoom_pan_history ) != 0:
        my_win.zoom_pan_list = my_win.zoom_pan_history.pop();
        self.refresh_waveforms = True;
        rts = True;# Force a refresh

  # K_t   : Toggle trigger attribute of selected
  elif event.key == pygame.K_t:
    # K_t is used in bd_shell for typing, so ignore if console is visible
    if ( self.file_dialog == None and not self.cmd_console.visible ):
      for each_sig in self.signal_list:
        if each_sig.selected and each_sig.triggerable:
          each_sig.trigger = not each_sig.trigger;
          rts = True;# Force a refresh

  # K_HOME : Set vertical offset of selected back to zero
# elif event.key == pygame.K_HOME:
#   for each_sig in self.signal_list:
#     if each_sig.selected:
#       each_sig.vertical_offset = 0;
#       rts = True;# Force a refresh
  return rts;


#####################################
def proc_cmd( self, cmd, quiet = False ):

  if "!" not in cmd:
    self.cmd_history += [ cmd ];
  else:
    if cmd == "!!":
      cmd = self.cmd_history[-1];
    elif "!" in cmd:
      try:
        cmd = self.cmd_history[ int(cmd[1:]) ];
      except:
        cmd = "";

  # Support "> foo.txt" results to a file.
  output_to_file = None;
  if ">" in cmd:
    (cmd,output_to_file) = cmd.split(">");
    output_to_file = output_to_file.replace(" ","");

  # Look for any variables ( like paths ) in cmd and replace if found.
  if "$" in cmd:
    for key in self.vars:
#     target = "$"+key;
      target = "$"+key+" ";
      if target in cmd:
#       cmd = cmd.replace(target,self.vars[key]);
        cmd = cmd.replace(target,self.vars[key]+ " ");

  # Don't log repetitive commands to bd_shell log as it slows UI.
  self.dont_log_list = ["pan_left","pan_right","zoom_in","zoom_out",
                        "scroll_up","scroll_down"];

  cmd = cmd.replace("="," = ");
  cmd_list = cmd.split('#');# Support lines ending with comments
  cmd = cmd_list[0];
  words = " ".join(cmd.split()).split(' ') + [None] * 4;
  cmd_txt = words[0];

# if ( self.cmd_console.visible == True and cmd not in self.dont_log_list ):
  if ( self.cmd_console.visible == True and cmd not in self.dont_log_list and not quiet ):
    self.cmd_console.add_output_line_to_log( cmd ,is_bold=False, remove_line_break=False);
# print(cmd);# Also use STDOUT
# print("proc_cmd() %s" % cmd_txt );
# print(cmd_txt);# Also use STDOUT
# self.cmd_console.add_output_line_to_log( cmd ,is_bold=True, remove_line_break=True);
  valid = False;
  rts = [];


  if   cmd_txt == "refresh"           : cmd_txt = "gui_refresh";
  if   cmd_txt == "quit" or cmd_txt == "die" : cmd_txt = "exit";
  if   cmd_txt == "ur"                : cmd_txt = "sump_user_read";
  if   cmd_txt == "uw"                : cmd_txt = "sump_user_write";
  if   cmd_txt == "user_read"         : cmd_txt = "sump_user_read";
  if   cmd_txt == "user_write"        : cmd_txt = "sump_user_write";
  if   cmd_txt == "cg"                : cmd_txt = "collapse_group";

  if   cmd_txt == "exit"              : shutdown(self); valid = True; sys.exit();
  elif cmd_txt == "source"            : rts = cmd_source(self, words ); valid = True;
  elif cmd_txt == "debug_containers"  : debug_containers(self);         valid = True;
  elif cmd_txt == "hide_all"          : hide_all(self);                 valid = True;
  elif cmd_txt == "stats"             : stats(self);                    valid = True;
  elif cmd_txt == "cd"                : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "pwd"               : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "more"              : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "ls"                : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "cp"                : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "vi"                : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "help"              : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "?"                 : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "manual"            : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "sleep_ms"          : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "env"               : rts = cmd_unix(self, words ); valid = True;
  elif cmd_txt == "sump_connect"      : rts = cmd_sump_connect(self); valid = True;

  elif cmd_txt == "debug"             : cmd_debug(self, words ); valid = True;
  elif cmd_txt == "sump_arm"          : cmd_sump_arm(self); valid = True;
  elif cmd_txt == "sump_acquire"      : cmd_sump_acquire(self); valid = True;
  elif cmd_txt == "sump_download"     : cmd_sump_download(self); valid = True;
  elif cmd_txt == "sump_query"        : rts = cmd_sump_query(self); valid = True;
  elif cmd_txt == "sump_force_trig"   : rts = cmd_sump_force_trig(self); valid = True;
  elif cmd_txt == "sump_force_stop"   : rts = cmd_sump_force_stop(self); valid = True;
  elif cmd_txt == "sump_idle"         : cmd_sump_idle(self); valid = True;
  elif cmd_txt == "sump_reset"        : cmd_sump_reset(self); valid = True;
  elif cmd_txt == "sump_sleep"        : cmd_sump_sleep(self); valid = True;

  elif cmd_txt == "sump_user_read"    : rts = cmd_sump_user_read(self, words ); valid = True;
  elif cmd_txt == "sump_user_write"   : rts = cmd_sump_user_write(self, words ); valid = True;

  elif cmd_txt == "sump_set_trigs"    : rts = cmd_sump_set_trigs(self,words ); valid = True;
# elif cmd_txt == "sump_clr_trigs"    : cmd_sump_clr_trigs(self,words); valid = True;
  elif cmd_txt == "sump_clear_trigs"  : cmd_sump_clear_trigs(self,words); valid = True;
  elif cmd_txt == "save_pza"          : rts = cmd_save_pza(self,words); valid = True;
  elif cmd_txt == "load_pza"          : rts = cmd_load_pza(self,words); valid = True;
  elif cmd_txt == "load_uut"          : rts = cmd_load_uut(self,words); valid = True;
  elif cmd_txt == "load_vcd"          : rts = cmd_load_vcd(self,words); valid = True;
  elif cmd_txt == "save_vcd"          : rts = cmd_save_vcd( self, words ); valid = True;
  elif cmd_txt == "gui_minimize"      : rts = cmd_gui_minimize(self,words); valid = True;
  elif cmd_txt == "gui_refresh"       : rts = cmd_gui_refresh(self,words); valid = True;
# elif cmd_txt == "gui_fullscreen"    : rts = cmd_gui_fullscreen(self,words); valid = True;
  elif cmd_txt == "r"                 : rts = cmd_read(self, words ); valid = True;
  elif cmd_txt == "w"                 : rts = cmd_write(self, words ); valid = True;
  elif cmd_txt == "print" or cmd_txt == "echo" : rts = cmd_print_var(self,words); valid = True;
# elif cmd_txt == "create_preset"     : rts = cmd_create_preset(self, words ); valid = True;
# elif cmd_txt == "remove_preset"     : rts = cmd_remove_preset(self, words ); valid = True;
  elif cmd_txt == "create_signal"     : rts = cmd_create_signal(self, words, defer_update = quiet ); valid = True;
  elif cmd_txt == "create_group"      : rts = cmd_create_group(self, words ); valid = True;
  elif cmd_txt == "create_bit_group"  : rts = cmd_create_bit_group(self, words ); valid = True;
  elif cmd_txt == "end_group"         : rts = cmd_end_group(self, words ); valid = True;
  elif cmd_txt == "create_fsm_state"  : rts = cmd_create_fsm_state(self, words ); valid = True;
  elif cmd_txt == "list_signal"       : rts = cmd_list_signal(self, words ); valid = True;
  elif cmd_txt == "delete_signal"     : rts = cmd_delete_signal(self, words ); valid = True;
  elif cmd_txt == "select_signal"     : rts = cmd_select_signal(self, words ); valid = True;
  elif cmd_txt == "deselect_signal"   : rts = cmd_deselect_signal(self, words ); valid = True;
  elif cmd_txt == "insert_signal"     : rts = cmd_insert_signal(self, words ); valid = True;
# elif cmd_txt == "clone_signal"      : rts = cmd_clone_signal(self, words ); valid = True;
  elif cmd_txt == "cut_signal"        : rts = cmd_cut_signal(self, words ); valid = True;
  elif cmd_txt == "rename_signal"     : rts = cmd_rename_signal(self, words ); valid = True;
  elif cmd_txt == "copy_signal"       : rts = cmd_copy_signal(self, words ); valid = True;
  elif cmd_txt == "paste_signal"      : rts = cmd_paste_signal(self, words ); valid = True;
  elif cmd_txt == "apply_attribute"   : rts = cmd_apply_attribute(self, words ); valid = True;
  elif cmd_txt == "add_signal"        : rts = cmd_add_signal(self, words ); valid = True;
  elif cmd_txt == "remove_signal"     : rts = cmd_remove_signal(self, words ); valid = True;
  elif cmd_txt == "hide_toggle_signal" : rts = cmd_hide_toggle_signal(self, words ); valid = True;
  elif cmd_txt == "mask_toggle_signal" : rts = cmd_mask_toggle_signal(self, words ); valid = True;
  elif cmd_txt == "hide_signal"       : rts = cmd_hide_signal(self, words ); valid = True;
  elif cmd_txt == "show_signal"       : rts = cmd_show_signal(self, words ); valid = True;
  elif cmd_txt == "create_view"       : rts = cmd_create_view( self, words ); valid = True;
  elif cmd_txt == "expand_group"      : rts = cmd_expand_group( self, words ); valid = True;
  elif cmd_txt == "collapse_group"    : rts = cmd_collapse_group( self, words ); valid = True;
  elif cmd_txt == "add_view_ontap"    : rts = cmd_add_view_ontap( self, words ); valid = True;
  elif cmd_txt == "remove_view_ontap" : rts = cmd_remove_view_ontap( self, words ); valid = True;
  elif cmd_txt == "list_view_ontap"   : rts = cmd_list_view_ontap( self, words ); valid = True;
  elif cmd_txt == "end_view"          : rts = cmd_end_view( self, words ); valid = True;
  elif cmd_txt == "list_view"         : rts = cmd_list_view( self, words ); valid = True;
  elif cmd_txt == "list_window_views" : rts = cmd_list_window_views( self, words ); valid = True;
  elif cmd_txt == "add_view"          : rts = cmd_add_view( self, words ); valid = True;
# elif cmd_txt == "save_view"         : rts = cmd_save_view( self, words ); valid = True;

# elif cmd_txt == "save_pic"          : rts = cmd_save_pic( self, words ); valid = True;
# elif cmd_txt == "save_png"          : rts = cmd_save_pic( self, words ); valid = True;
# elif cmd_txt == "save_jpg"          : rts = cmd_save_pic( self, words ); valid = True;
# elif cmd_txt == "save_bmp"          : rts = cmd_save_pic( self, words ); valid = True;

  elif cmd_txt == "save_view"         : rts = cmd_save_view( self, words ); valid = True;
  elif cmd_txt == "save_list"         : rts = cmd_save_list( self, words ); valid = True;

  elif cmd_txt == "save_window"        : rts = cmd_save_window( self, words ); valid = True;
  elif cmd_txt == "save_screen"        : rts = cmd_save_screen( self, words ); valid = True;
  elif cmd_txt == "add_measurement"    : rts = cmd_add_measurement( self, words ); valid = True;
  elif cmd_txt == "remove_measurement" : rts = cmd_remove_measurement( self, words ); valid = True;


  elif cmd_txt == "add_grid"          : rts = cmd_add_grid( self, words ); valid = True;
  elif cmd_txt == "remove__grid"      : rts = cmd_remove_grid( self, words ); valid = True;
  elif cmd_txt == "apply_view"        : rts = cmd_apply_view( self, words ); valid = True;
  elif cmd_txt == "remove_view"       : rts = cmd_remove_view( self, words ); valid = True;
  elif cmd_txt == "apply_view_all"    : rts = cmd_apply_view( self, ["","*","",""]); valid = True;
  elif cmd_txt == "remove_view_all"   : rts = cmd_remove_view( self,["","*","",""] ); valid = True;
  elif cmd_txt == "select_window"     : rts = cmd_select_window( self, words ); valid = True;
  elif cmd_txt == "close_window"      : rts = cmd_close_window( self, words ); valid = True;
  elif cmd_txt == "close_bd_shell"    : rts = cmd_close_bd_shell( self ); valid = True;
  elif cmd_txt == "open_bd_shell"     : rts = cmd_open_bd_shell( self ); valid = True;
  elif cmd_txt == "select_acquisition" : rts = cmd_select_acquisition( self ); valid = True;
  elif cmd_txt == "select_navigation"  : rts = cmd_select_navigation( self ); valid = True;
  elif cmd_txt == "select_viewconfig"  : rts = cmd_select_viewconfig( self ); valid = True;
# elif cmd_txt == "delete_view"       : rts = cmd_delete_view( self, words ); valid = True;
  elif cmd_txt == "font_smaller"      : rts = cmd_font_smaller( self ); valid = True;
  elif cmd_txt == "font_larger"       : rts = cmd_font_larger( self ); valid = True;
  elif cmd_txt == "zoom_to_cursors"   : rts = cmd_zoom_to_cursors( self ); valid = True;
  elif cmd_txt == "zoom_full"         : rts = cmd_zoom_full( self ); valid = True;
  elif cmd_txt == "zoom_in"           : rts = cmd_zoom_in( self ); valid = True;
  elif cmd_txt == "zoom_out"          : rts = cmd_zoom_out( self ); valid = True;
  elif cmd_txt == "scroll_up"         : rts = cmd_scroll_up( self ); valid = True;
  elif cmd_txt == "scroll_down"       : rts = cmd_scroll_down( self ); valid = True;
  elif cmd_txt == "scroll_analog_up"   : rts = cmd_scroll_analog_up( self ); valid = True;
  elif cmd_txt == "scroll_analog_down" : rts = cmd_scroll_analog_down( self ); valid = True;
  elif cmd_txt == "page_up"           : rts = cmd_page_up( self ); valid = True;
  elif cmd_txt == "page_down"         : rts = cmd_page_down( self ); valid = True;
  elif cmd_txt == "pan_left"          : rts = cmd_pan_left( self ); valid = True;
  elif cmd_txt == "pan_right"         : rts = cmd_pan_right( self ); valid = True;
  elif cmd_txt == "search_forward"    : rts = cmd_search_forward( self ); valid = True;
  elif cmd_txt == "search_backward"   : rts = cmd_search_backward( self ); valid = True;
  elif cmd_txt == "time_snap"         : rts = cmd_time_snap( self ); valid = True;
  elif cmd_txt == "time_lock"         : rts = cmd_time_lock( self ); valid = True;
  elif cmd_txt == "scale_up"          : rts = cmd_scale_up( self ); valid = True;
  elif cmd_txt == "scale_down"        : rts = cmd_scale_down( self ); valid = True;
  elif cmd_txt == "scale_up_fine"     : rts = cmd_scale_up_fine( self ); valid = True;
  elif cmd_txt == "scale_down_fine"   : rts = cmd_scale_down_fine( self ); valid = True;
  elif cmd_txt == "win_tab"           : rts = cmd_win_tab( self ); valid = True;
  elif cmd_txt == "win_pageup"        : rts = cmd_win_pageup( self ); valid = True;
  elif cmd_txt == "win_pagedown"      : rts = cmd_win_pagedown( self ); valid = True;
  elif cmd_txt == "test_dialog"       : rts = cmd_test_dialog( self, words ); valid = True;
# else:
#   print("IDK");

  if   cmd_txt == "history" :
    valid = True;
    rts = [ "%d %s" % ( i, each ) for (i,each) in enumerate( self.cmd_history ) ];

  # "sump_user_ctrl = a" and sump_user_ctrl[3:0] = a" are handled differently
  if words[1] == "=":
    if words[0][0:len("sump_user_ctrl")] == "sump_user_ctrl" and "[" in words[0] and "]" in words[0]: 
      rts = cmd_assign_user_ctrl_var( self, words ); value = True;
#   elif words[0][0:len("sump_user_stim")] == "sump_user_stim" and "[" in words[0] and "]" in words[0]: 
#     rts = cmd_assign_user_stim_var( self, words ); value = True;
    else:
      rts = cmd_assign_var( self, words ); value = True;

# if not valid:
#   rts = ["ERROR Unknown command: %s" % cmd_txt];

  if rts != None and not quiet:
    for each in rts:
      if ( self.cmd_console.visible == True and each != None ):
        if type( each ) == list:
          for each_each in each:
            try:
              self.cmd_console.add_output_line_to_log( each_each ,is_bold=False, remove_line_break=False);
            except:
              log(self,["ERROR-42"]);
        else:
          try:
            self.cmd_console.add_output_line_to_log( each ,is_bold=False, remove_line_break=False);
          except:
            log(self,["ERROR-43"]);
    log(self, rts );

  if output_to_file != None and self.path_to_uut != None:
    list2file( os.path.join(self.path_to_uut, output_to_file), rts );


# self.cmd_console.add_output_line_to_log("\n",is_bold=False, remove_line_break=False);
  if ( self.cmd_console.visible == True and not quiet ):
#   self.cmd_console.add_output_line_to_log( "\r",is_bold=False, remove_line_break=False);
    self.cmd_console.restore_default_prefix();
  return rts;

###############################################################################
def init_manual( self ):
  a = [];
  a+=["#####################################################################"];
  a+=["# SUMP3 by BlackMesaLabs  GNU GPL V2 Open Source License. Python 3.x "];
  a+=["# (C) Copyright 2024 Kevin M. Hubbard - All rights reserved.         "];
  a+=["#####################################################################"];
  a+=["1.0 Scope                                                            "];
  a+=[" This document describes the SUMP3 software and hardware.            "];
  a+=["                                                                     "];
  a+=["2.0 Software Architecture                                            "];
  a+=[" The SUMP3 application is a Python 3.x script using the PyGame module"];
  a+=[" for mouse and graphical user interface and PyGame-GUI module for    "];
  a+=[" standard GUI type widgets. Communication to hardware is over TCP    "];
  a+=[" Socket communications to a BD_SERVER.py instance. The software is   "];
  a+=[" architected as a GUI wrapper around a command line application with "];
  a+=[" a bd_shell interface.                                               "];
  a+=["                                                                     "];
  a+=["3.0 Hardware Architecture                                            "];
  a+=[" The SUMP3 hardware is parameterizable verilog RTL which infers three"];
  a+=[" types of data acquisition units of user specified width and lengths."];
  a+=[" Note that the digital_hs unit is deprecated and should not be used. "];
  a+=[" RLE pods with RLE disabled should be used instead. SUMP3 hardware   "];
  a+=[" is scalable to up to 256 RLE Hubs with each hub having up to 256    "];
  a+=[" RLE pods. Multiple RLE Hubs support multiple clock domains.         "];
  a+=["                                                                     "];
  a+=["                    -------------      ---------                     "];
  a+=["  digital_rle[:] ->| RLE Pod+RAM |<-->| RLE Hub |<-+                 "];
  a+=["                    -------------     |         |  |                 "];
  a+=["                    -------------     |         |  |                 "];
  a+=["  digital_rle[:] ->| RLE Pod+RAM |<-->|         |  |                 "];
  a+=["                    -------------      ---------   |                 "];
  a+=["                                                   |                 "];
  a+=["                    -------------      ---------   |                 "];
  a+=["  digital_ls[:] -->| Sample+Hold |--->| RAM     |<-+                 "];
  a+=["  analog_ls[:] --->|             |     ---------   |                 "];
  a+=["                    -------------                  |                 "];
  a+=["                                       ---------   |   -----------   "];
  a+=["  digital_hs[:] --------------------->| RAM     |<-+  | Software  |  "];
  a+=["                    ---------------    ---------   |  | Control   |  "];
  a+=["  events[31:0] --->| Trigger Logic |---------------+  | Interface |  "];
  a+=["                    ---------------                    -----------   "];
  a+=["                                                                     "];
  a+=["                                                                     "];
  a+=["4.0 Command Descriptions                                             "];
  a+=[" 4.1 GUI Control                                                     "];
  a+=["  gui_minimize      : Minimize the PyGame GUI. Useful for scripting. "];
# a+=["  gui_fulscreen     : Toggle in and out of fullscreen mode.          "];
  a+=["  exit              : Exit the PyGame GUI.                           "];
  a+=["  win_tab           : Rotate through active windows.                 "];
  a+=["  zoom_in           : Increase signal view magnification             "];
  a+=["  zoom_out          : Decrease signal view magnification             "];
  a+=["  zoom_full         : View all signal samples                        "];
  a+=["  zoom_to_cursors   : View region bound by cursors                   "];
  a+=["  pan_left          : Scroll to the left                             "];
  a+=["  pan_right         : Scroll to the right                            "];
  a+=["  page_up           : Page UP the signal list for selected window.   "];
  a+=["  page_down         : Page Down the signal list for selected window. "];
  a+=["  search_forward  / : Scroll right to next signal transition         "];
  a+=["  search_backward ? : Scroll left to previous signal transition      "];
  a+=["  time_snap         : Align all RLE windows in time to selected window"];
  a+=["  time_lock         : Lock all RLE windows in time to selected window"];
  a+=["  font_larger       : Increase GUI font size                         "];
  a+=["  font_smaller      : Decrease GUI font size                         "];
  a+=["  Up Arrow          : Zoom In                                        "];
  a+=["  Down Arrow        : Zoom Out                                       "];
  a+=["  Right Arrow       : Pan Right                                      "];
  a+=["  Left Arrow        : Pan Left                                       "];
  a+=["  Backspace         : Return previous view (bd_shell must be closed) "];
  a+=["  Delete            : Remove selected signal by making visible False "];
  a+=["  End               : Toggle selected signal hidden attribute        "];
  a+=["  Insert            : Show all signals hidden or not visible         "];
  a+=["  Esc               : Unselect selected signals                      "];
  a+=[" 4.2 Mouse Actions                                                   "];
  a+=["  LeftMouseClick    : Select signal                                  "];
  a+=["  Ctrl+MouseClick   : Select multiple signals                        "];
  a+=["  RightClick        : ZoomOut                                        "];
  a+=["  RightClickDrag    : Zoom to Region                                 "];
  a+=["  Scroll Wheel      : Zoom / Pan                                     "];
  a+=[" 4.3 SUMP Hardware                                                   "];
  a+=["  sump_connect      : Connect to Sump HW via bd_server socket server."];
  a+=["  sump_arm          : Arm for acquisition without polling.           "];
  a+=["  sump_acquire      : Arm for acquisition with polling until done.   "];
  a+=["  sump_download     : Download acquisition to local file.            "];
  a+=["  sump_force_trig   : Force a software induced trigger.              "];
  a+=["  sump_force_stop   : Force a software induced acquisition stop.     "];
  a+=["  sump_reset        : Reset sump HW and place in idle state.         "];
  a+=["  sump_idle         : Place HW in idle state.                        "];
  a+=[" 4.4 SUMP Software                                                   "];
  a+=["  4.4.1 Capture Save and Load to files                               "];
  a+=["   save_pza          : Save current capture data to a *.pza file.    "];
  a+=["   load_pza          : Load previous capture data from a *.pza file. "];
  a+=["   save_vcd          : Save current capture data to a *.vcd file.    "];
  a+=["   save_list         : Save current capture data to a list text file."];
  a+=["  4.4.2 Image Save                                                   "];
  a+=["   save_pic <file>   : Save Window or GUI to an image file.          "];
  a+=["   save_png          : Save Window or GUI to an autonamed PNG file.  "];
  a+=["   save_jpg          : Save Window or GUI to an autonamed JPG file.  "];
  a+=["   save_bmp          : Save Window or GUI to an autonamed BMP file.  "];
  a+=["  4.4.3 Views                                                        "];
  a+=["   select_window n   : Select the active window (1,2 or 3)           "];
  a+=["   create_view       : Create a new view.                            "];
  a+=["   remove_view       : Remove a view from a window.                  "];
# a+=["   delete_view       : Delete a view from a window.                  "];
  a+=["   add_view          : Add a view to a window.                       "];
  a+=["   apply_view        : Apply a view to a window.                     "];
  a+=["   list_view         : List view attributes.                         "];
# a+=["   include_view      : Include a view to be in selected list.        "];
  a+=["   add_view_ontap    : Add a view to the select list.                "];
  a+=["   remove_view_ontap : Remove a view from the select list.           "];
  a+=["   list_view_ontap   : List a view from the select list.             "];
  a+=["   save_view name    : Save current view to name.txt.                "];
  a+=["  4.4.4 Signals                                                      "];
  a+=["   create_signal     : Create a new signal for a view.               "];
  a+=["   remove_signal     : Remove a signal from being displayed.         "];
  a+=["   add_signal        : Add a signal to being displayed.              "];
  a+=["   hide_signal       : Remove signal from display.                   "];
  a+=["   show_signal       : Show the signal.                              "];
  a+=["   delete_signal     : Delete a signal.                              "];
  a+=["   paste_signal      : Paste a signal that was cut or copied.        "];
# a+=["   insert_signal     : Insert a signal that was deleted.             "];
# a+=["   clone_signal      : Clone a selected signal to a 2nd window.      "];
  a+=["   apply_attribute   : Apply attribute to selected or created signal."];
  a+=["   list_signal       : List signal attributes.                       "];
  a+=["   rename_signal     : Change the signal's name attribute.           "];
  a+=["  4.4.5 Groups                                                       "];
  a+=["   create_group      : Create a new group at existing group level.   "];
  a+=["   create_bit_group  : Create a new group of bits in one command.    "];
  a+=["   end_group         : Close out a newly created group.              "];
  a+=["   expand_group      : Expand a group so that children are visible.  "];
  a+=["   collapse_group    : Collapse group so children are not visible.   "];
# a+=["  4.4.6 Presets                                                      "];
# a+=["   create_preset     : Create a preset 1-8 that points to a script.  "];
# a+=["   remove_preset     : Remove a preset 1-8.                          "];
  a+=[" 4.5 bd_shell subsystem                                              "];
  a+=["  source            : Source a bd_shell text file.                   "];
  a+=["  sleep_ms          : Sleep (pause) for specified number of ms.      "];
  a+=["  print             : Print the value of an environment variable.    "];
  a+=["  r <addr>          : Read <addr> accessed via bd_server.            "];
  a+=["  w <addr> <data>   : Write <data> to <addr> accessed via bd_server. "];
  a+=[" 4.6 *NIX subsystem                                                  "];
  a+=["  pwd               : Display current directory path.                "];
  a+=["  cd                : Change current directory.                      "];
  a+=["  ls                : List contents of current directory.            "];
  a+=["  more              : Display text contents of file.                 "];
  a+=["  cp                : Copy a file.                                   "];
  a+=["  vi                : Edit text file using default text editor.      "];
  a+=["                                                                     "];
  a+=["5.0 Environment Variables                                            "];
  a+=[" The bd_shell environment has internal variables that may be modified"];
  a+=[" and read. Using a variable in a script requires preceding the var   "];
  a+=[" name with the '$' symbol. For example, bd_shell commands of:        "];
  a+=["    addr = 12345678                                                  "];
  a+=["    r $addr                                                          "];
  a+=[" Assigns a new variable called 'addr' to 0x12345678 and then reads   "];
  a+=[" the hardware memort location at that address.                       "];
  a+=[" Variables are loaded from the sump3.ini file on startup and internal"];
  a+=[" variables are the written back out to sump3.ini on exit.            "];
  a+=["  5.1 bd_server                                                              "];
  a+=["   bd_connection              : 'tcp' only supported connection type.        "];
  a+=["   bd_protocol                : 'poke' only supported connection protocol.   "];
  a+=["   bd_server_ip               : 'localhost' or IP ('127.0.0.1') of bd_server."];
  a+=["   bd_server_socket           : '21567' TCP/IP socket of bd_server.   "];
  a+=["   bd_server_quit_on_close    : Quit bd_server when GUI closes.       "];
  a+=["   aes_key                    : 256 bit hex AES key.                  "];
  a+=["   aes_authentication         : 1 = use AES authentication for remote."];
  a+=["  5.2 SUMP Hardware                                                  "];
  a+=["   sump_uut_addr              : Base address of SUMP Control+Data Regs.  "];
  a+=["   sump_user_ctrl             : 32 bit user_ctrl mux setting.            "];
# a+=["   sump_user_stim             : 32 bit user_stim stimulus setting.       "];
  a+=["   sump_ls_clock_div          : Clock divisor for Low Speed acquisition  "];
  a+=["   sump_trigger_analog_ch     : Analog channel number for comp trig.     "];
  a+=["   sump_trigger_analog_level  : Float analog units for comp trigger.     "];
  a+=["   sump_trigger_delay         : Trigger delay in float uS time units.    "];
  a+=["   sump_trigger_field         : 32bit hex trigger field value.           "];
  a+=["   sump_trigger_location      : trigger location. 0,25,50,75 or 100      "];
  a+=["   sump_trigger_nth           : Nth trigger to trigger on. 1 to 2^16     "];
  a+=["   sump_trigger_type          : Trigger type. or_rising, etc.            "];
  a+=["   sump_download_ondemand     : Only downlad Pods that have views applied."];
  a+=["   sump_thread_lock_en        : 1 to enable hardware thread locking.     "];
  a+=["   sump_thread_id             : Static thread_id or 00000000 for dynamic."];
  a+=["  5.3 Unit Under Test                                                    "];
  a+=["   uut_name                   : String name for UUT.                     "];
# a+=["   uut_rev                    : String revision for UUT.                 "];
  a+=["  5.4 VCD Exporting                                                      "];
  a+=["   vcd_viewer_en              : Enables launching external VCD viewer.   "];
  a+=["   vcd_viewer_path            : ie 'C:\\gtkwave\\bin\\gtkwave.exe'       "];
  a+=["   vcd_viewer_gtkw_en         : Enables generation of GTKwave *.gtkw file"];
  a+=["   vcd_viewer_width           : GTKwave width in pixels for GTKW file    "];
  a+=["   vcd_viewer_width           : GTKwave height in pixels for GTKW file   "];
  a+=["   vcd_hierarchical           : Enables VCD file with Hub+Pod hierarchy. "];
  a+=["   vcd_hubpod_names           : Embed Hub+Pod names in VCD signal names. "];
  a+=["   vcd_hubpod_nums            : Embed Hub+Pod numbers in VCD signal names."];
  a+=["   vcd_group_names            : Embed Group names in VCD signal names."];

  a+=["                                                                     "];
  a+=["6.0 Software Constructs                                              "];
  a+=[" 6.1 Signal                                                          "];
  a+=["  A Signal is a mapping of one or more digital bits or a single ADC  "];
  a+=["  channel into an end user recognizable object suitable for viewing. "];
  a+=["  Optional Signals of type Group and Spacer may be created in order  "];
  a+=["  to customize how Signals are displayed in Windows.                 "];
  a+=[" 6.2 View                                                            "];
  a+=["  A View is a construct for grouping together multiple signals that  "];
  a+=["  an end user would likely want to see together within a window.    "];
  a+=["  All the Signals within a single View must share the same Timezone. "];
  a+=["  A View may optionally have a User_ctrl attribute which determines  "];
  a+=["  if the View and the Signals assigned to the View are valid based   "];
  a+=["  on the User_ctrl setting for the acquisition.                      "];
  a+=[" 6.3 Window                                                          "];
  a+=["  A Window is one of three GUI regions for displaying Views. A Window"];
  a+=["  may contain one or more Views but all the Views within a single    "];
  a+=["  Window must share a timezone.                                      "];
  a+=[" 6.4 Timezone                                                        "];
  a+=["  A Timezone is a user defined name for one of multiple acquisition  "];
  a+=["  sample types. Example names might be 'ls', 'hs' and 'rle'.         "];
  a+=[" 6.5 Group                                                           "];
  a+=["  A Group is a Signal of -type group that may optionally be created  "];
  a+=["  to bundle multiple signals together in a single expandable and     "];
  a+=["  collapsable unit. A Group may contain lower level Groups.          "];
  a+=[" 6.6 Spacer                                                          "];
  a+=["  A Spacer is a Signal of -type spacer that may optionally be created"];
  a+=["  to add some white space between Signals when displayed in a Window."];
  a+=["  Spacers are boring but useful constructs when displaying analog    "];
  a+=["  waveforms.                                                         "];
# a+=[" 6.7 Presets                                                         "];
# a+=["  Presets are user defined buttons in the View panel which point to  "];
# a+=["  and execute a user designed script. They are intended to execute a "];
# a+=["  user defined macro for repetive steps such as GUI actions for:     "];
# a+=["    apply_view, collapse_group, remove_signal, hide_signal, etc.     "];
  a+=["                                                                     "];
  a+=["7.0 Signal Attributes                                                "];
  a+=[" 7.1 -source                                                         "];
  a+=["  A Signal that is not of -type Group or Spacer must have a -source  "];
  a+=["  attribute which defines the acquisition source at the hardware.    "];
  a+=["  Valid sources are digital_ls[:], digital_hs[:], analog_ls[] and    "];
  a+=["  digital_rle[:]. Digital signals may be a single bit like [2] or a  "];
  a+=["  collection of bits like [3:0]. The analog_ls[] must be the ADC     "];
  a+=["  channel number, starting with channel [0].                         "];
  a+=[" 7.2 -format                                                         "];
  a+=["  A Signal must have a display format such as 'binary', 'hex' or     "];
  a+=["  'analog'.                                                          "];
  a+=[" 7.3 -view                                                           "];
  a+=["  A Signal must be assigned a -view attribute as only Views may be   "];
  a+=["  assigned and displayed in a Window. If a Signal is assigned to a   "];
  a+=["  Group, it will automatically inherit the Group's -view attribute.  "];
  a+=[" 7.4 -group                                                          "];
  a+=["  A Signal may optionally be assigned to a signal of -type group.    "];
  a+=["  Groups may be expanded and collapsed. A Signal assigned to a Group "];
  a+=["  will automatically inherit the Group's -view attribute.            "];
  a+=[" 7.5 -color                                                          "];
  a+=["  A Signal may have a user defined color specified for it either in  "];
  a+=["  English ('blue') or in hex RGB ('0000FF'). The color red is used   "];
  a+=["  automatically to indicate trigger capable binary signals. Assigning"];
  a+=["  a binary signal that is not trigger capable is highly frowned upon."];
  a+=[" 7.6 -timezone                                                       "];
  a+=["  A Signal must belong to a timezone group. Default timezone group   "];
  a+=["  names are 'ls', 'hs' and 'rle'.                                    "];
  a+=[" 7.7 -visible                                                        "];
  a+=["  A Signal is only displayed in a window if -visible is True.        "];
  a+=[" 7.8 -hidden                                                         "];
  a+=["  A Signal with -hidden True will only have the signal name visible. "];
  a+=[" 7.10 -range                                                         "];
  a+=["  Analog ADC signals must have their integer range specified. Example"];
  a+=["  range would be 1023 for a 10 bit ADC.                              "];
  a+=[" 7.11 -units                                                         "];
  a+=[" 7.12 -units_per_code                                                "];
  a+=[" 7.13 -offset_units                                                  "];
  a+=[" 7.14 -offset_codes                                                  "];
  a+=[" 7.15 -units_per_division                                            "];
  a+=[" 7.15 -divisions_per_range                                           "];
  a+=["                                                                     "];
  a+=["8.0 Typical Work Flow                                                "];
  a+=[" 8.1 Apply power to the Unit Under Test.                             "];
  a+=["  This may seem silly to include as a step, but the vast majority of "];
  a+=["  SUMP communication problems involve either lack of power or lack of"];
  a+=["  clock to the UUT hardware.                                         "];
  a+=[" 8.2 Launch bd_server.py software.                                   "];
  a+=["  The bd_server server must be running on the computer that talks    "];
  a+=["  to the Unit Under Test hardware. Typically bd_server imports a     "];
  a+=["  design specific device driver which then communicates to the UUT   "];
  a+=["  hardware over a bus interface ( PCIe, FTDI UART serial, etc ).     "];
  a+=[" 8.3 Launch sump3.py software.                                       "];
  a+=["  The sump3.py application is the backend GUI user interface and may "];
  a+=["  run either on the same computer as bd_server, or optionally on a   "];
  a+=["  computer that has TCP/IP ( Ethernet / WiFi typ ) access to UUT.    "];
  a+=["  Note that the sump3.py application requires non-standard Python    "];
  a+=["  modules PyGame and PyGame-GUI be installed beforehand.             "];
  a+=[" 8.4 Select desired number of Windows.                               "];
  a+=["  By default sump3.py will display three Windows for signal viewing  "];
  a+=["  and support up to three different Timezones. Reducing the number of"];
  a+=["  of Windows displayed will increase the size of the visible Windows."];
  a+=["  Click [Navigation] button and then [Window-n] where n is 1,2 or 3  "];
  a+=["  to individually turn the three Windows on and off.                 "];
  a+=[" 8.5 Select the active Window.                                       "];
  a+=["  Only one Window may be active at a time and is indicated with a    "];
  a+=["  visible white outline. Toggling the <tab> key or clicking the mouse"];
  a+=["  button inside a Window will select it as the active Window.        "];
  a+=[" 8.6 Add View(s) to the active Window.                               "];
  a+=["  Click [ViewSetup] and select one or more Views to then [Apply] to  "];
  a+=["  the active Window. Repeat for all Windows that are enabled.        "];
  a+=[" 8.7 Connect to the SUMP Hardware.                                   "];
  a+=["  Click [Acquisition] and then [Connect] to connect to the UUT SUMP  "];
  a+=["  hardware engine. If the connection is successful the bottom right  "];
  a+=["  text area will list the acquisition information.                   "];
  a+=[" 8.8 Select Trigger Type.                                            "];
  a+=["  Click the text 'Trig Type' and then move the scroll bar above      "];
  a+=["  until the desired trigger type ( 'or_rising', etc ) is indicated.  "];
  a+=[" 8.9 Select Trigger Source.                                          "];
  a+=["  Select Signal(s) in red and then [Set_Trigs] to assign triggers.   "];
  a+=["  A '_/' symbol will show next to signal names that are now triggers."];
  a+=[" 8.10 Acquire samples.                                               "];
  a+=["  Click either [Arm] or [Acquire] to arm the SUMP HW for a single    "];
  a+=["  acquisition. Acquire will sit and poll the hardware until it has   "];
  a+=["  triggered and acquired all post-trigger samples. Arm will not poll."];
  a+=["  If Arm was used, click [Download] once the hardware has triggered. "];
  a+=[" 8.11 View the acquisition results.                                  "];
  a+=["  Click [Navigation] to see results, add cursors, zoom-in, out, etc. "];
  a+=[" 8.12 Save acquisition for offline viewing.                          "];
  a+=["  Click [Acquisition] then [Save_PZA] and specify the name for the   "];
  a+=["  *.pza file. [Load_PZA] may then be used to read it back in local   "];
  a+=["  or remotely on a sump3.py instance running offline.                "];
  a+=[" 8.13 Exit application.                                              "];
  a+=["  Click [Exit]. Certain parameters like main window dimensions and   "];
  a+=["  number of view windows that are enabled will be saved in the clear "];
  a+=["  text file sump3.ini. Other environment variables are stored here as"];
  a+=["  well and may be user modified once the sump3.py app has closed.    "];
  a+=["                                                                     "];
  a+=["9.0 View ROM Syntax                                                  "];
  a+=[" View ROMs are embedded alongside Sump3 logic to configure the Sump3 "];
  a+=[" software with signal names, types and attributes. View ROMs are     "];
  a+=[" primarily written in 7bit ASCII with a dozen special byte codes at  "];
  a+=[" 0xE0 - 0xFF range.                                                  "];
  a+=[" Code ParmBytes ASCII   Definition                                   "];
  a+=[" F0   0                 ROM Start                                    "];
  a+=[" F1   0         Yes     View Name                                    "];
  a+=[" F2   0                 Signal Source - This Pod                     "];
  a+=[" F3   2                 Signal Source Hub-N,Pod-N                    "];
  a+=[" F4   0         Yes     Signal Source Hub-Name.Pod-Name or analog_ls "];
  a+=[" F5   0         Yes     Group Name                                   "];
  a+=["                                                                     "];
  a+=[" F6   2         Yes     Signal Bit source, Name                      "];
  a+=[" F7   4         Yes     Signal Vector Rip, Name                      "];
  a+=[" F8   1         Yes     FSM Binary State, Name                       "];
  a+=[" F9   4         Yes     Signal Vector Rip Group, Name                "];
  a+=[" FD   0         Yes     Reserved for possible bd_shell use           "];
  a+=[" FE   0         Yes     Attribute for last signal declaration        "];
  a+=["                                                                     "];
  a+=[" E0   0                 ROM End                                      "];
  a+=[" E1   0                 View End                                     "];
  a+=[" E2   0                 Source End                                   "];
  a+=[" E3   0                 Source End                                   "];
  a+=[" E4   0                 Source End                                   "];
  a+=[" E5   0                 Group End                                    "];
  a+=["                                                                     "];
  a+=[" Example:                                                            "];
  a+=[" .view_rom_txt (                                                     "];
  a+=[" {                                                                   "];
  a+=["  64'd0,                                    // Reqd 2-DWORD postamble"];
  a+=["  8'hF0,                                    // ROM Start             "];
  a+=["   8'hF1, 'u1_pod',                         // Name for this view    "];
  a+=["     8'hF4, 'ck100_hub.u1_pod',             // Signal source         "];
  a+=["     8'hF5, 'u1_pod_events',                // Top level group       "];
  a+=["       8'hF7, 16'd3, 16'd0, 'u1_pod_e[3:0]',// create_signal vector  "];
  a+=["         8'hF8, 8'd0, 'st_reset',           // State Name            "];
  a+=["         8'hF8, 8'd1, 'st_run',             // State Name            "];
  a+=["         8'hF8, 8'd2, 'st_halt',            // State Name            "];
  a+=["       8'hF9, 16'd3, 16'd0, 'u1_pod_e[3:0]',// create_bit_group      "];
  a+=["       8'hF5, 'u1_pod_e[7:4]',              // Sub level group       "];
  a+=["         8'hF6, 16'd7, 'u1_pod_e[7]',       // create_signal bit     "];
  a+=["         8'hF6, 16'd6, 'u1_pod_e[6]',                                "];
  a+=["         8'hF6, 16'd5, 'u1_pod_e[5]',                                "];
  a+=["         8'hF6, 16'd4, 'u1_pod_e[4]',                                "];
  a+=["       8'hE5,                               // End Group             "];
  a+=["     8'hE5,                                 // End Group             "];
  a+=["     8'hE4,                                 // End Source            "];
  a+=["   8'hE1,                                   // End View              "];
  a+=["  8'hE0                                     // End ROM               "];
  a+=[" })                                                                  "];
  a+=["                                                                     "];
  a+=["10.0 SUMP History                                                    "];
  a+=[" The original OSH+OSS SUMP was designed in 2007 as an external logic "];
  a+=[" logic analyzer using a Xilinx FPGA eval board for capturing external"];
  a+=[" electrical signals non compressed to all available FPGA block RAM.  "];
  a+=[" See http://www.sump.org/projects/analyzer/                          "];
  a+=[" The original developer published the serial communication protocol  "];
  a+=[" and also wrote a Java based waveform capture tool. The simplicity of"];
  a+=[" the protocol and the quality and maintenance of the Open-Source Java"];
  a+=[" client has inspired many new SUMP compliant projects such as:       "];
  a+=[" 'Open Logic Sniffer' : https://www.sparkfun.com/products/9857       "];
  a+=["                                                                     "];
  a+=[" 10.1 SUMP1-RLE ( 2014 )                                             "];
  a+=["  Black Mesa Labs developed the SUMP1-RLE hardware in 2014 as a      "];
  a+=["  software protocol compatible SUMP engine that was capable of real  "];
  a+=["  time hardware compression of samples ( Run Length Encoded ). The   "];
  a+=["  idea of the project was to leverage the open-source Java software  "];
  a+=["  and couple it with new hardware IP that was capable of storing deep"];
  a+=["  capture acquisitions using only a single FPGA Block RAM, allowing  "];
  a+=["  SUMP to be used internally with existing FPGA designs rather than  "];
  a+=["  a standalone device. FPGA vendor closed license logic analyzers all"];
  a+=["  store using no compression requiring vast amount of Block RAMS to  "];
  a+=["  be useful and typically do not fit will within the limited fabric  "];
  a+=["  resources of an existing FPGA design requiring debugging. SUMP1-RLE"];
  a+=["  was later enhanced to include 2 DWORDs of sampled data along with  "];
  a+=["  the RLE compressed signal events. This enhancement required new    "];
  a+=["  software which was written in .NET Powershell for Windows platform."];
  a+=["                                                                     "];
  a+=[" 10.2 SUMP2-RLE ( 2016 )                                             "];
  a+=["  SUMP2 is a software and hardware complete redesign to improve upon "];
  a+=["  the SUMP1-RLE concept. For SUMP2 the .NET software was tossed due  "];
  a+=["  to poor user interface performance and replaced with a PyGame based"];
  a+=["  VCD waveform viewer ( chip_wave.py also from BML ). The SUMP2 HW   "];
  a+=["  is now a single Verilog file with no backwards compatibility with  "];
  a+=["  any legacy SUMP hardware or software systems. SUMP2 hardware is    "];
  a+=["  designed to capture 512bits of DWORDs and 32bits of events versus  "];
  a+=["  the SUMP1 limits of 16 event bits and 64bits of DWORDs. Sample     "];
  a+=["  depth for SUMP2 is now completely defined by a hardware instance   "];
  a+=["  with software that automatically adapts.  The RLE aspect of SUMP2  "];
  a+=["  is optional and not required for simple data intensive captures.   "];
  a+=["  SUMP2 software includes bd_shell support for changing variables    "];
  a+=["  on the fly and providing simple low level hardware access to regs. "];
  a+=["                                                                     "];
  a+=[" 10.3 SUMP2-DeepSump ( 2018 )                                        "];
  a+=["  DeepSump is an optional hardware addon to SUMP2-RLE. It works by   "];
  a+=["  capturing RLE samples of the 32 events to a deeper and potentially "];
  a+=["  slower memory device such as DRAM. A FIFO is used to maintain full "];
  a+=["  bandwidth for short bursts of time. DeepSump captures are not      "];
  a+=["  displayed in the sump2.py GUI, but are instead downloaded and      "];
  a+=["  directly converted to VCD format for viewing in an external VCD    "];
  a+=["  viewer such as GTKwave. The SUMP2-RLE format for compression is    "];
  a+=["  very similar to VCD format, so conversion is very simple and fast. "];
  a+=["                                                                     "];
  a+=[" 10.4 SUMP-2 Near Field / Far Field ( 2022 )                         "];
  a+=["  RLE Masking/Unmasking has been replaced with Near Field/Far Field. "];
  a+=["  An event signal that is Near Field only is sampled around the      "];
  a+=["  trigger and stored in non-RLE sample memory. Far Field events are  "];
  a+=["  RLE compressed and stored in RLE memory. By specifying more events "];
  a+=["  to be Near Field, fewer events go into RLE memory which allows for "];
  a+=["  much wider Far Field captures in absolute time.                    "];
  a+=["  The sump hardware can automatically detect spurious signals and    "];
  a+=["  assign them to Near Field. The user may also assign Near Field     "];
  a+=["  prior to arming.                                                   "];
  a+=["                                                                     "];
  a+=[" 10.5 SUMP2 Sunsetting (2023)                                        "];
  a+=["  SUMP2 architecture is fundamentally limited to simultaneous capture"];
  a+=["  of 32 RLE compressible binary signals. The maximum capture length  "];
  a+=["  is limited to a few milliseconds. The RLE architecture was never   "];
  a+=["  designed to support things like asynchronous ADC samples and highly"];
  a+=["  compressible acquisitions of hundreds of milliseconds to seconds.  "];
  a+=["  SUMP2 was architected to being a fully functional FPGA ILA that    "];
  a+=["  only required one or two 36Kbit block RAMs - less than 5% of the   "];
  a+=["  memory resources of a 90nm generation $10 FPGA. SUMP2 was never    "];
  a+=["  intended to be used in 2nm FPGAs with almost unlimited RAM that are"];
  a+=["  coming very soon. The decision was made to take SUMP in a new      "];
  a+=["  direction to address these needs while still maintaining the best  "];
  a+=["  legacy features of the SUMP2 design.                               "];
  a+=["                                                                     "];
  a+=[" 10.6 SUMP3 Mixed-Signal (2023)                                      "];
  a+=["  SUMP3 inherits and enhances many design aspects of SUMP2 while     "];
  a+=["  also including mixed signal ADC samples and digital sample and hold"];
  a+=["  signals at a user adjustable sample rate supporting captures in    "];
  a+=["  the one to ten second range for slowly sampled signals while also  "];
  a+=["  capturing high speed digital signals that are all correlated in    "];
  a+=["  time with a common trigger. Better RLE compression using multiple  "];
  a+=["  RLE engines which are divided in 8 bit boundaries with no single   "];
  a+=["  32bit RLE limit. Faster RLE rendering by not merging non-RLE       "];
  a+=["  samples and rendering RLE as RLE points without decompressing.     "];
  a+=["  SUMP3's unique feature is providing up to three different capture  "];
  a+=["  mechanisms that may all be displayed at once with a single trigger "];
  a+=["  as a timing reference point between them. It is designed to capture"];
  a+=["  thousands of signals at once, and/or using user_ctrl input muxes.  "];
  a+=["                                                                     "];
  a+=["11.0 BD_SERVER.py                                                    "];
  a+=["  The SUMP2.py application does not communicate directly to hardware "];
  a+=["  but instead uses BD_SERVER.py as an interface layer. BD_SERVER is  "];
  a+=["  a multi use server application that accepts requests via TCP to    "];
  a+=["  read and write to low level hardware and then translates those     "];
  a+=["  requests using one of many low level hardware protocols available. "];
  a+=["  BD_SERVER allows the low level communications to easily change from"];
  a+=["  interfaces like USB FTDI serial to PCI without requiring any change"];
  a+=["  to the high level application. This interface also supports the    "];
  a+=["  debugging of an embedded system from a users regular desktop with  "];
  a+=["  a standard Ethernet or Wifi connection between the two. Typical use"];
  a+=["  is to run both python applications on same machine and use the TCP "];
  a+=["  localhost feature within the TCP stack for communications.         "];
  a+=["  The separation of sump2.py from bd_server.py allows for sump2.py to"];
  a+=["  remain completely open source while internal proprietary versions  "];
  a+=["  of bd_server.py may be created to communicate with closed source   "];
  a+=["  systems.                                                           "];
  a+=["  Available at https://github.com/blackmesalabs/MesaBusProtocol      "];
  a+=["                                                                     "];
  a+=["    ------------           --------------           ---------------  "];
  a+=["   |  sump3.py  |<------->| bd_server.py |<------->| SUMP Hardware | "];
  a+=["    ------------  Ethernet --------------  USB,PCI  ---------------  "];
  a+=["                                                                     "];
  a+=["12.0 License                                                         "];
  a+=[" This software is released under the GNU GPLv3 license.              "];
  a+=["   Full license is available at http://www.gnu.org                   "];
  a+=[" The hardware is released under CERN Open Hardware Licence v1.2.     "];
  a+=["   Full license is available at http://ohwr.org/cernohl              "];
  a+=[" SUMP3 HW+SW available at https://github.com/blackmesalabs/sump3     "];
  return a;


#####################################
if __name__ == '__main__':
  app = main()
  app.run()
# EOF

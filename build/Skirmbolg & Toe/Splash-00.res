tcl86t.dll      tk86t.dll       tk              __splash              �  �  �   �   Xtcl86t.dll tk\text.tcl tk\tk.tcl tk\ttk\utils.tcl tk\ttk\cursors.tcl tk\ttk\fonts.tcl tk86t.dll tk\license.terms VCRUNTIME140.dll tk\ttk\ttk.tcl proc _ipc_server {channel clientaddr clientport} {
set client_name [format <%s:%d> $clientaddr $clientport]
chan configure $channel \
-buffering none \
-encoding utf-8 \
-eofchar \x04 \
-translation cr
chan event $channel readable [list _ipc_caller $channel $client_name]
}
proc _ipc_caller {channel client_name} {
chan gets $channel cmd
if {[chan eof $channel]} {
chan close $channel
exit
} elseif {![chan blocked $channel]} {
if {[string match "update_text*" $cmd]} {
global status_text
set first [expr {[string first "(" $cmd] + 1}]
set last [expr {[string last ")" $cmd] - 1}]
set status_text [string range $cmd $first $last]
}
}
}
set server_socket [socket -server _ipc_server -myaddr localhost 0]
set server_port [fconfigure $server_socket -sockname]
set env(_PYIBoot_SPLASH) [lindex $server_port 2]
image create photo splash_image
splash_image put $_image_data
unset _image_data
proc canvas_text_update {canvas tag _var - -} {
upvar $_var var
$canvas itemconfigure $tag -text $var
}
package require Tk
set image_width [image width splash_image]
set image_height [image height splash_image]
set display_width [winfo screenwidth .]
set display_height [winfo screenheight .]
set x_position [expr {int(0.5*($display_width - $image_width))}]
set y_position [expr {int(0.5*($display_height - $image_height))}]
frame .root
canvas .root.canvas \
-width $image_width \
-height $image_height \
-borderwidth 0 \
-highlightthickness 0
.root.canvas create image \
[expr {$image_width / 2}] \
[expr {$image_height / 2}] \
-image splash_image
wm attributes . -transparentcolor magenta
.root.canvas configure -background magenta
pack .root
grid .root.canvas -column 0 -row 0 -columnspan 1 -rowspan 2
wm overrideredirect . 1
wm geometry . +${x_position}+${y_position}
wm attributes . -topmost 1
raise .�PNG

   IHDR   !   1   c�0�   `PLTE�J/�vD�Ԫ�r�oPt?9?(2�(5�;D�v"��4��ac�M>�H&\B<>N� ��,�������܋��Zi�:Df&+D� D%h8l�P��uz跖i��c�    tRNS ����������������������������������v   �IDAT8���A�0��fk�t�����Id�җ��2�_�3�pI��@2���gd���H#�n�BK�/"� g�wf�=�� �2A#LA*�^Tӽ��KE�B��K3`oz�D���F*�$t#O�sžH;ۋط�P��u~=��5�Ě@��jp,�
�,�xA�N�j��QY]�ڋl5    IEND�B`�
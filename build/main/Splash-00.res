tcl86t.dll      tk86t.dll       tk              __splash              �  �  �   �   Xtk\tk.tcl tk\ttk\utils.tcl tk86t.dll tk\ttk\ttk.tcl tk\text.tcl tk\ttk\cursors.tcl VCRUNTIME140.dll tcl86t.dll tk\license.terms tk\ttk\fonts.tcl proc _ipc_server {channel clientaddr clientport} {
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
   IHDR   4   q   ��4  �IDATx��=N#A�����W�B+ �\�;l��p.���d�"�����������ʘ���]߼�����t4=�p?/�&��W� )Ʃ�PƩ�O8t�@(8�7�$(I� 
@�0@g����;�ޛ�����R�^0�r��: �ܑ����+ZHb@=Ǎ/ -�sQ���Z����^s��@�T��Dl<JE�������XOn�؝S����ꐄ؀(KN�����1������HC�����C��<r� @ء��9�^�]l�e ����_\�����o ���g�v)�F�l;`�B��b@�#cw$%�r�j�J��{�ڣ���%{�>��>q�I�I���C1��q�\�T ~�o/���u�r%\ӏ�������� qI�zz ֶ�O2���:��~p�?G;M@� (�B��lHcw�Db�.N��!��#YM7� dJ9��C�xU@���k��݇SͱS�7�C���y�ښ�+u���1駃�8�@��;�x̤��I k�8��bs���u*
d՝�̌���~�]� P̝X�\�ƱQ���澺C.�.&�U�jPZ�B�@m ����-5�ľ�+�J.P
�(�4�-�XL+����M7?C�7�ь1�f�J�~ h�H�����nR4�4�?�r[��5w(��w�c(��ڵ��F�٢p==�l��8��m(��܉i �c��U��,Pkch%=k��WW��`�2��r�V��*�f��q@��k��r�=����}�)�E��b�Vĩ�O��Xƪ�ni�l�~�0n��#���9���n�~C�׼M���g� �f�cp������Ѹ�`�I�,5Y[�27�Z�d]&_/Syo۪��8*w�dq��v�n�e�j�v��S,�������)J�����_qQ��%�֋W}r�@�j9�T� �9�����    IEND�B`�
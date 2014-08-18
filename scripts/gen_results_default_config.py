mp.rcParams['ps.useafm'] = True
mp.rcParams['pdf.use14corefonts'] = True
#mp.rcParams['text.usetex'] = True

figure_size = (17,9)
config_fname = "local.config.py"
EXTENSIONS=['.csv']
# hatch_patterns = ('//', 'o', 'x', '\\\\', '*', '+', 'O', '.')
hatch_patterns = ( ' ', 'oo', '', '\\\\', 'x', '++', '//', 'O', '..', 'O', '-')
marker_patterns = ( 's' , 'd' , '<' , 'h' , '^' , 'o' , 'p' , 'D' , 'H' ,
 '_' , '>' , 'v' , 'x' , ',', '+' , '*' , ',' , '.' , '1' , '2' , '3' , '4' , )
xticks_id = 0 # the ID of the column that holds the xtick (horizontal) labels
xticks_per_bar_id = 1 # the ID of the column that holds the xtick (horizontal) labels
column_names = ["First", "Second", "Third"]
column_ids_data = [1, 2, 3]
column_ids_err = []
#num_clustered = 2 # number of clustered bars for stacked-cluster charts
cluster_groups = [6, 4, 21] # number of clustered bars for stacked-cluster charts
xtitle='X-Axis Title'
ytitle='Y-Axis Title'
title = "from-filename"
legend_ncol = 5 # make legend in one row (horizontal)
legend_loc = 9
# 'best'         : 0, (only implemented for axis legends)
# 'upper right'  : 1,
# 'upper left'   : 2,
# 'lower left'   : 3,
# 'lower right'  : 4,
# 'right'        : 5,
# 'center left'  : 6,
# 'center right' : 7,
# 'lower center' : 8,
# 'upper center' : 9,
# 'center'       : 10,

lable_angle_rotation=0
lable_y_space=0

title_fontsize=16
xtitle_fontsize=14
ytitle_fontsize=14
xlabel_fontsize=12.5
ylabel_fontsize=14
legend_fontsize=14
text_fontsize=14.5
numbers_fontsize=14

labels_rotation='horizontal'
labels_y=-0.08
label_enable=1

bbox=(0, 0, 1, 1)
shrink_width_factor=1.
shrink_height_factor=1.

# palete_blue_simple = "#0070C0 lightblue"
# palete_contrast = "green yellow lightsteelblue lightblue"
### http://www.netstrider.com/tutorials/HTMLRef/color/
palette_netscape_blue_green = "darkcyan lightseagreen turquoise aqua mediumturquoise cadetblue azure #AFEEEE darkturquoise teal"
# palette_netscape_green = "forestgreen limegreen lime chartreuse lawngreen greenyellow palegreen lightgreen springgreen mediumspringgreen darkgreen seagreen mediumseagreen darkseagreen mediumaquamarine aquamarine green darkolivegreen olivedrab olive"
### http://www.colourlovers.com/palette/944213/forever_lost?widths=0
palette_forever_lost = "#5D4157 #838689 #A8CABA #CAD7B2 #EBE3AA"
### http://www.colourlovers.com/palette/1542449/fighting_the_9-5.?widths=0
palette_fighting = "#262626 #475959 #689493 #9DC4C4 #EBDDC7"
### http://www.colorcombos.com/color-schemes/2/ColorCombo2.html etc
#palette_blue2 = "#097054 #FFDE00 #6599FF #FF9900 "
#palette_blue25 = "#0000FF #FF0000 #FFFFFF #333333 "
#palette_blue15 = "#CC0000 #99FF00 #FFCC00 #3333FF "
palette_1 = "#777777 #FFFFFF #CCCCCC #FFFFFF "
palette_2 = "#DDDDDD #FFFFFF #FFFFFF #DDDDDD "
palette_3 = "#333333 #777777 #CCCCCC #FFFFFF "

colors = [colorConverter.to_rgb(a) for a in (palette_1 + palette_2 + palette_3).split()] # use palette_blue2+palette_blue15 for colored

my_ylim = {}

def row_data_process(r):
	return r

import sys

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import CustomJS, Slider
from bokeh.plotting import ColumnDataSource, figure, output_file, show
from bokeh. palettes import Greens7, OrRd3
import numpy as np

from lib import File, segmentation, image_adjustments

def reverse_palette(palette):
    list_palette = [x for x in palette]
    list_palette.reverse()
    return list_palette

file_name = sys.argv[1]

RGreens7 = reverse_palette(Greens7)
ROrRd3 = reverse_palette(OrRd3)

channel_file = File.from_tiff(file_name)
segmented_image_stack = segmentation.segment_stack(
    channel_file, 
    "autolocal", 
    window_size=1,
    c_factor=1,
    min_vox_size=3,
    max_vox_size=9999
)
segmented_image_stack = segmented_image_stack.labelled_image > 1

nominal_image_stack = image_adjustments.rescale_intensity(channel_file)

main_fig = figure(
    plot_height=500, 
    plot_width=500, 
    title="Segmentation",
    sizing_mode="scale_both"
)

layer = Slider(start=0, end=len(nominal_image_stack), value=0, step=1, title="z layer")
window_size = Slider(start=1, end=30, value=1, step=2, title="window size")
c = Slider(start=1, end=30, value=1, step=1, title="c")
min_voxel_size = Slider(start=0, end=50, value=1, step=1, title="min voxel size")
max_voxel_size = Slider(start=0, end=9999, value=9999, step=1, title="min voxel size")

prev_layer = 0
prev_window_size = 1
prev_c = 1

prev_min_voxel_size = 1
prev_max_voxel_size = 9999



segmented_image_source = ColumnDataSource(data=dict(image=[segmented_image_stack[0]]))
nominal_image_source = ColumnDataSource(data=dict(image=[nominal_image_stack[0]]))


main_fig.image(
    source=nominal_image_source, 
    image="image",
    x=0, 
    y=0, 
    dw=10, 
    dh=10, 
    level="image",
    palette=RGreens7
)
main_fig.image(
    source=segmented_image_source, 
    image="image", 
    x=0, 
    y=0, 
    dw=10, 
    dh=10, 
    level="image", 
    palette=ROrRd3,
    alpha=0.3,
)

def callback():
    print("updating")
    print(prev_c,  c.value, prev_window_size,layer.value)
    if prev_c != c.value or prev_window_size != window_size.value:
        new_segmented_image_stack = segmentation.segment_stack(
        channel_file, 
        "autolocal", 
        window_size=window_size.value,
        c_factor=c.value,
        min_vox_size=min_voxel_size.value,
        max_vox_size=max_voxel_size.value
        )
        new_segmented_image_stack = new_segmented_image_stack.labelled_image > 1
        segmented_image_source.data = dict(image=[new_segmented_image_stack[layer.value]])
    else:
        segmented_image_source.data = dict(image=[segmented_image_stack[layer.value]])
    nominal_image_source.data = dict(image=[nominal_image_stack[layer.value]])
    


controls = [layer, window_size, c, min_voxel_size, max_voxel_size]
for control in controls:
    control.on_change('value', lambda attr, old, new: callback())


callback()

curdoc().add_root(row(main_fig, column(controls, width=150), height=500, width=750))

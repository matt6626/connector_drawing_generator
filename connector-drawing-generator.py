import drawsvg as draw
import sys, os
import numpy as np

# reference images
# https://res.cloudinary.com/rsc/image/upload/b_rgb:FFFFFF,c_pad,dpr_2.625,f_auto,h_214,q_auto,w_380/c_pad,h_214,w_380/Y1791575-01?pgw=1
# https://www.kit-elec-shop.com/19791-large_default/molex-mini-fit-socket-female-angled-6-pin.jpg
# https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/556/5569/039300080_sd.pdf?inline
# https://www.we-online.com/components/products/datasheet/649002227222.pdf
# https://www.we-online.com/components/products/datasheet/649002127222.pdf
# keying reference: https://docs.rs-online.com/8694/0900766b8150e87e.pdf
# single row: https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/556/5569/039303045_sd.pdf?inline
# single row: https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/556/5569/039303035_sd.pdf?inline


def draw_minifit_jr(
    pin_count: int = 10,
    row_count: int = 2,
    right_angle: bool = True,
):
    # dimensions are in mm * 10
    if row_count == 2 and pin_count % 2 != 0:
        raise Exception("2 row minifit_jr must have even pin count")
    if row_count > 2:
        raise Exception("minifit_jr can't have more than 2 rows")

    # main images controls
    # TODO: move stroke widths to variables here
    bg_stroke = "None"
    bg_stroke_width = 0

    # colours
    bg_fill_color = "#ffffff"
    conn_fill_color = "#f5f5f5"
    pin_fill_color = "#d1d1d1"
    pcb_pin_fill_color = "#d1d1d1"

    # body outline
    # reference:
    #   6 pin: width = 13.8
    #   pin pitch = 4.2
    #
    # body_width = pin_width * pin_count / row_count + 2 * border_width
    # solving the two point formula gives:
    #   border_width = 0.6
    pin_width = 42
    pin_height = 42
    border_width = 6
    body_width = pin_width * pin_count / row_count + 2 * border_width
    body_height = 54 if row_count == 1 else 96  # not including latch or pins
    pcb_pin_height = 35
    pcb_pin_width = 11.4
    pcb_pin_fillet_height = 10
    connector_margin = pin_width / 2
    drawing_width = (
        2 * connector_margin + body_width
    )  # add spacing on either side of drawing
    if right_angle:
        drawing_height = body_height + 1.5 * connector_margin + pcb_pin_height
    else:
        drawing_height = body_height + 2 * connector_margin
    d = draw.Drawing(drawing_width, drawing_height, origin=(0, 0))

    # background
    d.append(
        draw.Rectangle(
            0,
            0,
            drawing_width,
            drawing_height,
            stroke=bg_stroke,
            stroke_width=bg_stroke_width,
            fill=bg_fill_color,
        )
    )

    # connector "board offset rails"
    board_offset_rail_height = 4
    d.append(
        draw.Rectangle(
            connector_margin,
            connector_margin + body_height - board_offset_rail_height,
            board_offset_rail_height * 2,
            board_offset_rail_height * 2,
            stroke="black",
            stroke_width=1.2,
            fill=conn_fill_color,
        )
    )
    d.append(
        draw.Rectangle(
            connector_margin + body_width - 2 * board_offset_rail_height,
            connector_margin + body_height - board_offset_rail_height,
            board_offset_rail_height * 2,
            board_offset_rail_height * 2,
            stroke="black",
            stroke_width=1.2,
            fill=conn_fill_color,
        )
    )

    # connector rib line (background)
    if row_count == 2 and right_angle == True:
        bg_rib_line_y_offset = 1.5 * border_width
        d.append(
            draw.ArcLine(
                connector_margin + body_width,
                connector_margin + bg_rib_line_y_offset,
                border_width / 2,
                -90,
                90,
                stroke="black",
                stroke_width=1.2,
                fill=conn_fill_color,
            )
        )

    # pcb pins
    def draw_pcb_pin(x, y, fill):
        return (
            draw.Rectangle(
                x,
                y,
                pcb_pin_width,
                pcb_pin_height - pcb_pin_fillet_height,
                stroke="black",
                stroke_width=1.2,
                fill=fill,
            ),
            draw.Lines(
                # 1
                x,
                y + pcb_pin_height - pcb_pin_fillet_height,
                # 2
                x + pcb_pin_width,
                y + pcb_pin_height - pcb_pin_fillet_height,
                # 3
                x + pcb_pin_width * 2 / 3,
                y + pcb_pin_height,
                # 4
                x + pcb_pin_width * 1 / 3,
                y + pcb_pin_height,
                # 5
                x,
                y + pcb_pin_height - pcb_pin_fillet_height,
                stroke="black",
                stroke_width=1.2,
                fill=fill,
                close=True,
            ),
        )

    if right_angle:
        for cols in range(int(pin_count / row_count)):
            pcb_pin_element1, pcb_pin_element2 = draw_pcb_pin(
                connector_margin
                + body_width
                - border_width
                - pin_width * cols
                - pin_width / 2
                - pcb_pin_width / 2,
                connector_margin + body_height,
                fill=pcb_pin_fill_color,
            )
            d.append(pcb_pin_element1)
            d.append(pcb_pin_element2)

    # initial outline
    d.append(
        draw.Rectangle(
            connector_margin,
            connector_margin,
            body_width,
            body_height,
            stroke="black",
            stroke_width=2,
            fill=conn_fill_color,
            rx=border_width / 2,
        )
    )

    if row_count == 1:
        # connector rib line (foreground)
        d.append(
            draw.ArcLine(
                connector_margin + body_width - pin_width / 2 - border_width,
                connector_margin,
                border_width / 2,
                0,
                180,
                stroke="black",
                stroke_width=2,
                stroke_linecap="square",
                fill=conn_fill_color,
            )
        )

    if row_count == 2:
        # connector rib line (foreground)
        fg_rib_line_y_offset = border_width + 1.5 * pin_height
        d.append(
            draw.ArcLine(
                connector_margin + body_width,
                connector_margin + fg_rib_line_y_offset,
                border_width / 2,
                -90,
                90,
                stroke="black",
                stroke_width=2,
                stroke_linecap="square",
                fill=conn_fill_color,
            )
        )

    pin_margin = 5

    def draw_square_pin(x, y, fill):
        return draw.Rectangle(
            x + pin_margin / 2,
            y + pin_margin / 2,
            pin_width - pin_margin,
            pin_height - pin_margin,
            stroke="black",
            stroke_width=2,
            fill=fill,
        )

    def draw_irregular_hexagon_pin(x, y, fill):
        return draw.Lines(
            # p1
            x + pin_margin / 2,
            y + pin_margin / 2,
            # p2
            x + pin_width - pin_margin / 2,
            y + pin_margin / 2,
            # p3
            x + pin_width - pin_margin / 2,
            y + pin_margin / 2 + (pin_height - pin_margin) * 3 / 4,
            # p4
            x + pin_margin / 2 + (pin_width - pin_margin) * 3 / 4,
            y + pin_height - pin_margin / 2,
            # p5
            x + pin_margin / 2 + (pin_width - pin_margin) * 1 / 4,
            y + pin_height - pin_margin / 2,
            # p6
            x + pin_margin / 2,
            y + pin_margin / 2 + (pin_height - pin_margin) * 3 / 4,
            # p7
            x + pin_margin / 2,
            y + pin_margin / 2,
            stroke="black",
            stroke_width=2,
            fill=fill,
            close=True,
        )

    def draw_pin_number(x, y, pin_number):
        return draw.Text(
            f"{pin_number}",
            14,
            x + pin_width / 2,
            y + pin_width / 2,
            center=True,
            font_family="arial",
            font_weight="bold",
        )

    pin1_xpos = connector_margin + body_width - border_width - pin_width
    pin1_ypos = connector_margin + body_height - border_width - pin_height
    pin_xpos = pin1_xpos
    pin_ypos = pin1_ypos

    # single row keying doesn't seem to have a pattern
    pin_shape_key = {"square": 0, "hexagon": 1}
    one_row_2pin = [pin_shape_key["hexagon"], pin_shape_key["square"]]
    one_row_3pin = [
        pin_shape_key["hexagon"],
        pin_shape_key["square"],
        pin_shape_key["square"],
    ]
    one_row_4pin = [
        pin_shape_key["square"],
        pin_shape_key["square"],
        pin_shape_key["hexagon"],
        pin_shape_key["square"],
    ]
    one_row_4pin = [
        pin_shape_key["square"],
        pin_shape_key["square"],
        pin_shape_key["hexagon"],
        pin_shape_key["square"],
    ]
    one_row_5pin = [
        pin_shape_key["hexagon"],
        pin_shape_key["square"],
        pin_shape_key["square"],
        pin_shape_key["hexagon"],
        pin_shape_key["hexagon"],
    ]

    curr_row = 0
    curr_col = 0
    draw_pin = {0: draw_square_pin, 1: draw_irregular_hexagon_pin}
    for pin in range(pin_count):
        curr_row = int(pin / (pin_count / row_count))
        curr_col = int(pin % (pin_count / row_count))

        pin_xpos = pin1_xpos - pin_width * curr_col
        pin_ypos = pin1_ypos - pin_height * curr_row

        if row_count == 1:
            if pin_count == 2:
                pin_shape = one_row_2pin[pin]
            if pin_count == 3:
                pin_shape = one_row_3pin[pin]
            elif pin_count == 4:
                pin_shape = one_row_4pin[pin]
            elif pin_count == 5:
                pin_shape = one_row_5pin[pin]
        else:
            if curr_row == 0:
                pin_shape = pin_shape_key["square"]
                if curr_col % 4 == 1 or curr_col % 4 == 2:
                    pin_shape = pin_shape_key["hexagon"]

            else:
                pin_shape = pin_shape_key["hexagon"]
                if curr_col % 4 == 1 or curr_col % 4 == 2:
                    pin_shape = pin_shape_key["square"]

        d.append(draw_pin[pin_shape](pin_xpos, pin_ypos, fill=pin_fill_color))

        d.append(draw_pin_number(pin_xpos, pin_ypos, pin + 1))

    # connector latch
    latch_height = 14
    latch_width = 34
    d.append(
        draw.Rectangle(
            connector_margin + body_width / 2 - latch_width / 2,
            connector_margin - latch_height,
            latch_width,
            latch_height,
            stroke="black",
            stroke_width=2,
            fill=conn_fill_color,
        )
    )

    # export drawing to file
    d.set_pixel_scale(10)  # Set number of pixels per geometry unit
    # d.set_render_size(400, 200)  # Alternative to set_pixel_scale
    right_angle_dict = {False: "vert", True: "horiz"}
    file_name = f"mini-fit-jr_{right_angle_dict[right_angle]}_{row_count}x{int(pin_count / row_count)}"
    path_name = os.path.abspath(os.path.dirname(sys.argv[0]))

    save_dir = f"{path_name}/output/"
    save_dir_svg = f"{save_dir}svg/"
    save_dir_png = f"{save_dir}png/"
    dirs = [save_dir, save_dir_svg, save_dir_png]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)
    # print(f"{path}".svg")
    d.save_svg(f"{save_dir}/svg/{file_name}.svg")
    d.save_png(f"{save_dir}/png/{file_name}.png")
    # d.save_png(f"{path}.svg")
    # os.system(f"open {file_name}")

draw_minifit_jr(2, 1, True)
draw_minifit_jr(3, 1, True)
draw_minifit_jr(4, 1, True)
draw_minifit_jr(5, 1, True)
draw_minifit_jr(2, 2, True)
draw_minifit_jr(4, 2, True)
draw_minifit_jr(6, 2, True)
draw_minifit_jr(8, 2, True)
draw_minifit_jr(10, 2, True)
draw_minifit_jr(12, 2, True)
draw_minifit_jr(14, 2, True)
draw_minifit_jr(16, 2, True)
draw_minifit_jr(18, 2, True)
draw_minifit_jr(20, 2, True)
draw_minifit_jr(22, 2, True)
draw_minifit_jr(24, 2, True)
draw_minifit_jr(2, 1, False)
draw_minifit_jr(3, 1, False)
draw_minifit_jr(4, 1, False)
draw_minifit_jr(5, 1, False)
draw_minifit_jr(2, 2, False)
draw_minifit_jr(4, 2, False)
draw_minifit_jr(6, 2, False)
draw_minifit_jr(8, 2, False)
draw_minifit_jr(10, 2, False)
draw_minifit_jr(12, 2, False)
draw_minifit_jr(14, 2, False)
draw_minifit_jr(16, 2, False)
draw_minifit_jr(18, 2, False)
draw_minifit_jr(20, 2, False)
draw_minifit_jr(22, 2, False)
draw_minifit_jr(24, 2, False)

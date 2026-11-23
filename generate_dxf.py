import math
import os
import ezdxf
from ezdxf.enums import TextEntityAlignment

OUT_DIR = r"C:\Users\Habib\Desktop\شقتي"
DXF_PATH = os.path.join(OUT_DIR, "Zedan_Apartment_CAD.dxf")


def create_apartment_dxf():
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.CM
    msp = doc.modelspace()

    layers = [
        ("WALLS_EXTERIOR", 7, 50),
        ("WALLS_INTERIOR", 8, 35),
        ("COLUMNS_STRUCTURAL", 1, 30),
        ("DOORS", 30, 25),
        ("WINDOWS", 4, 25),
        ("BALCONY", 6, 30),
        ("GYPSUM_CEILING", 252, 15),
        ("STAIRWELL_HATCH", 9, 18),
        ("SHAFT_HATCH", 3, 20),
        ("UTILITIES", 3, 20),
        ("KITCHEN_CAD", 140, 20),
        ("FURNITURE", 42, 20),
        ("FURNITURE_DETAIL", 253, 13),
        ("DIMENSIONS", 2, 18),
        ("LABELS", 7, 18),
    ]
    for name, color, lw in layers:
        if name not in doc.layers:
            doc.layers.add(name, color=color, lineweight=lw)

    def cy(y_plan):
        return 1180.0 - y_plan

    def add_wall_rect(x1, y1, x2, y2, layer="WALLS_INTERIOR"):
        pts = [(x1, cy(y1)), (x2, cy(y1)), (x2, cy(y2)), (x1, cy(y2)), (x1, cy(y1))]
        msp.add_lwpolyline(pts, dxfattribs={"layer": layer})

    def add_hatched_zone(x1, y1, x2, y2, layer, pattern="ANSI31", scale=10.0, color=8):
        pts = [(x1, cy(y1)), (x2, cy(y1)), (x2, cy(y2)), (x1, cy(y2)), (x1, cy(y1))]
        msp.add_lwpolyline(pts, dxfattribs={"layer": layer})
        hatch = msp.add_hatch(color=color, dxfattribs={"layer": layer})
        hatch.set_pattern_fill(pattern, scale=scale)
        hatch.paths.add_polyline_path(pts[:-1], is_closed=True)

    def add_filled_column(x1, y1, x2, y2):
        add_hatched_zone(x1, y1, x2, y2, layer="COLUMNS_STRUCTURAL", pattern="ANSI31", scale=4.0, color=1)

    def add_door(hinge_x, hinge_y, width, angle_start, angle_end, leaf_dx, leaf_dy):
        hy_cad = cy(hinge_y)
        msp.add_line((hinge_x, hy_cad), (hinge_x + leaf_dx, hy_cad + leaf_dy), dxfattribs={"layer": "DOORS"})
        msp.add_arc(
            center=(hinge_x, hy_cad),
            radius=width,
            start_angle=angle_start,
            end_angle=angle_end,
            dxfattribs={"layer": "DOORS"},
        )

    def add_window(x1, y1, x2, y2, thickness=14):
        cx1, cy1 = x1, cy(y1)
        cx2, cy2 = x2, cy(y2)
        if y1 == y2:
            msp.add_line((cx1, cy1), (cx2, cy2), dxfattribs={"layer": "WINDOWS"})
            msp.add_line((cx1, cy1 + thickness / 2), (cx2, cy2 + thickness / 2), dxfattribs={"layer": "WINDOWS"})
            msp.add_line((cx1, cy1 - thickness / 2), (cx2, cy2 - thickness / 2), dxfattribs={"layer": "WINDOWS"})
        else:
            msp.add_line((cx1, cy1), (cx2, cy2), dxfattribs={"layer": "WINDOWS"})
            msp.add_line((cx1 + thickness / 2, cy1), (cx2 + thickness / 2, cy2), dxfattribs={"layer": "WINDOWS"})
            msp.add_line((cx1 - thickness / 2, cy1), (cx2 - thickness / 2, cy2), dxfattribs={"layer": "WINDOWS"})

    # 1. Outer Perimeter Footprint
    outer_pts = [
        (0, cy(0)),
        (805, cy(0)),
        (805, cy(660)),
        (1210, cy(660)),
        (1210, cy(1180)),
        (0, cy(1180)),
        (0, cy(0)),
    ]
    msp.add_lwpolyline(outer_pts, dxfattribs={"layer": "WALLS_EXTERIOR"})

    # 2. Room Boundaries (Partitions)
    add_wall_rect(240, 0, 250, 240, layer="WALLS_INTERIOR")
    add_wall_rect(240, 330, 250, 355, layer="WALLS_INTERIOR")
    add_wall_rect(240, 465, 250, 670, layer="WALLS_INTERIOR")
    add_wall_rect(240, 750, 250, 760, layer="WALLS_INTERIOR")
    add_wall_rect(0, 350, 245, 360, layer="WALLS_INTERIOR")
    add_wall_rect(0, 460, 245, 470, layer="WALLS_INTERIOR")
    add_wall_rect(135, 355, 145, 465, layer="WALLS_INTERIOR")
    add_wall_rect(0, 755, 245, 765, layer="WALLS_INTERIOR")

    # Lightwell Shaft (منور)
    add_hatched_zone(0, 355, 140, 465, layer="SHAFT_HATCH", pattern="ANSI37", scale=8.0, color=3)

    # Reception & Stairwell
    add_wall_rect(417, 383, 690, 393, layer="WALLS_INTERIOR")
    add_wall_rect(790, 383, 805, 393, layer="WALLS_INTERIOR")
    add_hatched_zone(422, 388, 805, 660, layer="STAIRWELL_HATCH", pattern="ANSI31", scale=14.0, color=9)
    add_wall_rect(417, 388, 427, 660, layer="WALLS_INTERIOR")
    add_wall_rect(422, 655, 865, 665, layer="WALLS_INTERIOR")

    # Horizontal Corridor & Bottom Row Dividers (Salon 0..422, Kids 422..865, Master 865..1210)
    add_wall_rect(245, 755, 285, 765, layer="WALLS_INTERIOR")
    add_wall_rect(372, 755, 585, 765, layer="WALLS_INTERIOR")
    add_wall_rect(675, 755, 865, 765, layer="WALLS_INTERIOR")
    add_wall_rect(417, 760, 427, 1180, layer="WALLS_INTERIOR")
    add_wall_rect(860, 660, 870, 1180, layer="WALLS_INTERIOR")

    # Gypsum Ceiling Trays
    for gx1, gy1, gx2, gy2 in [
        (280, 35, 770, 353),
        (35, 795, 387, 1145),
        (457, 795, 830, 1145),
        (900, 695, 1175, 1145),
    ]:
        add_wall_rect(gx1, gy1, gx2, gy2, layer="GYPSUM_CEILING")

    # Stepped Balcony
    balc_pts = [
        (805, cy(0)),
        (895, cy(0)),
        (895, cy(570)),
        (1300, cy(570)),
        (1300, cy(1180)),
        (1210, cy(1180)),
        (1210, cy(660)),
        (805, cy(660)),
        (805, cy(0)),
    ]
    msp.add_lwpolyline(balc_pts, dxfattribs={"layer": "BALCONY"})

    # 3. Structural Columns
    columns = [
        (100, 465, 140, 485),
        (350, 1170, 390, 1180),
        (422, 920, 434, 960),
        (850, 920, 865, 966),
        (1198, 760, 1210, 815),
        (1167, 1155, 1210, 1180),
    ]
    for x1, y1, x2, y2 in columns:
        add_filled_column(x1, y1, x2, y2)

    # 4. Doors & Windows
    add_door(690, 388, 100, 0, 90, 0, 100)     # Main Door
    add_door(245, 240, 90, 180, 270, -90, 0)   # Kitchen Door
    add_door(245, 670, 80, 180, 270, -80, 0)   # Bathroom Door
    add_door(285, 760, 87, 270, 360, 0, -87)   # Salon Door
    add_door(585, 760, 90, 270, 360, 0, -90)   # Kids Door
    add_door(865, 666, 87, 270, 360, 87, 0)    # Master Door
    add_door(1210, 665, 90, 180, 270, -90, 0)  # Balcony Door

    add_window(40, 355, 100, 355)
    add_window(45, 465, 95, 465)
    add_window(805, 100, 805, 280)
    add_window(805, 480, 805, 570)
    add_window(135, 1180, 285, 1180)
    add_window(560, 1180, 730, 1180)
    add_window(980, 1180, 1100, 1180)

    # 4B. Engineer's Kitchen CAD Layout & Contract Furniture Blocks
    def add_furn_box(x1, y1, x2, y2, label="", layer="FURNITURE", th=6.5, rot=0):
        pts = [(x1, cy(y1)), (x2, cy(y1)), (x2, cy(y2)), (x1, cy(y2)), (x1, cy(y1))]
        msp.add_lwpolyline(pts, dxfattribs={"layer": layer})
        if label:
            t = msp.add_text(label, dxfattribs={"layer": layer, "height": th, "rotation": rot})
            t.set_placement(((x1 + x2) / 2.0, cy((y1 + y2) / 2.0)), align=TextEntityAlignment.MIDDLE_CENTER)

    # Kitchen West, North & East Walls
    add_furn_box(8, 315, 66, 348, "دولاب تنظيف", "KITCHEN_CAD", 5.5)
    add_furn_box(8, 256, 66, 315, "أجهزة ومايكرويف", "KITCHEN_CAD", 5.5)
    add_furn_box(8, 218, 66, 256, "تربو", "KITCHEN_CAD", 5.5)
    add_furn_box(8, 158, 68, 218, "غسالة بيكو 60x60", "KITCHEN_CAD", 5.5)
    add_furn_box(8, 94, 66, 158, "حوض مطبخ", "KITCHEN_CAD", 5.5)
    add_wall_rect(16, 104, 56, 148, "FURNITURE_DETAIL")
    msp.add_circle((36, cy(126)), 3.5, dxfattribs={"layer": "FURNITURE_DETAIL"})
    add_furn_box(8, 58, 66, 94, "3 درج", "KITCHEN_CAD", 5.5)
    add_furn_box(8, 8, 66, 58, "خزين ركنة", "KITCHEN_CAD", 5.5)
    add_furn_box(66, 8, 152, 68, "بوتاجاز 6 شعلة + شفاط", "KITCHEN_CAD", 5.5)
    for bx in (86, 109, 132):
        for by in (24, 48):
            msp.add_circle((bx, cy(by)), 5.5, dxfattribs={"layer": "FURNITURE_DETAIL"})
    add_furn_box(152, 8, 182, 66, "ترول زيت", "KITCHEN_CAD", 5.0)
    add_furn_box(182, 8, 238, 66, "وحدة خزين", "KITCHEN_CAD", 5.5)
    add_furn_box(182, 66, 238, 114, "وحدة خزين", "KITCHEN_CAD", 5.5)
    add_furn_box(178, 114, 238, 162, "فريزر أفقي", "KITCHEN_CAD", 5.5)
    add_furn_box(174, 162, 238, 212, "ثلاجة", "KITCHEN_CAD", 5.5)
    add_furn_box(192, 212, 238, 238, "نيش", "KITCHEN_CAD", 5.5)

    for dy_ref, off_x in [(165, -24), (245, -48)]:
        d_k = msp.add_linear_dim(
            base=(off_x, 0),
            p1=(0, cy(355)),
            p2=(0, cy(355 - dy_ref)),
            angle=90,
            dimstyle="Standard",
            override={"dimtxt": 11, "dimasz": 7},
            dxfattribs={"layer": "DIMENSIONS"},
        )
        d_k.render()

    # Washer, Bathroom & Entry
    add_furn_box(152, 380, 212, 440, "غسالة ملابس", "FURNITURE", 5.5)
    msp.add_circle((182, cy(410)), 16, dxfattribs={"layer": "FURNITURE_DETAIL"})
    add_furn_box(115, 472, 180, 518, "حوض", "FURNITURE", 5.5)
    add_furn_box(18, 550, 68, 605, "WC", "FURNITURE", 5.5)
    add_furn_box(12, 675, 147, 747, "شاور / بانيو", "FURNITURE", 6.5)
    add_furn_box(376, 475, 414, 575, "جزامة", "FURNITURE", 6.0, rot=90)

    # Reception (الصالة): ركنة عمولة + سفرة زمردة
    add_furn_box(450, 10, 795, 98, "ركنة عمولة 4م (البا 5)")
    add_furn_box(705, 98, 795, 230, "ركنة 2.20م", rot=90)
    add_furn_box(535, 125, 635, 185, "ترابيزة ركنة", "FURNITURE", 6.0)
    add_furn_box(440, 334, 620, 379, "بوفيه زمردة 2م")
    add_furn_box(255, 12, 350, 56, "نيش 1م", "FURNITURE", 6.0)
    add_furn_box(315, 95, 405, 270, "سفرة زمردة 180x90", rot=90)
    for cy_chair in (113, 165, 217):
        add_wall_rect(293, cy_chair, 313, cy_chair + 34, "FURNITURE_DETAIL")
        add_wall_rect(407, cy_chair, 427, cy_chair + 34, "FURNITURE_DETAIL")

    # Salon (الصالون x=0..422): انترية كريمة + ترابيزة دهبي
    add_furn_box(12, 820, 94, 1030, "كنبة 2.20م (تيد 5)", rot=90)
    add_furn_box(328, 820, 410, 1030, "كنبة 2.20م (تيد 3)", rot=90)
    add_furn_box(32, 1072, 110, 1150, "فوتيه 1", "FURNITURE", 6.0)
    add_furn_box(312, 1072, 390, 1150, "فوتيه 2", "FURNITURE", 6.0)
    msp.add_circle((194, cy(938)), 27, dxfattribs={"layer": "FURNITURE"})
    msp.add_circle((236, cy(962)), 25, dxfattribs={"layer": "FURNITURE"})

    # Kids Room (أطفال خفرع x=422..865)
    add_furn_box(675, 768, 855, 828, "دولاب أطفال 2م")
    add_furn_box(432, 772, 477, 812, "مراية", "FURNITURE", 5.5)
    add_furn_box(432, 835, 480, 935, "تسريحة خفرع", "FURNITURE", 5.5, rot=90)
    add_furn_box(485, 965, 605, 1168, "سرير 120سم (1)")
    add_wall_rect(505, 1125, 585, 1155, "FURNITURE_DETAIL")
    add_furn_box(625, 1118, 675, 1168, "كمود", "FURNITURE", 5.5)
    add_furn_box(695, 965, 815, 1168, "سرير 120سم (2)")
    add_wall_rect(715, 1125, 795, 1155, "FURNITURE_DETAIL")

    # Master Bedroom (نوم بلازا)
    add_furn_box(872, 865, 932, 1165, "دولاب بلازا 3م (6 ضلف)", rot=90)
    msp.add_line((872, cy(1015)), (932, cy(1015)), dxfattribs={"layer": "FURNITURE_DETAIL"})
    add_furn_box(995, 880, 1202, 1050, "سرير ميكانزم 160سم")
    add_wall_rect(1158, 895, 1188, 955, "FURNITURE_DETAIL")
    add_wall_rect(1158, 975, 1188, 1035, "FURNITURE_DETAIL")
    add_furn_box(1154, 825, 1202, 875, "كمود 50سم", "FURNITURE", 5.0)
    add_furn_box(1154, 1055, 1202, 1105, "كمود 50سم", "FURNITURE", 5.0)
    add_furn_box(985, 668, 1105, 714, "تسريحة بلازا", "FURNITURE", 6.0)
    msp.add_circle((1045, cy(739)), 19, dxfattribs={"layer": "FURNITURE"})
    add_furn_box(875, 765, 925, 810, "مراية نص دايرة", "FURNITURE", 5.0)

    # Utilities
    for ux, uy, ulbl in [
        (264, 205, "GAS METER"),
        (402, 420, "ELEC PANEL"),
        (192, 452, "DRAIN"),
        (212, 482, "HEATER"),
    ]:
        msp.add_circle((ux, cy(uy)), 10, dxfattribs={"layer": "UTILITIES"})
        ut = msp.add_text(ulbl, dxfattribs={"layer": "UTILITIES", "height": 5.5})
        ut.set_placement((ux, cy(uy) - 16), align=TextEntityAlignment.MIDDLE_CENTER)

    # 5. Room Labels
    labels = [
        (122, 177, "KITCHEN (المطبخ)\n245 x 465 cm | 11.39 m2"),
        (70, 410, "SHAFT (منور)\n50 x 46 cm"),
        (192, 410, "WASHER\n80 x 105 cm"),
        (122, 612, "BATHROOM (الحمام)\n240 x 195 cm | 4.68 m2"),
        (525, 194, "RECEPTION (الصالة)\n560 x 470 cm | 26.32 m2"),
        (613, 524, "STAIRWELL (بئر السلم)\n272 x 425 cm"),
        (315, 435, "ENTRY CORRIDOR\n260 x 177 cm"),
        (555, 710, "CORRIDOR (الطرقة) 575 x 100 cm"),
        (211, 970, "SALON (الصالون)\n380 x 345 cm | 13.20 m2"),
        (643, 970, "KIDS BEDROOM (أطفال)\n420 x 350 cm | 14.70 m2"),
        (1037, 920, "MASTER BEDROOM (الماستر)\n350 x 470 cm | 15.20 m2"),
        (1255, 920, "BALCONY\n90 cm"),
    ]
    for lx, ly, txt in labels:
        lines = txt.split("\n")
        for idx, line in enumerate(lines):
            t = msp.add_text(
                line,
                dxfattribs={"layer": "LABELS", "height": 18 if idx == 0 else 13},
            )
            t.set_placement((lx, cy(ly) - idx * 24), align=TextEntityAlignment.MIDDLE_CENTER)

    # 6. Exterior Overall Dimensions
    for base_pt, p1, p2, ang in [
        ((0, cy(-70)), (0, cy(0)), (895, cy(0)), 0),
        ((0, cy(1250)), (0, cy(1180)), (1300, cy(1180)), 0),
        ((1360, 0), (1300, cy(1180)), (1300, cy(570)), 90),
        ((-70, 0), (0, cy(1180)), (0, cy(0)), 90),
    ]:
        dim_obj = msp.add_linear_dim(
            base=base_pt,
            p1=p1,
            p2=p2,
            angle=ang,
            dimstyle="Standard",
            override={"dimtxt": 22, "dimasz": 12},
            dxfattribs={"layer": "DIMENSIONS"},
        )
        dim_obj.render()

    doc.saveas(DXF_PATH)
    print(f"SUCCESS: Saved upgraded CAD DXF to {DXF_PATH}")


if __name__ == "__main__":
    create_apartment_dxf()

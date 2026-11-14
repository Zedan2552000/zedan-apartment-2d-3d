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
        ("STAIRWELL_HATCH", 9, 18),
        ("SHAFT_HATCH", 3, 20),
        ("UTILITIES", 3, 20),
        ("KITCHEN_CAD", 140, 20),
        ("FURNITURE", 42, 20),
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

    # 1. Outer Perimeter Footprint (Full West Wall x=0 from y=0..1180)
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

    # 2. Room Boundaries (Centerlines / Partitions)
    # Left Service Wing (x=0..245): Kitchen (0..355), Shaft+Washer (355..465), Bathroom (465..760)
    add_wall_rect(240, 0, 250, 240, layer="WALLS_INTERIOR")    # Kitchen East wall above door
    add_wall_rect(240, 330, 250, 355, layer="WALLS_INTERIOR")  # Kitchen East wall below door
    add_wall_rect(240, 465, 250, 670, layer="WALLS_INTERIOR")  # Bath East wall closed above door
    add_wall_rect(240, 750, 250, 760, layer="WALLS_INTERIOR")  # Bath East wall south pier
    add_wall_rect(0, 350, 245, 360, layer="WALLS_INTERIOR")
    add_wall_rect(0, 460, 245, 470, layer="WALLS_INTERIOR")
    add_wall_rect(135, 355, 145, 465, layer="WALLS_INTERIOR")  # Shaft / Washer divider
    add_wall_rect(0, 755, 245, 765, layer="WALLS_INTERIOR")    # Bathroom / Salon divider

    # Lightwell Shaft (منور): x=0..140, y=355..465
    add_hatched_zone(0, 355, 140, 465, layer="SHAFT_HATCH", pattern="ANSI37", scale=8.0, color=3)

    # Reception (الصالة): x=245..805, y=0..388 (with open archway to vertical corridor at x=245..422)
    add_wall_rect(417, 383, 690, 393, layer="WALLS_INTERIOR")
    add_wall_rect(790, 383, 805, 393, layer="WALLS_INTERIOR")

    # Stairwell (بئر السلم): x=422..805, y=388..660
    add_hatched_zone(422, 388, 805, 660, layer="STAIRWELL_HATCH", pattern="ANSI31", scale=14.0, color=9)
    add_wall_rect(417, 388, 427, 660, layer="WALLS_INTERIOR")
    add_wall_rect(422, 655, 865, 665, layer="WALLS_INTERIOR")

    # Horizontal Corridor (الطرقة): x=245..865, y=660..760 (openings for Salon 285..372 & Kids 585..675)
    add_wall_rect(245, 755, 285, 765, layer="WALLS_INTERIOR")
    add_wall_rect(372, 755, 585, 765, layer="WALLS_INTERIOR")
    add_wall_rect(675, 755, 865, 765, layer="WALLS_INTERIOR")

    # Bottom Row Rooms (y=760..1180): Salon (0..555), Kids (555..865), Master (865..1210, y=660..1180)
    add_wall_rect(550, 760, 560, 1180, layer="WALLS_INTERIOR")
    add_wall_rect(860, 660, 870, 1180, layer="WALLS_INTERIOR")

    # Right-Side Stepped Balcony (البلكونة)
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
        (100, 465, 140, 485),    # Bath Column 20x40
        (470, 1170, 510, 1180),  # Salon South Column 40x10
        (555, 920, 567, 960),    # Kids West 40x10
        (850, 920, 865, 966),    # Kids East 46x15
        (1198, 760, 1210, 815),  # Master East 55x10
        (1167, 1155, 1210, 1180),# Master Corner 43x25
    ]
    for x1, y1, x2, y2 in columns:
        add_filled_column(x1, y1, x2, y2)

    # 4. Doors & Windows
    # Main Door (100 cm) on South wall of Reception at y=388, x=690..790
    add_door(690, 388, 100, 0, 90, 0, 100)
    # Kitchen Door (90 cm) on East wall at x=245, y=240..330
    add_door(245, 240, 90, 180, 270, -90, 0)
    # Bathroom Door (80 cm) on East wall at x=245, y=670..750
    add_door(245, 670, 80, 180, 270, -80, 0)
    # Salon Door (87 cm) on North wall at y=760, x=285..372
    add_door(285, 760, 87, 270, 360, 0, -87)
    # Kids Door (90 cm) on North wall at y=760, x=585..675
    add_door(585, 760, 90, 270, 360, 0, -90)
    # Master Entrance Door (87 cm) on West wall at x=865, y=666..753
    add_door(865, 666, 87, 270, 360, 87, 0)
    # Master Balcony Door (90 cm) on East wall at x=1210, y=665..755
    add_door(1210, 665, 90, 180, 270, -90, 0)

    # Windows
    add_window(40, 355, 100, 355)      # Kitchen Shaft Window 60 cm
    add_window(45, 465, 95, 465)       # Bath Shaft Window 50 cm
    add_window(805, 100, 805, 280)     # Reception Balcony Window 180 cm
    add_window(805, 480, 805, 570)     # Stairwell Window 90 cm
    add_window(200, 1180, 350, 1180)   # Salon South Window 150 cm
    add_window(625, 1180, 795, 1180)   # Kids South Window 170 cm
    add_window(980, 1180, 1100, 1180)  # Master South Window 120 cm

    # 4B. Engineer's Kitchen CAD Layout (kit.m2.pdf + Beko 14-place Dishwasher 60x60) & PDF Furniture
    def add_furn_box(x1, y1, x2, y2, label="", layer="FURNITURE", th=7):
        pts = [(x1, cy(y1)), (x2, cy(y1)), (x2, cy(y2)), (x1, cy(y2)), (x1, cy(y1))]
        msp.add_lwpolyline(pts, dxfattribs={"layer": layer})
        if label:
            t = msp.add_text(label, dxfattribs={"layer": layer, "height": th})
            t.set_placement(((x1 + x2) / 2.0, cy((y1 + y2) / 2.0)), align=TextEntityAlignment.MIDDLE_CENTER)

    # Kitchen West Wall (x=8..66, South-to-North):
    add_furn_box(8, 315, 66, 348, "دولاب تنظيف", "KITCHEN_CAD", 6)
    add_furn_box(8, 256, 66, 315, "دولاب خزين ومايكرويف", "KITCHEN_CAD", 6)
    add_furn_box(8, 218, 66, 256, "تربو", "KITCHEN_CAD", 6)
    add_furn_box(8, 158, 68, 218, "غسالة اطباق بيكو 60x60", "KITCHEN_CAD", 6)
    add_furn_box(8, 94, 66, 158, "حوض مطبخ", "KITCHEN_CAD", 6)
    add_furn_box(8, 58, 66, 94, "3 درج", "KITCHEN_CAD", 6)
    add_furn_box(8, 8, 66, 58, "خزين ركنة", "KITCHEN_CAD", 6)
    # Kitchen North Wall (y=8..68):
    add_furn_box(66, 8, 152, 68, "بوتاجاز 6 شعلة + شفاط", "KITCHEN_CAD", 6)
    add_furn_box(152, 8, 182, 66, "ترول زيت", "KITCHEN_CAD", 5.5)
    add_furn_box(182, 8, 238, 66, "وحدة خزين", "KITCHEN_CAD", 6)
    # Kitchen East Wall (x=174..238, y=66..238):
    add_furn_box(182, 66, 238, 114, "وحدة خزين", "KITCHEN_CAD", 6)
    add_furn_box(178, 114, 238, 162, "فريزر افقي", "KITCHEN_CAD", 6)
    add_furn_box(174, 162, 238, 212, "ثلاجة", "KITCHEN_CAD", 6)
    add_furn_box(192, 212, 238, 238, "نيش", "KITCHEN_CAD", 6)

    # Kitchen 165 & 245 cm reference dimensions from South wall (y=355)
    for dy_ref, off_x, txt_dim in [(165, -24, "165"), (245, -48, "245")]:
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

    # Washer Alcove & Bathroom Fixtures
    add_furn_box(152, 380, 212, 440, "غسالة ملابس", "FURNITURE", 6)
    add_furn_box(115, 472, 180, 518, "حوض", "FURNITURE", 6)
    add_furn_box(18, 550, 68, 605, "WC", "FURNITURE", 6)
    add_furn_box(12, 675, 147, 747, "شاور / بانيو", "FURNITURE", 7)
    add_furn_box(376, 475, 414, 575, "جزامة", "FURNITURE", 6.5)

    # Reception (الصالة): ركنة عمولة 4م × 2.20م + سفرة زمردة
    add_furn_box(450, 10, 795, 98, "ركنة عمولة 4م (البا 5)")
    add_furn_box(705, 98, 795, 230, "ركنة 2.20م")
    add_furn_box(535, 125, 635, 185, "ترابيزة ركنة", "FURNITURE", 6)
    add_furn_box(255, 10, 435, 55, "بوفيه زمردة 2م")
    add_furn_box(253, 65, 298, 160, "نيش 1م", "FURNITURE", 6.5)
    add_furn_box(295, 110, 465, 200, "سفرة 180x90 + 6 كراسي")

    # Salon (الصالون): انترية كريمة + ترابيزة دهبي
    add_furn_box(12, 850, 98, 1070, "كنبة 2.20م (تيد 5 طوبي)")
    add_furn_box(455, 850, 542, 1070, "كنبة 2.20م (تيد 3 كريمي)")
    add_furn_box(155, 1075, 238, 1158, "فوتيه 1", "FURNITURE", 6.5)
    add_furn_box(315, 1075, 398, 1158, "فوتيه 2", "FURNITURE", 6.5)
    add_furn_box(225, 925, 325, 1005, "ترابيزة متداخلة", "FURNITURE", 6.5)

    # Kids Room (أطفال خفرع)
    add_furn_box(680, 768, 855, 828, "دولاب أطفال 2م")
    add_furn_box(563, 772, 605, 812, "مراية", "FURNITURE", 5.5)
    add_furn_box(563, 855, 610, 950, "تسريحة خفرع", "FURNITURE", 6)
    add_furn_box(568, 965, 688, 1168, "سرير 120سم (1)")
    add_furn_box(688, 1120, 734, 1168, "كمود", "FURNITURE", 5.5)
    add_furn_box(734, 965, 854, 1168, "سرير 120سم (2)")

    # Master Bedroom (نوم بلازا)
    add_furn_box(872, 795, 932, 1095, "دولاب بلازا 3م (6 ضلف)")
    add_furn_box(995, 880, 1202, 1050, "سرير ميكانزم 160سم")
    add_furn_box(1154, 825, 1202, 875, "كمود 50سم", "FURNITURE", 5.5)
    add_furn_box(1154, 1055, 1202, 1105, "كمود 50سم", "FURNITURE", 5.5)
    add_furn_box(985, 668, 1105, 714, "تسريحة بلازا", "FURNITURE", 6.5)
    add_furn_box(1025, 720, 1065, 758, "بف", "FURNITURE", 5.5)
    add_furn_box(878, 1120, 928, 1165, "مراية نص دايرة", "FURNITURE", 5.5)

    # 5. Room Labels
    labels = [
        (122, 177, "KITCHEN (المطبخ)\n245 x 465 cm | 11.39 m2"),
        (70, 410, "SHAFT (منور)\n50 x 46 cm"),
        (192, 410, "WASHER\n80 x 105 cm"),
        (122, 612, "BATHROOM (الحمام)\n240 x 195 cm | 4.68 m2"),
        (525, 194, "RECEPTION (الصالة)\n560 x 470 cm | 26.32 m2"),
        (613, 524, "STAIRWELL (بئر السلم)\n272 x 425 cm"),
        (333, 507, "ENTRY CORRIDOR\n260 x 177 cm"),
        (555, 710, "CORRIDOR (الطرقة) 575 x 100 cm"),
        (277, 970, "SALON (الصالون)\n380 x 345 cm | 13.20 m2"),
        (710, 970, "KIDS BEDROOM (أطفال)\n420 x 350 cm | 14.70 m2"),
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
    dim_top = msp.add_linear_dim(
        base=(0, cy(-70)),
        p1=(0, cy(0)),
        p2=(895, cy(0)),
        dimstyle="Standard",
        override={"dimtxt": 22, "dimasz": 12},
        dxfattribs={"layer": "DIMENSIONS"},
    )
    dim_top.render()

    dim_bot = msp.add_linear_dim(
        base=(0, cy(1250)),
        p1=(0, cy(1180)),
        p2=(1300, cy(1180)),
        dimstyle="Standard",
        override={"dimtxt": 22, "dimasz": 12},
        dxfattribs={"layer": "DIMENSIONS"},
    )
    dim_bot.render()

    dim_right = msp.add_linear_dim(
        base=(1360, 0),
        p1=(1300, cy(1180)),
        p2=(1300, cy(570)),
        angle=90,
        dimstyle="Standard",
        override={"dimtxt": 22, "dimasz": 12},
        dxfattribs={"layer": "DIMENSIONS"},
    )
    dim_right.render()

    dim_left = msp.add_linear_dim(
        base=(-70, 0),
        p1=(0, cy(1180)),
        p2=(0, cy(0)),
        angle=90,
        dimstyle="Standard",
        override={"dimtxt": 22, "dimasz": 12},
        dxfattribs={"layer": "DIMENSIONS"},
    )
    dim_left.render()

    doc.saveas(DXF_PATH)
    print(f"SUCCESS: Saved updated CAD DXF to {DXF_PATH}")


if __name__ == "__main__":
    create_apartment_dxf()

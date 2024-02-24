from __future__ import annotations

import logging
from enum import Enum, auto
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from build123d import Box, Part
from gridfinity_build123d import (
    Base,
    BaseEqual,
    BasePlate,
    BasePlateBlockFull,
    BasePlateBlockSkeleton,
    BasePlateEqual,
    Bin,
    BottomCorners,
    BottomMiddle,
    Compartment,
    CompartmentsEqual,
    HoleFeature,
    Label,
    MagnetHole,
    ScrewHole,
    ScrewHoleCounterbore,
    ScrewHoleCountersink,
    StackingLip,
    TopCorners,
    TopMiddle,
    Weighted,
)
from gridfinity_build123d.feature_locations import FeatureLocation


class CameraPosition(Enum):
    CAMERA_TOP = auto()
    CAMERA_BOT = auto()

    @staticmethod
    def pos_to_str(pos: CameraPosition) -> str:
        if pos == CameraPosition.CAMERA_TOP:
            return "0,0,0,55,0,25,0"
        if pos == CameraPosition.CAMERA_BOT:
            return "0,0,0,125,0,25,0"
        msg = "Unknown camera position"
        raise ValueError(msg)


class Convert:
    @staticmethod
    def part_to_png(part: Part, file_name: str, camera_pos: CameraPosition) -> None:
        with TemporaryDirectory() as tmp_dir:
            Convert._part_to_png(part, Path(tmp_dir), file_name, camera_pos)

    @staticmethod
    def parts_to_gif(
        part_list: list[Part],
        file_name: str,
        camera_pos: CameraPosition,
    ) -> None:
        with TemporaryDirectory() as tmp_dir:
            for idx, part in enumerate(part_list):
                Convert._part_to_png(
                    part,
                    Path(tmp_dir),
                    str(Path(tmp_dir).joinpath(f"{idx}")),
                    camera_pos,
                )
            check_call(
                [
                    "/usr/bin/convert",
                    "-delay",
                    "75",
                    "-loop",
                    "0",
                    tmp_dir + "/*.png",
                    f"{file_name}.gif",
                ],
            )
            file_path = Path(file_name + ".gif").resolve()
            logging.info("gif written to %s", file_path)

    @staticmethod
    def _part_to_png(
        part: Part,
        work_dir: Path,
        file_name: str,
        camera_pos: CameraPosition,
    ) -> None:
        tmp_stl = work_dir.joinpath("tmp.stl")
        tmp_scad = work_dir.joinpath("tmp.scad")
        part.export_stl(str(tmp_stl))
        with tmp_scad.open("w") as file:
            file.write(f'import("{tmp_stl}");\n')

        check_call(
            [
                "/usr/bin/openscad",
                "--autocenter",
                "--viewall",
                "--camera",
                CameraPosition.pos_to_str(camera_pos),
                "-o",
                file_name + ".png",
                "--imgsize=720,720",
                "--colorscheme",
                "BeforeDawn",
                tmp_scad.resolve(),
            ],
        )

        file_path = Path(file_name + ".png").resolve()
        logging.info("Image written to %s", file_path)

        tmp_stl.unlink()
        tmp_scad.unlink()


###########
# Objects #
###########

# Bases

Convert.part_to_png(Base([[True, True], [True]]), "base", CameraPosition.CAMERA_BOT)
Convert.part_to_png(BaseEqual(2, 2), "base_equal", CameraPosition.CAMERA_BOT)
Convert.part_to_png(
    BaseEqual(
        2,
        2,
        [MagnetHole(BottomCorners()), ScrewHole(BottomCorners())],
    ),
    "base_holes",
    CameraPosition.CAMERA_BOT,
)

# Bins
Convert.part_to_png(Bin(Base(), height_in_units=4), "bin", CameraPosition.CAMERA_TOP)

Convert.part_to_png(
    Bin(
        Base(),
        height_in_units=4,
        compartments=CompartmentsEqual(
            div_x=2,
            compartment_list=Compartment(Label()),
        ),
    ),
    "bin_compartment",
    CameraPosition.CAMERA_TOP,
)

Convert.part_to_png(
    Bin(
        Base(),
        height_in_units=4,
        compartments=CompartmentsEqual(
            div_x=2,
            compartment_list=Compartment(Label()),
        ),
        lip=StackingLip(),
    ),
    "bin_lip",
    CameraPosition.CAMERA_TOP,
)

# Baseplates
Convert.part_to_png(
    BasePlate([[True, True], [True]]),
    "base_plate",
    CameraPosition.CAMERA_TOP,
)
Convert.part_to_png(BasePlateEqual(2, 2), "base_plate_equal", CameraPosition.CAMERA_TOP)
Convert.part_to_png(
    BasePlateEqual(2, 2, BasePlateBlockFull()),
    "base_plate_full",
    CameraPosition.CAMERA_TOP,
)
Convert.part_to_png(
    BasePlateEqual(
        2,
        2,
        BasePlateBlockFull(
            features=[
                ScrewHoleCountersink(BottomCorners()),
                Weighted(BottomMiddle()),
            ],
        ),
    ),
    "base_plate_weigthed",
    CameraPosition.CAMERA_BOT,
)


############
# Features #
############
f_loc_mock = MagicMock(spec=FeatureLocation)

Convert.part_to_png(
    Box(3, 3, 3) - HoleFeature(f_loc_mock, 1, 2).create_obj(),
    "hole_feature",
    CameraPosition.CAMERA_TOP,
)

Convert.part_to_png(
    Box(4, 4, 3) - ScrewHole(f_loc_mock).create_obj(),
    "screw_hole",
    CameraPosition.CAMERA_TOP,
)

Convert.part_to_png(
    Box(8, 8, 4) - MagnetHole(f_loc_mock).create_obj(),
    "magnet_hole",
    CameraPosition.CAMERA_TOP,
)

Convert.part_to_png(
    Box(10, 10, 4) - ScrewHoleCountersink(f_loc_mock).create_obj(),
    "countersink",
    CameraPosition.CAMERA_TOP,
)

Convert.part_to_png(
    Box(8, 8, 4) - ScrewHoleCounterbore(f_loc_mock, counter_bore_depth=0).create_obj(),
    "counterbore",
    CameraPosition.CAMERA_TOP,
)

Convert.part_to_png(
    Weighted(f_loc_mock).create_obj(),
    "weigthed",
    CameraPosition.CAMERA_TOP,
)

Convert.part_to_png(
    Bin(
        Base(),
        height_in_units=4,
        compartments=CompartmentsEqual(
            compartment_list=Compartment(Label()),
        ),
    ),
    "label",
    CameraPosition.CAMERA_TOP,
)

obj = Base(
    features=[
        MagnetHole(feature_location=TopCorners()),
        ScrewHoleCountersink(feature_location=TopMiddle()),
        ScrewHoleCounterbore(feature_location=BottomCorners()),
        Weighted(feature_location=BottomMiddle()),  # type: ignore[list-item]
    ],
)
Convert.part_to_png(
    obj,
    "base_feature_rich_top",
    CameraPosition.CAMERA_TOP,
)

Convert.part_to_png(
    obj,
    "base_feature_rich_bot",
    CameraPosition.CAMERA_BOT,
)

########
# Gifs #
########

# Baseplate

Convert.parts_to_gif(
    [
        BasePlate([[True]]),
        BasePlate([[True, True]]),
        BasePlate([[True, True, True]]),
        BasePlate([[True, True, True], [True]]),
        BasePlate([[True, True, True], [True, True]]),
        BasePlate([[True, True, True], [True, True], [True]]),
        BasePlate(
            [[True, True, True], [True, True], [True]],
            BasePlateBlockSkeleton(features=MagnetHole(TopCorners())),
        ),
        BasePlate(
            [[True, True, True], [True, True], [True]],
            BasePlateBlockFull(features=MagnetHole(TopCorners())),
        ),
    ],
    "baseplate",
    CameraPosition.CAMERA_TOP,
)

# Bin

Convert.parts_to_gif(
    [
        Bin(
            BaseEqual(),
            height_in_units=2,
            compartments=CompartmentsEqual(Compartment()),
        ),
        Bin(
            BaseEqual(),
            height_in_units=3,
            compartments=CompartmentsEqual(Compartment()),
        ),
        Bin(
            BaseEqual(),
            height_in_units=4,
            compartments=CompartmentsEqual(Compartment()),
        ),
        Bin(
            BaseEqual(),
            height_in_units=4,
            compartments=CompartmentsEqual(Compartment(Label())),
        ),
        Bin(
            BaseEqual(),
            height_in_units=4,
            compartments=CompartmentsEqual(Compartment(Label())),
            lip=StackingLip(),
        ),
        Bin(
            BaseEqual(),
            height_in_units=4,
            compartments=CompartmentsEqual(Compartment(Label()), div_x=2),
            lip=StackingLip(),
        ),
        Bin(
            BaseEqual(),
            height_in_units=4,
            compartments=CompartmentsEqual(Compartment(Label()), div_x=3),
            lip=StackingLip(),
        ),
        Bin(
            BaseEqual(2),
            height_in_units=4,
            compartments=CompartmentsEqual(Compartment(Label()), div_x=6),
            lip=StackingLip(),
        ),
        Bin(
            Base([[True, True], [False, True]]),
            height_in_units=4,
            compartments=CompartmentsEqual(
                Compartment(Label()),
                div_x=6,
                div_y=2,
                inner_wall=2.4,
            ),
            lip=StackingLip(),
        ),
        Bin(
            Base([[True, True], [False, True], [False, True]]),
            height_in_units=4,
            compartments=CompartmentsEqual(
                Compartment(Label()),
                div_x=6,
                div_y=3,
                inner_wall=2.4,
            ),
            lip=StackingLip(),
        ),
    ],
    "bin",
    CameraPosition.CAMERA_TOP,
)

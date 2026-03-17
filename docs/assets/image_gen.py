from __future__ import annotations

import logging
import shutil
from enum import Enum, auto
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

import build123d
from build123d import Box, Compound, Part

from gridfinity_build123d import (
    Base,
    BaseEqual,
    BasePlate,
    BasePlateBlockFull,
    BasePlateBlockSkeleton,
    BasePlateBottomSideRound,
    BasePlateEqual,
    Bin,
    BottomCorners,
    BottomMiddle,
    BottomSides,
    Compartment,
    CompartmentsEqual,
    Direction,
    GridfinityRefinedConnectionCutout,
    GridfinityRefinedMagnetHolePressfit,
    GridfinityRefinedMagnetHoleSide,
    GridfinityRefinedScrewHole,
    GridfinityRefinedThreadedScrewHole,
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

logger = logging.getLogger(__name__)


OPENSCAD_DEFAULT_PATH = "/usr/bin/openscad"
IMAGEMAGICK_DEFAULT_PATH = "/usr/bin/convert"


def resolve_openscad_cmd() -> str:
    """Resolve OpenSCAD executable path for the current developer environment."""
    if Path(OPENSCAD_DEFAULT_PATH).exists():
        return OPENSCAD_DEFAULT_PATH

    # Check if "openscad" is in PATH
    openscad_in_path = shutil.which("openscad")
    if openscad_in_path:
        return openscad_in_path

    msg = "OpenSCAD executable not found. Install 'openscad' in PATH."
    raise FileNotFoundError(msg)


def resolve_imagemagick_cmd() -> str:
    """Resolve ImageMagick executable for GIF generation."""
    if Path(IMAGEMAGICK_DEFAULT_PATH).exists():
        return IMAGEMAGICK_DEFAULT_PATH

    convert_in_path = shutil.which("convert")
    if convert_in_path:
        return convert_in_path

    magick_in_path = shutil.which("magick")
    if magick_in_path:
        return magick_in_path

    msg = "ImageMagick executable not found. Install 'convert'/'magick' in PATH."
    raise FileNotFoundError(msg)


class CameraPosition(Enum):
    CAMERA_TOP = auto()
    CAMERA_BOT = auto()

    @staticmethod
    def pos_to_str(pos: CameraPosition) -> str:
        match pos:
            case CameraPosition.CAMERA_TOP:
                return "0,0,0,55,0,25,0"
            case CameraPosition.CAMERA_BOT:
                return "0,0,0,125,0,25,0"


class Convert:
    @staticmethod
    def part_to_png(part: Compound, file_name: str, camera_pos: CameraPosition) -> None:
        with TemporaryDirectory() as tmp_dir:
            Convert._part_to_png(part, Path(tmp_dir), file_name, camera_pos)

    @staticmethod
    def parts_to_gif(
        part_list: list[Part],
        file_name: str,
        camera_pos: CameraPosition,
    ) -> None:
        imagemagick_cmd = resolve_imagemagick_cmd()
        with TemporaryDirectory() as tmp_dir:
            for idx, part in enumerate(part_list):
                Convert._part_to_png(
                    part,
                    Path(tmp_dir),
                    str(Path(tmp_dir).joinpath(f"{idx}".zfill(3))),
                    camera_pos,
                )
            _ = check_call(
                [
                    imagemagick_cmd,
                    "-delay",
                    "75",
                    "-loop",
                    "0",
                    tmp_dir + "/*.png",
                    f"{file_name}.gif",
                ],
            )
            file_path = Path(file_name + ".gif").resolve()
            logger.info("gif written to %s", file_path)

    @staticmethod
    def _part_to_png(
        part: Compound,
        work_dir: Path,
        file_name: str,
        camera_pos: CameraPosition,
    ) -> None:
        openscad_cmd = resolve_openscad_cmd()
        tmp_stl = work_dir.joinpath("tmp.stl")
        tmp_scad = work_dir.joinpath("tmp.scad")
        _ = build123d.export_stl(part, str(tmp_stl))  # pyright: ignore[reportUnknownMemberType]
        with tmp_scad.open("w") as file:
            _ = file.write(f'import("{tmp_stl}");\n')

        _ = check_call(
            [
                openscad_cmd,
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
        logger.info("Image written to %s", file_path)

        tmp_stl.unlink()
        tmp_scad.unlink()


###########
# Objects #
###########

# Bases

Convert.part_to_png(
    Base(
        grid=[[True, True], [True]],
    ),
    "base",
    CameraPosition.CAMERA_BOT,
)
Convert.part_to_png(
    BaseEqual(
        grid_x=2,
        grid_y=2,
    ),
    "base_equal",
    CameraPosition.CAMERA_BOT,
)
Convert.part_to_png(
    BaseEqual(
        grid_x=2,
        grid_y=2,
        features=[
            MagnetHole(BottomCorners()),
            ScrewHole(BottomCorners()),
        ],
    ),
    "base_holes",
    CameraPosition.CAMERA_BOT,
)

# Bins
Convert.part_to_png(
    Bin(
        Base(),
        height_in_units=4,
    ),
    "bin",
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
    BasePlate(
        grid=[[True, True], [True]],
    ),
    "base_plate",
    CameraPosition.CAMERA_TOP,
)
Convert.part_to_png(
    BasePlateEqual(
        size_x=2,
        size_y=2,
    ),
    "base_plate_equal",
    CameraPosition.CAMERA_TOP,
)
Convert.part_to_png(
    BasePlateEqual(
        size_x=2,
        size_y=2,
        baseplate_block=BasePlateBlockFull(),
    ),
    "base_plate_full",
    CameraPosition.CAMERA_TOP,
)
Convert.part_to_png(
    BasePlateEqual(
        size_x=2,
        size_y=2,
        baseplate_block=BasePlateBlockFull(
            features=[
                ScrewHoleCountersink(BottomCorners()),
                Weighted(BottomMiddle()),
            ],
        ),
    ),
    "base_plate_weighted",
    CameraPosition.CAMERA_BOT,
)
Convert.part_to_png(
    BasePlateEqual(
        size_x=2,
        size_y=2,
        features=BasePlateBottomSideRound(radius=1, direction=Direction.FRONT),
    ),
    "base_plate_bottom_side_round_single",
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
    "weighted",
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
        Weighted(feature_location=BottomMiddle()),
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
        BasePlate(
            [[True, True, True], [True, True], [True]],
            BasePlateBlockFull(bottom_height=3),
        ),
        BasePlate(
            [[True, True, True], [True, True], [True]],
            BasePlateBlockFull(bottom_height=3),
            features=GridfinityRefinedConnectionCutout(BottomSides(nr_x=3, nr_y=3)),
        ),
        BasePlate(
            [[True, True, True], [True, True], [True]],
            BasePlateBlockFull(
                bottom_height=3,
                features=GridfinityRefinedScrewHole(BottomMiddle()),
            ),
            features=GridfinityRefinedConnectionCutout(BottomSides(nr_x=3, nr_y=3)),
        ),
        BasePlate(
            [[True, True, True], [True, True], [True]],
            baseplate_block=BasePlateBlockFull(
                bottom_height=3,
                features=[
                    GridfinityRefinedScrewHole(BottomMiddle()),
                    GridfinityRefinedMagnetHolePressfit(BottomCorners()),
                ],
            ),
            features=GridfinityRefinedConnectionCutout(BottomSides(nr_x=3, nr_y=3)),
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

Convert.parts_to_gif(
    [
        BaseEqual(),
        BaseEqual(features=[ScrewHole(BottomCorners())]),
        BaseEqual(features=[ScrewHole(BottomCorners()), MagnetHole(BottomCorners())]),
        BaseEqual(
            features=[
                ScrewHole(BottomCorners()),
                MagnetHole(BottomCorners()),
                GridfinityRefinedThreadedScrewHole(BottomMiddle()),
            ],
        ),
        BaseEqual(
            features=[
                GridfinityRefinedMagnetHoleSide(BottomCorners()),
                GridfinityRefinedThreadedScrewHole(BottomMiddle()),
            ],
        ),
    ],
    "base",
    CameraPosition.CAMERA_BOT,
)

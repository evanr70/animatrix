"""Render animations of NumPy arrays."""

import subprocess
from collections.abc import Callable
from functools import partial
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter
from pqdm.processes import pqdm


def divisible_frame_size(fig: plt.Figure, dpi: int = 100) -> tuple[int, int]:
    """Return a frame size that is divisible by 2.

    Parameters
    ----------
    fig : plt.Figure
        Figure to get the frame size from.
    dpi : int, optional
        Dots per inch, by default 100.

    Returns
    -------
    tuple[int, int]
        Frame size that is divisible by 2.
    """
    original = np.floor(fig.get_size_inches() * dpi).astype(int)
    divisible = original + original % 2
    return divisible / dpi


def modify_figure_size(figure: plt.Figure, figsize: tuple[int, int]) -> plt.Figure:
    """Modify the figure size."""
    figure.set_size_inches(figsize[0], figsize[1])
    return figure


def generate_frame(
    func: Callable[[np.ndarray], plt.Figure],
    array_frame: np.ndarray,
    figsize: tuple[int, int] | None = None,
    dpi: int = 100,
) -> BytesIO:
    """Generate a frame of an animation.

    Parameters
    ----------
    func : Callable[[np.ndarray], plt.Figure]
        Function that generates a figure from an array.
    array_frame : np.ndarray
        Array to generate a frame from.
    figsize : tuple[int, int] | None, optional
        Figure size, by default None.
    dpi : int, optional
        Dots per inch, by default 100.

    Returns
    -------
    BytesIO
        BytesIO object containing the frame.
    """
    fig = func(array_frame)
    fig.dpi = dpi
    if figsize is not None:
        fig = modify_figure_size(fig, figsize)
    bytes_io = BytesIO()
    fig.savefig(bytes_io, format="rgba", dpi=dpi)
    plt.close(fig)
    return bytes_io


def generate_frames(
    func: Callable[[np.ndarray], plt.Figure],
    array_frames: np.ndarray,
    dpi: int = 100,
) -> list[BytesIO]:
    """Generate frames of an animation.

    Parameters
    ----------
    func : Callable[[np.ndarray], plt.Figure]
        Function that generates a figure from an array.
    array_frames : np.ndarray
        Array to generate frames from.
    dpi : int, optional
        Dots per inch, by default 100.

    Returns
    -------
    list[BytesIO]
        List of BytesIO objects containing the frames.
    """
    first_frame = func(array_frames[0])
    first_frame.canvas.draw()
    figsize = divisible_frame_size(first_frame)
    plt.close(first_frame)

    partial_generate_frame = partial(generate_frame, func, figsize=figsize, dpi=dpi)

    return pqdm(
        array=array_frames,
        function=partial_generate_frame,
        n_jobs=12,
        desc="Generating frames",
        exception_behaviour="immediate",
    ), figsize


class AnimationError(RuntimeError):
    """Error raised when an animation fails to render."""

    def __init__(self: "AnimationError", proc: subprocess.Popen) -> None:
        """Initialize an AnimationError.

        Parameters
        ----------
        proc : subprocess.Popen
            Process that failed.
        """
        self.returncode = proc.returncode
        self.stderr_output = proc.stderr.read()
        super().__init__(
            f"Error creating animation, ffmpeg returned error code "
            f"{self.returncode}:\n\n{self.stderr_output}"
        )


def create_ffmpeg_args(
    filename: str,
    figsize: tuple[int, int],
    fps: int = 30,
    dpi: int = 100,
) -> list[str]:
    """Create an FFMpegWriter.

    Parameters
    ----------
    filename : str
        Filename to write to.
    figsize : tuple[int, int]
        Figure size.
    fps : int, optional
        Frames per second, by default 30.
    dpi : int, optional
        Dots per inch, by default 100.

    Returns
    -------
    list[str]
        Arguments for ffmpeg.
    """
    writer = FFMpegWriter(fps=fps)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    writer.fig = fig
    writer.dpi = fig.dpi
    writer.outfile = filename
    args = writer._args()  # noqa: SLF001
    plt.close(fig)
    return args


def ffmpeg_write_frames(
    frames: list[BytesIO],
    filename: str,
    figsize: tuple[int, int],
    fps: int = 30,
    dpi: int = 100,
) -> None:
    """Write frames to a file using ffmpeg.

    Parameters
    ----------
    frames : list[BytesIO]
        List of BytesIO objects containing the frames.
    filename : str
        Filename to write to.
    figsize : tuple[int, int]
        Figure size.
    fps : int, optional
        Frames per second, by default 30.
    dpi : int, optional
        Dots per inch, by default 100.
    """
    ffmpeg_args = create_ffmpeg_args(filename, figsize, fps, dpi)

    pipe = subprocess.PIPE
    proc = subprocess.Popen(
        ffmpeg_args,  # noqa: S603
        stdin=pipe,
        stdout=pipe,
        stderr=pipe,
        creationflags=0,
        universal_newlines=True,
    )

    for frame in frames:
        proc.stdin.buffer.write(frame.getvalue())
    proc.stdin.close()
    proc.wait()
    if proc.returncode:
        raise AnimationError(proc)


def render_animation(
    func: Callable[[np.ndarray], plt.Figure],
    array_frames: np.ndarray,
    filename: str,
    fps: int = 30,
    dpi: int = 100,
) -> None:
    """Render an animation.

    Parameters
    ----------
    func : Callable[[np.ndarray], plt.Figure]
        Function that generates a figure from an array.
    array_frames : np.ndarray
        Array to generate frames from.
    filename : str
        Filename to write to.
    fps : int, optional
        Frames per second, by default 30.
    dpi : int, optional
        Dots per inch, by default 100.
    """
    frames, figsize = generate_frames(func, array_frames, dpi)
    ffmpeg_write_frames(frames, filename, figsize, fps, dpi)

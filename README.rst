.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/animatrix.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/animatrix
    .. image:: https://readthedocs.org/projects/animatrix/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://animatrix.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/animatrix/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/animatrix
    .. image:: https://img.shields.io/pypi/v/animatrix.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/animatrix/
    .. image:: https://img.shields.io/conda/vn/conda-forge/animatrix.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/animatrix
    .. image:: https://pepy.tech/badge/animatrix/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/animatrix
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/animatrix

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

=========
animatrix
=========


    Animate matplotlib plots in parallel.


Given a function that generates a matplotlib plot, animatrix will run the
function in parallel for a list of inputs and save the resulting plots as
a movie using ffmpeg.


=====
Usage
=====
::

    def plotter(array: np.ndarray, ymin: float, ymax: float) -> plt.Figure:
        fig, axes = plt.subplots(4, sharex=True, sharey=True)
        for axis, arr in zip(axes[:3], array):
            axis.plot(arr)
        axes[-1].plot(array.mean(axis=0))
        axes[-1].set_ylim(ymin, ymax)
        return fig

    def partial_plotter(array: np.ndarray) -> plt.Figure:
        return plotter(array, ymin=-1, ymax=1)

    x = np.arange(100)
    freqs = np.array([0.1, 0.2, 0.3])
    scaled = x * freqs[:, None]
    t = np.arange(300) * 0.5
    waves = np.sin(scaled[None] + t[:, None, None])

    render.render_animation(
        func=partial_plotter,
        array_frames=waves,
        filename="waves.gif",
        n_jobs=12,
        fps=30,
        dpi=100,
    )

.. image:: https://raw.githubusercontent.com/evanr70/animatrix/master/docs/assets/waves.gif
    :alt: waves
    :align: center

.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.

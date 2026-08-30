"""The two things every builder does: label a line end, size the box."""

from __future__ import annotations

from ..theme import MONO


def direct_label(fig, x, y, text, color, dx=6):
    fig.add_annotation(x=x, y=y, text=f" {text}", showarrow=False,
                       xanchor="left", yanchor="middle", xshift=dx,
                       font=dict(family=MONO, size=11, color=color))


def frame(fig, h=340, legend=True, **kw):
    fig.update_layout(height=h, showlegend=legend, **kw)
    return fig

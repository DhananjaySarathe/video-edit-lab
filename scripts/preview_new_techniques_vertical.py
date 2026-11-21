"""The newer technique demonstrations with native portrait crops and overlays."""

from functools import partial

from preview_new_techniques import AUDIO, POSTERS, SCENES as WIDESCREEN


SIZE = 360, 640
SCENES = {key: partial(scene, size=SIZE) for key, scene in WIDESCREEN.items()}

"""Scrollable camera / viewport logic.

The camera determines which rectangular slice of the full map is visible
on screen.  It stays centered on the player but clamps at map edges so
the viewport never shows out-of-bounds space.
"""


def compute_camera(player_x, player_y, map_width, map_height, view_w, view_h):
    """Return the top-left corner ``(cam_y, cam_x)`` of the viewport.

    The viewport is ``view_w`` columns wide and ``view_h`` rows tall.
    It tries to keep the player in the center, but is clamped so it
    never extends past the map boundaries.

    Parameters
    ----------
    player_x : int
        Player column in full-map coordinates.
    player_y : int
        Player row in full-map coordinates.
    map_width : int
        Total number of columns in the map.
    map_height : int
        Total number of rows in the map.
    view_w : int
        Width of the viewport (columns visible on screen).
    view_h : int
        Height of the viewport (rows visible on screen).

    Returns
    -------
    tuple[int, int]
        ``(cam_y, cam_x)`` — the row and column of the top-left map
        cell that should appear in the viewport.
    """
    # Start by centering the window on the player
    cam_x = player_x - view_w // 2
    cam_y = player_y - view_h // 2

    # Clamp so the window stays inside the map
    cam_x = max(0, min(cam_x, map_width - view_w))
    cam_y = max(0, min(cam_y, map_height - view_h))

    return cam_y, cam_x


if __name__ == '__main__':
    MAP_W, MAP_H = 40, 7
    VW, VH = 9, 7

    cases = [
        ('Left edge',   2,  3),
        ('Middle',     20,  3),
        ('Right edge', 37,  3),
        ('Top-left',    1,  0),
        ('Bottom-right',38, 6),
    ]

    for label, px, py in cases:
        cy, cx = compute_camera(px, py, MAP_W, MAP_H, VW, VH)
        print(f'{label:15s}  player=({py},{px})  cam=({cy},{cx})  '
              f'visible cols [{cx}..{cx + VW - 1}]  '
              f'visible rows [{cy}..{cy + VH - 1}]')

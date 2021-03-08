from PyQt5.QtWidgets import QGridLayout


def add_grid_to_layout(grid: list, layout: QGridLayout, start_index: int = 0):
    """Automatically adds a specified grid of QWidgets to
    a given Layout

    :param grid: The Grid to add to the Layout
    :param layout: The Layout to use
    :param start_index: What index to start at
    """
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] is not None:
                column_span = 1
                for k in range(j + 1, len(grid[i])):
                    if grid[i][k] is not None:
                        break
                    column_span += 1
                if isinstance(grid[i][j], tuple):
                    for grid_widget in grid[i][j]:
                        layout.addWidget(grid_widget, i + start_index, j, 1, column_span)
                else:
                    layout.addWidget(grid[i][j], i + start_index, j, 1, column_span)

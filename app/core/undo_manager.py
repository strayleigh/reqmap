"""
Undo/Redo command manager for ReqMap.
Provides QUndoStack support and LambdaUndoCommand for reversible operations.
"""
from typing import Callable
from PySide6.QtGui import QUndoCommand


class LambdaUndoCommand(QUndoCommand):
    """
    Generic undo command that wraps undo and redo callback functions.
    The first call to redo() triggered by QUndoStack.push() is ignored
    because the action was already executed immediately prior to push.
    """
    def __init__(self, undo_fn: Callable[[], None], redo_fn: Callable[[], None], description: str = ""):
        super().__init__(description)
        self.undo_fn = undo_fn
        self.redo_fn = redo_fn
        self._first_run = True

    def undo(self):
        self.undo_fn()

    def redo(self):
        if self._first_run:
            self._first_run = False
            return
        self.redo_fn()

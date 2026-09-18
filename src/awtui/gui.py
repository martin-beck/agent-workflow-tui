"""Premium Linux desktop renderer for the Agent Workflow decision session.

The GUI is an adapter over the same ``LiveInteraction`` view-model used by
the terminal renderer.  Qt is optional so headless/SSH environments retain a
small, reliable TUI installation.
"""
from __future__ import annotations

import sys
from typing import Any

from .discussion import Proposal
from .live import LiveInteraction, _default_packet, _packet_from_decisions


def _qt():
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
    except ImportError as error:  # pragma: no cover - depends on host install
        raise RuntimeError("GUI support requires the gui extra: pip install 'agent-workflow-ui[gui]'") from error
    return QtCore, QtGui, QtWidgets


class DecisionWindow:
    """Qt window exposing the complete batched decision interaction."""

    def __init__(self, interaction: LiveInteraction, *, title: str = "Agent Workflow", on_event=None) -> None:
        QtCore, QtGui, QtWidgets = _qt()
        self.QtCore, self.QtGui, self.QtWidgets = QtCore, QtGui, QtWidgets
        self.interaction = interaction
        self.on_event = on_event
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle(title)
        self.window.setMinimumSize(1050, 700)
        self.window.setStyleSheet(
            "QMainWindow { background:#10141d; } QWidget { color:#e7edf7; font-size:13px; }"
            "QFrame, QListWidget, QTextBrowser, QLineEdit { background:#171d29; border:1px solid #334158; border-radius:8px; }"
            "QPushButton { background:#2b6de0; border:0; border-radius:6px; padding:8px 14px; }"
            "QPushButton:hover { background:#4a86ed; } QListWidget::item:selected { background:#315fba; }"
        )
        self._build()
        self._refresh()

    def _build(self) -> None:
        QtWidgets = self.QtWidgets
        central = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(central)
        header = QtWidgets.QLabel("AGENT WORKFLOW  /  HUMAN DECISION SESSION")
        header.setStyleSheet("font-size:16px; font-weight:700; color:#8eb8ff; padding:4px;")
        root.addWidget(header)
        split = QtWidgets.QSplitter(self.QtCore.Qt.Orientation.Horizontal)
        docs = QtWidgets.QSplitter(self.QtCore.Qt.Orientation.Vertical)
        self.design = QtWidgets.QTextBrowser(); self.workplan = QtWidgets.QTextBrowser()
        self.design.setOpenExternalLinks(False); self.workplan.setOpenExternalLinks(False)
        docs.addWidget(self.design); docs.addWidget(self.workplan); docs.setSizes([1, 1])
        split.addWidget(docs)
        right = QtWidgets.QWidget(); right_layout = QtWidgets.QVBoxLayout(right)
        self.status = QtWidgets.QLabel(); right_layout.addWidget(self.status)
        self.points = QtWidgets.QListWidget(); self.points.currentRowChanged.connect(self._select_point); right_layout.addWidget(self.points, 2)
        self.proposals = QtWidgets.QListWidget(); self.proposals.currentRowChanged.connect(self._select_proposal); right_layout.addWidget(self.proposals, 2)
        self.helper = QtWidgets.QTextBrowser(); right_layout.addWidget(self.helper, 3)
        buttons = QtWidgets.QHBoxLayout()
        for label, callback in (("Select", self._select), ("Reject", lambda: self._respond("reject")), ("Clarify", lambda: self._respond("clarify")), ("More evidence", self._request_evidence), ("Reopen", self._reopen), ("Edit own proposal", self._edit)):
            button = QtWidgets.QPushButton(label); button.clicked.connect(callback); buttons.addWidget(button)
        right_layout.addLayout(buttons)
        bottom = QtWidgets.QHBoxLayout()
        self.document_button = QtWidgets.QPushButton("Switch document"); self.document_button.clicked.connect(self._switch_document); bottom.addWidget(self.document_button)
        save = QtWidgets.QPushButton("Save"); save.clicked.connect(self._save); bottom.addWidget(save)
        exit_button = QtWidgets.QPushButton("Save + Exit"); exit_button.clicked.connect(self._save_exit); bottom.addWidget(exit_button)
        right_layout.addLayout(bottom)
        split.addWidget(right); split.setSizes([700, 420])
        root.addWidget(split, 1)
        self.window.setCentralWidget(central)

    def _select_point(self, index: int) -> None:
        if index >= 0:
            self.interaction.point_index = index
            self.interaction.proposal_index = 0
            self._refresh()

    def _select_proposal(self, index: int) -> None:
        if index >= 0:
            self.interaction.proposal_index = index
            self._refresh_helper()

    def _respond(self, disposition: str) -> None:
        self.interaction.respond(disposition)
        if self.on_event is not None:
            self.on_event({"event_type": disposition, "point_id": self.interaction.point.point_id,
                           "disposition": disposition,
                           "selected": self.interaction.responses[self.interaction.point.point_id].selected})
        self._refresh()

    def _select(self) -> None:
        self._respond("select")

    def _request_evidence(self) -> None:
        self.helper.setPlainText("More evidence requested for this decision. The Coordinator will keep it unresolved until evidence is supplied.")

    def _reopen(self) -> None:
        self.interaction.responses.pop(self.interaction.point.point_id, None)
        self.interaction.saved = False
        if self.on_event is not None:
            self.on_event({"event_type": "reopen", "point_id": self.interaction.point.point_id})
        self._refresh()

    def _switch_document(self) -> None:
        self.interaction.switch_document(); self._refresh()

    def _save(self) -> None:
        self.interaction.saved = True; self._refresh()

    def _save_exit(self) -> None:
        self._save()
        if self.on_event is not None:
            self.on_event({"event_type": "safe-exit", "point_id": self.interaction.point.point_id})
        self.window.close()

    def _edit(self) -> None:
        if not self.interaction.begin_edit_proposal():
            self._new_proposal()
            return
        self._new_proposal(editing=True)

    def _new_proposal(self, *, editing: bool = False) -> None:
        QtWidgets = self.QtWidgets
        dialog = QtWidgets.QDialog(self.window); dialog.setWindowTitle("Edit proposal" if editing else "Add proposal")
        form = QtWidgets.QFormLayout(dialog)
        fields = []
        values = [self.interaction.proposal.label.removeprefix("User: ") if editing else "", self.interaction.proposal.rationale if editing else "", str(self.interaction.proposal.confidence) if editing else "0.7", self.interaction.proposal.tradeoffs if editing else ""]
        for name, value in zip(("Label", "Rationale", "Confidence (0..1)", "Trade-offs"), values):
            field = QtWidgets.QLineEdit(value); form.addRow(name, field); fields.append(field)
        ok = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel); form.addRow(ok)
        ok.accepted.connect(dialog.accept); ok.rejected.connect(dialog.reject)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            try:
                proposal = Proposal("User: " + fields[0].text().strip(), fields[1].text().strip(), float(fields[2].text()), fields[3].text().strip())
                self.interaction.add_proposal(proposal); self._refresh()
                if self.on_event is not None:
                    self.on_event({"event_type": "add-proposal", "point_id": self.interaction.point.point_id,
                                   "user_proposal": {"label": proposal.label, "rationale": proposal.rationale,
                                                      "confidence": proposal.confidence, "tradeoffs": proposal.tradeoffs}})
            except (ValueError, TypeError) as error:
                QtWidgets.QMessageBox.warning(self.window, "Invalid proposal", str(error))

    def _refresh_helper(self) -> None:
        self.helper.setPlainText(self.interaction.render_helper())

    def _highlight_document(self, widget: Any, phrase: str) -> None:
        cursor = widget.document().find(phrase)
        selections = []
        if not cursor.isNull():
            selection = self.QtWidgets.QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format.setBackground(self.QtGui.QColor("#d6a84f"))
            selection.format.setForeground(self.QtGui.QColor("#111722"))
            selections.append(selection)
            widget.setTextCursor(cursor)
            widget.ensureCursorVisible()
        widget.setExtraSelections(selections)

    def _refresh(self) -> None:
        self.points.blockSignals(True); self.points.clear()
        for point in self.interaction.packet.points:
            response = self.interaction.responses.get(point.point_id)
            marker = "✓" if response and response.disposition == "select" else "•"
            self.points.addItem(f"{marker} {point.point_id}  {point.anchor}")
        self.points.setCurrentRow(self.interaction.point_index); self.points.blockSignals(False)
        self.proposals.blockSignals(True); self.proposals.clear()
        point = self.interaction.point
        response = self.interaction.responses.get(point.point_id)
        visible = [self.interaction.proposal] if response and response.selected else list(point.proposals)
        for proposal in visible: self.proposals.addItem(proposal.label)
        self.proposals.setCurrentRow(min(self.interaction.proposal_index, max(0, len(visible) - 1))); self.proposals.blockSignals(False)
        design_document = self.interaction.packet_document("design") if hasattr(self.interaction, "packet_document") else ""
        workplan_document = self.interaction.packet_document("workplan") if hasattr(self.interaction, "packet_document") else ""
        self.design.setMarkdown(design_document)
        self.workplan.setMarkdown(workplan_document)
        self._highlight_document(self.design, self.interaction.point.document_highlights.get("design", self.interaction.point.highlight or self.interaction.point.question))
        self._highlight_document(self.workplan, self.interaction.point.document_highlights.get("workplan", self.interaction.point.highlight or self.interaction.point.question))
        self.status.setText(f"Decision {self.interaction.point_index + 1}/{len(self.interaction.packet.points)}  |  {'saved' if self.interaction.saved else 'unsaved'}  |  selected {sum(r.disposition == 'select' for r in self.interaction.responses.values())}/{len(self.interaction.packet.points)}")
        self._refresh_helper()

    def run(self) -> int:
        self.window.show()
        return self.app.exec()


def build_gui_application(*, design_document: str = "# Design\n\nAwaiting AR context", workplan: str = "# Work plan\n\nAwaiting AR context", decisions: list[dict[str, Any]] | None = None, on_event=None) -> DecisionWindow:
    packet = _packet_from_decisions(decisions, design_document, workplan) if decisions else _default_packet("design", "Review the design")
    interaction = LiveInteraction(packet)
    # Keep source Markdown in the shared view-model for both renderers.
    interaction.packet_document = lambda mode: design_document if mode == "design" else workplan  # type: ignore[attr-defined]
    return DecisionWindow(interaction, on_event=on_event)


def main() -> int:
    return build_gui_application().run()


if __name__ == "__main__":
    raise SystemExit(main())

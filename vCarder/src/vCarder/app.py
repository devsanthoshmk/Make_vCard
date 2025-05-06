#!/usr/bin/env python
"""
vCarder - A cross-platform app for creating vCards from various data sources.

Usage:
    $ python -m toga_demo
    or if installed as an app:
    $ vcarder
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import re
import os


class VCarderApp(toga.App):
    """Main application class for vCarder."""

    def startup(self):
        """Build and show the main window for the vCarder application."""
        # Prevent recursive dropdown updates
        self._updating_dropdowns = False

        # Main window configuration
        self.main_window = toga.MainWindow(title="vCarder", size=(800, 600))

        # Track selected columns for dynamic exclusion
        self.selected_columns = set()

        # Sample data for preview
        self.dummy_data = [
            {
                "First": "John",
                "Last": "Doe",
                "Phone": "555-1234",
                "Email": "john@example.com",
                "Address": "123 Main St",
                "Company": "ACME Inc",
                "Position": "Developer",
                "Website": "johndoe.com",
            },
            {
                "First": "Jane",
                "Last": "Smith",
                "Phone": "555-9876",
                "Email": "jane@example.com",
                "Address": "456 Oak Ave",
                "Company": "TechCorp",
                "Position": "Designer",
                "Website": "janesmith.com",
            },
            {
                "First": "Alex",
                "Last": "Johnson",
                "Phone": "555-5555",
                "Email": "alex@example.com",
                "Address": "789 Pine Blvd",
                "Company": "StartupXYZ",
                "Position": "Manager",
                "Website": "alexj.net",
            },
        ]
        self.all_columns = list(self.dummy_data[0].keys())

        # Scrollable main container
        main_scroll = toga.ScrollContainer(horizontal=False, style=Pack(flex=1))
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))

        # Build UI sections
        main_box.add(self.create_file_chooser_section())
        main_box.add(self.create_data_preview_section())
        main_box.add(self.create_field_mapping_section())
        main_box.add(self.create_additional_fields_section())
        main_box.add(self.create_action_section())
        main_box.add(self.create_footer())

        main_scroll.content = main_box
        self.main_window.content = main_scroll
        self.main_window.show()

    def create_menus(self):
        """Create application menu structure."""
        file_group = toga.Group("File", order=0)
        contact_group = toga.Group("Contact", order=1)
        help_group = toga.Group("Help", order=2)

        self.commands.add(
            toga.Command(
                self.action_open_file,
                text="Open Source File…",
                shortcut=toga.Key.MOD_1 + "o",
                group=file_group,
            ),
            toga.Command(
                lambda w: self.exit(),
                text="Exit",
                shortcut=toga.Key.MOD_1 + "q",
                group=file_group,
            ),
            toga.Command(
                lambda w: self.open_url("mailto:contact@vcarder.app"),
                text="Email",
                group=contact_group,
            ),
            toga.Command(
                lambda w: self.open_url("tel:+1234567890"),
                text="Phone",
                group=contact_group,
            ),
            toga.Command(
                lambda w: self.open_url("https://github.com/vcarder"),
                text="Github",
                group=contact_group,
            ),
            toga.Command(
                lambda w: self.open_url("https://instagram.com/vcarder"),
                text="Instagram",
                group=contact_group,
            ),
            toga.Command(self.show_about, text="About vCarder", group=help_group),
        )

    def create_file_chooser_section(self):
        section = toga.Box(style=Pack(direction=COLUMN, padding_bottom=20))
        section.add(
            toga.Label("Source File", style=Pack(font_size=16, padding_bottom=10))
        )
        btn = toga.Button(
            "Choose Source File", on_press=self.action_open_file, style=Pack(padding=10)
        )
        self.file_label = toga.Label("No file selected", style=Pack(padding_top=10))
        section.add(btn)
        section.add(self.file_label)
        return section

    def create_data_preview_section(self):
        section = toga.Box(style=Pack(direction=COLUMN, padding_bottom=20))
        section.add(
            toga.Label("Data Preview", style=Pack(font_size=16, padding_bottom=10))
        )
        self.data_table = toga.Table(
            headings=self.all_columns,
            data=[[row[col] for col in self.all_columns] for row in self.dummy_data],
            style=Pack(height=150),
        )
        scroll = toga.ScrollContainer(horizontal=True, style=Pack(height=200))
        scroll.content = self.data_table
        section.add(scroll)
        return section

    def create_field_mapping_section(self):
        section = toga.Box(style=Pack(direction=COLUMN, padding_bottom=20))
        section.add(
            toga.Label("Field Mapping", style=Pack(font_size=16, padding_bottom=10))
        )
        self.mapping_fields = {}
        for field in [
            "First Name",
            "Last Name",
            "Full Name",
            "Phone",
            "Address",
            "Email",
        ]:
            box = toga.Box(style=Pack(direction=ROW, padding=5))
            box.add(toga.Label(f"{field}:", style=Pack(width=120, padding_top=8)))
            sel = toga.Selection(
                items=self.get_available_columns(),
                on_change=self.on_mapping_selection,
                style=Pack(flex=1, padding=5),
            )
            self.mapping_fields[field] = sel
            box.add(sel)
            section.add(box)
        return section

    def create_additional_fields_section(self):
        section = toga.Box(style=Pack(direction=COLUMN, padding_bottom=20))
        section.add(
            toga.Label("Additional", style=Pack(font_size=16, padding_bottom=10))
        )
        self.additional_fields = [
            "Additional Phone Number",
            "Organization",
            "Title",
            "URL",
            "Birthday",
        ]
        self.additional_field_selections = {}
        selector = toga.Selection(
            items=self.additional_fields,
            on_change=self.on_additional_field_select,
            style=Pack(padding=5),
        )
        box = toga.Box(style=Pack(direction=ROW, padding=5))
        box.add(toga.Label("Add field:", style=Pack(width=120, padding_top=8)))
        box.add(selector)
        section.add(box)
        self.additional_fields_box = toga.Box(style=Pack(direction=COLUMN))
        section.add(self.additional_fields_box)
        return section

    def create_action_section(self):
        section = toga.Box(style=Pack(direction=COLUMN, padding_bottom=20))
        btn_vcard = toga.Button(
            "Get vCard", on_press=self.action_get_vcard, style=Pack(padding=10)
        )
        btn_report = toga.Button(
            "Report!", on_press=self.action_report_issue, style=Pack(padding=10)
        )
        box = toga.Box(style=Pack(direction=ROW, padding=5))
        box.add(btn_vcard)
        box.add(btn_report)
        section.add(box)
        return section

    def create_footer(self):
        footer = toga.Box(style=Pack(direction=ROW, padding=10, alignment="center"))
        footer.add(toga.Label("vCarder v0.1", style=Pack(padding=(0, 10))))
        for text, url in [
            ("Email", "mailto:contact@vcarder.app"),
            ("Phone", "tel:+1234567890"),
            ("Github", "https://github.com/vcarder"),
            ("Instagram", "https://instagram.com/vcarder"),
        ]:
            footer.add(
                toga.Button(
                    text,
                    on_press=lambda w, u=url: self.open_url(u),
                    style=Pack(padding=(0, 5)),
                )
            )
        footer.add(toga.Label("© 2025 vCarder", style=Pack(padding=(0, 10))))
        return footer

    def get_available_columns(self):
        return [c for c in self.all_columns if c not in self.selected_columns]

    def on_mapping_selection(self, widget, **kwargs):
        # Update selection set
        self.selected_columns.clear()
        for sel in list(self.mapping_fields.values()) + list(
            self.additional_field_selections.values()
        ):
            if sel.value:
                self.selected_columns.add(sel.value)
        self.update_all_dropdowns()

    def on_additional_field_select(self, widget, **kwargs):
        field = widget.value
        if not field or field in self.additional_field_selections:
            widget.value = None
            return
        box = toga.Box(style=Pack(direction=ROW, padding=5))
        box.add(toga.Label(f"{field}:", style=Pack(width=120, padding_top=8)))
        sel = toga.Selection(
            items=self.get_available_columns(),
            on_change=self.on_mapping_selection,
            style=Pack(flex=1, padding=5),
        )
        btn = toga.Button(
            "✕",
            on_press=lambda w, f=field: self.remove_additional_field(f),
            style=Pack(width=30),
        )
        self.additional_field_selections[field] = sel
        box.add(sel)
        box.add(btn)
        self.additional_fields_box.add(box)
        widget.value = None

    def remove_additional_field(self, field):
        # Remove field box and selection
        for child in self.additional_fields_box.children:
            if child.children[0].text.startswith(field):
                sel = self.additional_field_selections.pop(field)
                if sel.value:
                    self.selected_columns.discard(sel.value)
                self.additional_fields_box.remove(child)
                break
        self.update_all_dropdowns()

    def update_all_dropdowns(self):
        if self._updating_dropdowns:
            return
        self._updating_dropdowns = True
        try:
            cols = self.get_available_columns()
            for sel in list(self.mapping_fields.values()) + list(
                self.additional_field_selections.values()
            ):
                val = sel.value
                sel.items = [val] + [c for c in cols if c != val] if val else cols
                sel.value = val
        finally:
            self._updating_dropdowns = False

    def action_open_file(self, widget):
        try:
            self.main_window.open_file_dialog(
                title="Select Source File",
                file_types=["csv", "xlsx", "ods"],
                on_result=self.file_dialog_result,
            )
        except ValueError as e:
            self.main_window.error_dialog("Error", str(e))

    def file_dialog_result(self, dialog, path):
        if path:
            self.file_label.text = f"Selected: {os.path.basename(path)}"

    def action_get_vcard(self, widget):
        mappings = {}
        for k, sel in self.mapping_fields.items():
            if sel.value:
                mappings[k] = sel.value
        for k, sel in self.additional_field_selections.items():
            if sel.value:
                mappings[k] = sel.value
        print("vCard mappings:", mappings)

    def action_report_issue(self, widget):
        self.show_report_dialog()

    def show_report_dialog(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        # Email input
        ebox = toga.Box(style=Pack(direction=ROW, padding=5))
        ebox.add(toga.Label("Email:", style=Pack(width=100)))
        email_input = toga.TextInput(style=Pack(flex=1))
        ebox.add(email_input)
        # Issue input
        ibox = toga.Box(style=Pack(direction=COLUMN, padding=5))
        ibox.add(toga.Label("Describe the issue:", style=Pack(padding_bottom=5)))
        issue_input = toga.MultilineTextInput(style=Pack(height=150))
        ibox.add(issue_input)
        box.add(ebox)
        box.add(ibox)

        def on_submit(dialog):
            if not self.validate_email(email_input.value):
                self.main_window.error_dialog(
                    "Invalid Email", "Please enter a valid email."
                )
                return
            if not issue_input.value.strip():
                self.main_window.error_dialog(
                    "Missing Information", "Please describe the issue."
                )
                return
            dialog.close()
            self.main_window.info_dialog(
                "Report Submitted",
                f"Thanks! We'll respond to {email_input.value} soon.",
            )
            print("Report:", email_input.value, issue_input.value)

        self.main_window.dialog(
            title="Report an Issue", content=box, on_result=on_submit
        )

    def validate_email(self, email):
        return bool(
            re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email or "")
        )

    def show_about(self, widget):
        self.main_window.info_dialog("About vCarder", "vCarder v0.1 - © 2025 vCarder")

    def open_url(self, url):
        import webbrowser

        try:
            webbrowser.open(url)
        except Exception as e:
            self.main_window.error_dialog("Error", str(e))


def main():
    return VCarderApp()


if __name__ == "__main__":
    app = main()
    app.main_loop()

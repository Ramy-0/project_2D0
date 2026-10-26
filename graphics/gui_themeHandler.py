import flet as ft
from catppuccin import PALETTE

def get_theme_catppuccin(theme:str):
    if theme in ['latte', 'frappe', 'macchiato', 'mocha']:
        # for now always return frappe
        flavor = PALETTE.frappe.colors

        page_theme = ft.Theme(
        use_material3=True,
        scaffold_bgcolor=flavor.base.hex,
        card_bgcolor=flavor.surface0.hex,
        color_scheme=ft.ColorScheme(
            primary=flavor.mauve.hex,
            on_primary=flavor.base.hex,
            primary_container=flavor.surface1.hex,
            on_primary_container=flavor.mauve.hex,

            secondary=flavor.pink.hex,
            on_secondary=flavor.base.hex,
            secondary_container=flavor.surface1.hex,
            on_secondary_container=flavor.pink.hex,

            tertiary=flavor.teal.hex,
            on_tertiary=flavor.base.hex,
            tertiary_container=flavor.surface1.hex,
            on_tertiary_container=flavor.teal.hex,

            error=flavor.red.hex,
            on_error=flavor.base.hex,
            error_container=flavor.surface1.hex,
            on_error_container=flavor.red.hex,

            surface=flavor.base.hex,
            on_surface=flavor.text.hex,
            on_surface_variant=flavor.subtext0.hex,
            surface_container_lowest=flavor.crust.hex,
            surface_container_low=flavor.mantle.hex,
            surface_container=flavor.surface0.hex,
            surface_container_high=flavor.surface1.hex,
            surface_container_highest=flavor.surface2.hex,

            outline=flavor.overlay1.hex,
            outline_variant=flavor.overlay0.hex,
            shadow=flavor.crust.hex,
            scrim=flavor.crust.hex,

            inverse_surface=flavor.text.hex,
            on_inverse_surface=flavor.base.hex,
            inverse_primary=flavor.lavender.hex,
        ),
    )

        return page_theme, flavor

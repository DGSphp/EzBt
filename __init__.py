import logging
import os
from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import panel_custom
from .const import DOMAIN, CONF_SHOW_SIDEBAR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EzBt from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Register the static path for the panel files
    static_path = os.path.join(os.path.dirname(__file__), "www")
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/ezbt_static", static_path, False)]
    )

    # Register/Remove the custom panel based on options
    show_sidebar = entry.options.get(CONF_SHOW_SIDEBAR, True)
    if show_sidebar:
        try:
            await panel_custom.async_register_panel(
                hass,
                webcomponent_name="ezbt-panel",
                frontend_url_path="ezbt",
                sidebar_title="EzBt",
                sidebar_icon="mdi:bluetooth",
                module_url="/ezbt_static/ezbt-panel.js",
                require_admin=True,
            )
        except ValueError:
            # Panel already registered (can happen on reload)
            pass

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    from .coordinator import BluetoothCoordinator
    coordinator = BluetoothCoordinator(hass)
    hass.data[DOMAIN]["coordinator"] = coordinator

    async def handle_scan(call):
        devices = await coordinator.async_scan()
        return {"devices": list(devices.values())}

    async def handle_pair(call):
        address = call.data.get("address")
        _LOGGER.info("Pairing with device: %s", address)
        # In a real implementation, this would call bluetooth pairing logic
        if address in coordinator.discovered_devices:
            coordinator.discovered_devices[address]["connected"] = True
            coordinator.async_set_updated_data(coordinator.discovered_devices)
        return True

    async def handle_disconnect(call):
        address = call.data.get("address")
        _LOGGER.info("Disconnecting device: %s", address)
        if address in coordinator.discovered_devices:
            coordinator.discovered_devices[address]["connected"] = False
            coordinator.async_set_updated_data(coordinator.discovered_devices)
        return True

    hass.services.async_register(
        DOMAIN, "scan", handle_scan, supports_response=SupportsResponse.OPTIONAL
    )
    hass.services.async_register(DOMAIN, "pair_device", handle_pair)
    hass.services.async_register(DOMAIN, "disconnect_device", handle_disconnect)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop("coordinator", None)
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

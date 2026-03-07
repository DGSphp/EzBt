import logging
import os
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.frontend import async_register_panel, async_remove_panel
from .const import DOMAIN, CONF_SHOW_SIDEBAR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EzBt from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Register the static path for the panel files
    static_path = os.path.join(os.path.dirname(__file__), "www")
    hass.http.register_static_path("/ezbt_static", static_path, cache_headers=False)

    # Register/Remove the custom panel based on options
    show_sidebar = entry.options.get(CONF_SHOW_SIDEBAR, True)
    if show_sidebar:
        async_register_panel(
            hass,
            "ezbt",
            "ezbt-panel",
            sidebar_title="EzBt",
            sidebar_icon="mdi:bluetooth",
            module_url="/ezbt_static/ezbt-panel.js",
            require_admin=True,
        )
    else:
        async_remove_panel(hass, "ezbt")

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    from .coordinator import BluetoothCoordinator
    coordinator = BluetoothCoordinator(hass)
    hass.data[DOMAIN]["coordinator"] = coordinator

    async def handle_scan(call):
        await coordinator.async_scan()

    async def handle_pair(call):
        address = call.data.get("address")
        _LOGGER.info("Pairing with device: %s", address)
        # Here we would use the bluetooth component to connect
        # For now, we simulate success
        return True

    hass.services.async_register(DOMAIN, "scan", handle_scan)
    hass.services.async_register(DOMAIN, "pair_device", handle_pair)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    async_remove_panel(hass, "ezbt")
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

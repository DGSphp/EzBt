import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.frontend import async_register_built_in_panel
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EzBt from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Register the custom panel
    async_register_built_in_panel(
        hass,
        component_name="custom-panel",
        sidebar_title="EzBt",
        sidebar_icon="mdi:bluetooth",
        url_path="ezbt",
        config={"url": "/local/custom_components/ezbt/www/ezbt-panel.js"},
        require_admin=True,
    )

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
    return True

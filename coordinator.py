import logging
import asyncio
from typing import Dict, Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.components.bluetooth import (
    async_get_scanner,
    async_discovered_service_info,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class BluetoothCoordinator(DataUpdateCoordinator):
    """Bluetooth Discovery Coordinator."""

    def __init__(self, hass: HomeAssistant):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name="EzBt Bluetooth Discovery",
            update_interval=None,  # Manual updates
        )
        self.discovered_devices: Dict[str, Any] = {}

    @callback
    def _async_device_discovered(self, service_info, change):
        """Handle discovered devices."""
        device = service_info.device
        adv_data = service_info.advertisement
        
        # Filter for Speaker/HID (Simplified)
        # In a real scenario, we'd check adv_data.service_uuids or manufacturer_data
        is_relevant = False
        name = (device.name or adv_data.local_name or "").lower()
        relevant_keywords = ["speaker", "hid", "mouse", "keyboard", "headset"]
        if any(keyword in name for keyword in relevant_keywords):
            is_relevant = True
            
        if is_relevant:
            self.discovered_devices[device.address] = {
                "name": device.name or adv_data.local_name or "Unknown",
                "address": device.address,
                "rssi": service_info.rssi,
                "connected": False, # Initial state
            }
            self.async_set_updated_data(self.discovered_devices)

    async def async_scan(self):
        """Perform a scan for Bluetooth devices."""
        self.discovered_devices = {}
        # Get discovered info from HA bluetooth component
        for service_info in async_discovered_service_info(self.hass):
            self._async_device_discovered(service_info, "discovered")
        
        return self.discovered_devices

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
        
        # Store all discovered devices (removing the filter to ensure we see everything)
        self.discovered_devices[device.address] = {
            "name": device.name or adv_data.local_name or "Unknown",
            "address": device.address,
            "rssi": service_info.rssi,
            "connected": False, # Initial state
        }
        self.async_set_updated_data(self.discovered_devices)

    async def async_scan(self):
        """Perform a scan for Bluetooth devices."""
        _LOGGER.info("Starting EzBt diagnostic scan...")
        
        # Check scanner availability
        scanner = async_get_scanner(self.hass)
        if scanner:
             _LOGGER.info("EzBt: Bluetooth scanner is available: %s", scanner)
        else:
             _LOGGER.warning("EzBt: No Bluetooth scanner found! Bluetooth might not be enabled or configured.")

        self.discovered_devices = {}
        # Get discovered info from HA bluetooth component
        all_info = list(async_discovered_service_info(self.hass))
        _LOGGER.info("EzBt: HA Bluetooth cache contains %d devices", len(all_info))
        
        for service_info in all_info:
            device = service_info.device
            adv_data = service_info.advertisement
            _LOGGER.debug(
                "EzBt: Discovered device: %s [%s] RSSI: %d", 
                device.name or adv_data.local_name or "Unknown", 
                device.address,
                service_info.rssi
            )
            self._async_device_discovered(service_info, "discovered")
        
        _LOGGER.info("EzBt diagnostic scan complete. Found %d valid devices.", len(self.discovered_devices))
        return self.discovered_devices

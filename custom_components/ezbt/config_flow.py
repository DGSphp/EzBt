from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN, CONF_SHOW_SIDEBAR

class EzBtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EzBt."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="EzBt", data={})

        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return EzBtOptionsFlowHandler(config_entry)

class EzBtOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle EzBt options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SHOW_SIDEBAR,
                        default=self.config_entry.options.get(CONF_SHOW_SIDEBAR, True),
                    ): bool,
                }
            ),
        )
